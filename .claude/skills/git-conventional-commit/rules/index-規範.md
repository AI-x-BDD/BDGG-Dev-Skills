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
