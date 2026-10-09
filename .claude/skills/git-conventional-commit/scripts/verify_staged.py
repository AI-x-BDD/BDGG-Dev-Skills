# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""把 repo 的 index(已經 stage 的內容)匯出到暫存目錄,在那裡執行建置與測試指令。

用來確認「即將提交的這一筆」單獨取出時建置與測試會通過:匯出的目錄只有 index 裡的檔案,
不含工作目錄裡還沒 stage 的變更。不會動到工作目錄與 index,跑完就刪掉暫存目錄。

結果以一份 JSON 寫到 stdout:
  passed     true 代表 --cmd 以 exit code 0 結束
  exit_code  --cmd 的 exit code
  output     --cmd 輸出(stdout 與 stderr)的最後 60 行

exit code:0 通過;1 --cmd 沒有通過;2 沒辦法執行(不是 git repo、--link 的路徑不對)。
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

OUTPUT_TAIL_LINES = 60


def fail(message):
    print(f"錯誤: {message}", file=sys.stderr)
    sys.exit(2)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", required=True, type=Path, help="要驗證的 git repo 的根目錄")
    parser.add_argument("--cmd", required=True, help="建置與測試指令,在匯出的目錄以 shell 執行,例如 \"npm test\"")
    parser.add_argument("--link", action="append", default=[], metavar="PATH",
                        help="被 gitignore 的建置相依,寫相對於 repo 根目錄的路徑(例如 node_modules);"
                             "以 symlink 連進匯出的目錄,不必重新安裝。可以重複給,沒有就不給")
    args = parser.parse_args()

    top = subprocess.run(["git", "-C", str(args.repo), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, encoding="utf-8")
    if top.returncode != 0:
        fail(f"{args.repo} 不是 git repo({top.stderr.strip()})。--repo 要給 git repo 的根目錄。")
    root = Path(top.stdout.strip())

    links = []
    for raw in args.link:
        rel = Path(raw)
        if rel.is_absolute() or ".." in rel.parts:
            fail(f"--link 收到 {raw},預期是相對於 repo 根目錄、不含 .. 的路徑(例如 node_modules)。")
        if not (root / rel).exists():
            fail(f"--link 指到的 {root / rel} 不存在。--link 要給 repo 裡已經裝好的建置相依,相對於 repo 根目錄。")
        links.append(rel)

    export = Path(tempfile.mkdtemp(prefix="verify-staged-"))
    try:
        # --prefix 結尾的分隔符號不能省,否則會變成檔名的前綴
        out = subprocess.run(["git", "-C", str(root), "checkout-index", "-a", f"--prefix={export}/"],
                             capture_output=True, text=True, encoding="utf-8")
        if out.returncode != 0:
            fail(f"匯出 index 失敗({out.stderr.strip()})。先確認 {root} 的 index 沒有未解決的衝突。")
        for rel in links:
            dest = export / rel
            if dest.exists() or dest.is_symlink():
                fail(f"--link 的 {rel} 已經在 index 裡,不是被 gitignore 的相依。--link 只給沒有進版控的路徑。")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.symlink_to(root / rel, target_is_directory=(root / rel).is_dir())
        print(f"已把 index 匯出到 {export},執行: {args.cmd}", file=sys.stderr)

        run = subprocess.run(args.cmd, shell=True, cwd=export, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, encoding="utf-8", errors="replace")
    finally:
        # rmtree 不會跟著 symlink 進去,--link 指到的原件不受影響
        shutil.rmtree(export, ignore_errors=True)

    result = {
        "passed": run.returncode == 0,
        "exit_code": run.returncode,
        "output": "\n".join(run.stdout.splitlines()[-OUTPUT_TAIL_LINES:]),
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
