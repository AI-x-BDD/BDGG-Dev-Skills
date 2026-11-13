# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""檢查 testplan.md 有沒有涵蓋範疇內的每一條需求,測試案例的編號、歸屬、受測操作與驗證方式是否對得上,以及每個替身有沒有實跑案例。

範疇:讀 testplan 開頭「- **範疇**:使用者故事 5、6;…」裡列出的故事序號;沒有這一行就是 spec 的全部故事。
一條需求在範疇內,是指它寫在範疇內某個「### 使用者故事 N」底下,或它在「## 全域需求」寫的「適用」
列到範疇內的故事;SC 在範疇內,是指範疇內某條需求的內文引用了它。範疇是全部故事時,spec 的每一條
FR、NFR、SC 都在範疇內。範疇外的需求可以出現在需求覆蓋表,但不要求。

檢查十件事:
1. 範疇內每個 FR-、NFR-、SC- 編號,在「需求覆蓋」表都有一列;這一列要指到至少一個有定義的案例,
   或標「不在範疇」並在「不在本次範疇」表寫了為什麼不測與之後怎麼驗(全是 — 的列不算涵蓋);「邊界:」開頭的列同樣要求有案例或「不在範疇」
2. 範疇是全部故事時,spec「### 邊界情況」有幾條,需求覆蓋表就有幾列以「邊界:」開頭;範疇只含部分故事時不檢查
   (邊界情況沒有標它屬於哪個故事,沒辦法只挑出範疇內的)
3. 需求覆蓋表的「歸屬」:spec 只屬於一個故事的需求寫「故事 N」;適用兩個以上故事的需求與 SC 寫「全域」,
   而且出現在全域測試區的「全域 NFR 的涵蓋彙整」表
4. 每個定義過的案例 ID 都出現在需求覆蓋表(X~Y 展開成範圍);計劃裡引用的案例 ID 都有定義
5. 案例 ID 的格式是 US<k>-<端點代號>-NN、US<k>-AJ-NN 或 G-NN;每種前綴的流水號從 01 起連續、不重複
   (同一節的功能案例與非功能案例共用一個序列,出現的先後不限)
6. 每個案例的「受測操作」以受測操作表「寫法」欄的某一種開頭;以 → 串起的每一段,含 › 的也要以某一種寫法開頭
7. 每個案例的「則」從 則1 起以 <br> 分隔、依序編號,「要抓的錯」不是空白
8. 有「驗證方式」欄的案例,驗證方式是「🔴🟢 行為測試」「📏 量測」「📏 人工」其中一種
9. 範疇內每條 NFR(需求覆蓋表沒標不在範疇的)至少被一個有「驗證方式」欄的案例在「需求」欄列出
10. 待測端點表「替身」欄不是「無」或「—」時,以 <br> 分隔的每個替身寫成「替身(代替的真元件)→ …」,
   → 後面指到至少一個有定義、驗證方式是「📏 量測」或「📏 人工」的案例 ID,或寫「無法實跑:」加原因
11. 驗證方式是「📏 量測」或「📏 人工」的案例,「副作用與護欄」欄以「時機:節內」或「時機:整合」開頭
12.「### 測試指令」表有「快速層」與「全部」兩列,「指令」欄都不是空白也不是填位符號
13.(有給 --contracts 時)受測操作表「規格錨點」欄指到的每個合約操作(OpenAPI 的 `paths./<路徑>.<method>`、
   AsyncAPI 的 `operations.<id>`),它底下名稱以 `x-` 開頭、含 error 或 failure 的欄位列出的每個錯誤碼,
   都有一個案例:受測操作對到這個操作,且案例那一列寫到這個代碼;或「不在本次範疇」表有一列同時寫到
   這個代碼與這個操作的 operationId,並寫了為什麼不測與之後怎麼驗。案例對到操作的方式:受測操作的某一段
   以受測操作表某一列的寫法開頭;那一列只有一個操作時就是它,有好幾個操作時,用 › 後面的方法名比對
   operationId(忽略大小寫與底線,`search_library` 對 `searchLibrary`)。一個案例串起好幾個操作時,錯誤碼只算給
   同一段(<br> 分隔)也寫到那個方法名的操作。沒給 --contracts 時不做這一項

結果以 JSON 寫到 stdout,第一行是摘要;有任何一項不過時 exit code 是 1。
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

R_REQ = "範疇內每條需求在需求覆蓋表都有一列,列上有存在的案例或明確不在範疇"
R_EDGE = "每條邊界情況在需求覆蓋表都有一列"
R_SCOPE = "需求的歸屬對得上 spec,全域需求列在涵蓋彙整"
R_COVER = "每個案例都在需求覆蓋表,引用的案例都有定義"
R_SEQ = "案例 ID 格式正確,從 01 起連續、不重複"
R_OPS = "受測操作取自受測操作表"
R_THEN = "則依序編號,要抓的錯有寫"
R_VERIFY = "驗證方式是三種之一"
R_NFR = "範疇內每條 NFR 都有標明驗證方式的案例"
R_DOUBLE = "每個替身都指到一個 📏 實跑案例,或寫明無法實跑"
R_TIMING = "📏 案例的副作用與護欄以實跑時機開頭"
R_CONTRACT = "範疇內每個合約操作的每個錯誤碼都有案例,或寫明不在範疇"
R_CMDS = "測試指令表寫出快速層與全部的指令"
RULES = [R_REQ, R_EDGE, R_SCOPE, R_COVER, R_SEQ, R_OPS, R_THEN, R_VERIFY, R_NFR, R_DOUBLE, R_TIMING, R_CMDS]

VERIFY_KINDS = {"🔴🟢 行為測試", "📏 量測", "📏 人工"}
REAL_RUN_KINDS = {"📏 量測", "📏 人工"}
TIMING = re.compile(r"^時機[::](節內|整合)(?:[;;,,]|$)")
NO_DOUBLE = {"無", "—", "-", ""}
CANNOT_RUN = re.compile(r"^無法實跑[::]\s*(\S.*)?$")
SPEC_REQ = re.compile(r"\*\*((?:FR|NFR|SC)-\d+)\*\*")
REQ_REF = re.compile(r"\b((?:FR|NFR|SC)-\d+)\b")
CASE_LIKE = re.compile(r"^(?:US\d+-[A-Z]+|[A-Z]+)-\d+$")
CASE_ID = re.compile(r"^(US\d+-[A-Z]+|G)-(\d{2})$")
ID_TOKEN = r"(?:US\d+-)?[A-Z]+"
ERROR_CODE = re.compile(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+")
SPEC_FILE = re.compile(r"[\w./-]+\.(?:ya?ml)")
OPENAPI_OP = re.compile(r"paths\.(/[^`\s、,,;]*?)\.(get|put|post|delete|patch|head|options)\b")
ASYNCAPI_OP = re.compile(r"operations\.([A-Za-z_][\w-]*)")


def read(path: Path, label: str) -> str:
    if not path.is_file():
        print(f"錯誤: 找不到 {label} `{path}`。請給檔案的路徑。", file=sys.stderr)
        sys.exit(2)
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"錯誤: {path} 不是 UTF-8 編碼。請把它轉存成 UTF-8 再執行。", file=sys.stderr)
        sys.exit(2)


def section(text: str, heading: re.Pattern[str]) -> list[str] | None:
    """回傳符合 heading 的那一節(不含標題),到下一個同級或更高級的標題為止。"""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if heading.match(line):
            level = len(line) - len(line.lstrip("#"))
            body = []
            for rest in lines[index + 1 :]:
                stripped = rest.lstrip("#")
                if rest.startswith("#") and stripped.startswith(" ") and len(rest) - len(stripped) <= level:
                    break
                body.append(rest)
            return body
    return None


def tables(lines: list[str]) -> list[tuple[list[str], list[list[str]]]]:
    """回傳每張表的 (表頭, 資料列);分隔列跳過。"""
    result: list[tuple[list[str], list[list[str]]]] = []
    current: tuple[list[str], list[list[str]]] | None = None
    for line in lines:
        if not line.startswith("|"):
            current = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if current is None:
            current = (cells, [])
            result.append(current)
        elif not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
            current[1].append(cells)
    return result


def expand(text: str, prefixes: set[str]) -> set[str]:
    found = set()
    for start, low, end, high in re.findall(rf"\b({ID_TOKEN})-(\d+)~({ID_TOKEN})-(\d+)\b", text):
        if start == end and start in prefixes:
            found |= {f"{start}-{n:0{len(low)}d}" for n in range(int(low), int(high) + 1)}
    for prefix, number in re.findall(rf"\b({ID_TOKEN})-(\d+)\b", text):
        if prefix in prefixes:
            found.add(f"{prefix}-{number}")
    return found


def error_codes(node: object, inside: bool = False, found: set[str] | None = None) -> set[str]:
    """收集名稱以 x- 開頭、含 error 或 failure 的欄位底下的錯誤碼:字串清單的項目、字典的鍵、code: 的值與單一字串值。"""
    found = set() if found is None else found
    if isinstance(node, dict):
        for key, value in node.items():
            hit = inside or (isinstance(key, str) and key.startswith("x-") and ("error" in key or "failure" in key))
            if hit and isinstance(key, str) and ERROR_CODE.fullmatch(key):
                found.add(key)
            if hit and isinstance(value, str) and ERROR_CODE.fullmatch(value.strip()):
                found.add(value.strip())
            error_codes(value, hit, found)
    elif isinstance(node, list):
        for value in node:
            if inside and isinstance(value, str) and ERROR_CODE.fullmatch(value.strip()):
                found.add(value.strip())
            error_codes(value, inside, found)
    return found


def contract_ops(cell: str, contracts: Path, docs: dict[str, object]) -> tuple[list[tuple[str, str, set[str]]], list[str]]:
    """規格錨點欄的一格 → ([(規格檔名, operationId, 錯誤碼)], [找不到的錨點])。"""
    found: list[tuple[str, str, set[str]]] = []
    missing: list[str] = []
    files = list(SPEC_FILE.finditer(cell))
    for index, match in enumerate(files):
        name = Path(match.group(0)).name
        segment = cell[match.end(): files[index + 1].start() if index + 1 < len(files) else len(cell)]
        refs = [("openapi", m.group(1), m.group(2)) for m in OPENAPI_OP.finditer(segment)]
        refs += [("asyncapi", m.group(1), "") for m in ASYNCAPI_OP.finditer(segment)]
        if not refs:
            continue
        if name not in docs:
            path = contracts / name
            docs[name] = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else None
        doc = docs[name]
        if not isinstance(doc, dict):
            missing.append(f"{name}(--contracts 資料夾裡沒有這個檔)")
            continue
        for kind, key, method in refs:
            if kind == "openapi":
                op = (doc.get("paths") or {}).get(key, {}).get(method)
                label = f"paths.{key}.{method}"
            else:
                op = (doc.get("operations") or {}).get(key)
                label = f"operations.{key}"
            if not isinstance(op, dict):
                missing.append(f"{name} § {label}")
                continue
            op_id = op.get("operationId") or key
            found.append((name, op_id, error_codes(op)))
    return found, missing


def squash(name: str) -> str:
    """比對方法名與 operationId 用:去掉反引號、括號後的參數與底線,轉小寫。"""
    return re.split(r"[(]", name.replace("`", "").strip())[0].replace("_", "").lower()


def anchor(writing: str) -> str:
    """受測操作表一種寫法的開頭:› 之前那段;沒有 › 就取第一個 . 或 ( 之前那段。"""
    if "›" in writing:
        return writing.split("›")[0].strip()
    return re.split(r"[.(]", writing, maxsplit=1)[0].strip()


def spec_scopes(spec: str) -> tuple[dict[str, set[int]], dict[str, str], set[int]]:
    """回傳 (需求 → 適用的故事, 需求 → 定義它的那一行, spec 的全部故事)。SC 的適用故事是空集合。"""
    scopes: dict[str, set[int]] = {}
    lines_of: dict[str, str] = {}
    stories: set[int] = set()
    story: int | None = None
    in_global = False
    for line in spec.splitlines():
        heading = re.match(r"^###\s+使用者故事\s*(\d+)", line)
        if heading:
            story, in_global = int(heading.group(1)), False
            stories.add(story)
        elif line.startswith("## "):
            story, in_global = None, "全域需求" in line
        for req in SPEC_REQ.findall(line):
            lines_of[req] = line
            applies = re.search(r"適用[::]([^))]*)", line)
            if req.startswith("SC-"):
                scopes[req] = set()
            elif applies:
                scopes[req] = {int(n) for n in re.findall(r"\d+", applies.group(1))}
            elif story is not None and not in_global:
                scopes[req] = {story}
            else:
                scopes[req] = set()
    return scopes, lines_of, stories


def main() -> int:
    parser = argparse.ArgumentParser(
        description="檢查 testplan.md 是否涵蓋範疇內的每一條需求,案例 ID、歸屬、受測操作與驗證方式是否對得上,待測端點表的每個替身是否指到 📏 實跑案例。"
    )
    parser.add_argument("--spec", required=True, type=Path, help="功能規格 spec.md 的路徑")
    parser.add_argument("--plan", required=True, type=Path, help="要檢查的 testplan.md 的路徑")
    parser.add_argument(
        "--contracts",
        type=Path,
        help="spec package 的 contracts 資料夾(放 OpenAPI/AsyncAPI 規格檔);給了才檢查合約的每個操作 × 錯誤碼都有案例或寫明不在範疇",
    )
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    spec = read(args.spec, "spec.md")
    plan = read(args.plan, "testplan.md")
    violations: dict[str, list[dict[str, str]]] = {rule: [] for rule in RULES}

    coverage = section(plan, re.compile(r"^## .*需求覆蓋\s*$"))
    catalog = section(plan, re.compile(r"^### 受測操作\s*$"))
    if coverage is None or catalog is None:
        missing = "「## N. 需求覆蓋」" if coverage is None else "「### 受測操作」"
        print(f"錯誤: {args.plan} 找不到 {missing} 這一節。請照 templates/testplan.md 的標題寫。", file=sys.stderr)
        return 2
    summary = section(plan, re.compile(r"^### .*全域 NFR 的涵蓋彙整\s*$")) or []
    coverage_tables = tables(coverage)
    if not coverage_tables:
        print(f"錯誤: {args.plan} 的需求覆蓋這一節沒有表格。", file=sys.stderr)
        return 2
    cov_header, coverage_rows = coverage_tables[0]

    # 範疇
    scopes, lines_of, all_stories = spec_scopes(spec)
    scope_line = re.search(r"\*\*範疇\*\*[::]([^\n]*)", plan)
    in_scope_stories = all_stories
    if scope_line:
        story_part = re.search(r"使用者故事\s*([\d、,, ]+)", scope_line.group(1))
        if story_part:
            in_scope_stories = {int(n) for n in re.findall(r"\d+", story_part.group(1))}
    full_scope = in_scope_stories >= all_stories
    if full_scope:
        required = list(scopes)
    else:
        required = [req for req, applies in scopes.items() if applies & in_scope_stories]
        referenced = {ref for req in required for ref in REQ_REF.findall(lines_of[req]) if ref.startswith("SC-")}
        required += [sc for sc in scopes if sc in referenced and sc not in required]

    # 1. 需求
    row_of: dict[str, list[str]] = {}
    for cells in coverage_rows:
        for ref in REQ_REF.findall(cells[0]):
            row_of.setdefault(ref, cells)
    for req in required:
        if req not in row_of:
            violations[R_REQ].append({"item": req, "reason": "這條需求在範疇內,需求覆蓋表沒有它的列"})

    # 2. 邊界情況
    edges = section(spec, re.compile(r"^### 邊界情況\s*$")) or []
    edge_count = sum(1 for line in edges if line.startswith("- "))
    edge_rows = sum(1 for cells in coverage_rows if cells[0].startswith("邊界:"))
    if full_scope and edge_count != edge_rows:
        violations[R_EDGE].append(
            {"item": "邊界情況", "reason": f"spec 有 {edge_count} 條邊界情況,需求覆蓋表有 {edge_rows} 列以「邊界:」開頭"}
        )

    # 3. 歸屬
    owner_at = cov_header.index("歸屬") if "歸屬" in cov_header else None
    summary_reqs = {ref for _, rows in tables(summary) for cells in rows for ref in REQ_REF.findall(cells[0])}
    if owner_at is None:
        violations[R_SCOPE].append({"item": "需求覆蓋表", "reason": "表頭沒有「歸屬」欄;照 templates/testplan.md 的表頭寫"})
    else:
        for req, cells in row_of.items():
            if req not in scopes or len(cells) <= owner_at:
                continue
            applies = scopes[req]
            expected = f"故事 {next(iter(applies))}" if len(applies) == 1 else "全域"
            if cells[owner_at] != expected:
                violations[R_SCOPE].append(
                    {"item": req, "reason": f"spec 裡這條需求適用 {sorted(applies) or 'SC(跨故事)'},歸屬應寫「{expected}」,收到「{cells[owner_at]}」"}
                )
            elif expected == "全域" and req not in summary_reqs:
                violations[R_SCOPE].append({"item": req, "reason": "歸屬是全域,但全域測試區的「全域 NFR 的涵蓋彙整」表沒有它的列"})

    # 找出案例:需求覆蓋表以外、第一格像案例 ID 的列,連同所在表的表頭
    plan_tables = tables(plan.splitlines())
    coverage_set = {id(rows) for _, rows in coverage_tables}
    cases: list[tuple[str, list[str], list[str]]] = []  # (id, 表頭, 整列)
    for header, rows in plan_tables:
        if id(rows) in coverage_set or header[:1] != ["ID"]:
            continue
        for cells in rows:
            if CASE_LIKE.match(cells[0]) and not REQ_REF.fullmatch(cells[0]):
                cases.append((cells[0], header, cells))
    defined = [case_id for case_id, _, _ in cases]
    prefixes = {case_id.rsplit("-", 1)[0] for case_id in defined}

    # 4. 覆蓋與引用
    covered_cases = expand("\n".join(coverage), prefixes)
    for case_id in defined:
        if case_id not in covered_cases:
            violations[R_COVER].append({"item": case_id, "reason": "這個案例沒有出現在需求覆蓋表"})
    for ref in sorted(expand(plan, prefixes) - set(defined)):
        violations[R_COVER].append({"item": ref, "reason": "計劃裡引用了這個案例 ID,但沒有任何案例定義它"})

    # 1b. 每一列要有案例,或明確不在範疇並寫理由
    excluded = section(plan, re.compile(r"^## .*不在本次範疇\s*$")) or []
    excluded_rows = [cells for _, rows in tables(excluded) for cells in rows]
    case_set = set(defined)
    def reason_given(label: str, ids: list[str]) -> bool:
        """「不在本次範疇」表有一列提到這條需求(或邊界情況),且「為什麼不測」「之後怎麼驗」都有寫。"""
        topic = label.removeprefix("邊界:").strip()
        for row in excluded_rows:
            mentioned = any(i in REQ_REF.findall(row[0]) for i in ids) or (not ids and topic and topic in row[0])
            if mentioned and len(row) >= 3 and row[1] and row[2]:
                return True
        return False

    for req in required:
        cells = row_of.get(req)
        if cells is None or expand(" ".join(cells[1:]), prefixes) & case_set:
            continue
        if any(cell == "不在範疇" for cell in cells[1:]):
            if not reason_given(req, [req]):
                violations[R_REQ].append(
                    {"item": req, "reason": "標了「不在範疇」,但「不在本次範疇」表沒有提到這條需求,或沒寫「為什麼不測」與「之後怎麼驗」"}
                )
        else:
            violations[R_REQ].append({"item": req, "reason": "需求覆蓋表這一列沒有任何有定義的案例 ID,也沒有標「不在範疇」;補案例,或標不在範疇並寫理由"})
    for cells in coverage_rows:
        if not cells[0].startswith("邊界:") or expand(" ".join(cells[1:]), prefixes) & case_set:
            continue
        if "不在範疇" not in cells[1:]:
            violations[R_REQ].append({"item": cells[0], "reason": "這條邊界情況的列沒有任何有定義的案例 ID,也沒有標「不在範疇」"})
        elif not reason_given(cells[0], []):
            violations[R_REQ].append(
                {"item": cells[0], "reason": "標了「不在範疇」,但「不在本次範疇」表沒有提到這條邊界情況,或沒寫「為什麼不測」與「之後怎麼驗」"}
            )

    # 5. 格式、連續與不重複
    for case_id in defined:
        if not CASE_ID.match(case_id):
            violations[R_SEQ].append(
                {"item": case_id, "reason": "案例 ID 要寫成 US<故事序號>-<端點代號>-NN、US<故事序號>-AJ-NN 或 G-NN(NN 是兩位數)"}
            )
    for prefix in sorted(prefixes):
        numbers = [int(case_id.rsplit("-", 1)[1]) for case_id in defined if case_id.rsplit("-", 1)[0] == prefix]
        duplicated = sorted({n for n in numbers if numbers.count(n) > 1})
        missing = sorted(set(range(1, max(numbers) + 1)) - set(numbers))
        if duplicated or missing:
            reason = f"{prefix} 的流水號要從 01 起連續、各一次(功能與非功能案例共用一個序列)"
            if missing:
                reason += f";缺 {[f'{prefix}-{n:02d}' for n in missing]}"
            if duplicated:
                reason += f";重複的有 {[f'{prefix}-{n:02d}' for n in duplicated]}"
            violations[R_SEQ].append({"item": prefix, "reason": reason})

    # 6. 受測操作
    anchors: set[str] = set()
    for header, rows in tables(catalog):
        if "寫法" in header:
            at = header.index("寫法")
            anchors |= {anchor(cells[at]) for cells in rows if len(cells) > at}
    anchors.discard("")
    for case_id, header, cells in cases:
        at = header.index("受測操作") if "受測操作" in header else None
        operation = cells[at] if at is not None and len(cells) > at else ""
        segments = [segment.strip() for segment in operation.split("→")]
        bad = [
            segment
            for index, segment in enumerate(segments)
            if (index == 0 or "›" in segment) and not any(segment.startswith(a) for a in anchors)
        ]
        if not operation or bad:
            violations[R_OPS].append(
                {
                    "item": case_id,
                    "reason": f"受測操作「{operation}」的「{bad[0] if bad else '(空白)'}」不是以受測操作表的任何一種寫法開頭;可用的開頭有 {sorted(anchors)}",
                }
            )

    # 7. 則的編號與要抓的錯;8. 驗證方式
    nfr_cases: dict[str, list[str]] = {}
    for case_id, header, cells in cases:
        if len(cells) != len(header):
            violations[R_THEN].append({"item": case_id, "reason": f"這一列有 {len(cells)} 格,表頭有 {len(header)} 欄"})
            continue
        if "則" not in header or "要抓的錯" not in header:
            violations[R_THEN].append({"item": case_id, "reason": "案例表的表頭沒有「則」或「要抓的錯」欄;照 templates/testplan.md 的表頭寫"})
            continue
        then_text = cells[header.index("則")]
        parts = [part.strip() for part in then_text.split("<br>")]
        numbers = [int(m.group(1)) if (m := re.match(r"^則(\d+):\S", part)) else None for part in parts]
        if numbers != list(range(1, len(parts) + 1)):
            violations[R_THEN].append(
                {"item": case_id, "reason": f"「則」要寫成 則1:… 再以 <br>則2:… 依序接上,每條冒號後都要有內容;收到「{then_text}」"}
            )
        if not cells[header.index("要抓的錯")]:
            violations[R_THEN].append({"item": case_id, "reason": "「要抓的錯」是空白;寫出換成哪一種錯誤實作時這個案例會不過"})
        if "驗證方式" in header:
            kind = cells[header.index("驗證方式")]
            if kind not in VERIFY_KINDS:
                violations[R_VERIFY].append({"item": case_id, "reason": f"驗證方式要是 {sorted(VERIFY_KINDS)} 其中一種,收到「{kind}」"})
            if "需求" in header:
                for ref in REQ_REF.findall(cells[header.index("需求")]):
                    nfr_cases.setdefault(ref, []).append(case_id)

    # 9. NFR
    required_nfrs = [req for req in required if req.startswith("NFR-")]
    for req in required_nfrs:
        cells = row_of.get(req)
        if cells and any(cell == "不在範疇" for cell in cells[1:]) and req not in nfr_cases:
            continue
        if req not in nfr_cases:
            violations[R_NFR].append({"item": req, "reason": "沒有任何有「驗證方式」欄的案例在「需求」欄列出這條 NFR"})

    # 10. 替身與實跑案例
    verify_of = {case_id: cells[header.index("驗證方式")] for case_id, header, cells in cases if "驗證方式" in header and len(cells) == len(header)}
    doubles = 0
    for header, rows in plan_tables:
        if header[:1] != ["端點"] or "替身" not in header:
            continue
        at = header.index("替身")
        for cells in rows:
            cell = cells[at] if len(cells) > at else ""
            if cell in NO_DOUBLE:
                continue
            for entry in [part.strip() for part in cell.split("<br>")]:
                doubles += 1
                item = f"{cells[0]}:{entry}"
                double, arrow, target = (part.strip() for part in entry.partition("→"))
                if not arrow or not double:
                    violations[R_DOUBLE].append(
                        {"item": item, "reason": "替身要寫成「替身(代替的真元件)→ 實跑案例 ID」或「替身(代替的真元件)→ 無法實跑:原因」,多個替身以 <br> 分隔"}
                    )
                    continue
                cannot = CANNOT_RUN.match(target)
                if cannot:
                    if not cannot.group(1):
                        violations[R_DOUBLE].append({"item": item, "reason": "寫了「無法實跑:」但沒有寫原因"})
                    continue
                ids = expand(target, prefixes | {m.rsplit("-", 1)[0] for m in re.findall(rf"\b{ID_TOKEN}-\d+\b", target)})
                real = [case_id for case_id in sorted(ids) if verify_of.get(case_id) in REAL_RUN_KINDS]
                if real:
                    continue
                if not ids:
                    reason = f"→ 後面「{target}」沒有案例 ID;指到接真元件的 📏 案例,或寫「無法實跑:原因」"
                elif not ids & set(defined):
                    reason = f"指到的 {sorted(ids)} 沒有任何案例定義它"
                else:
                    kinds = {case_id: verify_of.get(case_id, "功能案例(🔴🟢)") for case_id in sorted(ids & set(defined))}
                    reason = f"指到的案例驗證方式是 {kinds},不是 📏 量測或 📏 人工;實跑案例要接真元件"
                violations[R_DOUBLE].append({"item": item, "reason": reason})

    # 11. 📏 案例的實跑時機
    timed = 0
    for case_id, header, cells in cases:
        if "驗證方式" not in header or "副作用與護欄" not in header or len(cells) != len(header):
            continue
        if cells[header.index("驗證方式")] not in REAL_RUN_KINDS:
            continue
        timed += 1
        guard = cells[header.index("副作用與護欄")].strip()
        if not TIMING.match(guard):
            violations[R_TIMING].append(
                {"item": case_id, "reason": f"「副作用與護欄」要以「時機:節內」或「時機:整合」開頭,實際是「{guard[:30]}」;不花錢、不改外部狀態、不需本人在場寫節內,否則寫整合"}
            )

    # 12. 測試指令
    command_section = section(plan, re.compile(r"^### 測試指令\s*$"))
    layers: dict[str, str] = {}
    for header, rows in tables(command_section or []):
        if "層" in header and "指令" in header:
            for cells in rows:
                if len(cells) > max(header.index("層"), header.index("指令")):
                    layers[cells[header.index("層")].strip()] = cells[header.index("指令")].strip()
    if command_section is None:
        violations[R_CMDS].append({"item": "### 測試指令", "reason": "找不到「### 測試指令」這一節;照 templates/testplan.md 在第 1 節寫出快速層與全部的指令"})
    else:
        for layer in ("快速層", "全部"):
            command = layers.get(layer, "")
            if not command or command in {"—", "-"} or "{{" in command:
                violations[R_CMDS].append({"item": layer, "reason": f"「測試指令」表沒有「{layer}」這一列,或它的「指令」欄是空的;寫出可以直接執行的指令"})

    # 13. 合約的操作 × 錯誤碼
    rules = RULES + ([R_CONTRACT] if args.contracts else [])
    violations.setdefault(R_CONTRACT, [])
    pair_count = 0
    if args.contracts:
        if not args.contracts.is_dir():
            print(f"錯誤: --contracts 指到的 {args.contracts} 不是資料夾。請給 spec package 底下的 contracts/。", file=sys.stderr)
            return 2
        docs: dict[str, object] = {}
        catalog_rows: list[tuple[str, bool, list[tuple[str, str, set[str]]]]] = []
        for header, rows in tables(catalog):
            if "規格錨點" not in header or "寫法" not in header:
                continue
            at_anchor, at_writing = header.index("規格錨點"), header.index("寫法")
            for cells in rows:
                if len(cells) <= max(at_anchor, at_writing):
                    continue
                ops, missing = contract_ops(cells[at_anchor], args.contracts, docs)
                for item in missing:
                    violations[R_CONTRACT].append({"item": item, "reason": "受測操作表的規格錨點指到的操作在規格檔裡找不到;照規格檔的路徑與 method 或 operationId 寫"})
                if ops:
                    writing = cells[at_writing].strip()
                    placeholder = "<" in writing
                    catalog_rows.append((anchor(writing) if placeholder else writing, placeholder, ops))
        covered: set[tuple[str, str, str]] = set()
        for case_id, header, cells in cases:
            at = header.index("受測操作") if "受測操作" in header else None
            operation = cells[at] if at is not None and len(cells) > at else ""
            targets: list[tuple[str, tuple[str, str, set[str]]]] = []
            for segment in (part.strip() for part in operation.split("→")):
                matches = [row for row in catalog_rows if row[0] and segment.startswith(row[0])]
                if not matches:
                    continue
                longest = max(len(row[0]) for row in matches)
                method = squash(segment.split("›", 1)[1]) if "›" in segment else ""
                for prefix, placeholder, ops in (row for row in matches if len(row[0]) == longest):
                    picked = [op for op in ops if squash(op[1]) == method] if len(ops) > 1 else ops
                    targets += [(method, op) for op in picked]
            if len({op[1] for _, op in targets}) == 1:
                mentioned = set(ERROR_CODE.findall(" | ".join(cells)))
                covered |= {(name, op_id, code) for _, (name, op_id, codes) in targets for code in codes & mentioned}
                continue
            # 一個案例串起好幾個操作時,錯誤碼只算給同一段(<br> 分隔)也寫到那個方法名的操作
            for piece in " | ".join(cells).split("<br>"):
                in_piece = set(ERROR_CODE.findall(piece))
                flat = piece.replace("`", "").replace("_", "").lower()
                for method, (name, op_id, codes) in targets:
                    if method and method in flat:
                        covered |= {(name, op_id, code) for code in codes & in_piece}
        required_pairs = sorted({(name, op_id, code) for _, _, ops in catalog_rows for name, op_id, codes in ops for code in codes})
        pair_count = len(required_pairs)
        for name, op_id, code in required_pairs:
            if (name, op_id, code) in covered:
                continue
            if any(code in row[0] and op_id in row[0] and len(row) >= 3 and row[1] and row[2] for row in excluded_rows):
                continue
            violations[R_CONTRACT].append(
                {
                    "item": f"{name} {op_id} × {code}",
                    "reason": f"沒有案例的受測操作對到 {op_id} 而且寫到 {code};補案例,或在「不在本次範疇」表寫一列同時寫到 `{code}` 與 `{op_id}`,並寫為什麼不測與之後怎麼驗",
                }
            )

    scope_text = "全部故事" if full_scope else "故事 " + "、".join(str(n) for n in sorted(in_scope_stories))
    evidence = {
        R_REQ: f"範疇({scope_text})內的 {len(required)} 條 FR/NFR/SC 都在需求覆蓋表,且各有案例或明確不在範疇",
        R_EDGE: f"spec 的 {edge_count} 條邊界情況,需求覆蓋表各有一列" if full_scope else f"範疇只含{scope_text},不檢查邊界情況條數",
        R_SCOPE: f"需求覆蓋表 {len(row_of)} 條需求的歸屬都對得上 spec,全域需求都在涵蓋彙整",
        R_COVER: f"{len(defined)} 個案例都在需求覆蓋表,引用的案例 ID 都有定義",
        R_SEQ: "、".join(f"{p} 01~{sum(1 for d in defined if d.rsplit('-', 1)[0] == p):02d}" for p in sorted(prefixes)) + " 格式正確、連續且不重複",
        R_OPS: f"{len(cases)} 個案例的受測操作都以受測操作表的寫法開頭",
        R_THEN: f"{len(cases)} 個案例的則都從 則1 起依序編號,要抓的錯都有寫",
        R_VERIFY: f"{sum(1 for _, h, _ in cases if '驗證方式' in h)} 個非功能與全域案例的驗證方式都是三種之一",
        R_NFR: f"範疇內 {len(required_nfrs)} 條 NFR 都有標明驗證方式的案例",
        R_DOUBLE: f"待測端點表的 {doubles} 個替身都指到 📏 實跑案例或寫明無法實跑",
        R_TIMING: f"{timed} 個 📏 案例的副作用與護欄都以實跑時機開頭",
        R_CMDS: f"測試指令表的快速層是 {layers.get('快速層', '')[:60]},全部是 {layers.get('全部', '')[:60]}",
        R_CONTRACT: f"受測操作表指到的合約操作共 {pair_count} 組操作 × 錯誤碼,都有案例或寫明不在範疇",
    }
    checks = [
        {
            "rule": rule,
            "result": "不過" if violations[rule] else "過",
            "evidence": "" if violations[rule] else evidence[rule],
            "violations": violations[rule],
        }
        for rule in rules
    ]
    total = sum(len(violations[rule]) for rule in rules)
    passed = total == 0
    print(f"檢查了 {len(cases)} 個案例、{doubles} 個替身與範疇({scope_text})內 {len(required)} 條需求,{total} 個不符項")
    print(json.dumps({"spec": str(args.spec), "plan": str(args.plan), "passed": passed, "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
