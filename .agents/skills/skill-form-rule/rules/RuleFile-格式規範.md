# Rule 1 [must] - Rule File 只由 Rule 組成
- 檔案裡每個 `#` 標題都是一條 Rule,沒有其他種類的 section
- 表格、片段的格式定義也寫成一條 Rule,內容放進它的 desc;整份生成內容的樣板不放進 Rule File,放 `templates/`
- 為什麼:逐條對照只會走過 Rule,放在 Rule 以外的內容不會被檢查,也沒有 example 示範

## good example
- **動詞表自己就是一條 Rule**,表格放在 desc;整個檔案只有 Rule 一種東西,逐條對照時不會漏掉它
```markdown
# Rule 1 [must] - 步驟以動詞表的動詞開頭
- 每一步的第一個詞必須是下表的動詞之一

| 動詞 | 意思 |
|---|---|
| Read | 讀檔、讀指令輸出 |
| Ask | 問使用者並等回答 |

## good example
...
## bad example
...

# Rule 2 [must] - 一步只做一件事
...
```

## bad example
- 同一份內容,但**動詞表被放在 Rule 以外的 section**;它沒有 example,逐條對照時也不會被當成規則檢查
```markdown
# 動詞表

| 動詞 | 意思 |
|---|---|
| Read | 讀檔、讀指令輸出 |
| Ask | 問使用者並等回答 |

# Rule 1 [must] - 步驟以動詞開頭
- 每一步的第一個詞必須是〈動詞表〉的動詞之一

## good example
...
## bad example
...

# Rule 2 [must] - 一步只做一件事
...
```

# Rule 2 [must] - 每條 Rule 照固定格式寫
- 依序是標題、desc、`## good example`、`## bad example`,四段都必填
- 標題裡的流水號後面標明這條 Rule 的強度
- example 可以重複多組,每一組都是 good 在前、bad 緊接在後
- 格式如下

```markdown
# Rule <流水號> [<must 或 should>] - <Rule 名稱>
- <desc:這條規則要求什麼;可以用 md table 呈現資料,也可以用 code section 呈現格式定義>
- ...
- 為什麼:<這條規則在防什麼>

## good example
- <說明這份案例資料為什麼是 good example,強調重點>
<用具體案例資料完整展示一個好示範如何遵守此規則;可以是 code section 花大篇幅描述 1..* 筆資料,也可以是條列的情境描述,或兩者混合>

## bad example
- <說明這份案例資料為什麼是 bad example,強調重點>
<用具體案例資料完整展示一個壞示範如何違反此規則;形式同上>
```

- 為什麼:每條 Rule 長得一樣,讀的人才知道去哪裡找要求、去哪裡找示範

## good example
- **四段都在、順序正確**,兩個 example 都先用一行說明重點,再給案例資料
````markdown
# Rule 2 [must] - 一步只做一件事
- 要兩個動詞才講得完,就拆成兩步
- 為什麼:開頭的動詞只有一個,第二件事會被它蓋住

## good example
- **設計與提問拆成兩步**,只看動詞就知道流程在第 3 步暫停
```
2. Think 設計這次開發的類別組織。
3. Ask 問使用者是否可以進入開發。
```

## bad example
- 同一段流程,但**兩件事塞在同一行**,看動詞看不出流程會暫停
```
2. Think 設計類別組織並詢問使用者是否可以進入開發。
```
````

## bad example
- 同一條 Rule,但 **good example 只貼資料、沒有說明重點**,而且**少了 bad example**,讀的人不知道界線在哪
````markdown
# Rule 2 [must] - 一步只做一件事
- 要兩個動詞才講得完,就拆成兩步
- 為什麼:開頭的動詞只有一個,第二件事會被它蓋住

## good example
```
2. Think 設計這次開發的類別組織。
3. Ask 問使用者是否可以進入開發。
```
````

# Rule 3 [must] - 一條 Rule 只管一件事
- desc 的多個 bullet 都在補充同一件事
- 兩個 bullet 若可以「一個遵守、一個違反」,就拆成兩條 Rule
- 為什麼:一條 Rule 裝了兩件事,example 就得同時示範兩個差異,對照時也說不清是哪一點沒過

## good example
- **一條 Rule 一件事**:第一條的兩個 bullet 都在講「用哪個動詞開頭」,「一步做幾件事」另立一條(為了聚焦,各條的為什麼與 example 省略)
```markdown
# Rule 1 [must] - 步驟以動詞表的動詞開頭
- 每一步的第一個詞必須是動詞表的動詞之一
- 動詞照表上的寫法寫,不翻成中文

# Rule 2 [must] - 一步只做一件事
- 要兩個動詞才講得完,就拆成兩步
```

## bad example
- 同樣的內容全收在一條;**三個 bullet 可以各自被違反**,一組 example 得同時示範三件事,對照時也說不清是哪一點沒過
```markdown
# Rule 1 [must] - 步驟的寫法
- 每一步的第一個詞必須是動詞表的動詞之一
- 要兩個動詞才講得完,就拆成兩步
- 分支只寫在行尾
```

## good example
- 邊界:有兩個 bullet,但**違反其中一個就必然違反另一個**(用了巢狀清單,分支就不在行尾),所以仍然是一件事
```markdown
# Rule 7 [must] - 分支與回頭只寫在行尾
- 寫法固定為 `;若 <條件> → 跳至 Phase N Step M。`
- 不用巢狀清單表達分支
```

## bad example
- 邊界:兩個 bullet 看起來都在講「步驟要短」,但**一行裡可以塞兩件事,一件事也可以寫成好幾行**,兩者可以各自被違反,要拆成兩條
```markdown
# Rule 5 [must] - 步驟要短
- 每一步只有一行
- 要兩個動詞才講得完,就拆成兩步
```

# Rule 4 [must] - desc 寫出為什麼
- `- 為什麼:` 寫的是這條規則在防什麼後果,不是把要求換一句話再講一次
- 為什麼:example 涵蓋不到的情況,要靠理由判斷,而不是照字面套

## good example
- 邊界:寫出**少了這條規則會發生什麼事**;遇到沒看過的情況,可以拿「第二件事會不會被蓋住」來判斷
```markdown
# Rule 2 [must] - 一步只做一件事
- 要兩個動詞才講得完,就拆成兩步
- 為什麼:開頭的動詞只有一個,第二件事會被它蓋住
```

## bad example
- 邊界:同一條 Rule,`為什麼` 有寫、讀起來也通順,但**只是把要求倒過來說**,遇到沒看過的情況幫不上忙
```markdown
# Rule 2 [must] - 一步只做一件事
- 要兩個動詞才講得完,就拆成兩步
- 為什麼:因為一步裡不應該有兩件事
```

# Rule 5 [must] - good 與 bad example 用同一個案例
- bad example 是 good example 那個案例寫錯的版本
- 兩邊只差在這條 Rule 管的那一點
- 為什麼:兩個案例若有好幾處不同,讀的人分不出哪一處才是這條 Rule 在管的

## good example
- bad example 沿用**同一段流程**,只把兩步併成一行,差異一眼看得出來
````markdown
## good example
- 設計與提問拆成兩步
```
2. Think 設計這次開發的類別組織。
3. Ask 問使用者是否可以進入開發。
```

## bad example
- 同一段流程,但兩件事塞在同一行
```
2. Think 設計類別組織並詢問使用者是否可以進入開發。
```
````

## bad example
- 同一個 good example,但 bad example **換成另一段不相干的流程**,讀的人得自己比對才找得到差異在哪
````markdown
## good example
- 設計與提問拆成兩步
```
2. Think 設計這次開發的類別組織。
3. Ask 問使用者是否可以進入開發。
```

## bad example
- 讀檔與寫報告塞在同一行
```
1. Read 設定檔並把結果寫進報告。
```
````

# Rule 6 [should] - 需要判斷的 Rule 附邊界案例
- 只看形式分不出過不過的 Rule,至少有一組 example 是邊界案例:good 剛好在界線內,bad 剛好在界線外
- 邊界案例的說明以 `邊界:` 開頭,並講清楚它為什麼落在這一邊
- 為什麼:會寫錯的多半是模稜兩可的情況,一眼看得出對錯的案例教不了界線在哪

## good example
- 邊界:這條 Rule 看起來只要數動詞,但「同一個動詞讀兩個東西」算幾件事要靠判斷,所以**在明顯的那一組之後,再補一組貼著界線的**
````markdown
# Rule 5 [must] - 一步只做一件事
- 要兩個動詞才講得完,就拆成兩步
- 為什麼:開頭的動詞只有一個,第二件事會被它蓋住

## good example
- 設計與提問拆成兩步
```
2. Think 設計這次開發的類別組織。
3. Ask 問使用者是否可以進入開發。
```

## bad example
- 同一段流程,但兩件事塞在同一行
```
2. Think 設計類別組織並詢問使用者是否可以進入開發。
```

## good example
- 邊界:同一個動詞作用在兩個對象,仍然是一件事
```
1. Read 這次開發會動到的現有程式碼與測試。
```

## bad example
- 邊界:只多了半句,但「挑出」是判斷,已經是第二件事
```
1. Read 這次開發會動到的現有程式碼,挑出要改的類別。
```
````

## bad example
- 邊界:同一條 Rule,example 成對、格式也都對,但**只有一眼看得出對錯的那一組**;遇到「Read A 與 B」這種情況,讀的人還是不知道算不算違反
````markdown
# Rule 5 [must] - 一步只做一件事
- 要兩個動詞才講得完,就拆成兩步
- 為什麼:開頭的動詞只有一個,第二件事會被它蓋住

## good example
- 設計與提問拆成兩步
```
2. Think 設計這次開發的類別組織。
3. Ask 問使用者是否可以進入開發。
```

## bad example
- 同一段流程,但兩件事塞在同一行
```
2. Think 設計類別組織並詢問使用者是否可以進入開發。
```
````

# Rule 7 [must] - 用名稱引用 Rule
- 從 SOP 步驟或別條 Rule 指向某條 Rule 時,寫成〈Rule 名稱〉,不寫流水號
- 為什麼:流水號在插入或刪除 Rule 時會位移,名稱不會

## good example
- **指向名稱**,之後在前面插入新的 Rule 也不會指錯
```markdown
# Rule 2 [must] - 一步只做一件事
- 要兩個〈步驟以動詞表的動詞開頭〉裡的動詞才講得完,就拆成兩步
```

## bad example
- 同一句,但**指向流水號**;之後在前面插入一條 Rule,〈Rule 1〉就指到別條去了
```markdown
# Rule 2 [must] - 一步只做一件事
- 要兩個〈Rule 1〉裡的動詞才講得完,就拆成兩步
```

# Rule 8 [must] - 強度依有沒有正當例外來決定
- 強度只有兩種,依下表決定

| 強度 | 什麼時候用 | 對照時沒做到 |
|---|---|---|
| must | 想不到正當理由不照做 | 回頭改,不能放行 |
| should | 特定情況下有正當理由不照做 | 可以放行,但要向使用者說明理由 |

- 許可(可以怎麼做)不是強度,不另立一條 Rule,寫成相關 Rule 的 desc 裡的一句話
- 為什麼:每條 Rule 看起來一樣重的時候,agent 不是全部硬套,就是自己挑著違反

## good example
- 邊界:「載入規則」這類 Phase 做完沒有可以檢查的產出,卻是流程需要的,**有正當理由不照做,所以標 should**
```markdown
# Rule 2 [should] - Phase 依產出分組
- 一組動作做完留下一個可以檢查的產出,一組就是一個 Phase
```

## bad example
- 邊界:同一條 Rule 標成 must,看起來更嚴謹,但**遇到載入類的 Phase 就永遠過不了**,只能硬湊一個產出,或假裝沒看到
```markdown
# Rule 2 [must] - Phase 依產出分組
- 一組動作做完留下一個可以檢查的產出,一組就是一個 Phase
```

# Rule 9 [must] - 一個 Rule File 只規範一種產出物
- 檔案裡每條 Rule 都在規範同一種產出物,檔名以那個產出物開頭
- 為什麼:SOP 的步驟是照「現在要寫什麼」去載入 Rule File 的,混了兩種產出物,每次都會多讀用不到的那一半

## good example
- **一種產出物一個檔**,寫 SOP 的步驟只需要載入第一個
```
rules/
├── SOP-格式規範.md         ← 都在規範 SOP
└── RuleFile-格式規範.md    ← 都在規範 Rule File
```

## bad example
- 同樣的 Rule,但**兩種產出物收在同一個檔**,只是要寫 SOP,也得把 Rule File 的規範一起讀進來
```
rules/
└── 格式規範.md             ← SOP 與 Rule File 的 Rule 混在一起
```

# Rule 10 [should] - 步驟用不到的 Rule 拆到別的檔
- SOP 裡若有步驟只用得到檔案中的一部分 Rule,就沿著步驟把檔案拆開,讓每個步驟只載入它用得到的
- 每個會載入這個檔的步驟都用得到全部的 Rule,就不拆,不論檔案多長
- 為什麼:Rule File 是按需載入的,拆檔唯一的好處是少讀;沒有任何步驟能因此少讀,就只是多一個檔

## good example
- revert 的 Rule 只有「這次是 revert」那一步用得到,**拆出去之後,平常的 commit 不必讀它**
```
rules/
├── commit-格式規範.md         ← 每次 commit 都讀
└── commit-revert-格式規範.md  ← 只有走到 revert 那一步才讀
```

## bad example
- 同樣的 Rule,但 **revert 的那幾條留在同一個檔**,每次 commit 都要把用不到的一起讀進來
```
rules/
└── commit-格式規範.md         ← 含 revert 的 Rule,每次 commit 都讀
```

## good example
- 邊界:檔案有兩百多行,但**只有一個 Write 步驟會讀它,而且每一條都用得到**,所以不拆
```
rules/
└── SOP-格式規範.md            ← 10 條,同一個步驟全部用得到
```

## bad example
- 邊界:同一份內容因為「太長」而依主題拆成兩個檔,但**同一個步驟兩個都要讀**,沒有少讀任何東西
```
rules/
├── SOP-Phase-格式規範.md      ← 同一個步驟要讀
└── SOP-步驟-格式規範.md       ← 同一個步驟也要讀
```
