# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查專案 constitution/ 資料夾裡每個憲法檔的結構。

檢查項目:
  路徑合法      每個檔是 <SDD Skill>/<產出物>.md 或 _shared/<主題>.md;合法的產出物從本 skill 同層
                各 SDD Skill 的 templates/ 推出(去掉 .template 與副檔名,不含 .example 檔與委派指示)
  applies_to    _shared/ 的檔有 applies_to 檔頭,列出的每個 <skill>/<產出物> 都合法;其他檔沒有 applies_to
  Rule 格式     每個 # 標題都是 `# Rule N [must|should] - 名稱`,N 從 1 起連號,每條都有 `- 為什麼:`
  example 成對  每條 Rule 至少有一個 ## good example 與一個 ## bad example,每個 example 都附 code block
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

SDD_SKILLS = [
    "specify",
    "technical-research",
    "system-analysis",
    "api-plan",
    "data-plan",
    "deploy-plan",
    "uiux-plan",
    "tasks",
]
NOT_ARTIFACTS = {"委派指示"}

RULE_HEADING = re.compile(r"^# Rule (\d+) \[(must|should)\] - \S")
FRONT_APPLIES = re.compile(r"^applies_to:\s*\[(.*)\]\s*$")

CHECK_PATH = "路徑合法"
CHECK_APPLIES = "applies_to"
CHECK_RULE = "Rule 格式"
CHECK_EXAMPLE = "example 成對"


def legal_artifacts(skills_dir: Path) -> dict[str, set[str]]:
    """每支 SDD Skill 的合法產出物,從它的 templates/ 推出。"""
    result: dict[str, set[str]] = {}
    for skill in SDD_SKILLS:
        templates = skills_dir / skill / "templates"
        names: set[str] = set()
        if templates.is_dir():
            for f in templates.iterdir():
                if not f.is_file() or ".example" in f.name:
                    continue
                stem = f.name.split(".")[0]
                if stem and stem not in NOT_ARTIFACTS:
                    names.add(stem)
        result[skill] = names
    return result


def split_front(lines: list[str]) -> tuple[list[str] | None, list[str], int]:
    """拆出檔頭;回傳 (檔頭的行或 None, 本文的行, 本文第一行的行號)。"""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[1:i], lines[i + 1 :], i + 2
        return lines[1:], [], len(lines) + 1
    return None, lines, 1


def check_body(rel: str, body: list[str], first_line: int, bad) -> int:
    """檢查本文的 Rule 與 example;回傳 Rule 條數。"""
    rules: list[dict] = []
    current: dict | None = None
    section: dict | None = None
    in_fence = False
    for offset, line in enumerate(body):
        lineno = first_line + offset
        if line.startswith("```"):
            in_fence = not in_fence
            if in_fence and section is not None:
                section["fence"] = True
            continue
        if in_fence:
            continue
        if line.startswith("# "):
            m = RULE_HEADING.match(line)
            if not m:
                bad(CHECK_RULE, rel, f"第 {lineno} 行", f"標題「{line.strip()}」不是 `# Rule N [must|should] - 名稱`")
                current = None
                section = None
                continue
            current = {"no": int(m.group(1)), "line": lineno, "why": False, "sections": []}
            rules.append(current)
            section = None
        elif line.startswith("## "):
            title = line[3:].strip()
            if current is None:
                bad(CHECK_EXAMPLE, rel, f"第 {lineno} 行", f"「{title}」不在任何一條 Rule 底下")
                continue
            if title not in ("good example", "bad example"):
                bad(CHECK_EXAMPLE, rel, f"第 {lineno} 行", f"「## {title}」只能是 `## good example` 或 `## bad example`")
                section = None
                continue
            section = {"kind": title.split()[0], "line": lineno, "fence": False}
            current["sections"].append(section)
        elif current is not None and section is None and line.startswith("- 為什麼:"):
            current["why"] = True
        elif current is None and line.strip():
            bad(CHECK_RULE, rel, f"第 {lineno} 行", "第一條 Rule 之前有內容;檔頭以外的內容都要放在某一條 Rule 底下")
    if in_fence:
        bad(CHECK_EXAMPLE, rel, "檔尾", "有 code block 沒有用 ``` 收尾")

    if not rules:
        bad(CHECK_RULE, rel, "全檔", "沒有任何一條 `# Rule N [must|should] - 名稱`")
    for expected, rule in enumerate(rules, start=1):
        where = f"第 {rule['line']} 行 Rule {rule['no']}"
        if rule["no"] != expected:
            bad(CHECK_RULE, rel, where, f"流水號是 {rule['no']},照順序應該是 {expected}")
        if not rule["why"]:
            bad(CHECK_RULE, rel, where, "desc 沒有 `- 為什麼:` 這一行")
        kinds = [s["kind"] for s in rule["sections"]]
        if "good" not in kinds or "bad" not in kinds:
            bad(CHECK_EXAMPLE, rel, where, f"要至少一個 good example 與一個 bad example,現在是 {kinds or '沒有 example'}")
        for s in rule["sections"]:
            if not s["fence"]:
                bad(CHECK_EXAMPLE, rel, f"第 {s['line']} 行 {s['kind']} example", "沒有附 code block")
    return len(rules)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="檢查專案 constitution/ 資料夾裡每個憲法檔的路徑、applies_to 檔頭、Rule 格式與 good/bad example。"
    )
    parser.add_argument(
        "--constitution",
        required=True,
        help="專案根目錄底下的 constitution 資料夾(裡面是 <skill>/<產出物>.md 與 _shared/),不是單一個檔",
    )
    args = parser.parse_args()

    root = Path(args.constitution)
    if not root.is_dir():
        print(
            f"找不到資料夾 {root};--constitution 要給專案根目錄底下的 constitution 資料夾,不是單一個憲法檔",
            file=sys.stderr,
        )
        return 2

    skills_dir = Path(__file__).resolve().parents[2]
    artifacts = legal_artifacts(skills_dir)
    if not any(artifacts.values()):
        print(
            f"在 {skills_dir} 找不到任何 SDD Skill 的 templates/(預期有 {', '.join(SDD_SKILLS)});"
            "這支腳本要放在和它們同一層的 constitution/scripts/ 底下",
            file=sys.stderr,
        )
        return 2
    legal_ids = {f"{s}/{a}" for s, names in artifacts.items() for a in names}

    violations: dict[str, list[dict]] = {CHECK_PATH: [], CHECK_APPLIES: [], CHECK_RULE: [], CHECK_EXAMPLE: []}

    def bad(check: str, file: str, where: str, message: str) -> None:
        violations[check].append({"file": file, "where": where, "message": message})

    files = sorted(p for p in root.rglob("*") if p.is_file())
    summary = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        parts = rel.split("/")
        shared = len(parts) == 2 and parts[0] == "_shared"
        if path.suffix != ".md":
            bad(CHECK_PATH, rel, "路徑", "憲法檔只能是 .md")
            continue
        if not shared:
            if len(parts) != 2:
                bad(CHECK_PATH, rel, "路徑", "要是 <SDD Skill>/<產出物>.md 或 _shared/<主題>.md")
                continue
            skill, artifact = parts[0], path.stem
            if skill not in artifacts:
                bad(CHECK_PATH, rel, "路徑", f"「{skill}」不是 SDD Skill;可以用的是 {', '.join(SDD_SKILLS)}")
                continue
            if artifact not in artifacts[skill]:
                legal = ", ".join(sorted(artifacts[skill])) or "(沒有)"
                bad(CHECK_PATH, rel, "路徑", f"{skill} 沒有「{artifact}」這個產出物;可以用的是 {legal}")

        lines = path.read_text(encoding="utf-8").splitlines()
        front, body, first_line = split_front(lines)
        applies: list[str] = []
        if front is not None:
            for line in front:
                m = FRONT_APPLIES.match(line.strip())
                if m:
                    applies = [x.strip() for x in m.group(1).split(",") if x.strip()]
        if shared:
            if not applies:
                bad(CHECK_APPLIES, rel, "檔頭", "_shared/ 的檔要有 `---` 包住的 `applies_to: [<skill>/<產出物>, ...]`")
            elif len(applies) < 2:
                bad(CHECK_APPLIES, rel, "檔頭", f"applies_to 只有 {applies};只管一種產出物的條文放 <skill>/<產出物>.md")
            for item in applies:
                if item not in legal_ids:
                    bad(CHECK_APPLIES, rel, "檔頭", f"applies_to 的「{item}」不是合法的 <skill>/<產出物>")
        elif front is not None:
            bad(CHECK_APPLIES, rel, "檔頭", "只有 _shared/ 的檔才有檔頭;這個檔的約束對象就是它的路徑")

        count = check_body(rel, body, first_line, bad)
        summary.append({"file": rel, "rules": count, "applies_to": applies if shared else [rel[:-3]]})

    checks = [
        {"check": name, "result": "不過" if items else "過", "violations": items}
        for name, items in violations.items()
    ]
    passed = all(not items for items in violations.values())
    print(
        json.dumps(
            {"constitution": str(root), "passed": passed, "files": summary, "checks": checks},
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"檢查了 {len(files)} 個檔,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
