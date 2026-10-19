# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""檢查 uiux-plan 交出的 HTML 原型。

檢查項目:有入口 index.html 與狀態總覽 states.html、本地的 href 與 src 都指得到檔案、
原型頁沒有測試用的控制(切換狀態、模擬、快轉的按鈕)、
狀態總覽替每個畫面的每個 data-state 都有一格 `頁面.html?state=狀態` 的 iframe、
style.css 的 :root 有變數且 :root 以外與 HTML 裡都沒有寫死的顏色或 style 屬性、
每個畫面都載入 mock.js 且原型沒有呼叫 fetch、XMLHttpRequest、WebSocket、EventSource、
畫面的 script 不直接讀寫 localStorage(一律經過 Proto.load 與 Proto.save)、
這台機器有 node 時 mock.js 與每段內嵌的 script 都通過 `node --check`(沒有就標成略過)、
plan.md 這一步端點的需求出處都對得到畫面的 data-requirements、data-requirements 的需求編號都在 spec.md 裡。
結果以 JSON 寫到 stdout;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ENDPOINT_ROW = re.compile(r"^\| E(\d+) \|(.*)\|$")
WAVE_ROW = re.compile(r"^\| (\d+) \| S(\d+) \| E(\d+) ")
RANGE = re.compile(r"\b(FR|NFR|SC)-(\d+)\s*[–—~]\s*(?:(?:FR|NFR|SC)-)?(\d+)\b")
REQUIREMENT_ID = re.compile(r"\b((?:FR|NFR|SC)-\d+)\b")
COLOR_LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla)\(")
NETWORK_CALL = re.compile(r"\bfetch\s*\(|\bXMLHttpRequest\b|\bnew\s+WebSocket\s*\(|\bnew\s+EventSource\s*\(")
DIRECT_STORAGE = re.compile(r"\blocalStorage\b")
TEST_CONTROL = re.compile(r"^(?:模擬|快轉)|切換狀態")
STATE_FRAME = re.compile(r"^([\w-]+\.html)\?state=([\w-]+)$")
EXTERNAL = re.compile(r"^(?:[a-z]+:|//|#)", re.IGNORECASE)

R_ENTRY = "有入口 index.html 與狀態總覽 states.html"
R_LINKS = "本地的 href 與 src 都指得到檔案"
R_CLEAN = "原型頁不放測試用的控制"
R_STATES = "狀態總覽涵蓋每個畫面的每個狀態"
R_TOKENS = "審美設定只寫在 :root 變數"
R_MOCK = "每個畫面載入 mock.js 且不連真的後端"
R_STORAGE = "畫面不直接讀寫 localStorage"
R_JS = "JavaScript 通過 node --check"
R_COVERAGE = "plan.md 這一步的需求出處都對得到畫面"
R_SOURCES = "data-requirements 的需求編號都在 spec.md 裡"
RULES = [R_ENTRY, R_LINKS, R_CLEAN, R_STATES, R_TOKENS, R_MOCK, R_STORAGE, R_JS, R_COVERAGE, R_SOURCES]


class Page(HTMLParser):
    """收集一個畫面裡要檢查的屬性與內嵌的 script。"""

    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.states: set[str] = set()
        self.buttons: set[str] = set()
        self.frames: list[str] = []
        self.button_texts: list[str] = []
        self.has_proto_bar = False
        self._in_button = False
        self.requirements = ""
        self.styled: list[str] = []
        self.scripts: list[str] = []
        self.has_style_block = False
        self._in_script = False

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        for key in ("href", "src"):
            if attr.get(key):
                self.refs.append(attr[key])
        if "data-state" in attr:
            self.states.add(attr["data-state"] or "")
        if "data-show-state" in attr:
            self.buttons.add(attr["data-show-state"] or "")
        if tag == "iframe" and attr.get("src"):
            self.frames.append(attr["src"])
        if "proto-bar" in (attr.get("class") or "").split():
            self.has_proto_bar = True
        if tag == "button":
            self._in_button = True
            self.button_texts.append("")
        if tag == "body":
            self.requirements = attr.get("data-requirements") or ""
        if "style" in attr:
            self.styled.append(tag)
        if tag == "style":
            self.has_style_block = True
        self._in_script = tag == "script" and not attr.get("src")
        if self._in_script:
            self.scripts.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False
        if tag == "button":
            self._in_button = False

    def handle_data(self, data):
        if self._in_button:
            self.button_texts[-1] += data.strip()
        if self._in_script:
            self.scripts[-1] += data


def section(lines: list[str], heading: str) -> list[str]:
    """取出某個標題底下、到下一個同級或更高標題之前的行。"""
    level = len(heading) - len(heading.lstrip("#"))
    inside, picked = False, []
    for line in lines:
        if line.startswith("#") and not line.startswith("#" * (level + 1)):
            inside = line.strip() == heading
            continue
        if inside:
            picked.append(line)
    return picked


def requirement_ids(text: str) -> set[str]:
    """取出一段文字裡的需求編號,`FR-001–FR-019` 這類範圍展開成每一個編號。"""
    ids = set(REQUIREMENT_ID.findall(text))
    for kind, start, end in RANGE.findall(text):
        ids |= {f"{kind}-{n:0{len(start)}d}" for n in range(int(start), int(end) + 1)}
    return ids


def strip_root(css: str) -> tuple[str, str]:
    """把 style.css 拆成 :root 區塊與其他部分。"""
    match = re.search(r":root\s*\{([^}]*)\}", css)
    if not match:
        return "", css
    return match.group(1), css[: match.start()] + css[match.end():]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prototype", required=True, type=Path, help="prototype 資料夾的路徑,裡面要有 index.html、style.css 與 mock.js")
    parser.add_argument("--plan", required=True, type=Path, help="system-analysis 產出的 plan.md 路徑,用來找這一步分析的端點與需求出處")
    parser.add_argument("--spec", required=True, type=Path, help="spec.md 的路徑,用來確認需求編號都有定義")
    parser.add_argument("--step", required=True, help="這份原型對應的波段表步驟編號,例如 S1")
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    step_match = re.fullmatch(r"S?(\d+)", args.step.strip())
    if not step_match:
        print(f"錯誤: --step 收到「{args.step}」,要給波段表的步驟編號,例如 S1。", file=sys.stderr)
        return 2
    step = int(step_match.group(1))
    if not args.prototype.is_dir():
        print(f"錯誤: 找不到資料夾 {args.prototype};--prototype 要給 prototype 資料夾,不是裡面的 html 檔。", file=sys.stderr)
        return 2
    for path in (args.plan, args.spec):
        if not path.is_file():
            print(f"錯誤: 找不到 {path};--plan、--spec 都要給檔案路徑。", file=sys.stderr)
            return 2

    violations: dict[str, list[dict]] = {rule: [] for rule in RULES}

    def bad(rule: str, where: str, reason: str) -> None:
        violations[rule].append({"where": where, "reason": reason})

    root = args.prototype
    pages = sorted(p for p in root.glob("*.html") if p.name != "states.html")
    for entry in ("index.html", "states.html"):
        if not (root / entry).is_file():
            bad(R_ENTRY, str(root), f"沒有 {entry}")
    overview = Page()
    if (root / "states.html").is_file():
        overview.feed((root / "states.html").read_text(encoding="utf-8"))
        for ref in overview.refs:
            target = ref.split("?", 1)[0].split("#", 1)[0]
            if ref and not EXTERNAL.match(ref) and target and not (root / target).is_file():
                bad(R_LINKS, "states.html", f"{ref} 指到的檔案不存在")
    framed: dict[str, set[str]] = {}
    for src in overview.frames:
        if m := STATE_FRAME.match(src):
            framed.setdefault(m.group(1), set()).add(m.group(2))
        else:
            bad(R_STATES, "states.html", f"iframe 的 src「{src}」要寫成 頁面.html?state=狀態代號")

    tagged: set[str] = set()
    inline_scripts: list[tuple[str, str]] = []
    for page_path in pages:
        page = Page()
        page.feed(page_path.read_text(encoding="utf-8"))
        name = page_path.name
        for ref in page.refs:
            if EXTERNAL.match(ref):
                continue
            target = ref.split("#", 1)[0].split("?", 1)[0]
            if target and not (root / target).is_file():
                bad(R_LINKS, name, f"{ref} 指到的檔案不存在")
        if page.buttons or page.has_proto_bar:
            bad(R_CLEAN, name, "有切換狀態的控制列或 data-show-state 按鈕,要搬到 states.html")
        for text in page.button_texts:
            if TEST_CONTROL.search(text):
                bad(R_CLEAN, name, f"按鈕「{text}」是測試用的控制,要搬到 states.html")
        if not page.states:
            bad(R_STATES, name, "沒有任何 data-state 區塊")
        for state in sorted(page.states - framed.get(name, set())):
            bad(R_STATES, name, f"data-state=\"{state}\" 在 states.html 沒有對應的 iframe")
        for state in sorted(framed.get(name, set()) - page.states):
            bad(R_STATES, "states.html", f"{name}?state={state} 在 {name} 裡沒有對應的 data-state 區塊")
        if page.styled:
            bad(R_TOKENS, name, f"{len(page.styled)} 個元素寫了 style 屬性")
        if page.has_style_block:
            bad(R_TOKENS, name, "有 <style> 區塊")
        if "mock.js" not in page.refs:
            bad(R_MOCK, name, "沒有載入 mock.js")
        for index, code in enumerate(page.scripts, start=1):
            if NETWORK_CALL.search(code):
                bad(R_MOCK, f"{name} 第 {index} 段 script", "呼叫了 fetch、XMLHttpRequest、WebSocket 或 EventSource")
            if DIRECT_STORAGE.search(code):
                bad(R_STORAGE, f"{name} 第 {index} 段 script", "直接讀寫 localStorage,要改用 Proto.load 與 Proto.save")
            if code.strip():
                inline_scripts.append((f"{name} 第 {index} 段 script", code))
        ids = requirement_ids(page.requirements)
        if not ids:
            bad(R_COVERAGE, name, "<body> 沒有 data-requirements")
        tagged |= ids

    style = root / "style.css"
    if not style.is_file():
        bad(R_TOKENS, "style.css", "不存在")
    else:
        root_block, rest = strip_root(style.read_text(encoding="utf-8"))
        if "--" not in root_block:
            bad(R_TOKENS, "style.css", ":root 裡沒有任何變數")
        for literal in sorted(set(COLOR_LITERAL.findall(rest))):
            bad(R_TOKENS, "style.css", f":root 以外寫死了顏色 {literal}")

    mock = root / "mock.js"
    if not mock.is_file():
        bad(R_MOCK, "mock.js", "不存在")
    elif NETWORK_CALL.search(mock.read_text(encoding="utf-8")):
        bad(R_MOCK, "mock.js", "呼叫了 fetch、XMLHttpRequest、WebSocket 或 EventSource")

    node = shutil.which("node")
    if node:
        sources = ([("mock.js", mock.read_text(encoding="utf-8"))] if mock.is_file() else []) + inline_scripts
        with tempfile.TemporaryDirectory() as tmp:
            for index, (where, code) in enumerate(sources):
                script = Path(tmp) / f"s{index}.js"
                script.write_text(code, encoding="utf-8")
                result = subprocess.run([node, "--check", str(script)], capture_output=True, text=True, encoding="utf-8")
                if result.returncode != 0:
                    detail = next((l for l in result.stderr.splitlines() if "Error" in l), result.stderr.strip()[:200])
                    bad(R_JS, where, detail)
    else:
        print("提示: 這台機器沒有 node,`node --check` 略過。", file=sys.stderr)

    plan_lines = args.plan.read_text(encoding="utf-8").splitlines()
    endpoint = next((int(m.group(3)) for l in section(plan_lines, "### 分析波段") if (m := WAVE_ROW.match(l.strip())) and int(m.group(2)) == step), None)
    needed: set[str] = set()
    if endpoint is None:
        bad(R_COVERAGE, "plan.md", f"`### 分析波段` 沒有 S{step}")
    else:
        row = next((m.group(2) for l in section(plan_lines, "### 端點盤點") if (m := ENDPOINT_ROW.match(l.strip())) and int(m.group(1)) == endpoint), None)
        if row is None:
            bad(R_COVERAGE, "plan.md", f"S{step} 分析的 E{endpoint} 不在 `### 端點盤點`")
        else:
            needed = requirement_ids(row.split("|")[-1])
    for rid in sorted(needed - tagged):
        bad(R_COVERAGE, rid, f"E{endpoint} 的需求出處 {rid} 沒有任何畫面的 data-requirements 對到")

    defined = set(re.findall(r"\*\*((?:FR|NFR|SC)-\d+)\*\*", args.spec.read_text(encoding="utf-8")))
    for rid in sorted(tagged - defined):
        bad(R_SOURCES, rid, f"{rid} 在 spec.md 裡沒有定義")

    passed_evidence = {
        R_ENTRY: "index.html 與 states.html 都存在",
        R_LINKS: f"{len(pages)} 個畫面的本地連結都指得到檔案",
        R_CLEAN: f"{len(pages)} 個原型頁都沒有測試用的控制",
        R_STATES: f"states.html 有 {len(overview.frames)} 格,涵蓋 {len(pages)} 個畫面的每個狀態",
        R_TOKENS: "style.css 的 :root 有變數,其他地方沒有寫死的顏色或 style 屬性",
        R_MOCK: f"{len(pages)} 個畫面都載入 mock.js,沒有網路呼叫",
        R_STORAGE: f"{len(pages)} 個畫面的 script 都經過 Proto.load 與 Proto.save",
        R_JS: f"mock.js 與 {len(inline_scripts)} 段內嵌 script 都通過 node --check",
        R_COVERAGE: f"S{step}(E{endpoint})的 {len(needed)} 個需求出處都對得到畫面",
        R_SOURCES: f"data-requirements 的 {len(tagged)} 個需求編號都在 spec.md 裡",
    }
    checks = []
    for rule in RULES:
        mine = violations[rule]
        skipped = rule == R_JS and node is None
        result = "略過" if skipped else ("不過" if mine else "過")
        evidence = "這台機器沒有 node" if skipped else (";".join(f"{v['where']}:{v['reason']}" for v in mine) if mine else passed_evidence[rule])
        checks.append({"rule": rule, "result": result, "evidence": evidence, "violations": mine})
    passed = not any(violations.values())
    report = {"prototype": str(root), "step": f"S{step}", "pages": [p.name for p in pages], "passed": passed, "checks": checks}
    print(f"檢查了 {len(pages)} 個畫面、{len(needed)} 個需求出處,{sum(len(v) for v in violations.values())} 個不符項", file=sys.stderr)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
