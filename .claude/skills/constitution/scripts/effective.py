# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""列出套用到指定產出物的憲法條文,以及被它們取代的 Skill 規範。

先執行同一個資料夾的 check_constitution.py;憲法檔的結構有不過時不列條文,直接以 exit code 1 結束。
套用到一個產出物的條文 = constitution/<skill>/<產出物>.md 的每一條,加上 _shared/ 裡 applies_to 含它的檔的每一條。
waive 是這些條文用 `- 取代:` 點名的 Skill 規範,寫成 `<規範檔名>〈Rule 名稱〉`,可以直接交給 check 腳本的 --waive。
專案沒有 constitution/ 資料夾時,條文與 waive 都是空的,exit code 是 0。
結果以 JSON 寫到 stdout。
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

RULE_HEADING = re.compile(r"^# Rule (\d+) \[(must|should)\] - (.+?)\s*$")
FRONT_APPLIES = re.compile(r"^applies_to:\s*\[(.*)\]\s*$")
REPLACE_LINE = re.compile(r"^- 取代[:：]\s*`?([\w-]+)/rules/([^`〈]+?)`?\s*〈(.+)〉\s*$")


def split_front(lines: list[str]) -> tuple[list[str], list[str]]:
    """拆出檔頭;回傳 (檔頭的行, 本文的行)。"""
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[1:i], lines[i + 1 :]
    return [], lines


def articles_of(path: Path, rel: str) -> list[dict]:
    """把一個憲法檔拆成一條一條的條文,保留每條的原文。"""
    _, body = split_front(path.read_text(encoding="utf-8").splitlines())
    result: list[dict] = []
    current: dict | None = None
    in_fence = False
    for line in body:
        if line.startswith("```"):
            in_fence = not in_fence
        if not in_fence and not line.startswith("```"):
            m = RULE_HEADING.match(line)
            if m:
                current = {
                    "file": rel,
                    "rule": int(m.group(1)),
                    "strength": m.group(2),
                    "name": m.group(3),
                    "replaces": [],
                    "lines": [],
                }
                result.append(current)
            elif current is not None:
                r = REPLACE_LINE.match(line.strip())
                if r:
                    current["replaces"].append(f"{Path(r.group(2).strip()).stem}〈{r.group(3).strip()}〉")
        if current is not None:
            current["lines"].append(line)
    for item in result:
        item["text"] = "\n".join(item.pop("lines")).strip()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="列出套用到指定產出物的憲法條文與被取代的 Skill 規範(waive),給 SDD Skill 在寫產出物之前讀。"
    )
    parser.add_argument(
        "--constitution",
        required=True,
        help="專案根目錄底下的 constitution 資料夾;資料夾不存在時視為沒有憲法",
    )
    parser.add_argument(
        "--artifact",
        required=True,
        action="append",
        help="產出物 ID,寫成 <skill>/<產出物>,例如 api-plan/openapi;要查好幾種就給好幾次",
    )
    args = parser.parse_args()

    root = Path(args.constitution)
    for artifact in args.artifact:
        if artifact.count("/") != 1:
            print(f"--artifact 收到「{artifact}」;要寫成 <skill>/<產出物>,例如 api-plan/openapi", file=sys.stderr)
            return 2

    if not root.is_dir():
        print(f"{root} 不存在,這個專案沒有憲法;照 Skill 自己的規範做", file=sys.stderr)
        print(json.dumps({"constitution": str(root), "exists": False, "artifacts": args.artifact,
                          "articles": [], "waive": []}, ensure_ascii=False, indent=2))
        return 0

    checker = Path(__file__).resolve().parent / "check_constitution.py"
    check = subprocess.run(
        [sys.executable, str(checker), "--constitution", str(root)],
        capture_output=True, text=True, encoding="utf-8",
    )
    if check.returncode != 0:
        print(check.stdout, file=sys.stderr)
        print(
            f"憲法檔的結構檢查沒有過(exit {check.returncode});先用 constitution skill 修好 {root},再取條文",
            file=sys.stderr,
        )
        return 1

    articles: list[dict] = []
    for path in sorted(p for p in root.rglob("*.md") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel.startswith("_shared/"):
            front, _ = split_front(path.read_text(encoding="utf-8").splitlines())
            applies: list[str] = []
            for line in front:
                m = FRONT_APPLIES.match(line.strip())
                if m:
                    applies = [x.strip() for x in m.group(1).split(",") if x.strip()]
            targets = [a for a in args.artifact if a in applies]
        else:
            targets = [a for a in args.artifact if a == rel[:-3]]
        if not targets:
            continue
        for item in articles_of(path, rel):
            item["applies_to"] = targets
            articles.append(item)

    waive = sorted({w for item in articles for w in item["replaces"]})
    print(json.dumps({"constitution": str(root), "exists": True, "artifacts": args.artifact,
                      "articles": articles, "waive": waive}, ensure_ascii=False, indent=2))
    print(f"套用到 {', '.join(args.artifact)} 的條文 {len(articles)} 條,取代 {len(waive)} 條 Skill 規範", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
