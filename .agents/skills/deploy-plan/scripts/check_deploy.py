# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""驗證 deploy-plan 交出的 compose.yaml 與它的附檔。

檢查項目:compose.yaml 是有 services 的 YAML、每個服務都有 x-requirements、
compose 用到的每個 ${變數} 都列在同一個資料夾的 .env.example 而且沒有值、名稱像機密的環境變數都寫成 ${變數}、
有 build 的服務找得到 Dockerfile、bind mount 指到的設定檔存在、
這台機器有 docker compose 時 `docker compose config -q` 通過(沒有就標成略過)、
plan.md 這一步端點的需求出處都對得到服務、x-requirements 的需求編號都在 spec.md 裡。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ENDPOINT_ROW = re.compile(r"^\| E(\d+) \|(.*)\|$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")  # Markdown 表格裡跳脫的 \| 是內容,不是欄分隔
WAVE_ROW = re.compile(r"^\| (\d+) \| S(\d+) \| E(\d+) ")
RANGE = re.compile(r"\b(FR|NFR|SC)-(\d+)\s*[–—~]\s*(?:(?:FR|NFR|SC)-)?(\d+)\b")
REQUIREMENT_ID = re.compile(r"\b((?:FR|NFR|SC)-\d+)\b")
VARIABLE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::?[-?+][^}]*)?\}")
SECRET_NAME = re.compile(r"PASSWORD|PASSWD|SECRET|TOKEN|CREDENTIAL|(?:^|_)(?:KEY|IV)(?:$|_)", re.IGNORECASE)
CONFIG_SUFFIXES = {".conf", ".yaml", ".yml", ".json", ".toml", ".ini", ".js", ".html", ".sql", ".sh", ".template"}

R_PARSE = "compose.yaml 是有 services 的 YAML"
R_TAGGED = "每個服務都有 x-requirements"
R_ENV = "${變數} 都列在 .env.example 且沒有值,機密都寫成 ${變數}"
R_FILES = "Dockerfile 與 bind mount 的設定檔都存在"
R_COMPOSE = "docker compose config -q 通過"
R_COVERAGE = "plan.md 這一步的需求出處都對得到服務"
R_SOURCES = "x-requirements 的需求編號都在 spec.md 裡"
RULES = [R_PARSE, R_TAGGED, R_ENV, R_FILES, R_COMPOSE, R_COVERAGE, R_SOURCES]


def section(lines: list[str], heading: str) -> list[str]:
    """取出某個標題底下、到下一個同級或更高標題之前的行。"""
    level = len(heading) - len(heading.lstrip("#"))
    inside, picked = False, []
    for line in lines:
        if line.startswith("#") and not line.startswith("#" * (level + 1)):
            inside = line.strip() == heading
            continue
        if inside:
            picked.append(line)
    return picked


def requirement_ids(text: str) -> set[str]:
    """取出一段文字裡的需求編號,`FR-001–FR-019` 這類範圍展開成每一個編號。"""
    ids = set(REQUIREMENT_ID.findall(text))
    for kind, start, end in RANGE.findall(text):
        ids |= {f"{kind}-{n:0{len(start)}d}" for n in range(int(start), int(end) + 1)}
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--compose", required=True, type=Path, help="deploy/compose.yaml 的路徑;.env.example 與附檔要在同一個資料夾")
    parser.add_argument("--plan", required=True, type=Path, help="system-analysis 產出的 plan.md 路徑,用來找這一步分析的端點與需求出處")
    parser.add_argument("--spec", required=True, type=Path, help="spec.md 的路徑,用來確認需求編號都有定義")
    parser.add_argument("--step", required=True, help="這份部署檔對應的波段表步驟編號,例如 S5")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    step_match = re.fullmatch(r"S?(\d+)", args.step.strip())
    if not step_match:
        print(f"錯誤: --step 收到「{args.step}」,要給波段表的步驟編號,例如 S5。", file=sys.stderr)
        return 2
    step = int(step_match.group(1))
    for path in (args.compose, args.plan, args.spec):
        if not path.is_file():
            print(f"錯誤: 找不到 {path};--compose、--plan、--spec 都要給檔案路徑。", file=sys.stderr)
            return 2

    deploy_dir = args.compose.parent
    raw = args.compose.read_text(encoding="utf-8")
    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, where: str, reason: str) -> None:
        violations[rule].append({"where": where, "reason": reason})

    compose = None
    try:
        compose = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        bad(R_PARSE, str(args.compose), f"不是合法的 YAML:{exc}")
    services = (compose or {}).get("services") if isinstance(compose, dict) else None
    if compose is not None and not isinstance(services, dict):
        bad(R_PARSE, str(args.compose), "沒有 services")
    services = services if isinstance(services, dict) else {}

    tagged: set[str] = set()
    for name, svc in services.items():
        svc = svc or {}
        reqs = svc.get("x-requirements") or []
        if not reqs:
            bad(R_TAGGED, f"services.{name}", "沒有 x-requirements")
        tagged |= {str(r) for r in reqs}

        env = svc.get("environment") or {}
        pairs = env.items() if isinstance(env, dict) else (tuple(e.split("=", 1)) if "=" in e else (e, None) for e in env)
        for key, value in pairs:
            if SECRET_NAME.search(str(key)) and value is not None and not VARIABLE.fullmatch(str(value).strip()):
                bad(R_ENV, f"services.{name}.environment.{key}", "名稱像機密,值要寫成 ${變數}")

        build = svc.get("build")
        if build is not None:
            context = deploy_dir / (build if isinstance(build, str) else build.get("context", "."))
            dockerfile = context / ("Dockerfile" if isinstance(build, str) else build.get("dockerfile", "Dockerfile"))
            if not dockerfile.is_file():
                bad(R_FILES, f"services.{name}.build", f"找不到 Dockerfile:{dockerfile}")

        for volume in svc.get("volumes") or []:
            source = volume.split(":", 1)[0] if isinstance(volume, str) else (volume or {}).get("source", "")
            if source.startswith((".", "/")) and Path(source).suffix in CONFIG_SUFFIXES and not (deploy_dir / source).is_file():
                bad(R_FILES, f"services.{name}.volumes", f"bind mount 的設定檔 {source} 不存在")

    used = set(VARIABLE.findall(raw))
    env_example = deploy_dir / ".env.example"
    listed: set[str] = set()
    if used and not env_example.is_file():
        bad(R_ENV, ".env.example", f"compose 用到 {len(used)} 個變數,但 {env_example} 不存在")
    elif env_example.is_file():
        for number, line in enumerate(env_example.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)", stripped)
            if not match:
                bad(R_ENV, f".env.example 第 {number} 行", "格式不符 NAME=")
                continue
            listed.add(match.group(1))
            if match.group(2).strip():
                bad(R_ENV, f".env.example 第 {number} 行", f"{match.group(1)} 有值,等號後面要留空")
        for var in sorted(used - listed):
            bad(R_ENV, ".env.example", f"compose 用到的 ${{{var}}} 沒有列在 .env.example")

    compose_skipped = True
    if compose is not None and shutil.which("docker"):
        probe = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
        if probe.returncode == 0:
            compose_skipped = False
            result = subprocess.run(["docker", "compose", "-f", str(args.compose.resolve()), "config", "-q"], capture_output=True, text=True, cwd=deploy_dir)
            if result.returncode != 0:
                bad(R_COMPOSE, str(args.compose), (result.stderr or result.stdout).strip().splitlines()[-1] if (result.stderr or result.stdout).strip() else f"exit code {result.returncode}")
    if compose_skipped:
        print("提示: 這台機器沒有 docker compose,`docker compose config -q` 略過。", file=sys.stderr)

    plan_lines = args.plan.read_text(encoding="utf-8").splitlines()
    endpoint = next((int(m.group(3)) for l in section(plan_lines, "### 分析波段") if (m := WAVE_ROW.match(l.strip())) and int(m.group(2)) == step), None)
    needed: set[str] = set()
    if endpoint is None:
        bad(R_COVERAGE, "plan.md", f"`### 分析波段` 沒有 S{step}")
    else:
        row = next((m.group(2) for l in section(plan_lines, "### 端點盤點") if (m := ENDPOINT_ROW.match(l.strip())) and int(m.group(1)) == endpoint), None)
        if row is None:
            bad(R_COVERAGE, "plan.md", f"S{step} 分析的 E{endpoint} 不在 `### 端點盤點`")
        else:
            needed = requirement_ids(CELL_SPLIT.split(row)[-1])
    for rid in sorted(needed - tagged):
        bad(R_COVERAGE, rid, f"E{endpoint} 的需求出處 {rid} 沒有任何服務的 x-requirements 對到")

    defined = set(re.findall(r"\*\*((?:FR|NFR|SC)-\d+)\*\*", args.spec.read_text(encoding="utf-8")))
    for rid in sorted(tagged - defined):
        bad(R_SOURCES, rid, f"{rid} 在 spec.md 裡沒有定義")

    passed_evidence = {
        R_PARSE: f"解析出 {len(services)} 個服務",
        R_TAGGED: f"{len(services)} 個服務都有 x-requirements",
        R_ENV: f"compose 用到的 {len(used)} 個變數都列在 .env.example 且沒有值",
        R_FILES: "Dockerfile 與 bind mount 的設定檔都找得到",
        R_COMPOSE: "docker compose config -q 通過",
        R_COVERAGE: f"S{step}(E{endpoint})的 {len(needed)} 個需求出處都對得到服務",
        R_SOURCES: f"x-requirements 的 {len(tagged)} 個需求編號都在 spec.md 裡",
    }
    checks = []
    for rule in RULES:
        mine = violations[rule]
        skipped = rule == R_COMPOSE and compose_skipped
        result = "略過" if skipped else ("不過" if mine else "過")
        evidence = "這台機器沒有 docker compose" if skipped else (";".join(f"{v['where']}:{v['reason']}" for v in mine) if mine else passed_evidence[rule])
        checks.append({"rule": rule, "result": result, "evidence": evidence, "violations": mine})
    passed = not any(violations.values())
    report = {"compose": str(args.compose), "step": f"S{step}", "passed": passed, "checks": checks}
    print(f"檢查了 {len(services)} 個服務、{len(needed)} 個需求出處,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
