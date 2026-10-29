# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""取得套用到產出物的憲法條文:轉交同層 constitution skill 的 scripts/effective.py,參數與結果原樣傳遞。

憲法的解析與結構檢查只維護在 constitution 那一份;這支腳本只負責找到它並執行。
結果以 JSON 寫到 stdout(由 constitution 的腳本產生):articles 是套用到產出物的條文,waive 是被它們取代的 Skill 規範。
專案沒有 constitution/ 時兩者都是空的、exit code 是 0;憲法檔結構有不過時 exit code 是 1;找不到 constitution 的腳本時是 2。
"""

import argparse
import subprocess
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent.parent / "constitution" / "scripts" / "effective.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--constitution",
        required=True,
        type=Path,
        help="專案根目錄底下的 constitution 資料夾,例如 constitution;資料夾不存在時視為沒有憲法",
    )
    parser.add_argument(
        "--artifact",
        required=True,
        action="append",
        help="產出物 ID,寫成 <skill>/<產出物>,例如 api-plan/openapi;要查好幾種就給好幾次",
    )
    args = parser.parse_args()

    sys.stderr.reconfigure(encoding="utf-8")

    if not TARGET.is_file():
        print(
            f"找不到 constitution 的條文腳本:{TARGET}。"
            "這支 skill 要和 constitution 放在同一個 skills 資料夾底下;請先安裝 constitution skill,或把兩支放到同一層後重跑。",
            file=sys.stderr,
        )
        return 2

    command = [sys.executable, str(TARGET), "--constitution", str(args.constitution)]
    for artifact in args.artifact:
        command += ["--artifact", artifact]
    return subprocess.run(command).returncode


if __name__ == "__main__":
    sys.exit(main())
