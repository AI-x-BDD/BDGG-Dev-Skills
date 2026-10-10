# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查 SKILL.md 的 # SOP 格式,並由 # SOP 產生 Mermaid 流程視覺圖(flowchart TD,有轉交別支 Skill 時加 sequenceDiagram),放在 SKILL.md 的檔尾。

格式檢查判 SOP-格式規範.md 與 SOP-按需載入-格式規範.md 裡結果只由 SOP 文字決定的 8 條 Rule。
步驟裡用 ** 標出的核心動作就是圖上的標籤;每一步剛好標一段,沒有標的步驟判〈粗體照固定寫法〉不過。
--write 與 --check 把檢查結果以 JSON 寫到 stdout;有任何一條不過時 exit code 是 1,而且不產圖、不寫檔。
"""

import argparse
import json
import re
import string
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Guard:
    condition: str
    target_type: str  # 'jump' or 'exit'
    target_phase: int | None = None
    target_step: int | None = None


@dataclass
class Step:
    phase_num: int
    step_num: int
    verb: str
    action_text: str
    guards: list[Guard] = field(default_factory=list)
    raw_line: str = ""
    line: int = 0
    core: str = ""  # 用 ** 標出的核心動作;〈粗體照固定寫法〉不過時是空字串

    @property
    def plain_text(self) -> str:
        """拿掉 ** 記號的動作描述。"""
        return self.action_text.replace("**", "")

    @property
    def node_id(self) -> str:
        return f"P{self.phase_num}S{self.step_num}"

    @property
    def position(self) -> str:
        return f"Phase {self.phase_num} Step {self.step_num}"

    @property
    def is_external_delegation(self) -> bool:
        return self.verb == "Delegate" and "轉交" in self.action_text

    @property
    def is_user_interaction(self) -> bool:
        return self.verb == "Ask"


@dataclass
class Phase:
    num: int
    title: str
    steps: list[Step] = field(default_factory=list)
    line: int = 0


@dataclass
class Violation:
    rule: str
    line: int
    text: str
    reason: str


def clean_label(text: str, max_len: int = 50) -> str:
    """清理並轉義 Mermaid 節點標籤文字。"""
    # 移除反引號與多餘空白
    text = text.replace("`", "").strip()
    # 移除結尾句號或分號
    text = re.sub(r"[;。]+$", "", text)
    # 轉義 Mermaid 保留字元
    text = text.replace('"', "#quot;").replace("[", "&#91;").replace("]", "&#93;")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("{", "&#123;").replace("}", "&#125;")
    if len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return text


LABEL_ESCAPES = {'"': "#quot;", "[": "&#91;", "]": "&#93;", "<": "&lt;", ">": "&gt;", "{": "&#123;", "}": "&#125;"}
WRAP_TOKEN = re.compile(r"[A-Za-z0-9_./\-]+|.")
NO_LINE_START = ",、。:;?!)」』》,:;?!)"


def display_width(text: str) -> int:
    """全形字算 2、半形字算 1。"""
    return sum(2 if ord(char) > 0x2E7F else 1 for char in text)


def wrap_label(text: str, width: int) -> str:
    """流程圖節點的標籤:整句都留著,依顯示寬度折成多行。

    英數字連成的詞(Skill 名稱、路徑、指令)不從中間斷開,標點不放在行首。
    """
    text = text.replace("`", "").strip()
    text = re.sub(r"[;。]+$", "", text)
    tokens = WRAP_TOKEN.findall(text)

    def fold(limit: int) -> list[str]:
        folded: list[str] = []
        current = ""
        for token in tokens:
            if current.strip() and token not in NO_LINE_START and display_width(current) + display_width(token) > limit:
                folded.append(current.strip())
                current = ""
            current += token
        if current.strip():
            folded.append(current.strip())
        return folded

    # 行數由 width 決定,再把每行的寬度收到剛好排得下,最後一行才不會只剩一兩個字
    lines = fold(width)
    for limit in range(-(-display_width(text) // max(len(lines), 1)), width):
        balanced = fold(limit)
        if len(balanced) <= len(lines):
            lines = balanced
            break
    return "<br/>".join("".join(LABEL_ESCAPES.get(char, char) for char in line) for line in lines)


def step_label(step: Step) -> str:
    """圖上顯示的那一步:動詞加上用 ** 標出的核心動作。"""
    return f"{step.step_num}. {step.verb}：{step.core}"


def simplify_condition_label(condition: str, width: int = 24) -> str:
    """精煉條件分支文字，提煉核心提問;整句都留著,依寬度折行。"""
    cond = condition.strip().replace("`", "")
    cond = re.sub(r"[;。？?]+$", "", cond)
    mappings = [
        (r"沒有步驟用得到.*", "無使用資源"),
        (r"對話裡有那一?次交給.*", "已有輸入與產出"),
        (r"要創建的是全新的.*", "創建全新 Skill"),
        (r"使用者同意.*每一個落差都不歸類", "落差皆不歸類"),
        (r"驗收紀錄裡有一列判定為對不上", "驗收對不上"),
        (r"寫出來的內容和藍圖不同", "內容與藍圖不同"),
        (r"掛上去的內容和藍圖不同", "內容與藍圖不同"),
        (r"指定那一步的寫法不變", "步驟寫法不變"),
        (r"結果不符預期且需要.*修正", "驗收不符預期"),
        (r".*未安裝或環境不支援", "未安裝或不支援"),
    ]
    for pattern, replacement in mappings:
        if re.search(pattern, cond):
            return wrap_label(replacement + "？", width)
    return wrap_label(cond + "？", width)


SEQUENCE_ESCAPES = {"#": "#35;", ";": "#59;", "<": "#lt;", ">": "#gt;", '"': "#quot;"}


def sequence_label(text: str) -> str:
    """時序圖的訊息不截字。

    訊息裡的 # 與 ; 會讓 Mermaid 把後面的字整段丟掉,所以連同 < > " 一起轉成實體。
    """
    text = re.sub(r"[;。]+$", "", text.replace("`", "").strip())
    return re.sub(r'[#;<>"]', lambda m: SEQUENCE_ESCAPES[m.group()], text)


HANDOFF = re.compile(r"轉交\s*([^,;。]+)")


def handoff_candidates(action: str) -> tuple[re.Match | None, list[str]]:
    """找出「轉交 A、B 或 C」裡的每一個對象;排除「對應 Derivers」這類通用說明詞。"""
    match = HANDOFF.search(action)
    if not match:
        return None, []
    names: list[str] = []
    for part in re.split(r"、|或|,", match.group(1)):
        name = part.strip()
        if name and name not in names and not name.startswith("對應"):
            names.append(name)
    return match, names


STEP_LABEL_WIDTH = 36  # 流程圖步驟節點一行的顯示寬度(約 18 個中文字)

VERBS = ("Read", "Write", "Think", "Ask", "Delegate")

R_SKELETON = "SOP 照固定骨架寫"
R_VERB = "步驟以動詞表的動詞開頭"
R_ONE_LINE = "一步只有一行"
R_BRANCH = "分支與回頭只寫在行尾"
R_ONCE = "資源只在用到它的那一步點名"
R_POINTER = "指標接在動詞後面並照固定寫法"
R_SCRIPT = "委派給腳本的步驟照固定寫法"
R_BOLD = "粗體照固定寫法"

# (Rule 名稱, 所在的規範檔);8 條的強度都是 must
RULES = [
    (R_SKELETON, "SOP-格式規範.md"),
    (R_VERB, "SOP-格式規範.md"),
    (R_ONE_LINE, "SOP-格式規範.md"),
    (R_BRANCH, "SOP-格式規範.md"),
    (R_BOLD, "SOP-格式規範.md"),
    (R_ONCE, "SOP-按需載入-格式規範.md"),
    (R_POINTER, "SOP-按需載入-格式規範.md"),
    (R_SCRIPT, "SOP-按需載入-格式規範.md"),
]

SOP_TITLE = re.compile(r"^# SOP[ \t]*$")
TOP_HEADING = re.compile(r"^# \S")
PHASE_TITLE = re.compile(r"^## Phase (\d+): (\S.*)$")
STEP_LINE = re.compile(r"^(\d+)\.\s+(\S+)\s*(.*)$")
NESTED_LINE = re.compile(r"^(\s+\S|[-*+]\s)")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
GUARD = re.compile(r"^(\S.*?)\s*→\s*(?:跳至\s*Phase\s*(\d+)\s*Step\s*(\d+)|結束)$")
RESOURCE = re.compile(r"`((?:rules|templates)/[^`\s]+)`")
SCRIPT_REF = re.compile(r"scripts/[\w.\-]+\.py")
NEGATIVE = re.compile(r"^(沒有|無|不|未)")
BOLD = re.compile(r"\*\*(.+?)\*\*")
BOLD_MAX_WIDTH = 36  # 粗體的顯示寬度上限(18 個中文字)
DIAGRAM_BLOCK = re.compile(
    r"<details[^>]*>\s*<summary>.*?流程視覺圖.*?</summary>.*?</details>",
    re.DOTALL,
)

_RULE_POINTER = r"依\s*`rules/[^`\s*]+`"
_TEMPLATE_POINTER = (
    r"骨架\s*`templates/([^`\s*]+?)\.([^`\s*./]+)`\s*與範例\s*`templates/\1\.example\.\2`"
)
POINTER_FORMS = [
    re.compile(rf"^{_RULE_POINTER}、{_TEMPLATE_POINTER}"),
    re.compile(rf"^依{_TEMPLATE_POINTER}"),
    re.compile(rf"^{_RULE_POINTER}"),
]
SCRIPT_STEP = re.compile(
    r"^(依\s*`rules/腳本執行-規範\.md`\s*)?執行\s*`uv run scripts/[\w.\-]+\.py[^`]*`"
)


def is_punctuation(char: str) -> bool:
    """Markdown 判斷粗體有沒有效時當成標點的字:ASCII 標點,以及 Unicode 的標點與符號。"""
    return char in string.punctuation or unicodedata.category(char)[0] in "PS"


def check_bold(step: Step, conditions: list[str], bad) -> None:
    """判〈粗體照固定寫法〉,並把合格的那一段記到 step.core。"""
    where = step.position
    if any("**" in condition for condition in conditions):
        bad(R_BOLD, step.line, f"{where} 的行尾條件裡有 `**`;粗體只標動作描述裡的核心動作,條件裡的要拿掉")
    spans = list(BOLD.finditer(step.action_text))
    if "**" in BOLD.sub("", step.action_text):
        bad(R_BOLD, step.line, f"{where} 的 `**` 沒有成對;粗體要寫成 `**<核心動作>**`")
        return
    if len(spans) > 1:
        bad(R_BOLD, step.line, f"{where} 標了 {len(spans)} 段粗體;一步只標一段,留下最能說明這一步在做什麼的那一段")
        return
    if not spans:
        bad(R_BOLD, step.line, f"{where} 沒有標粗體;把這一步的核心動作寫成連續的一段並用 `**` 包起來,一長串並列時先寫一個總稱標成粗體、冒號後面列細項")
        return
    span = spans[0]
    core = span.group(1)
    shown = core.replace("`", "")
    problems = []
    if core != core.strip() or not shown.strip():
        problems.append("粗體的開頭或結尾是空白,Markdown 不會把它當成粗體;把空白移到 `**` 外面")
    if display_width(shown) > BOLD_MAX_WIDTH:
        problems.append(f"粗體「{shown}」寬 {display_width(shown)} 個半形字,超過 {BOLD_MAX_WIDTH};改標短一點的一段")
    if RESOURCE.search(core) or SCRIPT_REF.search(core) or "uv run" in core:
        problems.append("粗體裡有資源路徑或指令;指標與指令放在 `**` 外面")
    before = step.action_text[: span.start()][-1:]
    after = step.action_text[span.end() :][:1]
    if shown.strip() and is_punctuation(core.strip()[0]) and before and not (before.isspace() or is_punctuation(before)):
        problems.append(f"粗體以「{core.strip()[0]}」開頭而前面緊接「{before}」,Markdown 不會把它當成粗體;在 `**` 前面加一個空白,或把「{core.strip()[0]}」移到粗體外面")
    if shown.strip() and is_punctuation(core.strip()[-1]) and after and not (after.isspace() or is_punctuation(after)):
        problems.append(f"粗體以「{core.strip()[-1]}」結尾而後面緊接「{after}」,Markdown 不會把它當成粗體;在 `**` 後面加一個空白,或把「{core.strip()[-1]}」移到粗體外面")
    for problem in problems:
        bad(R_BOLD, step.line, f"{where} 的{problem}")
    if not problems:
        step.core = shown.strip()


def skill_name_of(content: str) -> str:
    name_match = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", content, re.MULTILINE)
    return name_match.group(1).strip() if name_match else "Skill"


def parse_and_check(content: str) -> tuple[list[Phase], list[Violation], list[dict]]:
    """逐行解析 # SOP 並判 8 條 Rule。

    回傳 (phases, violations, candidates);violations 是空的時候 phases 才能拿去產圖。
    """
    lines = content.splitlines()
    violations: list[Violation] = []
    candidates: list[dict] = []
    phases: list[Phase] = []

    def bad(rule: str, number: int, reason: str) -> None:
        text = lines[number - 1].strip() if 0 < number <= len(lines) else ""
        violations.append(Violation(rule=rule, line=number, text=text, reason=reason))

    # 1. 找到 code fence 以外的 # SOP
    sop_line = 0
    fence = ""
    for number, line in enumerate(lines, start=1):
        marker = FENCE.match(line)
        if marker:
            if not fence:
                fence = marker.group(1)
            elif marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = ""
            continue
        if not fence and SOP_TITLE.match(line):
            sop_line = number
            break
    if not sop_line:
        violations.append(
            Violation(rule=R_SKELETON, line=0, text="", reason="找不到 `# SOP` 標題(獨立一行,前面沒有空白)")
        )
        return phases, violations, candidates

    # 2. 逐行分類 # SOP 底下的內容
    current: Phase | None = None
    fence = ""
    in_details = False
    for number in range(sop_line + 1, len(lines) + 1):
        line = lines[number - 1]
        if in_details:
            if "</details>" in line:
                in_details = False
            continue
        marker = FENCE.match(line)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = ""
            continue
        if marker:
            fence = marker.group(1)
            bad(R_SKELETON, number, "`# SOP` 底下只能有流程視覺圖、`## Phase N: <標題>` 與編號步驟,不能有 code block")
            continue
        if not line.strip():
            continue
        if line.startswith("<details"):
            block = "\n".join(lines[number - 1 :])
            end = block.find("</details>")
            if "流程視覺圖" not in (block[:end] if end >= 0 else block):
                bad(R_SKELETON, number, "`# SOP` 底下的 `<details>` 只能是腳本產生的流程視覺圖")
            in_details = "</details>" not in line
            continue
        if TOP_HEADING.match(line):
            break
        phase_match = PHASE_TITLE.match(line)
        if phase_match:
            expected = len(phases) + 1
            if int(phase_match.group(1)) != expected:
                bad(R_SKELETON, number, f"Phase 編號要從 1 連續編,這裡應該是 Phase {expected}")
            current = Phase(num=expected, title=phase_match.group(2).strip(), line=number)
            phases.append(current)
            continue
        if line.startswith("#"):
            bad(R_SKELETON, number, "`# SOP` 底下的標題只能寫成 `## Phase N: <標題>`")
            continue
        step_match = STEP_LINE.match(line)
        if step_match:
            if current is None:
                bad(R_SKELETON, number, "編號步驟前面沒有 `## Phase N: <標題>`")
                continue
            expected = len(current.steps) + 1
            if int(step_match.group(1)) != expected:
                bad(R_SKELETON, number, f"步驟編號要在每個 Phase 裡從 1 連續編,這裡應該是 {expected}")
            verb = step_match.group(2)
            rest = step_match.group(3).strip()
            if verb not in VERBS:
                shown = verb if len(verb) <= 8 else verb[:8] + "…"
                bad(R_VERB, number, f"Phase {current.num} Step {expected} 開頭是「{shown}」,不在動詞表(Read、Write、Think、Ask、Delegate)")
                rest = f"{verb} {rest}".strip()
            current.steps.append(
                Step(phase_num=current.num, step_num=expected, verb=verb, action_text=rest, raw_line=line.strip(), line=number)
            )
            continue
        if NESTED_LINE.match(line) and current is not None and current.steps:
            last = current.steps[-1]
            bad(R_ONE_LINE, number, f"{last.position} 底下掛了細節;細節放到 `rules/` 或 `templates/`,步驟裡只留指過去的名稱")
            continue
        bad(R_SKELETON, number, "這一行不是 `## Phase N: <標題>` 也不是 `<編號>. <動詞> <動作描述>`")

    if not phases:
        bad(R_SKELETON, sop_line, "`# SOP` 底下沒有任何 `## Phase N: <標題>`")
    for phase in phases:
        if not phase.steps:
            bad(R_SKELETON, phase.line, f"Phase {phase.num} 底下沒有編號步驟")

    steps = [step for phase in phases for step in phase.steps]
    positions = {(step.phase_num, step.step_num) for step in steps}

    # 3. 行尾的分支與回頭
    for step in steps:
        body = step.action_text
        if "；若" in body:
            bad(R_BRANCH, step.line, f"{step.position} 的「；若」用了全形分號,要寫成半形的 `;若`")
        parts = body.split(";若")
        step.action_text = parts[0].strip()
        check_bold(step, parts[1:], bad)
        if "→" in step.action_text:
            bad(R_BRANCH, step.line, f"{step.position} 的「→」前面沒有 `;若 <條件>`;要寫成 `;若 <條件> → 跳至 Phase N Step M。` 或 `;若 <條件> → 結束。`")
        for index, part in enumerate(parts[1:], start=1):
            text = part.strip()
            if index == len(parts) - 1:
                text = re.sub(r"[。.]$", "", text).strip()
            guard_match = GUARD.match(text)
            if not guard_match:
                bad(R_BRANCH, step.line, f"{step.position} 的第 {index} 個分支「;若{part.strip()}」不是固定寫法;要寫成 `;若 <條件> → 跳至 Phase N Step M。` 或 `;若 <條件> → 結束。`")
                continue
            condition = guard_match.group(1).strip()
            if guard_match.group(2):
                target = (int(guard_match.group(2)), int(guard_match.group(3)))
                if target not in positions:
                    bad(R_BRANCH, step.line, f"{step.position} 要跳至的 Phase {target[0]} Step {target[1]} 不存在")
                step.guards.append(Guard(condition=condition, target_type="jump", target_phase=target[0], target_step=target[1]))
            else:
                step.guards.append(Guard(condition=condition, target_type="exit"))
            if NEGATIVE.match(condition):
                candidates.append(
                    {
                        "rule": R_BRANCH,
                        "line": step.line,
                        "text": step.raw_line,
                        "reason": f"{step.position} 的條件「{condition}」以否定詞開頭;請判斷它是不是替天然冪等的下一步設的防禦性跳轉",
                    }
                )

    # 4. 資源的指標
    first_seen: dict[str, Step] = {}
    for step in steps:
        # 只算動作描述裡的路徑;行尾條件裡提到的是在講別的檔在不在,不是這支 skill 的指標
        for path in RESOURCE.findall(step.action_text):
            if path not in first_seen:
                first_seen[path] = step
            elif first_seen[path] is step:
                bad(R_ONCE, step.line, f"{step.position} 把 `{path}` 寫了兩次;每個資源路徑在 SOP 裡只出現一次")
            else:
                bad(R_ONCE, step.line, f"`{path}` 在 {first_seen[path].position} 已經點名,{step.position} 不再寫它的路徑")
        in_action = RESOURCE.findall(step.action_text)
        if in_action:
            form = next((m for m in (p.match(step.action_text) for p in POINTER_FORMS) if m), None)
            if form is None:
                bad(R_POINTER, step.line, f"{step.position} 的指標沒有緊接在動詞後面或不是固定寫法;要寫成 `<動詞> 依 `rules/<檔名>` …`、`<動詞> 依骨架 `templates/<名字>.<格式>` 與範例 `templates/<名字>.example.<格式>` …`,或兩者用「、」接起來")
            elif RESOURCE.findall(step.action_text[form.end() :]):
                bad(R_POINTER, step.line, f"{step.position} 在動作描述裡又寫了資源路徑;每個路徑都要放在緊接動詞的指標裡")

    # 5. 委派給腳本的步驟
    script_steps = [step for step in steps if SCRIPT_REF.search(step.raw_line)]
    for index, step in enumerate(script_steps):
        script_match = SCRIPT_STEP.match(step.action_text) if step.verb == "Delegate" else None
        if script_match is None:
            bad(R_SCRIPT, step.line, f"{step.position} 提到了 `scripts/` 底下的腳本但不是固定寫法;要寫成 `Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/<腳本名>.py <參數>` <取得什麼或留下什麼>`")
        elif index == 0 and not script_match.group(1):
            bad(R_SCRIPT, step.line, f"{step.position} 是第一個執行腳本的步驟,要寫「依 `rules/腳本執行-規範.md`」")

    return phases, violations, candidates


def _ranges(numbers: list[int]) -> str:
    return f"{numbers[0]}–{numbers[-1]}" if len(numbers) > 1 else str(numbers[0])


def build_checks(phases: list[Phase], violations: list[Violation]) -> list[dict]:
    """把違規整理成每條 Rule 一列;過的列也寫出看了哪裡、看到什麼。"""
    steps = [step for phase in phases for step in phase.steps]
    guarded = [step for step in steps if step.guards]
    resources = list(dict.fromkeys(path for step in steps for path in RESOURCE.findall(step.action_text)))
    pointed = [step for step in steps if RESOURCE.findall(step.action_text)]
    scripted = [step for step in steps if SCRIPT_REF.search(step.raw_line)]

    passed_evidence = {
        R_SKELETON: f"`# SOP` 底下是 Phase {_ranges([p.num for p in phases])},共 {len(steps)} 個編號步驟" if phases else "",
        R_VERB: ";".join(
            f"Phase {p.num} Step {_ranges([s.step_num for s in p.steps])} 是 {'、'.join(s.verb for s in p.steps)}"
            for p in phases
            if p.steps
        ),
        R_ONE_LINE: f"{len(steps)} 步都是一行,底下沒有掛細節",
        R_BRANCH: (
            f"{'、'.join(s.position for s in guarded)} 的分支都寫在行尾,要跳至的步驟都存在"
            if guarded
            else "沒有分支與回頭"
        ),
        R_BOLD: f"{len(steps)} 步各標了一段粗體,都在動作描述裡、不超過 {BOLD_MAX_WIDTH} 個半形字寬",
        R_ONCE: f"{len(resources)} 個資源路徑各出現一次" if resources else "沒有寫資源的指標",
        R_POINTER: (
            f"{'、'.join(s.position for s in pointed)} 的指標都緊接在動詞後面"
            if pointed
            else "沒有寫資源的指標"
        ),
        R_SCRIPT: (
            f"{'、'.join(s.position for s in scripted)} 寫成「Delegate … 執行 `uv run scripts/<腳本名>.py …`」"
            if scripted
            else "沒有委派給腳本的步驟"
        ),
    }

    checks = []
    for rule, source in RULES:
        mine = [v for v in violations if v.rule == rule]
        checks.append(
            {
                "rule": rule,
                "source": source,
                "strength": "must",
                "result": "不過" if mine else "過",
                "evidence": ";".join(v.reason for v in mine) if mine else passed_evidence[rule],
                "violations": [{"line": v.line, "text": v.text, "reason": v.reason} for v in mine],
            }
        )
    return checks


def inject(content: str, diagram_block: str) -> str:
    """回傳把流程視覺圖放到檔尾之後的整份內容;原本在別處的圖會先拿掉,重複執行結果不變。"""
    match = re.search(r"^# SOP[ \t]*$", content, re.MULTILINE)
    if not match:
        return content
    before = content[: match.end()]
    after = DIAGRAM_BLOCK.sub("", content[match.end() :], count=1).strip()
    return f"{before}\n\n{after}\n\n{diagram_block}"


def generate_flowchart(phases: list[Phase]) -> str:
    """生成 Mermaid flowchart TD。"""
    lines = ["```mermaid", "flowchart TD"]

    # 建立步驟查找表以判斷 fallthrough
    all_steps: list[Step] = []
    step_map: dict[tuple[int, int], Step] = {}
    for p in phases:
        for s in p.steps:
            all_steps.append(s)
            step_map[(s.phase_num, s.step_num)] = s

    for p in phases:
        lines.append(f'    subgraph P{p.num}["Phase {p.num}: {clean_label(p.title)}"]')
        for s in p.steps:
            action_display = wrap_label(step_label(s), STEP_LABEL_WIDTH)
            lines.append(f'        {s.node_id}["{action_display}"]')
            for g_idx, g in enumerate(s.guards, start=1):
                cond_display = simplify_condition_label(g.condition)
                g_id = f"G_{s.node_id}_{g_idx}"
                lines.append(f'        {g_id}{{"{cond_display}"}}')
        lines.append("    end")

    lines.append('    End["結束"]')

    # 繪製邊 (Edges)
    for idx, s in enumerate(all_steps):
        next_default_id: str
        if idx + 1 < len(all_steps):
            next_default_id = all_steps[idx + 1].node_id
        else:
            next_default_id = "End"

        if not s.guards:
            lines.append(f"    {s.node_id} --> {next_default_id}")
        else:
            lines.append(f"    {s.node_id} --> G_{s.node_id}_1")
            for g_idx, g in enumerate(s.guards, start=1):
                curr_g_id = f"G_{s.node_id}_{g_idx}"
                # True 分支
                if g.target_type == "exit":
                    lines.append(f"    {curr_g_id} -->|是| End")
                elif g.target_type == "jump" and g.target_phase and g.target_step:
                    target_id = f"P{g.target_phase}S{g.target_step}"
                    lines.append(f"    {curr_g_id} -->|是| {target_id}")

                # False 分支
                if g_idx < len(s.guards):
                    next_g_id = f"G_{s.node_id}_{g_idx + 1}"
                    lines.append(f"    {curr_g_id} -->|否| {next_g_id}")
                else:
                    lines.append(f"    {curr_g_id} -->|否| {next_default_id}")

    lines.append("```")
    return "\n".join(lines)


def generate_sequence(skill_name: str, phases: list[Phase]) -> str | None:
    """若存在外部 Skill 委派，生成 Mermaid sequenceDiagram；否則回傳 None。"""
    external_delegations: list[Step] = []
    has_user_interaction = False

    for p in phases:
        for s in p.steps:
            if s.is_external_delegation:
                external_delegations.append(s)
            if s.is_user_interaction:
                has_user_interaction = True

    if not external_delegations:
        return None

    # 解析所有被委派的對象
    # 規則：只在 Delegate 步驟的轉交語法中解析 Skill 目標
    sub_skills: list[str] = []
    for s in external_delegations:
        for name in handoff_candidates(s.plain_text)[1]:
            if name not in sub_skills:
                sub_skills.append(name)

    lines = ["```mermaid", "sequenceDiagram"]
    if has_user_interaction:
        lines.append("    actor User")
    lines.append(f"    participant Main as {skill_name}")

    sub_aliases: dict[str, str] = {}
    for idx, sub in enumerate(sub_skills, start=1):
        alias = f"Sub_{idx}"
        sub_aliases[sub] = alias
        lines.append(f"    participant {alias} as {sub}")

    # 繪製主要互動摘要
    span = ("User" if has_user_interaction else "Main") + "," + (list(sub_aliases.values())[-1] if sub_aliases else "Main")
    for p in phases:
        if any(s.verb == "Ask" or s.is_external_delegation for s in p.steps):
            # 讓讀圖的人知道底下的「N.」是哪一個 Phase 的第幾步
            lines.append(f"    Note over {span}: Phase {p.num}: {sequence_label(p.title)}")
        for s in p.steps:
            if s.verb == "Ask":
                lines.append(f"    Main->>User: {sequence_label(step_label(s))}")
                lines.append("    User-->>Main: 回覆確認")
            elif s.is_external_delegation:
                plain = s.plain_text
                match, names = handoff_candidates(plain)
                if not names:
                    # 一個對象都認不出來(例如只寫了「對應 Derivers」),用 Note 標註
                    target_desc = match.group(1).strip() if match else "子技能"
                    lines.append(f"    Note over Main: {s.step_num}. 委派分流：{sequence_label(target_desc)}")
                    continue
                # 「A、B 或 C」是擇一,畫成 alt / else;沒有「或」的多個對象依序各畫一組
                branching = len(names) > 1 and "或" in match.group(1)
                indent = "        " if branching else "    "
                for index, name in enumerate(names):
                    if branching:
                        lines.append(f"    {'else' if index else 'alt'} {name}")
                    alias = sub_aliases[name]
                    lines.append(f"{indent}Main->>{alias}: {sequence_label(step_label(s))}")
                    lines.append(f"{indent}{alias}-->>Main: 完成並交回產出")
                if branching:
                    lines.append("    end")

    lines.append("```")
    return "\n".join(lines)


def render_diagrams_block(skill_name: str, phases: list[Phase]) -> str:
    """生成包含 <details open> 的完整視覺圖 Markdown 區塊。"""
    flowchart_md = generate_flowchart(phases)
    sequence_md = generate_sequence(skill_name, phases)

    parts = [
        "<details open>",
        "<summary>🗺️ 流程視覺圖 (點擊展開/收合)</summary>",
        "",
        flowchart_md,
    ]

    if sequence_md:
        parts.extend(["", sequence_md])

    parts.extend(["</details>", ""])
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", required=True, type=Path, help="目標 skill 的 SKILL.md 路徑(含檔名)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="格式檢查全過時把流程視覺圖注入目標檔的檔尾;有不過時不寫檔。檢查結果以 JSON 寫到 stdout")
    mode.add_argument("--check", action="store_true", help="只檢查不寫檔:格式檢查,加上檔案裡的流程視覺圖是否與 # SOP 一致。檢查結果以 JSON 寫到 stdout")
    mode.add_argument("--stdout", action="store_true", help="格式檢查全過時把流程視覺圖的 Markdown 寫到 stdout,不寫檔(沒有指定模式時也是這個行為)")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.file.is_file():
        print(f"錯誤: 找不到檔案 {args.file}。--file 要給目標 skill 的 SKILL.md 路徑(含檔名)。", file=sys.stderr)
        return 2
    try:
        content = args.file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"錯誤: {args.file} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。", file=sys.stderr)
        return 2

    phases, violations, candidates = parse_and_check(content)
    format_ok = not violations
    diagram_block = render_diagrams_block(skill_name_of(content), phases) if format_ok else ""

    if not (args.write or args.check):
        if not format_ok:
            for v in violations:
                print(f"不過〈{v.rule}〉第 {v.line} 行: {v.reason}", file=sys.stderr)
            print(f"錯誤: {args.file} 的 # SOP 有 {len(violations)} 處格式不過,沒有產生流程視覺圖。改完再執行。", file=sys.stderr)
            return 1
        print(diagram_block)
        return 0

    report = {
        "file": str(args.file),
        "passed": format_ok,
        "checks": build_checks(phases, violations),
        "candidates": candidates,
        "diagram": {"result": "未檢查", "evidence": "格式檢查有不過,沒有產生流程視覺圖"},
    }
    if format_ok:
        updated = inject(content, diagram_block)
        if args.check:
            consistent = updated == content
            report["diagram"] = {
                "result": "一致" if consistent else "不一致",
                "evidence": "檔案裡的流程視覺圖與 # SOP 一致" if consistent else "流程視覺圖缺失、不在檔尾,或與 # SOP 不一致;執行 --write 重新注入",
            }
            report["passed"] = consistent
        else:
            if updated != content:
                args.file.write_text(updated, encoding="utf-8")
                report["diagram"] = {"result": "已注入", "evidence": "流程視覺圖已寫到檔尾"}
                print(f"已把流程視覺圖注入 {args.file}", file=sys.stderr)
            else:
                report["diagram"] = {"result": "一致", "evidence": "檔案裡的流程視覺圖已經與 # SOP 一致,沒有改檔"}
                print(f"{args.file} 的流程視覺圖已經是最新的,沒有改檔", file=sys.stderr)
    else:
        print(f"{args.file} 的 # SOP 有 {len(violations)} 處格式不過,沒有寫檔", file=sys.stderr)

    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
