# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""SOP 流程圖與時序圖自動化渲染器 (SSOT Compiler)

解析 SKILL.md 中的 # SOP 骨架，自動生成 Mermaid flowchart TD 與 sequenceDiagram，
並支援直接就地注入 (<details open> 區塊) 或比對一致性。
"""

import argparse
import re
import sys
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

    @property
    def node_id(self) -> str:
        return f"P{self.phase_num}S{self.step_num}"

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


def simplify_action_label(verb: str, action: str, max_len: int = 30) -> str:
    """過濾路徑與指令雜訊，提煉動詞與核心受詞。"""
    text = action.strip()
    # 剝離資源指標：依 rules/..., 依骨架 templates/...
    text = re.sub(r"^依\s*`?rules/[^`\s]+`?\s*", "", text)
    text = re.sub(r"^依骨架\s*`?templates/[^`\s]+`?\s*與範例\s*`?templates/[^`\s]+`?\s*", "", text)
    text = re.sub(r"^依骨架\s*`?templates/[^`\s]+`?\s*", "", text)
    text = re.sub(r"^依\s*`?[^`\s]+`?\s*與\s*`?[^`\s]+`?\s*", "", text)
    # 剝離腳本與指令前綴
    text = re.sub(r"^執行\s*`uv run scripts/[^`]+`\s*", "", text)
    text = re.sub(r"^執行\s*uv run scripts/\S+\s*", "", text)
    text = re.sub(
        r"^執行\s*([a-zA-Z0-9_-]+)\s+[a-zA-Z0-9_-]+\s*指令傳入任務指示檔並將最後輸出寫入紀錄檔",
        r"執行 \1",
        text,
    )
    # 簡化常見贅詞
    text = re.sub(r"^把使用者要的流程寫成", "寫出", text)
    text = re.sub(r"^把使用者要的規則寫成", "寫出", text)
    text = re.sub(r"^把使用者要的", "寫出", text)
    text = re.sub(r"^剛寫進目標 skill 的", "讀回", text)
    text = clean_label(text, max_len=max_len)
    return f"{verb}：{text}"


def simplify_condition_label(condition: str, max_len: int = 20) -> str:
    """精煉條件分支文字，提煉核心提問。"""
    cond = condition.strip().replace("`", "")
    cond = re.sub(r"[;。？?]+$", "", cond)
    mappings = [
        (r"沒有步驟用得到.*", "無使用資源"),
        (r"對話裡有那一次交給.*", "已有輸入與產出"),
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
            return clean_label(replacement, max_len=max_len) + "？"
    return clean_label(cond, max_len=max_len) + "？"


def parse_sop(content: str) -> tuple[str, list[Phase], str]:
    """從 SKILL.md 內容解析 SOP 結構。

    回傳: (skill_name, phases, full_sop_text_without_diagrams)
    """
    # 1. 取得 skill_name
    skill_name = "Skill"
    name_match = re.search(r"^name:\s*([a-zA-Z0-9_-]+)", content, re.MULTILINE)
    if name_match:
        skill_name = name_match.group(1).strip()

    # 2. 定位 # SOP 區塊
    sop_match = re.search(r"^# SOP\s*$", content, re.MULTILINE)
    if not sop_match:
        raise ValueError("檔案中找不到 `# SOP` 標題")

    sop_start = sop_match.end()

    # 尋找下一個頂層標題 # (但不是 ##) 或檔尾
    next_header = re.search(r"\n#[^#\n]", content[sop_start:])
    if next_header:
        sop_raw = content[sop_start : sop_start + next_header.start()]
    else:
        sop_raw = content[sop_start:]

    # 3. 移除既有的視覺圖折疊區塊 (若有)
    diagram_block_pattern = re.compile(
        r"<details[^>]*>\s*<summary>.*?流程視覺圖.*?</summary>.*?</details>",
        re.DOTALL,
    )
    clean_sop = diagram_block_pattern.sub("", sop_raw)

    # 4. 逐行解析 Phase 與 Step
    phases: list[Phase] = []
    current_phase: Phase | None = None

    lines = clean_sop.splitlines()
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        phase_match = re.match(r"^## Phase (\d+):\s*(.*)$", stripped)
        if phase_match:
            p_num = int(phase_match.group(1))
            p_title = phase_match.group(2).strip()
            current_phase = Phase(num=p_num, title=p_title)
            phases.append(current_phase)
            continue

        step_match = re.match(
            r"^(\d+)\.\s+(Read|Write|Think|Ask|Delegate)\b\s*(.*)$", stripped
        )
        if step_match and current_phase is not None:
            s_num = int(step_match.group(1))
            verb = step_match.group(2)
            rest = step_match.group(3).strip()

            parts = rest.split(";若")
            action = parts[0].strip()
            guards: list[Guard] = []

            for g_str in parts[1:]:
                gm = re.match(
                    r"^(.*?)\s*→\s*(跳至\s*Phase\s*(\d+)\s*Step\s*(\d+)|結束)[。.]?$",
                    g_str.strip(),
                )
                if gm:
                    cond = gm.group(1).strip()
                    tgt_str = gm.group(2).strip()
                    if tgt_str.startswith("跳至"):
                        jump_m = re.search(r"Phase\s*(\d+)\s*Step\s*(\d+)", tgt_str)
                        if jump_m:
                            guards.append(
                                Guard(
                                    condition=cond,
                                    target_type="jump",
                                    target_phase=int(jump_m.group(1)),
                                    target_step=int(jump_m.group(2)),
                                )
                            )
                    else:
                        guards.append(
                            Guard(
                                condition=cond,
                                target_type="exit",
                            )
                        )

            step = Step(
                phase_num=current_phase.num,
                step_num=s_num,
                verb=verb,
                action_text=action,
                guards=guards,
                raw_line=stripped,
            )
            current_phase.steps.append(step)

    return skill_name, phases, clean_sop


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
            action_display = simplify_action_label(s.verb, s.action_text)
            lines.append(f'        {s.node_id}["{s.step_num}. {action_display}"]')
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
        # 尋找 "轉交" 後面的文字
        m = re.search(r"轉交\s*([^,;。]+)", s.action_text)
        if m:
            raw_target = m.group(1).strip()
            # 依頓號、逗號或「或」切分候選
            candidates = re.split(r"、|或|,", raw_target)
            for c in candidates:
                cand = c.strip()
                # 排除通用說明詞如「對應 Derivers」
                if cand and cand not in sub_skills and not cand.startswith("對應"):
                    sub_skills.append(cand)

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
    for p in phases:
        for s in p.steps:
            if s.verb == "Ask":
                prompt = clean_label(s.action_text, max_len=30)
                lines.append(f"    Main->>User: {s.node_id} {prompt}")
                lines.append("    User-->>Main: 回覆確認")
            elif s.is_external_delegation:
                m = re.search(r"轉交\s*([^,;。]+)", s.action_text)
                target_desc = m.group(1).strip() if m else "子技能"
                # 檢查是否為單一已知 alias
                matched_alias = None
                for sub, alias in sub_aliases.items():
                    if sub == target_desc:
                        matched_alias = alias
                        break

                action_summary = clean_label(s.action_text, max_len=35)
                if matched_alias:
                    lines.append(f"    Main->>{matched_alias}: {s.node_id} {action_summary}")
                    lines.append(f"    {matched_alias}-->>Main: 完成並交回產出")
                else:
                    # 多候選或動態反覆，使用 Note 標註
                    lines.append(f"    Note over Main: {s.node_id} 委派分流：{clean_label(target_desc, max_len=40)}")

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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path, help="目標 SKILL.md 路徑")
    parser.add_argument("--write", action="store_true", help="將生成的視覺圖直接寫入目標檔案")
    parser.add_argument("--check", action="store_true", help="檢查檔案中既有的視覺圖是否與最新編譯結果一致")
    parser.add_argument("--stdout", action="store_true", help="將生成的 Markdown 輸出至標準輸出")

    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    if not args.file.is_file():
        print(f"錯誤: 找不到檔案 {args.file}", file=sys.stderr)
        return 1

    try:
        content = args.file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"錯誤: 檔案 {args.file} 不是 UTF-8 編碼", file=sys.stderr)
        return 1

    try:
        skill_name, phases, clean_sop = parse_sop(content)
    except Exception as e:
        print(f"解析錯誤: {e}", file=sys.stderr)
        return 1

    if not phases:
        print("錯誤: 未在 # SOP 下解析出任何 Phase", file=sys.stderr)
        return 1

    diagram_block = render_diagrams_block(skill_name, phases)

    if args.stdout:
        print(diagram_block)
        return 0

    if args.check:
        # 比對目前檔案中是否包含正確的 diagram_block
        if diagram_block in content:
            print(f"✓ {args.file} 視覺圖與 SOP 完全一致", file=sys.stderr)
            return 0
        else:
            print(f"✗ {args.file} 視覺圖缺失或與 SOP 最新內容不一致", file=sys.stderr)
            return 1

    if args.write:
        # 定位 # SOP
        sop_pattern = re.compile(r"^# SOP\s*$", re.MULTILINE)
        m = sop_pattern.search(content)
        if not m:
            print(f"錯誤: 找不到 # SOP", file=sys.stderr)
            return 1

        before_sop = content[: m.end()]
        after_sop = content[m.end() :]

        # 移除 after_sop 中的既有視覺圖折疊區塊
        diagram_block_pattern = re.compile(
            r"\s*<details[^>]*>\s*<summary>.*?流程視覺圖.*?</summary>.*?</details>\s*",
            re.DOTALL,
        )
        after_sop = diagram_block_pattern.sub("\n\n", after_sop).lstrip()

        # 組裝新檔案內容
        new_content = f"{before_sop}\n\n{diagram_block}\n{after_sop}"
        args.file.write_text(new_content, encoding="utf-8")
        print(f"✓ 已成功將流程視覺圖注入 {args.file}", file=sys.stderr)
        return 0

    # 預設行為：若無指定 --write/--check/--stdout，印出生成的區塊
    print(diagram_block)
    return 0


if __name__ == "__main__":
    sys.exit(main())
