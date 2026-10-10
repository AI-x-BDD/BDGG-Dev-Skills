# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""判定一次 copilot -p 調用是成功還是失敗。

讀 copilot 以 `--output-format json` 寫出的 JSONL 紀錄檔與同一次調用的 stderr 紀錄檔,結果以 JSON 寫到 stdout。
判得出結果時 exit code 是 0(不論判定是哪一種);JSONL 或 stderr 紀錄檔不存在或讀不了時是 2;
結束碼紀錄檔還沒有出現(copilot 還沒結束)時不判定,是 3。
"""

import argparse
import json
import sys
from pathlib import Path

EVIDENCE_LIMIT = 300


def first_line(text: str) -> str:
    """回傳 text 第一個非空白的行;沒有就回空字串。"""
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


def with_stderr(evidence: str, stderr: str) -> str:
    """失敗時把 stderr 的第一行接在依據後面,方便看出原因。"""
    line = first_line(stderr)
    if line:
        evidence = f"{evidence};stderr 第一行:{line}"
    return evidence[:EVIDENCE_LIMIT]


def judge(events: list[dict], stderr: str) -> dict:
    """沒有 result 事件、exitCode 不是 0、或沒有非空的回覆就是失敗,其餘是成功。"""
    denied_tools = 0
    has_reply = False
    result = None
    for event in events:
        kind = event.get("type")
        data = event.get("data")
        data = data if isinstance(data, dict) else {}
        if kind == "result":
            result = event
        elif kind == "assistant.message":
            content = data.get("content")
            if isinstance(content, str) and content.strip():
                has_reply = True
        elif kind == "tool.execution_complete":
            error = data.get("error")
            if data.get("success") is False and isinstance(error, dict) and error.get("code") == "denied":
                denied_tools += 1

    if result is None:
        evidence = with_stderr("JSONL 紀錄檔裡沒有 result 事件", stderr)
        return {"verdict": "failed", "evidence": evidence, "denied_tools": denied_tools}
    exit_code = result.get("exitCode")
    if exit_code != 0:
        evidence = with_stderr(f"result 事件的 exitCode 是 {exit_code}", stderr)
        return {"verdict": "failed", "evidence": evidence, "denied_tools": denied_tools}
    if not has_reply:
        evidence = with_stderr("result 事件的 exitCode 是 0,但沒有非空的 assistant.message", stderr)
        return {"verdict": "failed", "evidence": evidence, "denied_tools": denied_tools}
    return {
        "verdict": "success",
        "evidence": "result 事件的 exitCode 是 0,有非空的 assistant.message",
        "denied_tools": denied_tools,
    }


def read_text(path: Path, option: str) -> str:
    """讀紀錄檔;不存在或讀不了就說明哪個參數要改,以 exit code 2 結束。"""
    if not path.is_file():
        print(
            f"錯誤:{option} 收到 {path},這個檔不存在。"
            f"預期是這次調用的紀錄檔;先確認 copilot 的輸出有重導向到這個路徑,再重跑。",
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
        description="判定一次 copilot -p 調用是成功(success)還是失敗(failed)。結果以 JSON 寫到 stdout,"
        "欄位是 verdict、evidence(判定依據一行)與 denied_tools(被拒的工具呼叫次數)。"
    )
    parser.add_argument(
        "--jsonl",
        required=True,
        type=Path,
        help="copilot 以 --output-format json 執行時,stdout 重導向寫出的紀錄檔路徑(例如 copilot.jsonl)",
    )
    parser.add_argument(
        "--stderr",
        required=True,
        type=Path,
        help="同一次調用的 stderr 重導向寫出的紀錄檔路徑(例如 copilot.err)",
    )
    parser.add_argument(
        "--exit",
        required=True,
        type=Path,
        dest="exit_file",
        help="調用指令最後以 `; echo $? > copilot.exit` 寫出的結束碼紀錄檔路徑(例如 copilot.exit);這個檔還不存在就不判定",
    )
    args = parser.parse_args()

    if not args.exit_file.is_file():
        print(
            f"還不能判定:--exit 收到 {args.exit_file},這個檔還沒有出現,代表 copilot 還沒結束。"
            f"等它出現再重跑這一步;若 copilot 的行程已經不在而這個檔一直沒有出現,"
            f"代表整條調用指令被外部中斷,結束碼沒有寫出來。",
            file=sys.stderr,
        )
        sys.exit(3)

    raw = read_text(args.jsonl, "--jsonl")
    stderr = read_text(args.stderr, "--stderr")
    events = []
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)

    print(json.dumps(judge(events, stderr), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
