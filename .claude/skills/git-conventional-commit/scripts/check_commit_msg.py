# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查一份 commit 訊息草稿是否符合 Conventional Commits 1.0.0。

結果以一份 JSON 寫到 stdout:
  header    訊息的第一行
  skipped   true 代表這是 git 自動產生的 merge 訊息,規範未涵蓋,不檢查
  errors    違反規範的地方(https://www.conventionalcommits.org/en/v1.0.0/#specification)
  warnings  偏離 Angular / commitlint 常見慣例的地方,規範本身不要求

exit code:0 沒有 errors;1 有 errors;2 讀不到訊息檔。
"""
import argparse
import json
import re
import sys
from pathlib import Path

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

    for i, line in enumerate(lines[1:], start=2):
        if line.startswith(("BREAKING CHANGE: ", "BREAKING-CHANGE: ")):
            if not line.split(": ", 1)[1].strip():
                errors.append(f"第 {i} 行:BREAKING CHANGE 後面要有說明(規範 12)")
            if lines[i - 2].strip() and not FOOTER_RE.match(lines[i - 2]):
                errors.append(f"第 {i} 行:footer 區塊前面要空一行(規範 8)")
        elif BREAKING_ANYCASE_RE.match(line):
            errors.append(f"第 {i} 行:必須是全大寫的 `BREAKING CHANGE: `,冒號後接一個空格(規範 12、15)")

    return errors, warns, False


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", required=True, type=Path, help="commit 訊息草稿的檔案路徑(之後要交給 git commit -F 的那一個檔)")
    args = parser.parse_args()

    try:
        message = args.file.read_text(encoding="utf-8")
    except OSError as e:
        print(f"錯誤: 讀不到訊息檔 {args.file}({e.strerror})。--file 要給已經寫好的 commit 訊息草稿的檔案路徑。", file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError:
        print(f"錯誤: {args.file} 不是 UTF-8 的文字檔。--file 要給以 UTF-8 存檔的 commit 訊息草稿。", file=sys.stderr)
        sys.exit(2)

    errors, warns, skipped = check(message)
    result = {
        "header": strip_comments(message).split("\n")[0],
        "skipped": skipped,
        "errors": errors,
        "warnings": warns,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
