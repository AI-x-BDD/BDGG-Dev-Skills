# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6,<7", "openapi-spec-validator>=0.7,<0.8"]
# ///
"""驗證 api-plan 交出的 OpenAPI 與 AsyncAPI 規格檔。

檢查項目:OpenAPI 通過 openapi-spec-validator、AsyncAPI 3.0 的參照都接得上、
每個操作都有 x-requirements、每個成功回應(2xx 與 3xx 重新導向)與訊息都有 x-recipients、
4xx、5xx 與 default 回應都有 x-error-codes、x-error-codes 用到的錯誤碼都在 Error 的 code enum、plan.md 這一步端點的需求出處都對得到操作、
x-requirements 的需求編號都在 spec.md 裡。
--openapi 與 --asyncapi 至少給一個;沒給的那一份相關檢查標成略過。
被憲法以 `--waive "<規範檔名>〈Rule 名稱〉"` 取代的檢查標成略過,不算不過;只有下面 WAIVABLE 列的檢查接受取代。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from openapi_spec_validator import validate as validate_openapi

HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
ENDPOINT_ROW = re.compile(r"^\| E(\d+) \|(.*)\|$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")  # Markdown 表格裡跳脫的 \| 是內容,不是欄分隔
WAVE_ROW = re.compile(r"^\| (\d+) \| S(\d+) \| E(\d+) ")
RANGE = re.compile(r"\b(FR|NFR|SC)-(\d+)\s*[–—~]\s*(?:(?:FR|NFR|SC)-)?(\d+)\b")
REQUIREMENT_ID = re.compile(r"\b((?:FR|NFR|SC)-\d+)\b")

R_OPENAPI = "OpenAPI 通過 openapi-spec-validator"
R_ASYNCAPI = "AsyncAPI 3.0 的參照都接得上"
R_TAGGED = "每個操作都有 x-requirements"
R_RECIPIENTS = "每個成功回應與訊息都有 x-recipients"
R_ERRORS = "錯誤碼都在 Error 的 code enum"
R_COVERAGE = "plan.md 這一步的需求出處都對得到操作"
R_SOURCES = "x-requirements 的需求編號都在 spec.md 裡"
WAIVABLE = {
    "契約-規範〈伺服器把關的條件都有具名的錯誤〉": R_ERRORS,
    "契約-規範〈回應與推送寫明收件者與可見欄位〉": R_RECIPIENTS,
}

RULES = [R_OPENAPI, R_ASYNCAPI, R_TAGGED, R_RECIPIENTS, R_ERRORS, R_COVERAGE, R_SOURCES]


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


def resolve(doc: dict, ref: str):
    """照 `#/a/b` 的 JSON pointer 取值;接不上時回 None。"""
    node = doc
    for part in ref.removeprefix("#/").split("/"):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def error_enum(doc: dict) -> set[str]:
    code = (((doc.get("components") or {}).get("schemas") or {}).get("Error") or {}).get("properties", {}).get("code", {})
    return set(code.get("enum") or [])


def load(path: Path, label: str):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"錯誤: {label} {path} 不是合法的 YAML:{exc}", file=sys.stderr)
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--openapi", type=Path, help="contracts/openapi.yaml 的路徑;這個介面沒有 REST 操作就不給")
    parser.add_argument("--asyncapi", type=Path, help="contracts/asyncapi.yaml 的路徑;這個介面沒有推送操作就不給")
    parser.add_argument("--plan", required=True, type=Path, help="system-analysis 產出的 plan.md 路徑,用來找這一步分析的端點與需求出處")
    parser.add_argument("--spec", required=True, type=Path, help="spec.md 的路徑,用來確認需求編號都有定義")
    parser.add_argument("--step", required=True, help="這份規格檔對應的波段表步驟編號,例如 S2")
    parser.add_argument(
        "--waive",
        action="append",
        default=[],
        help="被憲法取代的 Skill 規範,寫成 <規範檔名>〈Rule 名稱〉,照 constitution_rules.py 交回的 waive 原樣給;可以給多次",
    )
    args = parser.parse_args()
    unknown = [w for w in args.waive if w not in WAIVABLE]
    if unknown:
        print(
            f"錯誤: --waive 收到 {unknown};只有這些規範對應得到檢查,可以被取代:{list(WAIVABLE)}。"
            "其他規範沒有對應的檢查或不可取代,不要給 --waive。",
            file=sys.stderr,
        )
        return 2
    waived = {WAIVABLE[w]: w for w in args.waive}

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if args.openapi is None and args.asyncapi is None:
        print("錯誤: --openapi 與 --asyncapi 至少要給一個。", file=sys.stderr)
        return 2
    step_match = re.fullmatch(r"S?(\d+)", args.step.strip())
    if not step_match:
        print(f"錯誤: --step 收到「{args.step}」,要給波段表的步驟編號,例如 S2。", file=sys.stderr)
        return 2
    step = int(step_match.group(1))
    for path in [p for p in (args.openapi, args.asyncapi, args.plan, args.spec) if p is not None]:
        if not path.is_file():
            print(f"錯誤: 找不到 {path};每個參數都要給檔案路徑。", file=sys.stderr)
            return 2

    openapi = load(args.openapi, "--openapi") if args.openapi else None
    asyncapi = load(args.asyncapi, "--asyncapi") if args.asyncapi else None
    if (args.openapi and not isinstance(openapi, dict)) or (args.asyncapi and not isinstance(asyncapi, dict)):
        print("錯誤: 規格檔讀不成 YAML 物件,請先修正語法。", file=sys.stderr)
        return 2

    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, where: str, reason: str) -> None:
        violations[rule].append({"where": where, "reason": reason})

    tagged: set[str] = set()
    operation_count = 0

    # OpenAPI
    if openapi is not None:
        try:
            validate_openapi(openapi)
        except Exception as exc:  # validator 的例外種類很多,一律轉成不符項
            bad(R_OPENAPI, "openapi", str(exc).splitlines()[0])
        enum = error_enum(openapi)
        for path, item in (openapi.get("paths") or {}).items():
            for method, op in (item or {}).items():
                if method not in HTTP_METHODS or not isinstance(op, dict):
                    continue
                operation_count += 1
                where = f"openapi {method.upper()} {path}"
                reqs = op.get("x-requirements") or []
                if not reqs:
                    bad(R_TAGGED, where, "沒有 x-requirements")
                tagged |= {str(r) for r in reqs}
                for status, resp in (op.get("responses") or {}).items():
                    if not isinstance(resp, dict):
                        continue
                    if str(status)[:1] in ("2", "3"):  # 3xx 重新導向也是成功,不是錯誤
                        if not resp.get("x-recipients"):
                            bad(R_RECIPIENTS, f"{where} {status}", "成功回應沒有 x-recipients")
                    else:
                        codes = resp.get("x-error-codes") or []
                        if not codes:
                            bad(R_ERRORS, f"{where} {status}", "失敗回應沒有 x-error-codes")
                        for code in codes:
                            if code not in enum:
                                bad(R_ERRORS, f"{where} {status}", f"錯誤碼 {code} 不在 Error 的 code enum")

    # AsyncAPI
    if asyncapi is not None:
        if not str(asyncapi.get("asyncapi", "")).startswith("3."):
            bad(R_ASYNCAPI, "asyncapi", f"版本是「{asyncapi.get('asyncapi')}」,要是 3.x")
        for name, channel in (asyncapi.get("channels") or {}).items():
            for key, msg in ((channel or {}).get("messages") or {}).items():
                ref = (msg or {}).get("$ref")
                if ref and resolve(asyncapi, ref) is None:
                    bad(R_ASYNCAPI, f"channels.{name}.messages.{key}", f"$ref {ref} 接不上")
        enum = error_enum(asyncapi)
        for name, op in (asyncapi.get("operations") or {}).items():
            operation_count += 1
            where = f"asyncapi operations.{name}"
            if (op or {}).get("action") not in ("send", "receive"):
                bad(R_ASYNCAPI, where, "action 要是 send 或 receive")
            channel_ref = ((op or {}).get("channel") or {}).get("$ref", "")
            if resolve(asyncapi, channel_ref) is None:
                bad(R_ASYNCAPI, where, f"channel 的 $ref「{channel_ref}」接不上")
            for msg in (op or {}).get("messages") or []:
                ref = (msg or {}).get("$ref", "")
                if not ref.startswith(channel_ref + "/messages/") or resolve(asyncapi, ref) is None:
                    bad(R_ASYNCAPI, where, f"message 的 $ref「{ref}」要指到 {channel_ref} 底下存在的訊息")
            reqs = (op or {}).get("x-requirements") or []
            if not reqs:
                bad(R_TAGGED, where, "沒有 x-requirements")
            tagged |= {str(r) for r in reqs}
            for code in (op or {}).get("x-error-codes") or []:
                if code not in enum:
                    bad(R_ERRORS, where, f"錯誤碼 {code} 不在 Error 的 code enum")
        for name, msg in ((asyncapi.get("components") or {}).get("messages") or {}).items():
            if not (msg or {}).get("x-recipients"):
                bad(R_RECIPIENTS, f"asyncapi components.messages.{name}", "訊息沒有 x-recipients")

    # 需求覆蓋
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
        bad(R_COVERAGE, rid, f"E{endpoint} 的需求出處 {rid} 沒有任何操作的 x-requirements 對到")

    defined = set(re.findall(r"\*\*((?:FR|NFR|SC)-\d+)\*\*", args.spec.read_text(encoding="utf-8")))
    for rid in sorted(tagged - defined):
        bad(R_SOURCES, rid, f"{rid} 在 spec.md 裡沒有定義")

    skipped = {R_OPENAPI: openapi is None, R_ASYNCAPI: asyncapi is None}
    passed_evidence = {
        R_OPENAPI: "openapi-spec-validator 沒有回報錯誤",
        R_ASYNCAPI: "channels 與 operations 的 $ref 都接得上,action 都是 send 或 receive",
        R_TAGGED: f"{operation_count} 個操作都有 x-requirements",
        R_RECIPIENTS: "成功回應與訊息都寫了 x-recipients",
        R_ERRORS: "x-error-codes 用到的錯誤碼都在 Error 的 code enum",
        R_COVERAGE: f"S{step}(E{endpoint})的 {len(needed)} 個需求出處都對得到操作",
        R_SOURCES: f"x-requirements 的 {len(tagged)} 個需求編號都在 spec.md 裡",
    }
    checks = []
    for rule in RULES:
        mine = violations[rule]
        if rule in waived:
            result, evidence = "略過", f"由憲法取代:{waived[rule]}"
        else:
            result = "略過" if skipped.get(rule) else ("不過" if mine else "過")
            evidence = "沒有給這一份規格檔" if skipped.get(rule) else (";".join(f"{v['where']}:{v['reason']}" for v in mine) if mine else passed_evidence[rule])
        checks.append({"rule": rule, "result": result, "evidence": evidence, "violations": mine})
    passed = not any(v for rule, v in violations.items() if rule not in waived)
    report = {
        "openapi": str(args.openapi) if args.openapi else None,
        "asyncapi": str(args.asyncapi) if args.asyncapi else None,
        "step": f"S{step}",
        "passed": passed,
        "checks": checks,
    }
    print(f"檢查了 {operation_count} 個操作、{len(needed)} 個需求出處,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
