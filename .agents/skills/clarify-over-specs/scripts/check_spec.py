# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查一份 spec.md 的結構:轉交同層 specify skill 的 scripts/check_spec.py,參數與結果原樣傳遞。

本 skill 改寫的是 specify 產出的 spec.md,結構規則只維護在 specify 那一份;這支腳本只負責找到它並執行。
結果以 JSON 寫到 stdout(由 specify 的腳本產生);有任何一項不過時 exit code 是 1,找不到 specify 的腳本時是 2。
"""

import argparse
import subprocess
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent.parent / "specify" / "scripts" / "check_spec.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--spec", required=True, type=Path, help="要檢查的 spec.md 檔案路徑,例如 specs/001-photo-album-organizer/spec.md")
    args = parser.parse_args()

    sys.stderr.reconfigure(encoding="utf-8")

    if not TARGET.is_file():
        print(
            f"找不到 specify 的結構檢查腳本:{TARGET}。"
            "clarify-over-specs 要和 specify 放在同一個 skills 資料夾底下;請先安裝 specify skill,或把兩支放到同一層後重跑。",
            file=sys.stderr,
        )
        return 2

    return subprocess.run([sys.executable, str(TARGET), "--spec", str(args.spec)]).returncode


if __name__ == "__main__":
    sys.exit(main())
