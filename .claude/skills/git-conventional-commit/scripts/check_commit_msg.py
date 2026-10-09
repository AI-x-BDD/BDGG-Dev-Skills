#!/usr/bin/env python3
"""檢查 commit 訊息是否符合 Conventional Commits 1.0.0。

ERROR = 違反規範(https://www.conventionalcommits.org/en/v1.0.0/#specification)
WARN  = 偏離 Angular / commitlint 的常見慣例,規範本身不要求

用法:
  check_commit_msg.py --file MSG_FILE     檢查一份訊息草稿
  check_commit_msg.py [-C REPO] --rev HEAD          檢查單一 commit
  check_commit_msg.py [-C REPO] --range main..HEAD  檢查一段歷史
  echo "feat: x" | check_commit_msg.py    從 stdin 讀

任何一筆有 ERROR 時結束碼為 1。
"""
import argparse
import re
import subprocess
import sys

COMMON_TYPES = {
    "feat", "fix", "build", "chore", "ci", "docs",
    "perf", "refactor", "revert", "style", "test",
}
HEADER_MAX = 100

# 規範 1、4、5、13:type、選用的 (scope)、選用的 !、必要的 ": "、description
HEADER_RE = re.compile(r"^(?P<type>[A-Za-z][\w-]*)(?:\((?P<scope>[^()\r\n]+)\))?(?P<bang>!)?: (?P<desc>\S.*)$")
# 規範 8、9:token 後接 ": " 或 " #";token 內以 - 取代空白,BREAKING CHANGE 例外
FOOTER_RE = re.compile(r"^(?P<token>BREAKING CHANGE|[A-Za-z][\w-]*)(?:: | #)\S")
BREAKING_ANYCASE_RE = re.compile(r"^breaking[ -]change\s*:", re.IGNORECASE)
MERGE_RE = re.compile(r"^Merge (branch|pull request|remote-tracking branch|tag|commit) ")


def strip_comments(text):
    return "\n".join(l for l in text.splitlines() if not l.startswith("#")).strip("\n")


def check(message):
    errors, warns = [], []
    lines = strip_comments(message).split("\n")
    header = lines[0] if lines else ""

    if not header.strip():
        return ["訊息是空的"], warns, False
    if MERGE_RE.match(header):
        return errors, warns, True

    m = HEADER_RE.match(header)
    if not m:
        if re.match(r"^[A-Za-z][\w-]*(\([^()]*\))?!?:\S", header):
            errors.append("冒號後面必須有一個空格再接 description(規範 1、5)")
        elif re.match(r"^[A-Za-z][\w-]*(\([^()]*\))?!?:\s*$", header):
            errors.append("缺少 description(規範 5)")
        elif re.match(r"^[A-Za-z][\w-]*!\(", header):
            errors.append("`!` 必須緊貼在 `:` 之前,放在 scope 的右括號之後(規範 13)")
        else:
            errors.append("header 不符合 `<type>[(scope)][!]: <description>`(規範 1)")
    else:
        t = m.group("type")
        if t.lower() not in COMMON_TYPES:
            warns.append(f"type `{t}` 不在常見清單內 —— 規範允許自訂 type,請確認不是打錯字")
        elif t != t.lower():
            warns.append(f"type `{t}` 建議小寫,並與既有歷史一致")
        if m.group("desc").rstrip().endswith("."):
            warns.append("description 結尾慣例上不加句點")
    if len(header) > HEADER_MAX:
        warns.append(f"header 長度 {len(header)},超過慣例的 {HEADER_MAX} 字元")

    if len(lines) > 1 and lines[1].strip():
        errors.append("header 與 body / footer 之間必須空一行(規範 6、8)")

    has_bang = bool(m and m.group("bang"))
    has_breaking_footer = False
    for i, line in enumerate(lines[1:], start=2):
        if line.startswith(("BREAKING CHANGE: ", "BREAKING-CHANGE: ")):
            has_breaking_footer = True
            if not line.split(": ", 1)[1].strip():
                errors.append(f"第 {i} 行:BREAKING CHANGE 後面要有說明(規範 12)")
            if lines[i - 2].strip() and not FOOTER_RE.match(lines[i - 2]):
                errors.append(f"第 {i} 行:footer 區塊前面要空一行(規範 8)")
        elif BREAKING_ANYCASE_RE.match(line):
            errors.append(f"第 {i} 行:必須是全大寫的 `BREAKING CHANGE: `,冒號後接一個空格(規範 12、15)")

    return errors, warns, False


REPO = "."


def git(*args):
    r = subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} 失敗(repo: {REPO}):{r.stderr.strip()}\n"
                 "不在目標 repo 的目錄下執行時,請用 -C <repo> 指定。")
    return r.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--file", help="訊息檔路徑")
    src.add_argument("--rev", help="單一 commit")
    src.add_argument("--range", dest="rng", help="commit 範圍,例如 main..HEAD")
    ap.add_argument("-C", "--repo", default=".", help="要檢查的 git repo(預設為目前目錄)")
    args = ap.parse_args()
    global REPO
    REPO = args.repo

    if args.file:
        items = [(args.file, open(args.file, encoding="utf-8").read())]
    elif args.rev:
        sha = git("rev-parse", "--short", args.rev).strip()
        items = [(sha, git("log", "-1", "--format=%B", args.rev))]
    elif args.rng:
        shas = git("log", "--reverse", "--format=%h", args.rng).split()
        items = [(s, git("log", "-1", "--format=%B", s)) for s in shas]
    else:
        items = [("stdin", sys.stdin.read())]

    failed = 0
    for label, msg in items:
        errors, warns, skipped = check(msg)
        header = strip_comments(msg).split("\n")[0]
        if skipped:
            print(f"SKIP  {label}  {header}  (merge commit,規範未涵蓋)")
            continue
        print(f"{'FAIL' if errors else 'OK  '}  {label}  {header}")
        for e in errors:
            print(f"      ERROR {e}")
        for w in warns:
            print(f"      WARN  {w}")
        failed += bool(errors)

    print(f"\n檢查 {len(items)} 筆,{failed} 筆不符規範")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
