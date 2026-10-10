# Rule 1 [must] - 跟著 repo 既有的慣例
- description 用什麼語言、有沒有慣用的 scope、type 清單(看 `commitlint.config.*` 之類的設定檔與既有歷史),都照 repo 已經在做的
- repo 是全新的、或既有歷史根本沒有照這套約定時,從這一筆開始照規範寫,不跟著舊的寫法走,也不回頭改寫舊歷史;此時用最通行的預設:type 小寫、不用 scope、description 用使用者與你溝通的語言
- 為什麼:規範留了很多彈性(type 可自訂、大小寫不限),同一份歷史裡保持一致比任何單一選擇都重要;半套照舊、半套照新,人與工具都讀不順

## good example
- 歷史裡 description 是英文、scope 用模組名;**這一筆照著寫**
```
$ git log -n 3 --format='%h %s'
a1b2c3d feat(cli): add list command
9f8e7d6 fix(store): close file after save
4c5d6e7 docs: add usage section

這一筆:feat(cli): add delete command
```

## bad example
- 同一份歷史,但**這一筆改用中文、也不寫 scope**;同一份 log 裡出現兩種寫法
```
這一筆:feat: 新增 delete 指令
```

## good example
- 邊界:歷史完全沒有照約定;**不跟著寫,從這一筆開始用預設**(使用者以繁體中文溝通)
```
$ git log -n 3 --format='%h %s'
a1b2c3d more tests
9f8e7d6 Update readme
4c5d6e7 first commit

這一筆:feat: 新增 count 指令
```

## bad example
- 邊界:同一份歷史,把「跟著 repo 既有的慣例」讀成跟著舊的寫法;**那些訊息不是一種慣例,只是沒有約定**
```
這一筆:add count command
```

# Rule 2 [must] - type 依變更的性質選
- 依序問:使用者會感覺到新能力嗎?→ `feat`。原本壞掉的行為被修好了嗎?→ `fix`。都不是,再從下表挑最貼切的

| type | 用在 | SemVer |
|---|---|---|
| `feat` | 新增一項功能(規範規定必須用) | MINOR |
| `fix` | 修正一個 bug(規範規定必須用) | PATCH |
| `docs` | 只改文件 | — |
| `style` | 不影響程式意義的變更(空白、排版、分號) | — |
| `refactor` | 既不修 bug 也不加功能的程式碼變更 | — |
| `perf` | 改善效能的程式碼變更 | — |
| `test` | 補上缺少的測試或修正既有測試 | — |
| `build` | 影響建置系統或外部相依的變更 | — |
| `ci` | CI 設定檔與腳本的變更 | — |
| `chore` | 其他不動到 src 與測試的雜務 | — |
| `revert` | 還原先前的 commit | — |

- 為什麼:工具靠 type 決定這一筆進不進 changelog、版號升哪一位;type 選錯,這筆變更不是被漏掉,就是被當成另一種性質發出去

## good example
- 新增的 `--json` 旗標只有五行,但**使用者拿到了新能力,是 `feat`**
```
+ parser.add_argument("--json", action="store_true")

feat(cli): add --json flag to list
```

## bad example
- 同一筆變更,因為「改動很小」就寫成 `chore`;**它從 changelog 與版號計算裡消失了**
```
chore(cli): add --json flag to list
```

## good example
- 邊界:把 `load()` 拆成兩個函式,行為沒有變,使用者感覺不到;**依序問下來兩題都不是,從表裡挑 `refactor`**
```
refactor(store): split load into read and parse
```

## bad example
- 邊界:同一筆變更,因為「程式變好了」就寫成 `feat`;**沒有新能力,版號卻會因此升一個 MINOR**
```
feat(store): split load into read and parse
```

# Rule 3 [must] - 這一筆才第一次進 repo 的東西整筆是 `feat`
- 這一筆才第一次進 repo 的東西,連同過程中在它身上發現並修掉的問題,整筆是 `feat`;修了什麼寫進 body
- 為什麼:`fix` 是給使用者已經拿到的壞行為用的;還沒進過 repo 的東西沒有「修正」可言,寫成 `fix` 會在 changelog 裡多出一條使用者從沒遇過的 bug

## good example
- delete 指令這一筆才第一次提交,開發途中修過的索引錯誤**一起算在 `feat`,寫進 body**
```
feat(cli): add delete command

Indexes are 1-based to match what list prints; an earlier draft was
off by one and deleted the wrong item.
```

## bad example
- 同一筆變更,但**因為過程中修過錯就寫成 `fix`**;changelog 會記一條「修正 delete 的索引」,而 delete 在這之前根本不存在
```
fix(cli): correct delete index
```

# Rule 4 [should] - 內容就是產品的 repo 自訂 type
- 內容就是產品的 repo(部落格、文件站)發一篇文章時,定一個自訂的 type(例如 `post`),然後從頭用到尾
- 訊息檢查會對自訂的 type 給 warning,那是預期的
- 為什麼:`docs` 是講這個專案本身的文件,`feat` 是程式的新能力,兩個都不貼近「發一篇文章」;硬套其中一個,文章與真正的文件修改、功能就分不開了

## good example
- 部落格 repo 發文章,**用自訂的 `post`**,和改 README 的 `docs` 分得開
```
post: 用 ZFS 快照做五層備份
docs: 更新 README 的本機預覽步驟
```

## bad example
- 同樣兩筆,但**文章也寫成 `docs`**;只看 log 分不出哪一筆是文章、哪一筆是專案文件
```
docs: 用 ZFS 快照做五層備份
docs: 更新 README 的本機預覽步驟
```

## good example
- 邊界:repo 的歷史已經一路用 `feat` 發文章;**有正當理由不自訂,照〈跟著 repo 既有的慣例〉繼續用 `feat`**
```
$ git log -n 2 --format='%s'
feat: 新增文章〈家用 DNS 雙軌〉
feat: 新增文章〈Unraid 升級筆記〉

這一筆:feat: 新增文章〈用 ZFS 快照做五層備份〉
```

## bad example
- 邊界:同一份歷史,這一筆開始改用 `post`;**type 本身選得沒錯,但同一類變更在歷史裡變成兩種 type**
```
這一筆:post: 用 ZFS 快照做五層備份
```

# Rule 5 [should] - scope 沿用 repo 已經出現過的
- scope 是描述「程式碼哪個區塊」的名詞,沿用 `git log` 裡已經出現過的;repo 沒在用 scope 就不要自己發明
- 為什麼:scope 是拿來篩選歷史的,同一個區塊有兩種寫法就篩不齊

## good example
- 歷史裡這個區塊叫 `store`,**這一筆也用 `store`**
```
$ git log --format='%s' | grep -o '^[a-z]*([a-z-]*)' | sort -u
feat(cli)
fix(store)

這一筆:fix(store): return empty list when the data file is empty
```

## bad example
- 同一筆變更,但**另外取了 `storage`**;之後用 `store` 篩歷史會漏掉它
```
這一筆:fix(storage): return empty list when the data file is empty
```

## good example
- 邊界:這一筆動的是歷史裡沒出現過的新區塊 `export`;**沒有可以沿用的,有正當理由新增一個名詞當 scope**
```
這一筆:feat(export): add csv export
```

## bad example
- 邊界:repo 的歷史完全沒有用 scope,這一筆卻開始加;**一筆有、其餘都沒有,篩不出任何東西**
```
$ git log -n 2 --format='%s'
feat: add list command
fix: close file after save

這一筆:feat(cli): add delete command
```

# Rule 6 [should] - description 照 Angular 的寫法
- 祈使句、現在式(英文用 "add" 而不是 "added" / "adds");開頭不大寫、結尾不加句點;整行 header 不超過 100 個字元
- 為什麼:規範對 description 的寫法沒有要求,這是 Angular / commitlint 的慣例,多數 repo 與 lint 設定都照這樣檢查

## good example
- **祈使句、小寫開頭、沒有句點**
```
fix(store): return empty list when the data file is empty
```

## bad example
- 同一筆變更,但**過去式、大寫開頭、有句點**
```
fix(store): Returned empty list when the data file is empty.
```

## good example
- 邊界:repo 的歷史一向大寫開頭;**有正當理由不照 Angular,照〈跟著 repo 既有的慣例〉**
```
$ git log -n 2 --format='%s'
feat: Add list command
fix: Close file after save

這一筆:fix: Return empty list when the data file is empty
```

## bad example
- 邊界:同一份歷史,這一筆照 Angular 小寫開頭;**寫法本身沒有錯,但和歷史不一致**
```
這一筆:fix: return empty list when the data file is empty
```

# Rule 7 [should] - body 寫為什麼要改
- body 寫為什麼要改,以及和先前行為的差別;「改了什麼」diff 自己會說
- 為什麼:半年後讀這一筆的人看得到 diff,看不到當時的理由;body 只把 diff 再唸一遍,等於沒寫

## good example
- body 寫的是**原本哪裡壞、現在行為變成什麼**
```
fix(store): return empty list when the data file is empty

load() crashed with JSONDecodeError on a zero-byte file, which is what
a fresh install creates. An empty file now means an empty list.
```

## bad example
- 同一筆變更,但 **body 只是把 diff 翻成句子**
```
fix(store): return empty list when the data file is empty

Read the file into a variable, check if it is blank, and call
json.loads only when it is not.
```

## good example
- 邊界:修一個錯字,**description 已經講完,有正當理由不寫 body**
```
docs: correct spelling of CHANGELOG
```

## bad example
- 邊界:同一筆變更,為了「每一筆都有 body」硬補一段;**沒有理由可以寫,只好重複 description**
```
docs: correct spelling of CHANGELOG

This commit corrects the spelling of CHANGELOG.
```

# Rule 8 [must] - 破壞性變更必須標示
- 只要這筆變更會讓既有的使用方(呼叫你 API 的程式、依賴 CLI 參數的腳本、讀你設定檔或資料格式的人)不改東西就壞掉,它就是 breaking change;任何 type 都可能是,不只是 `feat`
- 標示法是 header 的 `!`(緊貼在 `:` 之前,有 scope 時放在右括號之後)或 footer 的 `BREAKING CHANGE: <說明>`,擇一或並用
- 使用者沒有提到這是破壞性變更,也要主動判斷並標示
- 為什麼:漏標比多標嚴重得多,工具會把它當成一般的 MINOR / PATCH 發出去,使用方升級之後才發現壞掉

## good example
- 使用者只說「資料檔位置那個改好了」;diff 把 `--file` 改名了,**既有的腳本會壞,主動標 `!`**
```
- parser.add_argument("--file", default="todo.json")
+ parser.add_argument("--data-file", default=default_data_path())

feat(cli)!: rename --file to --data-file
```

## bad example
- 同一個 diff,但**使用者沒提就沒有標**;工具把它當成 MINOR 發出去
```
feat(cli): rename --file to --data-file
```

## good example
- 邊界:type 是 `refactor`,但對外的函式 `save()` 的參數順序換了;**呼叫它的程式不改就壞,`refactor` 一樣要標**
```
refactor(store)!: put path first in save
```

## bad example
- 邊界:同一筆變更,認為「`refactor` 不會改行為」就沒有標;**對內是重構,對呼叫方是破壞**
```
refactor(store): put path first in save
```

## good example
- 邊界:新增一個有預設值的選用參數,**既有的呼叫方不改也照樣能跑,不是 breaking,不標**
```
+ def save(path, items, indent=2):

feat(store): add indent option to save
```

## bad example
- 邊界:同一筆變更,因為「動到了公開函式的簽名」就標了 `!`;**沒有任何使用方會壞,版號卻因此升 MAJOR**
```
feat(store)!: add indent option to save
```

# Rule 9 [must] - 影響一句話講不完就 `!` 與 footer 並用
- 只用 `!` 而省略 footer 時,description 本身就要把破壞了什麼說清楚
- 影響不是一句話講得完的(不只一項破壞、或使用方需要知道怎麼遷移),就兩者並用:`!` 讓人在單行 log 裡一眼看到,footer 寫清楚要怎麼遷移;有多項破壞性變更就寫多條 footer
- 為什麼:使用方是照這段文字決定要改什麼的;只看到一個 `!`,知道會壞,卻不知道壞在哪、怎麼修

## good example
- 改名加上預設位置搬家,**兩項破壞各一條 footer,並寫出怎麼遷移**
```
feat(cli)!: rename --file to --data-file

BREAKING-CHANGE: `--file` is now `--data-file`; update scripts that pass it.
BREAKING-CHANGE: the default data file moved from ./todo.json to the user data directory; move the old file there or pass --data-file ./todo.json.
```

## bad example
- 同一筆變更,但**只有 `!`**;description 只講了改名,預設位置搬家與遷移方式都沒有人知道
```
feat(cli)!: rename --file to --data-file
```

## good example
- 邊界:只有一項破壞,**description 一句話就講完了、也沒有遷移步驟可寫**,只用 `!`
```
feat!: drop support for Python 3.8
```

## bad example
- 邊界:同樣只用 `!`,但 description 沒說破壞了什麼;**看得出是 breaking,看不出哪裡會壞**
```
feat!: update runtime requirements
```

# Rule 10 [must] - 訊息裡有 git trailer 時用 `BREAKING-CHANGE:`
- 訊息裡另有要給 git 原生工具讀的 trailer(`Co-Authored-By:`、`Signed-off-by:`)時,破壞性變更的 footer 寫成連字號的 `BREAKING-CHANGE:`;trailer 照常放在最後
- 為什麼:帶空白的 `BREAKING CHANGE:` 不是合法的 git trailer;區塊裡沒有 `Signed-off-by:` 時,`git interpret-trailers` 會把整個區塊都當成不是 trailer,連 `Co-Authored-By:` 也讀不到(2026-10-09 以 git 2.43 實測)

## good example
- 有 `Co-Authored-By:`,**用連字號的寫法**;兩行都被讀成 trailer
```
feat(cli)!: rename --file to --data-file

BREAKING-CHANGE: `--file` is now `--data-file`; update scripts that pass it.
Co-Authored-By: A <a@example.com>

$ git interpret-trailers --parse < <訊息檔>
BREAKING-CHANGE: `--file` is now `--data-file`; update scripts that pass it.
Co-Authored-By: A <a@example.com>
```

## bad example
- 同一份訊息,但**用帶空白的寫法**;`git interpret-trailers` 一行都讀不到,共同作者也跟著不見
```
feat(cli)!: rename --file to --data-file

BREAKING CHANGE: `--file` is now `--data-file`; update scripts that pass it.
Co-Authored-By: A <a@example.com>

$ git interpret-trailers --parse < <訊息檔>
(沒有輸出)
```

# Rule 11 [must] - revert 用 `revert` type 並以 `Refs:` 引用 SHA
- 還原先前的 commit 時 type 用 `revert`,footer 以 `Refs:` 列出被還原的 commit SHA;為什麼要還原寫進 body
- 為什麼:規範刻意不定義 revert 的行為,工具只能靠 type 與 footer 找出這一筆還原了誰;少了 SHA,就得逐筆比對 diff

## good example
- **`revert` type、body 寫原因、`Refs:` 引用 SHA**
```
revert: remove colored output

Colors render as garbage in the Windows terminal. Back it out until
it can be redone with proper detection.

Refs: 3e89e76
```

## bad example
- 同一次還原,但**沿用 git 預設的訊息**;沒有 type,工具會漏掉這一筆
```
Revert "feat: add colored output"

This reverts commit 3e89e76a1f0c.
```

# Rule 12 [must] - git 自動產生的 merge 訊息保留原樣
- git 自動產生的 merge commit 訊息保留 git 預設的寫法,不硬套 `<type>: <description>`
- 為什麼:規範沒有提到 merge commit;工具是靠 `Merge branch …` 這個開頭認出它並略過的,改寫之後它會被當成一筆一般的變更算進 changelog

## good example
- 合併時**保留 git 產生的訊息**;訊息檢查會回報 `skipped`
```
Merge branch 'feat/delete-command' into main
```

## bad example
- 同一次合併,但**改寫成慣例式的格式**;changelog 裡多了一筆其實沒有內容的 `chore`
```
chore: merge feat/delete-command into main
```
