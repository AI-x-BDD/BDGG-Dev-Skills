# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""依任務性質與 ai-quota 的剩餘額度,決定這次 agy 調用的 `--model`。

審查(review)預設用 Argon;`gemini-4-argon-7d` 剩餘低於門檻、stale、或查不到額度時改用 Flash。
開發(dev)一律用 Flash。Flash 用到的池(`gemini-5h`、`gemini-7d`)有一個剩 0% 時判定額度用完。
模型代號以 `agy models` 列出的為準(agy 1.4.5,2026-10-23)。
結果以 JSON 寫到 stdout。選得出模型 exit 0;額度用完 exit 1;參數或 --state-file 讀不了 exit 2。
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ARGON = "gemini-4-argon-high"
FLASH = "gemini-3.8-flash-medium"
ARGON_POOL = "gemini-4-argon-7d"
FLASH_POOLS = ("gemini-5h", "gemini-7d")
DEFAULT_URL = "http://192.0.2.10:8905/api/state"


def fail(message: str) -> None:
    """把錯誤寫到 stderr,以 exit code 2 結束。"""
    print(message, file=sys.stderr)
    sys.exit(2)


def load_state(url: str, state_file: Path | None) -> tuple[dict | None, str | None]:
    """讀 ai-quota 的 /api/state;回傳 (state, 讀不到的原因)。"""
    if state_file is not None:
        try:
            return json.loads(state_file.read_text(encoding="utf-8")), None
        except OSError as exc:
            fail(f"讀不到 --state-file {state_file}:{exc.strerror};要給 ai-quota /api/state 存下來的 JSON 檔")
        except json.JSONDecodeError as exc:
            fail(f"--state-file {state_file} 不是合法的 JSON:第 {exc.lineno} 行 {exc.msg}")
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return None, f"ai-quota {url} 查不到:{exc}"


def pools(state: dict | None) -> dict[str, dict]:
    """把 providers[].pools[] 攤平成 {pool id: {remaining_pct, stale}},只留 gemini 開頭的池。"""
    out = {}
    providers = state.get("providers") if isinstance(state, dict) else None
    for provider in providers if isinstance(providers, list) else []:
        entries = provider.get("pools") if isinstance(provider, dict) else None
        for pool in entries if isinstance(entries, list) else []:
            pid = pool.get("id") if isinstance(pool, dict) else None
            if isinstance(pid, str) and pid.startswith("gemini"):
                out[pid] = {"remaining_pct": pool.get("remaining_pct"), "stale": bool(pool.get("stale"))}
    return out


def usable(pool: dict | None, threshold: float) -> bool:
    """池存在、沒有 stale、剩餘是數字且不低於門檻。"""
    if not pool or pool["stale"]:
        return False
    pct = pool["remaining_pct"]
    return isinstance(pct, (int, float)) and pct >= threshold


def pick(kind: str, found: dict[str, dict], threshold: float, unreachable: str | None) -> dict:
    """先決定模型,再確認那個模型用到的池沒有見底。"""
    model, reason = FLASH, "開發類任務用 Flash"
    if kind == "review":
        argon = found.get(ARGON_POOL)
        if unreachable:
            reason = f"審查類預設 Argon,但{unreachable},改用 Flash"
        elif usable(argon, threshold):
            model, reason = ARGON, f"審查類用 Argon({ARGON_POOL} 剩 {argon['remaining_pct']}%)"
        elif argon is None:
            reason = f"審查類預設 Argon,但 ai-quota 沒有 {ARGON_POOL},改用 Flash"
        elif argon["stale"]:
            reason = f"審查類預設 Argon,但 {ARGON_POOL} 是 stale,改用 Flash"
        else:
            reason = f"審查類預設 Argon,但 {ARGON_POOL} 剩 {argon['remaining_pct']}% 低於 {threshold:g}%,改用 Flash"
    exhausted = []
    if model == FLASH:
        exhausted = [p for p in FLASH_POOLS if found.get(p) and not found[p]["stale"] and found[p]["remaining_pct"] == 0]
    return {"kind": kind, "model": model, "reason": reason, "exhausted": exhausted, "pools": found}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="依任務性質(review/dev)與 ai-quota 剩餘額度,輸出這次 agy 調用要帶的 --model"
    )
    parser.add_argument("--kind", required=True, choices=["review", "dev"], help="review:審查、驗收、第二意見;dev:開發、重構、探索")
    parser.add_argument("--state-url", default=DEFAULT_URL, help=f"ai-quota 的 /api/state 網址(預設 {DEFAULT_URL})")
    parser.add_argument("--state-file", type=Path, help="改讀已存下的 /api/state JSON 檔(離線測試用),給了就不連 --state-url")
    parser.add_argument("--threshold", type=float, default=20.0, help=f"{ARGON_POOL} 剩餘百分比低於此值就不用 Argon(預設 20)")
    args = parser.parse_args()

    state, unreachable = load_state(args.state_url, args.state_file)
    if unreachable:
        print(unreachable, file=sys.stderr)
    result = pick(args.kind, pools(state), args.threshold, unreachable)
    print(json.dumps(result, ensure_ascii=False))
    if result["exhausted"]:
        print(f"Flash 用到的池 {', '.join(result['exhausted'])} 剩 0%,這次不調用 agy", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
