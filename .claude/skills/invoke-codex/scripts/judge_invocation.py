# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""判定一次 codex exec 調用的結果:成功、用量用完或其他失敗。

讀 codex 以 `-o` 寫出的最後訊息檔、同一次調用的 stderr 紀錄檔與結束碼紀錄檔,結果以 JSON 寫到 stdout。
判得出結果時 exit code 是 0(不論判定是哪一種);stderr 紀錄檔不存在或讀不了時是 2;
結束碼紀錄檔還沒有出現(codex 還沒結束)時不判定,是 3。
"""

import argparse
import json
import re
import sys
from pathlib import Path

USAGE_LIMIT = "hit your usage limit"
RETRY_AT = re.compile(r"try again at ([^\"\\\n]+?)\.(?:\s|\"|\\|$)")
EVIDENCE_LIMIT = 300


def judge(output: str, stderr: str, exit_text: str) -> dict:
    """結束碼是 0 而且最後訊息檔有內容就是成功;否則 stderr 提到用量上限是用量用完,其餘是其他失敗。"""
    exit_text = exit_text.strip()
    if exit_text == "0" and output.strip():
        return {"verdict": "success", "evidence": "結束碼是 0,最後訊息檔有內容", "retry_at": None}

    limit_lines = [line.strip() for line in stderr.splitlines() if USAGE_LIMIT in line]
    if limit_lines:
        retry = RETRY_AT.search(limit_lines[-1]) or RETRY_AT.search("\n".join(limit_lines))
        return {
            "verdict": "quota_exhausted",
            "evidence": limit_lines[-1][:EVIDENCE_LIMIT],
            "retry_at": retry.group(1).strip() if retry else None,
        }

    if exit_text != "0":
        evidence = f"結束碼是 {exit_text or '空的'}"
    else:
        evidence = "結束碼是 0,但最後訊息檔不存在或沒有內容"
    last = next((line.strip() for line in reversed(stderr.splitlines()) if line.strip()), "")
    if last:
        evidence = f"{evidence};stderr 最後一行:{last}"
    return {"verdict": "failed", "evidence": evidence[:EVIDENCE_LIMIT], "retry_at": None}


def read_text(path: Path, option: str) -> str:
    """讀紀錄檔;不存在或讀不了就說明哪個參數要改,以 exit code 2 結束。"""
    if not path.is_file():
        print(
            f"錯誤:{option} 收到 {path},這個檔不存在。"
            f"預期是這次調用的紀錄檔;先確認 codex 的 stderr 有重導向到這個路徑,再重跑。",
            file=sys.stderr,
        )
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"錯誤:{option} 收到 {path},讀不了({exc})。預期是一個讀得到的文字檔。", file=sys.stderr)
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="判定一次 codex exec 調用的結果:成功(success)、用量用完(quota_exhausted)或其他失敗(failed)。"
        "結果以 JSON 寫到 stdout,欄位是 verdict、evidence(判定依據一行)"
        "與 retry_at(用量用完時 stderr 寫的可重試時間,其餘是 null)。"
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="codex exec 以 -o 寫出的最後訊息檔路徑(例如 codex.out);codex 沒有寫出這個檔時照樣傳,會當成沒有內容",
    )
    parser.add_argument(
        "--stderr",
        required=True,
        type=Path,
        help="同一次調用的 stderr 重導向寫出的紀錄檔路徑(例如 codex.err)",
    )
    parser.add_argument(
        "--exit",
        required=True,
        type=Path,
        dest="exit_file",
        help="調用指令最後以 `; echo $? > codex.exit` 寫出的結束碼紀錄檔路徑(例如 codex.exit);這個檔還不存在就不判定",
    )
    args = parser.parse_args()

    if not args.exit_file.is_file():
        print(
            f"還不能判定:--exit 收到 {args.exit_file},這個檔還沒有出現,代表 codex 還沒結束。"
            f"等它出現再重跑這一步;若 codex 的行程已經不在而這個檔一直沒有出現,"
            f"代表整條調用指令被外部中斷,結束碼沒有寫出來。",
            file=sys.stderr,
        )
        sys.exit(3)

    exit_text = read_text(args.exit_file, "--exit")
    stderr = read_text(args.stderr, "--stderr")
    output = args.output.read_text(encoding="utf-8", errors="replace") if args.output.is_file() else ""

    print(json.dumps(judge(output, stderr, exit_text), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
