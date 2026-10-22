# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""確認任務指示檔列出的 shell 指令都在 agy 的允許清單(settings.json 的 permissions.allow)裡。

讀任務指示檔裡「Run only the shell commands listed below」那一行底下縮排的 `- ` 子項,每項一條指令
(整項包在一對 Markdown 行內程式碼的反引號裡時只去掉外層那一對,指令裡的反引號保留;只寫 `none` 表示沒有指令),逐條比對允許清單的 `command(…)` 規則;其他種類(read_file 等)不參與比對。
比對方式照 agy 1.4.5 的權限文件(https://www.agy.dev/docs/permissions/ 的 command 一列與
「When commands require an exact match」一節,2026-10-23 讀)與 agent-dispatch MR !30 的本機實驗:
- 規則以空白切成 token,對指令開頭的 token 做前綴比對:`command(x)` 逐 token 字面相等,
  `command(regex:…)` 每個 token 是錨定的 `^(?:pat)$`;`command(*)` 全部放行
- `;`、`&&`、`||`、`|`、`&` 拆開的每一段都要有規則;`timeout`、`nohup`、`nice`、`env` 去掉後比對裡面的指令;
  `>`、`>>`、`<`、`2>&1` 這類檔案重導向不參與比對
- 單引號外(含雙引號內)出現 `$(`、反引號、`<(`、`>(`、`{a,b}`、換行,出現 `|&`、`;;`、`<<` 等沒有逐段語意的符號,
  或 shlex 切不開時,整行原文要和規則完全相同
  (regex 規則則整條 regex 完全符合整行)
- regex 規則切成 token 後有不合法的(例如 `^(ls|cat)( |$)` 群組裡的空白把它切斷),前綴比對時視為不成立,
  列在輸出的 `broken_rules`;agy 遇到這種規則的行為文件沒寫,這裡依觀察推定為不放行
- 引號外出現 `#`、`(`、`)`(不論位置、有沒有跳脫)、`$'…'`(ANSI-C 引號)或 `$"…"`,或含空白、tab、換行以外的控制字元或非 ASCII 字元(例如 U+00A0)時,
  一律整行比對
已知限制(刻意 fail-closed,不再逐一補 shell 註解與跳脫的解析邊角):含引號外 `#` 的指令要以整行原文寫進允許清單,
`echo a #c`、`echo a;#c` 這類合法的註解寫法也會被擋;引號內的 `#`(`echo '#x'`)照常前綴比對。
不實作 `$'…'` 的 ANSI-C 跳脫語意,遇到 `$'`、`$"` 一律整行比對。
其他需要刻意構造的 shell 語法邊角(本腳本是 agy 實際比對的近似,不是 bash 解析器)不再逐一改碼,只記在這裡;
真正放行與否仍由 agy 自己的權限引擎決定,這支腳本只是事前檢查。
結果以 JSON 寫到 stdout。全部在清單裡 exit 0;有不在清單的 exit 1;檔案讀不到或格式不符 exit 2。
"""

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

ANCHOR = "Run only the shell commands listed below"
SUB_ITEM = re.compile(r"^\s+- (.*)$")
CODE_SPAN = re.compile(r"^(`+) ?(.*?) ?\1$")
RULE = re.compile(r"^command\((.*)\)$")
DEFAULT_SETTINGS = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
OPERATORS = {";", "&&", "||", "|", "&"}
WRAPPERS = {"timeout", "nohup", "nice", "env"}
REDIRECTS = {">", ">>", "<", ">&", "<&", "&>", "&>>", ">|"}
UNSAFE_CHAR = re.compile(r"[^\x20-\x7e\t\n]")
PUNCT = re.compile(r"[;&|<>]+")
BRACE = re.compile(r"\{[^{}\s]*,[^{}\s]*\}")


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
        command = match.group(1).strip()
        span = CODE_SPAN.match(command)
        if span:
            command = span.group(2).strip()  # 只去掉外層的行內程式碼標記,裡面的反引號是命令替換,要留給比對判斷
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


def expandable_text(command: str) -> str:
    """回傳 shell 會展開的部分:單引號外的字元(雙引號內仍會展開);反斜線跳脫的字元是字面,不算。"""
    out, state, i = [], None, 0
    while i < len(command):
        ch = command[i]
        if state == "'":
            if ch == "'":
                state = None
        elif ch == "\\":
            i += 1  # 跳脫:下一個字元是字面(雙引號內的 \$、\` 也一樣)
        elif state == '"':
            if ch == '"':
                state = None
            else:
                out.append(ch)  # 雙引號內的單引號只是字元,$( 與反引號照樣展開
        elif ch in "'\"":
            state = ch
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def unquoted_text(command: str) -> str:
    """回傳所有引號外的字元,連反斜線跳脫的與開頭的引號字元也算(用來判斷 #、(、)、$'、$" 有沒有出現在引號外)。"""
    out, state, i = [], None, 0
    while i < len(command):
        ch = command[i]
        if state == "'":
            if ch == "'":
                state = None
        elif state == '"':
            if ch == "\\":
                i += 1
            elif ch == '"':
                state = None
        elif ch == "\\":
            out.append(command[i:i + 2])
            i += 1
        elif ch in "'\"":
            out.append(ch)  # 留下開頭引號,`$'…'`、`$"…"` 才看得出來
            state = ch
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def needs_exact_match(command: str) -> bool:
    """以下任一種就停用前綴比對、改整行比對(fail-closed,見檔頭的已知限制):
    會展開的部分有命令替換、反引號、程序替換、大括號展開或換行;引號外出現 #、( 或 )(子 shell、函式等)、$'…' 或 $"…";含空白、tab、換行以外的控制字元或非 ASCII 字元。"""
    outside = unquoted_text(command)
    if UNSAFE_CHAR.search(command) or any(ch in outside for ch in "#()") or "$'" in outside or '$"' in outside:
        return True
    text = expandable_text(command)
    return any(mark in text for mark in ("$(", "`", "<(", ">(", "\n", "\r")) or bool(BRACE.search(text))


def segments(command: str) -> list[list[str]] | None:
    """以 shlex 切 token、依串接符號分段;切不開時回 None。"""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|<>")
    lexer.whitespace_split = True
    lexer.whitespace = " \t\n"  # 分隔符只認空白、tab、換行與 ;&|<>;引號外的 ( ) 在 needs_exact_match 已改整行比對
    lexer.commenters = ""  # 含 # 的指令在 needs_exact_match 就改整行比對了,這裡不必也不該再判註解
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    result, current = [], []
    for token in tokens:
        if PUNCT.fullmatch(token) and token not in OPERATORS | REDIRECTS:
            return None  # `|&`、`;;`、`<<`、`<<<` 等沒有逐段語意的符號:切不清楚就改整行比對
        if token in OPERATORS:
            result.append(current)
            current = []
        else:
            current.append(token)
    result.append(current)
    cleaned = [drop_redirects(seg) for seg in result]
    if any(seg is None for seg in cleaned):
        return None
    return [strip_wrappers(seg) for seg in cleaned]


def drop_redirects(tokens: list[str]) -> list[str] | None:
    """去掉檔案重導向的運算子、它前面的 fd 數字與後面的目標;導向網路(/dev/tcp、/dev/udp)時回 None。"""
    kept, skip = [], False
    for token in tokens:
        if skip:
            skip = False
            if token.startswith(("/dev/tcp/", "/dev/udp/")):
                return None
            continue
        if token in REDIRECTS:
            if kept and kept[-1].isdigit():
                kept.pop()  # shlex 把 `2>` 切成 `2`、`>`;純數字視為 fd(依觀察推定)
            skip = True
            continue
        kept.append(token)
    return kept


def strip_wrappers(tokens: list[str]) -> list[str]:
    """去掉開頭的 timeout、nohup、nice、env 與它們的選項,留下真正執行的指令。"""
    while tokens and tokens[0] in WRAPPERS:
        name, tokens = tokens[0], tokens[1:]
        while tokens and (tokens[0].startswith("-") or (name == "env" and "=" in tokens[0])):
            option, tokens = tokens[0], tokens[1:]
            if name in {"nice", "timeout"} and option in {"-n", "-s", "-k", "--signal", "--kill-after"} and tokens:
                tokens = tokens[1:]
        if name == "timeout" and tokens:
            tokens = tokens[1:]  # 時限本身
    return tokens


def compiles(pattern: str) -> bool:
    """pattern 是不是合法的正規表示式。"""
    try:
        re.compile(pattern)
    except re.error:
        return False
    return True


def broken_rules(rules: list[str]) -> list[str]:
    """regex 規則切成 token 後有任何一個不是合法 regex 的(例如群組裡有空白),前綴比對時永遠不成立。"""
    broken = []
    for rule in rules:
        match = RULE.match(rule)
        if match and match.group(1).startswith("regex:"):
            if not all(compiles(p) for p in match.group(1)[len("regex:"):].split()):
                broken.append(rule)
    return broken


def rule_matches_segment(target: str, tokens: list[str]) -> bool:
    """規則以空白切 token,逐一對指令開頭的 token 做比對(regex: 為錨定 regex,否則字面相等)。"""
    if target.startswith("regex:"):
        patterns = target[len("regex:"):].split()
        if not all(compiles(p) for p in patterns):
            return False
        return len(tokens) >= len(patterns) and all(re.fullmatch(p, t) for p, t in zip(patterns, tokens))
    words = target.split()
    return len(tokens) >= len(words) and tokens[:len(words)] == words


def rule_matches_line(target: str, command: str) -> bool:
    """需要完全比對時:字面規則與整行原文相同,regex 規則完全符合整行。"""
    if target.startswith("regex:"):
        pattern = target[len("regex:"):]
        return compiles(pattern) and re.fullmatch(pattern, command) is not None
    return command == target


def is_allowed(command: str, rules: list[str]) -> bool:
    """指令依 agy 的 command 規則語意被允許清單放行(說明見檔頭)。"""
    targets = [m.group(1) for m in (RULE.match(rule) for rule in rules) if m]
    if "*" in targets:
        return True
    parts = None if needs_exact_match(command) else segments(command)
    if parts is None:
        return any(rule_matches_line(t, command) for t in targets)
    return all(seg and any(rule_matches_segment(t, seg) for t in targets) for seg in parts)


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
    if any("#" in unquoted_text(c) for c in denied):
        print("被擋的指令裡有引號外的 #:這類指令一律整行比對,要放行就把整行原文寫進允許清單,或把 # 放進引號", file=sys.stderr)
    broken = broken_rules(rules)
    if broken:
        print(f"允許清單有 {len(broken)} 條 regex 規則切成 token 後不是合法 regex(群組裡有空白?),agy 前綴比對時不會放行", file=sys.stderr)
    print(json.dumps({"allowed": allowed, "denied": denied, "broken_rules": broken, "settings": str(args.settings)}, ensure_ascii=False))
    sys.exit(1 if denied else 0)


if __name__ == "__main__":
    main()
