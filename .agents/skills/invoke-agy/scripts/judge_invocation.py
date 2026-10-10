# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""判定一次 agy --print 調用的結果:成功、逾時、權限中止、額度用完或其他失敗。

讀 agy 以 `--output-format json` 寫出的 JSON 紀錄檔與同一次調用的 stderr 紀錄檔,結果以 JSON 寫到 stdout。
判得出結果時 exit code 是 0(不論判定是哪一種);JSON 或 stderr 紀錄檔不存在或讀不了時是 2;
結束碼紀錄檔還沒有出現(agy 還沒結束)時不判定,是 3。
"""

import argparse
import json
import re
import sys
from pathlib import Path

QUOTA = re.compile(r"RESOURCE_EXHAUSTED|quota reached", re.IGNORECASE)
RESETS_IN = re.compile(r"Resets in ((?:\d+h)?(?:\d+m)?(?:\d+(?:\.\d+)?s)?)")
DENIED = "auto-denied"
TIMEOUT = "print timeout"
EVIDENCE_LIMIT = 300


def matching_line(text: str, matches) -> str | None:
    """回傳 text 裡第一個讓 matches 成立的那一行。"""
    for line in text.splitlines():
        if matches(line):
            return line.strip()[:EVIDENCE_LIMIT]
    return None


def judge(record: dict | None, stderr: str) -> dict:
    """依額度、權限、逾時、其他失敗、成功的順序判定,先符合的先用。"""
    error = record.get("error") if record else None
    error = error if isinstance(error, str) else ""

    quota_line = matching_line(stderr, QUOTA.search) or matching_line(error, QUOTA.search)
    if quota_line:
        resets = RESETS_IN.search(stderr) or RESETS_IN.search(error)
        resets_in = resets.group(1) if resets and resets.group(1) else None
        return {"verdict": "quota_exhausted", "evidence": quota_line, "resets_in": resets_in}

    denied_line = matching_line(stderr, lambda line: DENIED in line)
    denied_actions = record.get("denied_actions") if record else None
    if denied_actions or denied_line:
        evidence = denied_line or f"denied_actions: {json.dumps(denied_actions, ensure_ascii=False)}"[:EVIDENCE_LIMIT]
        return {"verdict": "permission_denied", "evidence": evidence, "resets_in": None}

    timeout_line = matching_line(stderr, lambda line: TIMEOUT in line)
    if timeout_line:
        return {"verdict": "timeout", "evidence": timeout_line, "resets_in": None}

    if record is None:
        return {"verdict": "failed", "evidence": "JSON 紀錄檔的內容不是一份 JSON 物件", "resets_in": None}
    status = record.get("status")
    if status != "SUCCESS":
        evidence = f"status: {status}; error: {error or '沒有'}"[:EVIDENCE_LIMIT]
        return {"verdict": "failed", "evidence": evidence, "resets_in": None}
    response = record.get("response")
    if not isinstance(response, str) or not response.strip():
        return {"verdict": "failed", "evidence": "status 是 SUCCESS,但 response 是空的", "resets_in": None}

    return {"verdict": "success", "evidence": "status 是 SUCCESS,response 有內容", "resets_in": None}


def read_text(path: Path, option: str) -> str:
    """讀紀錄檔;不存在或讀不了就說明哪個參數要改,以 exit code 2 結束。"""
    if not path.is_file():
        print(
            f"錯誤:{option} 收到 {path},這個檔不存在。"
            f"預期是這次調用的紀錄檔;先確認 agy 的輸出有重導向到這個路徑,再重跑。",
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
        description="判定一次 agy --print 調用的結果:成功(success)、逾時(timeout)、權限中止(permission_denied)、"
        "額度用完(quota_exhausted)或其他失敗(failed)。結果以 JSON 寫到 stdout,"
        "欄位是 verdict、evidence(判定依據的原文一行)與 resets_in(額度用完時的等待時間,其餘是 null)。"
    )
    parser.add_argument(
        "--json",
        required=True,
        type=Path,
        help="agy 以 --output-format json 執行時,stdout 重導向寫出的紀錄檔路徑(例如 agy.json)",
    )
    parser.add_argument(
        "--stderr",
        required=True,
        type=Path,
        help="同一次調用的 stderr 重導向寫出的紀錄檔路徑(例如 agy.err)",
    )
    parser.add_argument(
        "--exit",
        required=True,
        type=Path,
        dest="exit_file",
        help="調用指令最後以 `; echo $? > agy.exit` 寫出的結束碼紀錄檔路徑(例如 agy.exit);這個檔還不存在就不判定",
    )
    args = parser.parse_args()

    if not args.exit_file.is_file():
        print(
            f"還不能判定:--exit 收到 {args.exit_file},這個檔還沒有出現,代表 agy 還沒結束。"
            f"等它出現再重跑這一步;若 agy 的行程已經不在而這個檔一直沒有出現,"
            f"代表整條調用指令被外部中斷,結束碼沒有寫出來。",
            file=sys.stderr,
        )
        sys.exit(3)

    raw = read_text(args.json, "--json")
    stderr = read_text(args.stderr, "--stderr")
    try:
        record = json.loads(raw)
    except json.JSONDecodeError:
        record = None
    if not isinstance(record, dict):
        record = None

    print(json.dumps(judge(record, stderr), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
