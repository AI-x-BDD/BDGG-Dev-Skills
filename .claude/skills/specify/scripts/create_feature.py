# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""建立這個功能的規格資料夾 specs/<NNN>-<功能簡稱>/。

編號取 specs/ 底下 NNN- 開頭資料夾的最大編號加 1,沒有就從 001 開始;同一個功能簡稱已經有資料夾時沿用它,不另建。
不碰 git。結果以 JSON 寫到 stdout:branch(功能分支名稱)、spec_dir、spec_path、number。
"""

import argparse
import json
import re
import sys
from pathlib import Path

SHORT_NAME = re.compile(r"^[a-z][a-z0-9]*(-[a-z][a-z0-9]*){1,3}$")
FEATURE_DIR = re.compile(r"^(\d{3})-(.+)$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--short-name", required=True, help="功能簡稱:2 到 4 個小寫英文單字,以連字號連接,例如 photo-album-organizer")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="要建立 specs/ 的專案根目錄,預設為目前的工作目錄")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not SHORT_NAME.match(args.short_name):
        print(
            f"錯誤: 收到的功能簡稱是 {args.short_name!r};預期是 2 到 4 個小寫英文單字、以連字號連接,"
            "每個單字以字母開頭,例如 photo-album-organizer。",
            file=sys.stderr,
        )
        return 1
    if not args.root.is_dir():
        print(f"錯誤: --root 收到 {args.root},這不是一個存在的目錄;請給專案的根目錄。", file=sys.stderr)
        return 1

    specs = args.root / "specs"
    existing = {}
    if specs.is_dir():
        for path in specs.iterdir():
            match = FEATURE_DIR.match(path.name)
            if path.is_dir() and match:
                existing.setdefault(match.group(2), []).append(int(match.group(1)))

    if args.short_name in existing:
        number = max(existing[args.short_name])
        print(f"specs/ 底下已經有 {args.short_name} 的資料夾,沿用編號 {number:03d}", file=sys.stderr)
    else:
        number = max((n for numbers in existing.values() for n in numbers), default=0) + 1

    branch = f"{number:03d}-{args.short_name}"
    spec_dir = specs / branch
    spec_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "branch": branch,
        "spec_dir": spec_dir.as_posix(),
        "spec_path": (spec_dir / "spec.md").as_posix(),
        "number": f"{number:03d}",
    }
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
