# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""把端點節的檔接進 testplan 的骨架,寫成 testplan.md。

骨架裡每個端點節的位置寫一行 `<!-- 端點節:<檔名> -->`,這一行會換成 --parts 資料夾裡同名檔的內容(原文照貼,
不改一個字)。骨架裡點名的檔不存在、資料夾裡有沒被點名的檔、或同一個檔被點名兩次,都算錯,不寫出檔案。

結果以 JSON 寫到 stdout:接了哪些檔、各幾行;exit code 0 是寫好了,1 是有錯(錯誤寫在 JSON 的 errors),
2 是參數指到的檔或資料夾不存在。
"""

import argparse
import json
import re
import sys
from pathlib import Path

MARKER = re.compile(r"^<!-- 端點節:(\S+?) -->\s*$")


def main() -> int:
    parser = argparse.ArgumentParser(description="把端點節的檔接進 testplan 的骨架,寫成 testplan.md。")
    parser.add_argument("--skeleton", required=True, type=Path, help="主 agent 寫的骨架;每個端點節的位置寫一行 <!-- 端點節:<檔名> -->")
    parser.add_argument("--parts", required=True, type=Path, help="端點節 subagent 寫好的檔所在的資料夾(例如 <spec package>/.testplan-parts)")
    parser.add_argument("--out", required=True, type=Path, help="要寫出的 testplan.md 路徑;可以和 --skeleton 是同一個檔")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.skeleton.is_file():
        print(f"錯誤: 找不到骨架 {args.skeleton}。請先寫出骨架,再執行這支腳本。", file=sys.stderr)
        return 2
    if not args.parts.is_dir():
        print(f"錯誤: 找不到端點節的資料夾 {args.parts}。請確認端點節 subagent 把檔寫在這裡。", file=sys.stderr)
        return 2

    lines = args.skeleton.read_text(encoding="utf-8").split("\n")
    available = {p.name for p in args.parts.iterdir() if p.is_file() and p.suffix == ".md"}
    used: list[str] = []
    errors: list[str] = []
    out: list[str] = []
    joined: list[dict[str, object]] = []
    for number, line in enumerate(lines, start=1):
        marker = MARKER.match(line)
        if not marker:
            out.append(line)
            continue
        name = marker.group(1)
        if name in used:
            errors.append(f"骨架第 {number} 行再次點名 {name};每個端點節只接一次")
            continue
        if name not in available:
            errors.append(f"骨架第 {number} 行點名的 {name} 不在 {args.parts};確認檔名,或請那一節的 subagent 補寫")
            continue
        used.append(name)
        content = (args.parts / name).read_text(encoding="utf-8").rstrip("\n").split("\n")
        out.extend(content)
        joined.append({"file": name, "lines": len(content)})
    for name in sorted(available - set(used)):
        errors.append(f"{args.parts / name} 沒有被骨架點名;在骨架對應的位置加一行 <!-- 端點節:{name} -->")

    if errors:
        print(json.dumps({"written": False, "errors": errors, "joined": joined}, ensure_ascii=False, indent=2))
        return 1
    args.out.write_text("\n".join(out), encoding="utf-8")
    print(json.dumps({"written": True, "out": str(args.out), "joined": joined}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
