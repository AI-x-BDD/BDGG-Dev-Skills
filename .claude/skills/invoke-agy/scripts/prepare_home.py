# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""建一個給無頭 agy 用的全新家目錄:只複製 agy 需要讀的設定檔,不連結也不複製其他東西。

agy 1.4.5 沒有停用 MCP 的調用旗標(`agy --help` 沒有;`agy mcp disable` 改的是全域設定),
MCP 伺服器列在 `~/.gemini/config/mcp_config.json`;新家目錄裡沒有這個檔,`HOME=<--dest> agy -p …` 就看不到任何 MCP 伺服器。
複製的清單(COPIES)與理由:
- `.gemini/antigravity-cli/settings.json`:permissions 允許清單與預設模型;不帶它,無頭的 agy 每個指令都會被拒絕
- `.gitconfig`:git 的 user 與安全設定;不帶它,agy 執行的 git 沒有身分
登入不在這份清單裡:2026-10-23 實測只放 settings.json 的家目錄,`agy -p` 照常回覆(登入走系統金鑰圈,不讀 HOME 底下的檔)。
一律複製、不建符號連結:agy 以 accept-edits 寫進 $HOME 的東西(對話紀錄、快取、或任務誤寫的檔)只會落在新家目錄,
不會穿透到真正家目錄的 `.ssh`、`.config`、`.claude` 或 agy 自己的設定。
結果以 JSON 寫到 stdout。建好 exit 0;--dest 是符號連結、已存在且不是空目錄、或真正的家目錄沒有 settings.json 時 exit 2。
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

SETTINGS = Path(".gemini") / "antigravity-cli" / "settings.json"
COPIES = (SETTINGS, Path(".gitconfig"))
MCP_CONFIG = Path(".gemini") / "config" / "mcp_config.json"


def fail(message: str) -> None:
    """把錯誤寫到 stderr,以 exit code 2 結束。"""
    print(message, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="建一個只含 agy settings.json 與 .gitconfig 複本、沒有 MCP 設定的新家目錄,給 HOME=<dest> agy -p 用"
    )
    parser.add_argument("--dest", required=True, type=Path, help="要建出的家目錄路徑(不存在或空目錄),例如任務資料夾底下的 home")
    parser.add_argument("--home", type=Path, default=Path.home(), help="真正的家目錄(預設目前使用者的家目錄)")
    args = parser.parse_args()

    if not (args.home / SETTINGS).is_file():
        fail(f"{args.home / SETTINGS} 不存在;--home 要給裝了 agy、登入過的那個使用者的家目錄")
    if args.dest.is_symlink():
        fail(f"--dest {args.dest} 是符號連結;給一個真實的新路徑,寫入才不會落到連結指向的地方")
    if args.dest.exists() and (not args.dest.is_dir() or any(args.dest.iterdir())):
        fail(f"--dest {args.dest} 已存在且不是空目錄;每次調用給一個新的路徑,上一次的家目錄確認不用了再刪")
    args.dest.mkdir(parents=True, exist_ok=True, mode=0o700)
    args.dest.chmod(0o700)  # 既有的空目錄也收緊成只有自己能讀寫
    copied = []
    for rel in COPIES:
        src = args.home / rel
        if not src.is_file():
            print(f"{src} 不存在,略過", file=sys.stderr)
            continue
        target = args.dest / rel
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(src, target, follow_symlinks=True)
        target.chmod(0o600)
        copied.append(str(rel))
    print(json.dumps({"home": str(args.dest), "copied": copied, "mcp_config_present": (args.dest / MCP_CONFIG).exists()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
