# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""對一個目錄底下的每一支 Skill 執行 form 系列的四支檢查腳本,把結果合併成一份:SOP 與流程視覺圖、Rule File、樣板、腳本。

檢查腳本取自和本 skill 同一層目錄的 skill-form-sop、skill-form-rule、skill-form-template 與 skill-form-script。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。加上 --write-diagrams 時,先替 --only 指定的 Skill 注入流程視覺圖再檢查。
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

CHECKERS = {
    "sop": ("skill-form-sop", "render_sop_diagram.py"),
    "rule": ("skill-form-rule", "check_rule_file.py"),
    "template": ("skill-form-template", "check_templates.py"),
    "script": ("skill-form-script", "check_scripts.py"),
}


def fail(message: str) -> None:
    print(f"錯誤: {message}", file=sys.stderr)
    sys.exit(2)


def locate_checkers() -> dict[str, Path]:
    base = Path(__file__).resolve().parents[2]
    found = {}
    for key, (skill, script) in CHECKERS.items():
        path = base / skill / "scripts" / script
        if not path.is_file():
            fail(f"找不到 {path}。這支腳本要和 {skill} 放在同一層目錄,才借得到它的檢查腳本。")
        found[key] = path
    return found


def run_checker(script: Path, *arguments: str) -> dict:
    """執行一支檢查腳本並回傳它寫到 stdout 的 JSON;腳本自己失敗(不是檢查不過)時結束。"""
    try:
        done = subprocess.run(["uv", "run", "--quiet", str(script), *arguments], capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        fail("找不到 `uv`。先安裝 uv(https://docs.astral.sh/uv/getting-started/installation/)再執行。")
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError:
        fail(f"{script.name} {' '.join(arguments)} 沒有交出 JSON(exit code {done.returncode})。它的訊息:{done.stderr.strip()[:500]}")
    return {}


def item(part: str, owner: str, rule: str, file: str, line: int, text: str, reason: str) -> dict:
    return {"part": part, "owner": owner, "rule": rule, "file": file, "line": line, "text": text, "reason": reason}


def check_skill(skill: Path, checkers: dict[str, Path], write_diagram: bool) -> dict:
    items: list[dict] = []
    candidates: list[dict] = []
    skill_file = skill / "SKILL.md"

    injected = None
    if write_diagram:
        written = run_checker(checkers["sop"], "--write", "--file", str(skill_file))
        injected = written["diagram"]["result"]

    sop = run_checker(checkers["sop"], "--check", "--file", str(skill_file))
    for check in sop["checks"]:
        for violation in check["violations"]:
            items.append(item("SOP", "skill-form-sop", check["rule"], "SKILL.md", violation["line"], violation["text"], violation["reason"]))
    for candidate in sop["candidates"]:
        candidates.append(item("SOP", "skill-form-sop", candidate["rule"], "SKILL.md", candidate["line"], candidate["text"], candidate["reason"]))
    diagram = sop["diagram"]["result"]
    if diagram == "不一致":
        items.append(
            item(
                "流程視覺圖",
                "skill-form-sop",
                "流程視覺圖與 SOP 一致",
                "SKILL.md",
                0,
                "",
                "流程視覺圖缺失、不在 `# SOP` 正下方,或與 `# SOP` 不一致;SOP 的格式全過,可以用 --write-diagrams 直接注入",
            )
        )

    rules_dir = skill / "rules"
    for rule_file in sorted(rules_dir.glob("*.md")) if rules_dir.is_dir() else []:
        result = run_checker(checkers["rule"], "--file", str(rule_file))
        for problem in result.get("problems", []):
            items.append(item("Rule File", "skill-form-rule", problem["rule"], f"rules/{rule_file.name}", problem["line"], "", problem["message"]))

    for part, owner, key in (("樣板", "skill-form-template", "template"), ("腳本", "skill-form-script", "script")):
        result = run_checker(checkers[key], "--skill", str(skill))
        for check in result["checks"]:
            for violation in check["violations"]:
                items.append(item(part, owner, check["rule"], violation["file"], violation["line"], violation["text"], violation["reason"]))
        for candidate in result.get("candidates", []):
            candidates.append(item(part, owner, candidate["rule"], candidate["file"], candidate["line"], candidate["text"], candidate["reason"]))

    report = {"skill": skill.name, "passed": not items, "diagram": diagram, "items": items, "candidates": candidates}
    if injected is not None:
        report["write_diagram"] = injected
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skills", required=True, type=Path, help="放 Skill 的目錄;底下每個含 SKILL.md 的子目錄是一支 Skill(例如 .claude/skills)")
    parser.add_argument("--only", nargs="+", metavar="NAME", help="只檢查這幾支 Skill(子目錄的名字,可列多個);省略就檢查全部")
    parser.add_argument("--write-diagrams", action="store_true", help="先替 --only 指定的 Skill 注入流程視覺圖(SOP 格式不過的不會注入)再檢查;一定要搭配 --only")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.skills.is_dir():
        fail(f"{args.skills} 不是目錄。--skills 要給放 Skill 的那一層目錄(例如 .claude/skills)。")
    if args.write_diagrams and not args.only:
        fail("--write-diagrams 一定要搭配 --only <Skill 名稱>,不會一次改寫全部的 Skill。")

    available = {p.name: p for p in sorted(args.skills.iterdir()) if p.is_dir() and (p / "SKILL.md").is_file()}
    if not available:
        fail(f"{args.skills} 底下沒有任何含 SKILL.md 的子目錄。--skills 要給放 Skill 的那一層目錄。")
    if args.only:
        missing = [name for name in args.only if name not in available]
        if missing:
            fail(f"--only 指定的 {'、'.join(missing)} 不在 {args.skills} 底下。可以用的名字:{'、'.join(available)}")
        targets = [available[name] for name in dict.fromkeys(args.only)]
    else:
        targets = list(available.values())

    checkers = locate_checkers()
    skills = []
    for index, skill in enumerate(targets, start=1):
        print(f"[{index}/{len(targets)}] {skill.name}", file=sys.stderr)
        skills.append(check_skill(skill, checkers, args.write_diagrams))

    failed = [s for s in skills if not s["passed"]]
    report = {
        "skills_dir": str(args.skills),
        "passed": not failed,
        "summary": {
            "skills": len(skills),
            "failed_skills": len(failed),
            "items": sum(len(s["items"]) for s in skills),
            "candidates": sum(len(s["candidates"]) for s in skills),
        },
        "skills": skills,
    }
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
