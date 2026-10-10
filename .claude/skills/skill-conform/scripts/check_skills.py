# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""對一個目錄底下的每一支 Skill 執行 form 系列的四支檢查腳本,把結果合併成一份:SOP 與流程視覺圖、Rule File、樣板、腳本。

另外做兩項要跨檔才判得了的檢查:每個 Rule File 的 good example 裡的 SOP 步驟是否符合現行的 SOP 格式;
把關紀錄-格式規範.md 逐條列出的範例表格是否和同一支 Skill 的 SOP-格式規範.md 的 Rule 一致。

檢查腳本取自和本 skill 同一層目錄的 skill-form-sop、skill-form-rule、skill-form-template 與 skill-form-script。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。加上 --write-diagrams 時,先替 --only 指定的 Skill 注入流程視覺圖再檢查。
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKERS = {
    "sop": ("skill-form-sop", "render_sop_diagram.py"),
    "rule": ("skill-form-rule", "check_rule_file.py"),
    "template": ("skill-form-template", "check_templates.py"),
    "script": ("skill-form-script", "check_scripts.py"),
}

GOOD = "## good example"
BAD = "## bad example"
FENCE = re.compile(r"^(`{3,})(.*)$")
RULE_TITLE = re.compile(r"^# Rule \d+ \[(must|should)\] - (\S.*)$")
# 範例裡的 SOP 步驟:編號前面只能是空白或一個標籤(「after」「終態」「掛上之後的步驟:」),編號後面是 skill-form-sop 動詞表的動詞。
# 沒有動詞的編號行(commit 清單、情境敘述)不是 SOP 步驟,不抽。
EXAMPLE_STEP = re.compile(r"^(?P<label>|.*?[\s::])\d+\. (?P<body>(?:Read|Write|Think|Ask|Report|Delegate)\s.*)$")
# 這些標籤的行是刻意寫壞、正要被改寫的輸入,不檢查
BROKEN_INPUT_LABELS = ("原本",)
SYNTHETIC_HEADER = "# SOP\n\n## Phase 1: 檢查範例\n"
# 把步驟從各個範例抽出來排成同一份 SOP 才會出現的違規,和範例本身無關;以 render_sop_diagram.py 原因裡的字辨認。
# 那邊的用字改了,這裡會認不出來而把它們報成不過,不會漏報。
REORDER_ARTIFACTS = ("要跳至的", "已經點名", "是第一個執行腳本的步驟")
LEDGER_FILE = "把關紀錄-格式規範.md"
SOP_RULE_FILE = "SOP-格式規範.md"
LEDGER_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(must|should)\s*\|")


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


def item(part: str, owner: str, rule: str, source: str, file: str, line: int, text: str, reason: str) -> dict:
    """owner 是負責改寫 file 的那支 form skill。

    source 是那條 Rule 所在的規範檔名(在 owner 的 rules/ 底下);Rule 在別支 Skill 底下時寫成 `<Skill 名稱>/rules/<檔名>`,不是 Rule 的檢查項寫空字串。
    """
    return {"part": part, "owner": owner, "rule": rule, "source": source, "file": file, "line": line, "text": text, "reason": reason}


def good_example_blocks(rule_file: Path) -> list[dict]:
    """回傳 Rule File 裡接在 `## good example` 底下的每一個 code block:{"rule": 所屬 Rule 的名稱, "line": 開始的行號, "lines": [(行號, 內容)]}。

    block 裡自己還有 example 標題時(用四個反引號包住一整條 Rule 的示範),內層 `## bad example` 底下的行不收。
    """
    blocks: list[dict] = []
    rule = ""
    good = False
    open_length = 0
    inner_bad = False
    for number, line in enumerate(rule_file.read_text(encoding="utf-8").splitlines(), start=1):
        fence = FENCE.match(line)
        if open_length == 0:
            if fence:
                open_length = len(fence.group(1))
                inner_bad = False
                if good:
                    blocks.append({"rule": rule, "line": number, "lines": []})
            elif line.startswith("# "):
                title = RULE_TITLE.match(line.rstrip())
                rule, good = (title.group(2) if title else ""), False
            elif line.startswith("#"):
                good = line.rstrip() == GOOD
            continue
        if fence and len(fence.group(1)) >= open_length and not fence.group(2).strip():
            open_length = 0
        elif line.rstrip() in (GOOD, BAD):
            inner_bad = line.rstrip() == BAD
        elif good and not inner_bad:
            blocks[-1]["lines"].append((number, line))
    return blocks


def rule_titles(rule_file: Path) -> list[tuple[str, str]]:
    """回傳 Rule File 裡 code block 以外每一條 Rule 的 (名稱, 強度)。"""
    titles: list[tuple[str, str]] = []
    open_length = 0
    for line in rule_file.read_text(encoding="utf-8").splitlines():
        fence = FENCE.match(line)
        if fence:
            if open_length == 0:
                open_length = len(fence.group(1))
            elif len(fence.group(1)) >= open_length and not fence.group(2).strip():
                open_length = 0
            continue
        title = RULE_TITLE.match(line.rstrip()) if open_length == 0 else None
        if title:
            titles.append((title.group(2), title.group(1)))
    return titles


def check_example_steps(skill: Path, sop_checker: Path) -> list[dict]:
    """把這支 Skill 每個 Rule File 的 good example 裡的 SOP 步驟排成一份 SOP,交給 SOP 的檢查腳本判。"""
    rules_dir = skill / "rules"
    steps: list[tuple[str, int, str, str]] = []
    for rule_file in sorted(rules_dir.glob("*.md")) if rules_dir.is_dir() else []:
        for block in good_example_blocks(rule_file):
            for number, line in block["lines"]:
                step = EXAMPLE_STEP.match(line)
                if step and step.group("label").strip().rstrip("::").strip() not in BROKEN_INPUT_LABELS:
                    steps.append((rule_file.name, number, line.strip(), step.group("body")))
    if not steps:
        return []

    header_lines = SYNTHETIC_HEADER.count("\n")
    with tempfile.TemporaryDirectory() as temporary:
        synthetic = Path(temporary) / "SKILL.md"
        synthetic.write_text(SYNTHETIC_HEADER + "".join(f"{index}. {body}\n" for index, (*_, body) in enumerate(steps, start=1)), encoding="utf-8")
        result = run_checker(sop_checker, "--check", "--file", str(synthetic))

    items: list[dict] = []
    for check in result["checks"]:
        for violation in check["violations"]:
            if any(marker in violation["reason"] for marker in REORDER_ARTIFACTS):
                continue
            index = violation["line"] - header_lines
            if not 1 <= index <= len(steps):
                fail(
                    f"{sop_checker.name} 回報的第 {violation['line']} 行不是從 {skill.name} 的範例抽出來的步驟(共 {len(steps)} 步):{violation['reason']}。"
                    f"合成的 SOP 只有 `# SOP`、一個 Phase 標題與編號步驟;{sop_checker.name} 對骨架的要求改了的話,要跟著改這支腳本的 SYNTHETIC_HEADER。"
                )
            name, number, text, _body = steps[index - 1]
            position = f"Phase 1 Step {index}"
            reason = violation["reason"]
            if reason.startswith(position):
                reason = "這一步" + reason[len(position) :].lstrip()
            source = f"{CHECKERS['sop'][0]}/rules/{check['source']}"
            items.append(item("Rule File", CHECKERS["rule"][0], check["rule"], source, f"rules/{name}", number, text, f"good example 裡的 SOP 步驟:{reason}"))
    return sorted(items, key=lambda found: (found["file"], found["line"]))


def check_ledger_example(skill: Path) -> list[dict]:
    """把關紀錄規範第一個 good example 逐條列出的表格,要和同一支 Skill 的 SOP-格式規範.md 的 Rule 依序一致。

    這支 Skill 沒有這兩個檔時不檢查。
    """
    ledger = skill / "rules" / LEDGER_FILE
    sop_rules = skill / "rules" / SOP_RULE_FILE
    if not (ledger.is_file() and sop_rules.is_file()):
        return []

    def report(rule: str, line: int, text: str, reason: str) -> list[dict]:
        return [item("Rule File", CHECKERS["rule"][0], rule, f"{skill.name}/rules/{LEDGER_FILE}", f"rules/{LEDGER_FILE}", line, text, reason)]

    expected = rule_titles(sop_rules)
    blocks = good_example_blocks(ledger)
    if not blocks:
        return report("", 0, "", f"找不到第一個 good example 的 code block;它要逐條列出 `{SOP_RULE_FILE}` 的 {len(expected)} 條 Rule")
    block = blocks[0]
    rows = [(number, line.strip(), match.group(1), match.group(2)) for number, line in block["lines"] if (match := LEDGER_ROW.match(line))]
    actual = [(name, strength) for _number, _text, name, strength in rows]
    if actual == expected:
        return []

    expected_strength = dict(expected)
    listed = [name for name, _strength in actual]
    problems = []
    missing = [name for name, _strength in expected if name not in listed]
    if missing:
        problems.append("少了" + "、".join(f"〈{name}〉" for name in missing))
    extra = [name for name in listed if name not in expected_strength]
    if extra:
        problems.append("多了" + "、".join(f"〈{name}〉" for name in extra))
    wrong = [name for name, strength in actual if name in expected_strength and expected_strength[name] != strength]
    if wrong:
        problems.append("強度不同的有" + "、".join(f"〈{name}〉(規範是 {expected_strength[name]})" for name in wrong))
    if not problems:
        problems.append("順序不同或有重複的列")
    # 指到第一個對不上的列;前面都對得上而列數不同時,指到多出來的第一列,或(少列時)這個 code block 開始的那一行
    first = next((row for row, wanted in zip(rows, expected) if (row[2], row[3]) != wanted), None)
    if first is None and len(rows) > len(expected):
        first = rows[len(expected)]
    number, text = (first[0], first[1]) if first else (block["line"], "")
    return report(
        block["rule"],
        number,
        text,
        f"good example 的表格要和 `{SOP_RULE_FILE}` 的 {len(expected)} 條 Rule 依序一致(現在列了 {len(rows)} 列):{';'.join(problems)}",
    )


def check_skill(skill: Path, checkers: dict[str, Path], write_diagram: bool) -> dict:
    items: list[dict] = []
    candidates: list[dict] = []
    skill_file = skill / "SKILL.md"

    injected = None
    if write_diagram:
        written = run_checker(checkers["sop"], "--write", "--file", str(skill_file))
        injected = written["diagram"]["result"]

    sop = run_checker(checkers["sop"], "--check", "--file", str(skill_file))
    sop_sources = {check["rule"]: check["source"] for check in sop["checks"]}
    for check in sop["checks"]:
        for violation in check["violations"]:
            items.append(item("SOP", "skill-form-sop", check["rule"], check["source"], "SKILL.md", violation["line"], violation["text"], violation["reason"]))
    for candidate in sop["candidates"]:
        source = sop_sources.get(candidate["rule"], "")
        candidates.append(item("SOP", "skill-form-sop", candidate["rule"], source, "SKILL.md", candidate["line"], candidate["text"], candidate["reason"]))
    diagram = sop["diagram"]["result"]
    if diagram == "不一致":
        items.append(
            item(
                "流程視覺圖",
                "skill-form-sop",
                "流程視覺圖與 SOP 一致",
                "",
                "SKILL.md",
                0,
                "",
                "流程視覺圖缺失、不在檔尾,或與 `# SOP` 不一致;SOP 的格式全過,可以用 --write-diagrams 直接注入",
            )
        )

    rules_dir = skill / "rules"
    for rule_file in sorted(rules_dir.glob("*.md")) if rules_dir.is_dir() else []:
        result = run_checker(checkers["rule"], "--file", str(rule_file))
        for check in result["checks"]:
            for violation in check["violations"]:
                items.append(item("Rule File", "skill-form-rule", check["rule"], check["source"], f"rules/{rule_file.name}", violation["line"], violation["text"], violation["reason"]))
    items.extend(check_example_steps(skill, checkers["sop"]))
    items.extend(check_ledger_example(skill))

    for part, owner, key in (("樣板", "skill-form-template", "template"), ("腳本", "skill-form-script", "script")):
        result = run_checker(checkers[key], "--skill", str(skill))
        default_source = result["checks"][0]["source"] if result["checks"] else ""
        for check in result["checks"]:
            for violation in check["violations"]:
                items.append(item(part, owner, check["rule"], check["source"], violation["file"], violation["line"], violation["text"], violation["reason"]))
        for candidate in result.get("candidates", []):
            candidates.append(item(part, owner, candidate["rule"], default_source, candidate["file"], candidate["line"], candidate["text"], candidate["reason"]))

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
