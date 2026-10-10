# Rule 1 [must] - 資源只在用到它的那一步點名
- 資源是目標 skill 的 `rules/`、`templates/` 底下的檔;每個資源的路徑在 SOP 裡只出現一次,寫在第一個用到它的步驟
- 不另立 Read 步驟去讀資源,其他步驟也不再提它
- 為什麼:路徑出現在哪一步,就是告訴執行的人「走到這裡才去讀」;每一步都提,就分不出哪一步才需要載入

## good example
- 路徑**只出現在 Write 那一步**,走到那裡才需要載入
```
## Phase 1: 寫出 SOP
1. Read **目標 skill 已有的 SKILL.md**。
2. Write 依 `rules/SOP-格式規範.md` 把使用者要的流程**寫成目標 skill 的 `# SOP`**。
```

## bad example
- 同一段流程,但**一開始就先讀 Rule File,後面又用「規範」再提一次**,看不出到底哪一步才需要它
```
## Phase 1: 寫出 SOP
1. Read `rules/SOP-格式規範.md`。
2. Read **目標 skill 已有的 SKILL.md**。
3. Write 依規範的每條 Rule,把使用者要的流程**寫成目標 skill 的 `# SOP`**。
```

## good example
- 邊界:Write 和 Think 兩步都用得到同一個 Rule File,但**只在第一個用到的步驟點名**
```
2. Write 依 `rules/RuleFile-格式規範.md` 把使用者要的規則**寫成 Rule File**。
3. Think **逐條對照**;若有不過 → 跳至 Phase 1 Step 2。
```

## bad example
- 邊界:第二個用到的步驟也寫上路徑,看起來比較清楚,但**讀的人會以為這裡要再載入一次**
```
2. Write 依 `rules/RuleFile-格式規範.md` 把使用者要的規則**寫成 Rule File**。
3. Think 依 `rules/RuleFile-格式規範.md` **逐條對照**;若有不過 → 跳至 Phase 1 Step 2。
```

## good example
- 樣板的骨架與範例**兩個路徑都只出現在 Ask 那一步**,走到那裡才需要載入
```
2. Think **設計這次開發的類別組織**。
3. Ask 依骨架 `templates/class-diagram.mmd` 與範例 `templates/class-diagram.example.mmd` 用 Mermaid **提出設計**,問使用者是否可以進入開發。
```

## bad example
- 同一段流程,但**設計那一步也先提了骨架**;同一個路徑出現兩次,看不出哪一步才需要載入
```
2. Think 依骨架 `templates/class-diagram.mmd` **設計這次開發的類別組織**。
3. Ask 依骨架 `templates/class-diagram.mmd` 與範例 `templates/class-diagram.example.mmd` 用 Mermaid **提出設計**,問使用者是否可以進入開發。
```

# Rule 2 [must] - 指標接在動詞後面並照固定寫法
- 指標緊接在步驟開頭的動詞後面,依這一步用到的資源照下面三種寫法之一

```
<M>. <動詞> 依 `rules/<檔名>` <動作描述>
<M>. <動詞> 依骨架 `templates/<樣板名字>.<格式>` 與範例 `templates/<樣板名字>.example.<格式>` <動作描述>
<M>. <動詞> 依 `rules/<檔名>`、骨架 `templates/<樣板名字>.<格式>` 與範例 `templates/<樣板名字>.example.<格式>` <動作描述>
```

- 每個路徑都寫完整,不用「依規範」這類代稱,也不用萬用字元帶過
- 為什麼:執行的人是照步驟裡的路徑去開檔的,路徑不完整或換了說法,他得自己去猜是哪個檔;每一步的寫法都一樣,掃一眼 SOP 才找得到哪幾步要載入東西

## good example
- 指標**緊接在 Think 後面,而且是完整的路徑**
```
2. Think 依 `rules/類別圖-規範.md` **設計這次開發的類別組織**。
```

## bad example
- 同一步,但**指標放在句尾,又只寫了代稱**;執行的人得自己去 `rules/` 找是哪個檔
```
2. Think **設計這次開發的類別組織**,細節見類別圖規範。
```

## good example
- 樣板**骨架與範例兩個路徑都寫出來**,各自標明是哪一個
```
3. Ask 依骨架 `templates/class-diagram.mmd` 與範例 `templates/class-diagram.example.mmd` 用 Mermaid **提出設計**,問使用者是否可以進入開發。
```

## bad example
- 同一步,但**只寫了骨架**;範例明明存在,卻沒有任何一步會去讀它
```
3. Ask 依骨架 `templates/class-diagram.mmd` 用 Mermaid **提出設計**,問使用者是否可以進入開發。
```

## good example
- 邊界:這一步同時用到 Rule File 與樣板,行變長了,但**三個路徑仍然各自寫完整**
```
3. Ask 依 `rules/確認-規範.md`、骨架 `templates/class-diagram.mmd` 與範例 `templates/class-diagram.example.mmd` 用 Mermaid **提出設計**,問使用者是否可以進入開發。
```

## bad example
- 邊界:同一步為了縮短,用萬用字元一次帶過樣板;看起來涵蓋了兩個檔,但**沒有任何一個完整的樣板路徑**,執行的人得自己去列目錄猜
```
3. Ask 依 `rules/確認-規範.md` 與 `templates/class-diagram.*` 用 Mermaid **提出設計**,問使用者是否可以進入開發。
```

# Rule 3 [must] - 委派給腳本的步驟照固定寫法
- 把職責交給目標 skill `scripts/` 底下腳本的步驟,照下面的寫法

```
<M>. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/<腳本名>.py <參數>` <取得什麼或留下什麼>
```

- 指令寫完整:`uv run`、腳本的完整路徑、每一個參數;執行時才知道的值寫成 `<說明>`
- `rules/腳本執行-規範.md` 照〈資源只在用到它的那一步點名〉只寫在第一個執行腳本的步驟,之後的步驟省略「依 `rules/腳本執行-規範.md`」
- 腳本是每次都要執行的,不是載入一次就好的資源,不受〈資源只在用到它的那一步點名〉限制:同一支腳本可以在不同的步驟各執行一次,每一次都寫完整的指令
- 為什麼:執行的人是照步驟裡那一行去跑的;少了 `uv run`,他會改用 `python` 直接跑,腳本檔頭宣告的套件就沒有人裝。每一步的寫法都一樣,掃一眼 SOP 才找得到哪幾步在跑腳本

## good example
- **`uv run`、完整路徑與參數都在**,照抄就能執行
```
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/count_rules.py --skill <目標 skill 路徑>` **取得每個 Rule File 的統計**:Rule 條數與各條的強度。
```

## bad example
- 同一步,但**只點了腳本的路徑**;執行的人得自己決定用什麼跑、猜它要什麼參數
```
2. Delegate 依 `rules/腳本執行-規範.md` 用 `scripts/count_rules.py` **統計每個 Rule File 的 Rule**:條數與各條的強度。
```

## good example
- 邊界:修改前後各要數一次,兩步跑的是同一支腳本,**兩步都寫了完整的指令**
```
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/count_rules.py --skill <目標 skill 路徑>` **取得修改前每個 Rule File 的統計**:Rule 條數與各條的強度。
3. Write **依使用者選的處理改寫 Rule File**。
4. Delegate 執行 `uv run scripts/count_rules.py --skill <目標 skill 路徑>` **取得修改後每個 Rule File 的統計**:Rule 條數與各條的強度。
```

## bad example
- 邊界:同一段流程,第二次比照資源「只點名一次」而省略了指令;看起來比較精簡,但**腳本是要再執行一次的**,執行的人得回頭找第 2 步才知道要跑什麼
```
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/count_rules.py --skill <目標 skill 路徑>` **取得修改前每個 Rule File 的統計**:Rule 條數與各條的強度。
3. Write **依使用者選的處理改寫 Rule File**。
4. Delegate 再執行一次同一支腳本,**取得修改後每個 Rule File 的統計**:Rule 條數與各條的強度。
```
