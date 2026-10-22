# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""建一個給無頭 agy 用的家目錄:內容全部符號連結回真正的家目錄,只少了 MCP 設定檔。

agy 1.4.5 沒有停用 MCP 的調用旗標(`agy --help` 沒有;`agy mcp disable` 改的是全域設定),
MCP 伺服器列在 `~/.gemini/config/mcp_config.json`。這支腳本在 --dest 底下逐層連結真正家目錄的每一項,
只有 `.gemini/config/mcp_config.json` 不連,於是 `HOME=<--dest> agy -p …` 看不到任何 MCP 伺服器,
登入狀態、settings.json 的允許清單、git 設定與快取照常可用。
結果以 JSON 寫到 stdout。建好 exit 0;--dest 已存在且不是空目錄、或真正的家目錄沒有 `.gemini` 時 exit 2。
"""

import argparse
import json
import sys
from pathlib import Path

# 從家目錄往下逐層展開的路徑;最後一層是不連的那個檔
EXCLUDE = (".gemini", "config", "mcp_config.json")


def fail(message: str) -> None:
    """把錯誤寫到 stderr,以 exit code 2 結束。"""
    print(message, file=sys.stderr)
    sys.exit(2)


def mirror(src: Path, dest: Path, path: tuple[str, ...]) -> None:
    """把 src 底下每一項連結到 dest;path 的第一層展開成目錄往下遞迴,最後一層略過。"""
    dest.mkdir(parents=True, exist_ok=True)
    for entry in sorted(src.iterdir()):
        if entry.name == path[0]:
            if len(path) > 1:
                mirror(entry, dest / entry.name, path[1:])
            continue
        (dest / entry.name).symlink_to(entry)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="建一個連結回真正家目錄、但不含 ~/.gemini/config/mcp_config.json 的家目錄,給 HOME=<dest> agy -p 用"
    )
    parser.add_argument("--dest", required=True, type=Path, help="要建出的家目錄路徑(不存在或空目錄),例如任務資料夾底下的 home")
    parser.add_argument("--home", type=Path, default=Path.home(), help="真正的家目錄(預設目前使用者的家目錄)")
    args = parser.parse_args()

    if not (args.home / ".gemini").is_dir():
        fail(f"{args.home} 底下沒有 .gemini 目錄;--home 要給裝了 agy 的那個使用者的家目錄")
    if args.dest.exists() and (not args.dest.is_dir() or any(args.dest.iterdir())):
        fail(f"--dest {args.dest} 已存在且不是空目錄;給一個新的路徑,或先刪掉上一次建的家目錄")
    mirror(args.home, args.dest, EXCLUDE)
    excluded = args.home.joinpath(*EXCLUDE)
    print(json.dumps({"home": str(args.dest), "excluded": str(excluded), "excluded_existed": excluded.exists()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
