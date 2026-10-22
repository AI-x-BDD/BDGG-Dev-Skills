# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""確認任務指示檔列出的 shell 指令都在 agy 的允許清單(settings.json 的 permissions.allow)裡。

讀任務指示檔裡「Run only the shell commands listed below」那一行底下縮排的 `- ` 子項,每項一條指令
(去掉反引號;只寫 `none` 表示沒有指令),逐條比對允許清單:`command(x)` 是指令等於 x 或以 `x ` 開頭,
`command(regex:…)` 是 `re.match` 成立;其他種類(read_file 等)不參與比對。
結果以 JSON 寫到 stdout。全部在清單裡 exit 0;有不在清單的 exit 1;檔案讀不到或格式不符 exit 2。
"""

import argparse
import json
import re
import sys
from pathlib import Path

ANCHOR = "Run only the shell commands listed below"
SUB_ITEM = re.compile(r"^\s+- (.*)$")
RULE = re.compile(r"^command\((.*)\)$")
DEFAULT_SETTINGS = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"


def fail(message: str) -> None:
    """把錯誤寫到 stderr,以 exit code 2 結束。"""
    print(message, file=sys.stderr)
    sys.exit(2)


def listed_commands(prompt_path: Path) -> list[str]:
    """取出任務指示檔在 ANCHOR 那一行底下列的指令。"""
    try:
        lines = prompt_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        fail(f"讀不到任務指示檔 {prompt_path}:{exc.strerror};--prompt 要給 Phase 1 Step 2 寫出的指示檔路徑")
    starts = [i for i, line in enumerate(lines) if ANCHOR in line]
    if len(starts) != 1:
        fail(
            f"任務指示檔 {prompt_path} 裡「{ANCHOR}」出現 {len(starts)} 次,預期剛好 1 次;"
            "指示檔要照 templates/task-prompt.md 的 Constraints 寫"
        )
    commands = []
    for line in lines[starts[0] + 1:]:
        match = SUB_ITEM.match(line)
        if not match:
            break
        command = match.group(1).replace("`", "").strip()
        if command:
            commands.append(command)
    if not commands:
        fail(
            f"任務指示檔 {prompt_path} 在「{ANCHOR}」底下沒有縮排的 `- ` 子項;"
            "每條指令寫成一個子項,沒有指令就寫一個 `- none`"
        )
    if [c.lower() for c in commands] == ["none"]:
        return []
    return commands


def allow_rules(settings_path: Path) -> list[str]:
    """讀出 settings.json 的 permissions.allow。"""
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except OSError as exc:
        fail(f"讀不到 agy 設定檔 {settings_path}:{exc.strerror};--settings 要給 agy 的 settings.json 路徑")
    except json.JSONDecodeError as exc:
        fail(f"agy 設定檔 {settings_path} 不是合法的 JSON:第 {exc.lineno} 行 {exc.msg}")
    allow = data.get("permissions", {}).get("allow") if isinstance(data, dict) else None
    if not isinstance(allow, list) or not all(isinstance(rule, str) for rule in allow):
        fail(f"agy 設定檔 {settings_path} 沒有字串陣列形式的 permissions.allow;預期像 [\"command(git)\", …]")
    return allow


def is_allowed(command: str, rules: list[str]) -> bool:
    """指令符合任何一條 command(…) 規則就算允許。"""
    for rule in rules:
        match = RULE.match(rule)
        if not match:
            continue
        target = match.group(1)
        if target.startswith("regex:"):
            try:
                if re.match(target[len("regex:"):], command):
                    return True
            except re.error as exc:
                fail(f"允許清單的規則 {rule} 不是合法的正規表示式:{exc}")
        elif command == target or command.startswith(target + " "):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="確認任務指示檔「Run only the shell commands listed below」底下列的指令都在 agy 的 permissions.allow 裡"
    )
    parser.add_argument("--prompt", required=True, type=Path, help="Phase 1 Step 2 寫出的任務指示檔路徑")
    parser.add_argument(
        "--settings",
        type=Path,
        default=DEFAULT_SETTINGS,
        help=f"agy 的 settings.json 路徑(預設 {DEFAULT_SETTINGS})",
    )
    args = parser.parse_args()

    commands = listed_commands(args.prompt)
    rules = allow_rules(args.settings)
    allowed = [c for c in commands if is_allowed(c, rules)]
    denied = [c for c in commands if c not in allowed]
    print(json.dumps({"allowed": allowed, "denied": denied, "settings": str(args.settings)}, ensure_ascii=False))
    sys.exit(1 if denied else 0)


if __name__ == "__main__":
    main()
