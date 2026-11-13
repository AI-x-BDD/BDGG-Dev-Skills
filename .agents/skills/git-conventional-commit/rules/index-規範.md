# Rule 1 [must] - stage 的方法由粗到細選
- 依下表由上往下選,前一種夠用就不用下一種

| 這一筆的變更 | 方法 |
|---|---|
| 佔了整個檔案 | `git add <這件事涉及的檔案>` |
| 和另一筆的變更在同一個檔案裡 | `git diff <檔案> > <patch 檔>`,刪掉 patch 裡不屬於這一筆的 hunk 與行,再 `git apply --cached --recount <patch 檔>` |

- 為什麼:以檔案為單位不會切錯;動手改 patch 每多一次,就多一次把別筆的行帶進來、或把這一筆的行漏掉的機會

## good example
- delete 指令的三個檔**整個都屬於這一筆,用 `git add` 就夠**
```
$ git add todo/cli.py todo/store.py tests/test_delete.py
```

## bad example
- 同樣三個檔,但**每個檔都匯出 patch 再套回去**;多做的三次編輯沒有切出任何東西
```
$ git diff todo/cli.py > /tmp/cli.patch
$ git apply --cached --recount /tmp/cli.patch
$ git diff todo/store.py > /tmp/store.patch
$ git apply --cached --recount /tmp/store.patch
```

## good example
- 邊界:`todo/store.py` 同時有 fix 與 feat 的變更;**這個檔用 patch,其餘整個屬於這一筆的檔仍然用 `git add`**
```
$ git diff todo/store.py > /tmp/store.patch     # 刪掉 clear 指令的那個 hunk
$ git apply --cached --recount /tmp/store.patch
$ git add tests/test_load_empty.py
```

## bad example
- 邊界:同一個情況,因為「用 patch 太麻煩」就把整個 `store.py` 加進來;**feat 的 hunk 跟著進了 fix 那一筆**
```
$ git add todo/store.py tests/test_load_empty.py
```

# Rule 2 [must] - 不用互動式指令
- 不用 `git add -p`、`git add -i` 這類要在終端機逐項回答的指令
- 為什麼:agent 的 shell 沒有人可以回答,指令會停在第一個提問直到逾時

## good example
- 要切 hunk,**用匯出 patch、刪減、`git apply --cached --recount`**,全程不需要回答任何提問
```
$ git diff todo/store.py > /tmp/store.patch
$ git apply --cached --recount /tmp/store.patch
```

## bad example
- 同一件事,但**用 `git add -p`**;它印出第一個 hunk 之後等人輸入 y 或 n,這一步卡住
```
$ git add -p todo/store.py
Stage this hunk [y,n,q,a,d,s,e,?]?
```

# Rule 3 [must] - stage 完確認內容就是這一筆
- stage 完用 `git diff --staged` 讀過一遍,確認 index 裡的內容就是這一筆、沒有多也沒有少
- 為什麼:提交的是 index 不是計畫;改 patch 時多留或多刪一行,只有讀回來才看得到

## good example
- 套完 patch **讀回 `git diff --staged`**,看到的只有空檔案的修正
```
$ git apply --cached --recount /tmp/store.patch
$ git diff --staged --stat
 todo/store.py | 3 ++-
```

## bad example
- 同一個 patch,但**套完就直接往下做**;patch 裡沒刪乾淨的 `clear` 跟著進了這一筆,沒有人看到
```
$ git apply --cached --recount /tmp/store.patch
$ git commit -F <訊息檔>
```

# Rule 4 [must] - 判定這一筆有沒有被建置或測試讀到
- stage 完,判定這一筆 stage 的檔有沒有被建置或測試讀到;都沒有被讀到就跳過 Step 4,有被讀到就依下面決定 Step 4 的 `--cmd`
- 原始碼、測試、建置與相依設定本身,一律算被讀到
- 其他檔,在測試碼與建置設定裡搜它的路徑、檔名、所在目錄與副檔名的 glob;搜到任何一種就算被讀到
- 有測試會掃描全部追蹤的檔(例如 `git ls-files`、遍歷整個 repo)時,任何檔都算被它讀到
- 讀到的只有非程式的檔(原始碼、測試、建置與相依設定以外的檔)時,`--cmd` 只跑讀到它們的那幾支測試;這一筆有原始碼、測試或建置設定時,`--cmd` 照 repo 的建置與測試指令
- 為什麼:判定成沒讀到就會跳過驗證;只 grep 檔名,會漏掉用 `git ls-files` 掃全部的測試與用目錄組路徑的測試,這一筆壞了也沒有人跑到。反過來不判定就一律驗證,只改 markdown 的一筆也要等全部無關的測試跑完(曾經等了 22 分鐘);挑測試時憑「看起來相關」而不是搜到的證據,會挑到比全部更不相干的測試(曾經挑了 98 個讀的是別份原型的 Playwright)

## good example
- staged 的只有 `specs/003/spec.md`,搜到讀它的只有 `tests/test_spec_links.py`(glob `specs/*/spec.md`);**`--cmd` 只跑這一支**
```
staged   specs/003/spec.md
$ grep -rnE "spec\.md|specs/" tests/ pyproject.toml
tests/test_spec_links.py:6:    for path in ROOT.glob("specs/*/spec.md"):
tests/e2e/conftest.py:4:    PROTOTYPE = ROOT / "specs" / "002" / "prototype"
判定     test_spec_links 讀到(e2e 讀的是 002 的原型,沒有讀到這個檔) → 往 Step 4 走

$ uv run .claude/skills/git-conventional-commit/scripts/verify_staged.py --repo . --link .venv --cmd "uv run pytest tests/test_spec_links.py"
```

## bad example
- 同一筆,但**挑了「也讀 specs」的 `tests/e2e/`**;那些測試讀的是 `specs/002/prototype/`,沒有一支讀到這次改的 spec.md,讀到它的 `test_spec_links.py` 反而沒跑
```
staged   specs/003/spec.md
判定     tests/e2e 也讀 specs → 往 Step 4 走

$ uv run .claude/skills/git-conventional-commit/scripts/verify_staged.py --repo . --link .venv --cmd "uv run pytest tests/e2e"
```

## good example
- 邊界:staged 的只有 `docs/設計筆記.md`,檔名、目錄、glob 都搜不到;但**另外搜到 `tests/test_hygiene.py` 用 `git ls-files` 檢查所有追蹤的檔**,所以仍然算讀到,`--cmd` 只跑它
```
staged   docs/設計筆記.md
$ grep -rnE "設計筆記|docs/|\*\.md" tests/ pyproject.toml
(沒有結果)
$ grep -rnE "ls-files|os\.walk|rglob" tests/
tests/test_hygiene.py:8:    tracked = subprocess.run(["git", "ls-files"], ...)
判定     test_hygiene 掃描全部追蹤的檔 → 被讀到,往 Step 4 走

$ uv run .claude/skills/git-conventional-commit/scripts/verify_staged.py --repo . --link .venv --cmd "uv run pytest tests/test_hygiene.py"
```

## bad example
- 邊界:同一筆,**只搜了檔名、目錄與 glob 就判成沒讀到**;`test_hygiene.py` 會檢查這個新檔,卻沒有人跑它
```
staged   docs/設計筆記.md
$ grep -rnE "設計筆記|docs/|\*\.md" tests/ pyproject.toml
(沒有結果)
判定     沒有被讀到 → 跳至 Step 5
```

## good example
- 邊界:staged 的只有 `locale/zh-TW.json`,檔名搜不到;**再搜所在目錄 `locale`**,找到 `test_locale.py` 用目錄組出路徑讀它
```
staged   locale/zh-TW.json
$ grep -rn "zh-TW.json" tests/ pyproject.toml
(沒有結果)
$ grep -rn "locale" tests/ pyproject.toml
tests/test_locale.py:5:    path = ROOT / "locale" / f"{lang}.json"
判定     test_locale 讀到 → 往 Step 4 走

$ uv run .claude/skills/git-conventional-commit/scripts/verify_staged.py --repo . --link .venv --cmd "uv run pytest tests/test_locale.py"
```

## bad example
- 邊界:同一筆,**搜不到檔名就停了**;`test_locale.py` 讀的正是這個檔,翻譯格式寫壞了也不會被跑到
```
staged   locale/zh-TW.json
$ grep -rn "zh-TW.json" tests/ pyproject.toml
(沒有結果)
判定     沒有被讀到 → 跳至 Step 5
```

## good example
- 邊界:這一筆是 `todo/store.py` 加上 `docs/設計筆記.md`;**有原始碼,就照 repo 的測試指令跑全部**,不必再去搜誰讀到 store
```
staged   todo/store.py
         docs/設計筆記.md
判定     有原始碼 → 被讀到,往 Step 4 走

$ uv run .claude/skills/git-conventional-commit/scripts/verify_staged.py --repo . --link .venv --cmd "uv run pytest"
```

## bad example
- 邊界:同一筆,因為「只改了 store」就只跑 `test_store.py`;**`test_cli.py` 也透過 `todo.cli` 用到 store**,這一筆讓它壞掉也看不到
```
staged   todo/store.py
         docs/設計筆記.md
判定     有原始碼 → 被讀到,往 Step 4 走

$ uv run .claude/skills/git-conventional-commit/scripts/verify_staged.py --repo . --link .venv --cmd "uv run pytest tests/test_store.py"
```
