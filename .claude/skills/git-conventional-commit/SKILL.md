---
name: git-conventional-commit
description: 依 Conventional Commits 1.0.0 寫 git commit 訊息,並在提交前把不相關的變更拆成不同的 commit。只要準備執行 git commit、要寫或改寫 commit message、要決定 type 或 scope、要判斷是不是 breaking change、手上有一堆混在一起的 diff 要整理、要 revert / amend / squash,或使用者說「幫我 commit」「提交」「寫 commit 訊息」「切 commit」「commit 一下」,都先讀這支 skill —— 即使使用者完全沒提到 Conventional Commits 也一樣。
---

# Git Conventional Commit(慣例式提交)

> 驗證狀態:**未驗證** —— 尚未經學員在真實專案上連續使用並觀察。已用 skill-creator 的評測機制做過三輪 agent 對照測試(2026-10-05,測試題在 `evals/evals.json`),並依結果修訂過;第三輪的修訂依據是 agent 在一個真實專案上連續做三項功能後自己記下的試用心得。那都是 agent 測 agent,不能取代人的觀察。

Conventional Commits 是一套疊在 commit 訊息上的輕量約定。它要解決的事只有一件:**讓 commit 歷史同時讓人和工具都讀得懂** —— 人看得出每一筆變更的性質,工具可以據此自動產生 CHANGELOG、決定 SemVer 要升哪一位、觸發建置與發布。

所以寫訊息時真正要問的是:「半年後有人(或一支 changelog 工具)只看這一行,能不能知道這筆變更是什麼性質、會不會弄壞他?」

## 訊息結構

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

三段之間各以**一行空行**分隔。這個空行不是美觀問題:規範用它來界定 body 與 footer 從哪裡開始,少了它工具就會解析錯。

## 流程

### 1. 先看現況,不要憑印象寫

```bash
git status
git diff            # 尚未 stage 的
git diff --staged   # 已經 stage 的
git log -n 15 --format='%h %s'
```

`git log` 是為了看這個 repo **已經怎麼做**:description 用什麼語言、有沒有慣用的 scope、有沒有 `commitlint.config.*` 之類的設定檔。規範本身留了很多彈性(type 可自訂、大小寫不限),所以要跟著 repo 既有的慣例走,同一份歷史裡保持一致比任何單一選擇都重要。

repo 是全新的、或既有歷史根本沒有照這套約定(例如滿是 `update`、`wip`、`fix bug`)時,**從這一筆開始照規範寫**,不要跟著舊的寫法走;不必回頭改寫舊歷史。此時用最通行的預設:type 小寫、不用 scope、description 用使用者與你溝通的語言。

### 2. 把不相關的變更拆開 —— 但不要拆過頭

一個 commit 只裝一件邏輯上獨立的事。規範的 FAQ 對「一個 commit 同時符合多個 type」的回答很直接:**回頭把它拆成多個 commit**。

**要拆**:這批變更裡有**性質不同、彼此不需要對方就能成立**的事。典型的組合:新功能 / 無關的 bug 修正 / 順手做的 refactor / 排版調整 / 相依套件升級 / 文件。測試跟著它所驗證的那筆變更走(放進同一個 `feat` 或 `fix`),只有「單純補測試」才獨立成 `test`。

**不要再往下拆**:

- **同一種性質、同一個目的**的幾處修改,是一筆。README 裡修一個錯字、補一段說明、改一句介紹,就是一筆 `docs`,不是三筆。
- **交纏在同一行或同一段**的變更,是一筆。例如同一行同時改了選項名稱與預設值、兩處修改互相依賴才跑得動。這種情況在 description 寫主要的那件事,其餘的寫進 body(有多項破壞性變更就寫多條 `BREAKING CHANGE:` footer)。
- **拆開之後得由你動手寫出一個「中間版本」的檔案內容**,就不要拆。那個版本使用者沒寫過、沒人跑過,把它放進歷史等於提交一段沒驗證過的程式。

判斷的依據是「有幾種性質不同的事」,不是「改了幾個地方」,也不是 description 裡有沒有出現「以及」。拿不準時偏向少拆,並在回報裡說明;使用者想再細分很容易,要把拆錯的歷史合回來比較麻煩。

拆的方法(由粗到細,前一種夠用就不要用下一種):

```bash
# 1. 以檔案為單位 —— 絕大多數情況這樣就夠
git add <這件事涉及的檔案>
git diff --staged          # 確認 stage 的內容就是這一件事

# 2. 同一個檔案裡有兩件不相干的事,而且落在不同的 hunk
git diff <檔案> > /tmp/part.patch      # 匯出後刪掉不屬於這次的 hunk,只留要提交的
git apply --cached /tmp/part.patch
git diff --staged
```

`git add -p` 是互動式指令,在沒有終端機互動的環境(包括 agent)用不了,所以第二種情況用「匯出 patch、刪減、`git apply --cached`」代替。

拆完的每一個 commit 都要能獨立通過建置與測試 —— 否則日後 `git bisect` 或 revert 單一 commit 時會落在壞掉的狀態。

要驗的是**即將提交的那一筆**,不是工作目錄。只要還有東西沒 stage(上面兩種拆法都一樣),工作目錄就比 index 多了後面幾筆的內容;在工作目錄跑建置會通過,不代表這一筆單獨取出時也會通過。提交前把 index 匯出到暫存目錄,在那裡建置:

```bash
rm -rf /tmp/staged && git checkout-index -a --prefix=/tmp/staged/   # 結尾的斜線不能省
(cd /tmp/staged && <這個 repo 的建置指令>)
```

匯出的只有 index 裡的檔案,不會動到工作目錄。在這裡失敗,多半代表這一筆用到了還沒 stage 的東西:把它一起帶進來、調換提交的順序,或承認這兩件事其實分不開。

不要改用 `git stash --keep-index` 清出同樣的狀態:建置產物沒被 gitignore 時,`git stash pop` 會因為未追蹤的檔案已經存在而失敗,變更卡在 stash 裡(2026-10-05 以 git 2.53 實測)。

這支 skill 只管「怎麼切、訊息怎麼寫」。要提交在哪一條 branch,依使用者的指示或 repo 既有的整合方式,不要因為要 commit 就另外開 branch;實際提交在哪裡,寫進回報。

### 3. 選 type

規範只硬性定義兩個,其餘是業界慣用(來自 Angular 慣例與 `@commitlint/config-conventional`),規範允許但不強制:

| type | 用在 | SemVer |
|---|---|---|
| `feat` | 新增一項功能(**規範規定必須用**) | MINOR |
| `fix` | 修正一個 bug(**規範規定必須用**) | PATCH |
| `docs` | 只改文件 | — |
| `style` | 不影響程式意義的變更(空白、排版、分號) | — |
| `refactor` | 既不修 bug 也不加功能的程式碼變更 | — |
| `perf` | 改善效能的程式碼變更 | — |
| `test` | 補上缺少的測試或修正既有測試 | — |
| `build` | 影響建置系統或外部相依的變更 | — |
| `ci` | CI 設定檔與腳本的變更 | — |
| `chore` | 其他不動到 src 與測試的雜務 | — |
| `revert` | 還原先前的 commit | — |

依序問自己:使用者會感覺到新能力嗎?→ `feat`。原本壞掉的行為被修好了嗎?→ `fix`。都不是,再從下面挑最貼切的。不要因為「改動很小」就把功能寫成 `chore`,那會讓它從 changelog 與版號計算中消失。

repo 若有自訂的 type 清單(看 commitlint 設定或既有歷史),以 repo 的為準。

### 4. scope(選用)

放在 type 後面的括號裡,是一個描述「程式碼哪個區塊」的**名詞**:`feat(parser): ...`。沿用 `git log` 裡已經出現過的 scope;repo 沒在用 scope 就不要自己發明。

### 5. description

緊接在 `: `(冒號加一個空格)之後,是這筆變更的簡短摘要。

規範對寫法沒有更多要求;下面是 Angular / commitlint 的慣例,多數 repo 都照這樣做,除非 repo 既有歷史另有習慣:

- 祈使句、現在式(英文用 "add" 而不是 "added" / "adds")
- 開頭不大寫、結尾不加句點
- 整行 header 不超過 100 個字元

### 6. body(選用)

description 下面空一行再開始,格式自由、可以多段。寫**為什麼要改**,以及和先前行為的差別 —— 「改了什麼」diff 自己會說。

### 7. footer(選用)

body 下面空一行。每一條的形式是 `Token: value` 或 `Token #value`:

```
Reviewed-by: Z
Refs: #123
```

token 裡的空白要換成 `-`(例如 `Acked-by`),這樣工具才分得出 footer 與多段 body。唯一的例外是 `BREAKING CHANGE`。

### 8. 破壞性變更必須標示

只要這筆變更會讓**既有的使用方**(呼叫你 API 的程式、依賴 CLI 參數的腳本、讀你設定檔或資料格式的人)不改東西就壞掉,它就是 breaking change,對應 SemVer 的 MAJOR。**任何 type 都可能是 breaking**,不只是 `feat`。

兩種標示法,擇一或並用:

```
feat(api)!: send an email to the customer when a product is shipped
```

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

- `!` 要緊貼在 `:` 之前(有 scope 時放在右括號之後)。
- footer 的 `BREAKING CHANGE` **必須全大寫**,後面接冒號、空格、說明。`BREAKING-CHANGE` 是同義寫法。
- 訊息裡另有要給 git 原生工具讀的 trailer(`Co-Authored-By:`、`Signed-off-by:`)時,用連字號的 `BREAKING-CHANGE:`:中間帶空白的寫法會讓 `git interpret-trailers` 把整個 footer 區塊都當成不是 trailer,連後面那幾行也一起讀不到(2026-10-05 以 git 實測)。
- 只用 `!` 而省略 footer 時,description 本身就要把破壞了什麼說清楚。
- 影響不是一句話講得完的,就兩者並用:`!` 讓人在單行 log 裡一眼看到,footer 寫清楚要怎麼遷移。

漏標比多標嚴重得多:工具會把它當成一般的 MINOR / PATCH 發出去。

### 9. 提交並檢查

多行訊息用 heredoc 或檔案傳入,確保空行原樣保留:

```bash
git commit -F - <<'EOF'
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Refs: #123
EOF
```

提交前後可以用隨附的檢查腳本確認格式(只用 Python 標準函式庫):

```bash
python3 <skill 目錄>/scripts/check_commit_msg.py --file <訊息檔>                  # 提交前檢查草稿
python3 <skill 目錄>/scripts/check_commit_msg.py -C <repo> --rev HEAD            # 檢查剛提交的那一筆
python3 <skill 目錄>/scripts/check_commit_msg.py -C <repo> --range main..HEAD    # 檢查一段歷史
```

`-C <repo>` 指定要檢查的 repo;省略時用目前所在的目錄。

`ERROR` 代表違反規範,要修;`WARN` 代表偏離常見慣例(非規範要求),依 repo 習慣判斷。repo 若已經設定 commitlint,以 commitlint 的結果為準。

## 例外與邊界

| 情境 | 怎麼處理 | 依據 |
|---|---|---|
| 專案還在初期開發 | 照常遵守,當作產品已經發布 —— 總有人(哪怕只是隊友)想知道什麼修了、什麼壞了 | FAQ |
| type 大小寫 | 規範不限,但要一致;實務上一律小寫。`BREAKING CHANGE` 例外,必須大寫 | 規範 15、FAQ |
| 用錯 type(例如該是 `feat` 卻寫 `fix`),**尚未合併或發布** | 用 `git commit --amend` 或 `git rebase -i` 改掉。會改寫歷史 —— 已經 push 到共用分支的 commit,先問過使用者再動 | FAQ |
| 用錯 type,**已經發布** | 視使用的工具與流程而定,沒有統一做法;告知使用者,不要自行改寫已發布的歷史 | FAQ |
| 打錯成規範外的 type(`feet`) | 不是世界末日,只是工具會漏掉這一筆;還沒共用就順手改掉 | FAQ |
| revert | 規範**刻意不定義** revert 行為。建議做法:用 `revert` type,footer 以 `Refs:` 列出被還原的 commit SHA | FAQ |
| 團隊採 squash merge | 不必要求每位貢獻者都遵守;由維護者在合併時寫出符合規範的最終訊息 | FAQ |
| git 自動產生的 merge commit 訊息 | 規範沒有提到。本 skill 的做法(詮釋,非規範):保留 git 預設訊息,不硬套格式;檢查腳本會略過它們 | — |
| `Co-Authored-By:`、`Signed-off-by:` 等 trailer | 本身就是合法的 footer,照常放在最後 | 規範 8–9 |

revert 的範例:

```
revert: let us never again speak of the noodle incident

Refs: 676104e, a215868
```

## 完成後的回報

提交完成後,向使用者回報:

1. 這次變更拆成了幾個 commit、依什麼原則拆(或為什麼只需要一個);提交在哪一條 branch。
2. 每個 commit 的完整 header,以及選這個 type 的理由。
3. 有沒有 breaking change;有的話怎麼標示、影響誰。
4. 檢查腳本(或 commitlint)的結果;有 WARN 而決定保留的,說明原因。

同一段工作裡還用了其他也要求回報的 skill 時,合成一份:同一件事只講一次。

## 延伸閱讀

- `references/specification.md` —— 規範 16 條全文、FAQ 逐題整理、type 定義的出處。對某條規則拿不準、或遇到上表沒涵蓋的情況時再讀。

## 資料來源

- Conventional Commits 1.0.0(規範、範例、FAQ):<https://www.conventionalcommits.org/en/v1.0.0/>
- About(規範的來源與相關工具):<https://www.conventionalcommits.org/en/about/>
- Angular Commit Message Guidelines(type 定義、subject / body 寫法):<https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines>
- `@commitlint/config-conventional`(type 清單、長度與大小寫規則):<https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional>
- Semantic Versioning:<https://semver.org/>
- git trailer 格式:<https://git-scm.com/docs/git-interpret-trailers>

規範原文以 [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) 授權。整理日期:2026-10-05。
