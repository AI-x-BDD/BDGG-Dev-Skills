---
name: trunk-based-development
description: 以主幹式開發(Trunk-Based Development)的方式切分與整合變更 —— 功能切小、直接進 trunk 或走壽命不超過兩天的短期 branch、整合前先在本機跑完整建置與測試、讓 trunk 隨時可以發布、做不完的長變更用 feature flag 或 branch by abstraction。開始做一個功能、要決定開不開 branch、要 merge / push / 開 PR、變更太大一次做不完、要 release 或修 production bug、trunk 的建置壞了、或使用者問到 branching 策略(GitFlow、GitHub Flow、long-lived branch、主幹開發、TBD)時,都先讀這支 skill —— 即使使用者只說「幫我開發這個功能」而沒提到任何 branch 的事。
---

# Trunk-Based Development(主幹式開發)

> 驗證狀態:**未驗證** —— 尚未經學員在真實專案上連續使用並觀察。已用 skill-creator 的評測機制做過兩輪 agent 對照測試(2026-10-05,測試題在 `evals/evals.json`),並依結果修訂過;那是 agent 測 agent,不能取代人的觀察。

## 這套做法在防什麼

Trunk-Based Development 是一種 branching model:所有開發者在同一條名為 trunk 的 branch 上協作(Git 社群通常叫 `main`),並且用一組有名字的技巧**抗拒開出其他長期開發 branch 的壓力**。

它要縮短的是「距離」—— 還沒進到共用 branch 的程式碼,離整合有多遠。這段距離越長,越可能:

- 合併時弄壞意料之外的東西
- 很難合併
- 直到合併才發現有人做了重複的工作
- 藏著不會讓建置失敗、卻彼此不相容的問題

所以整套做法收斂成兩條承諾,其餘都是為了守住這兩條:

1. **不弄壞建置**(never break the build)
2. **隨時可以發布**(always release ready)—— 主管走進來說「現在就上線」,最差的回答也只能是「給我們一小時」

## 開工前:三個判斷

### 判斷一:trunk 是哪一條、「建置」是哪一道指令

```bash
git symbolic-ref --short refs/remotes/origin/HEAD   # 或看 repo 的預設 branch
git branch -a
```

找出這個 repo 的完整建置指令(編譯 + 單元測試 + 整合測試),通常在 README、`Makefile`、`package.json` 的 scripts、或 CI 設定檔裡。**開發者提交前跑的建置,必須和 CI 跑的是同一套** —— 找 CI 設定檔對照。找不到任何自動化測試時,先告訴使用者:沒有測試就無法證明「沒弄壞建置」,這是這套做法的前提。

### 判斷二:這件事夠不夠小

理想的大小是**動手後幾個小時內**就能完成並送出;上限是一兩天。超過的話就會出現把它放在 branch 上慢慢做的壓力,而那正是這套做法要避免的。

太大就先切:

- 切成**薄的垂直切片**(thin vertical slice):每一片都貫穿所需的各層、可以單獨完成、單獨上線。
- 一張需求卡不等於一次整合。可以先送一筆 refactor,再送一筆新功能,再送一筆 refactor —— 三次整合共用同一張卡。
- 會波及所有人的動作(大規模改名、搬目錄)單獨先送一筆「鋪路 commit」(facilitating commit),讓後面的變更變小。

切不小、而且會持續好幾天的變更,不要開長期 branch,改用下面〈長變更〉的技巧。

### 判斷三:直接進 trunk,還是短期 branch

| | 直接 commit 到 trunk | 短期 feature branch |
|---|---|---|
| 適合 | 很小的團隊(含單人),彼此知道對方在做什麼;建置快而且夠完整 | 需要在落地前做 code review 與 CI 驗證;人數較多 |
| 好處 | 最容易形成「一連串小 commit 流進 trunk」的節奏 | trunk 幾乎不會壞 |
| 代價 | 壞掉的 commit 會直接被隊友拉走,所以提交前的本機建置沒有任何折扣空間 | review 或建置一慢,就會把一天的工作拖成多天 |

先看 repo 既有的做法:trunk 有 branch protection、歷史上都是 PR 合併,就走短期 branch;歷史上都是直接推,而且是小團隊或個人專案,就直接進 trunk。拿不準就問使用者。

## 每一次整合的循環

不論哪一種風格,都是同一個循環,而且一天要走很多次:

1. **同步 trunk**。開工前、提交前都拉一次(chase HEAD)。
   ```bash
   git switch main && git pull --rebase
   ```
2. **(短期 branch 才需要)從最新的 trunk 開 branch**。
   ```bash
   git switch -c <簡短描述這一小步的名稱>
   ```
3. **做一小步,連同測試**。
4. **把 trunk 的最新狀態帶進來**。別人可能已經先推了。
   ```bash
   git pull --rebase origin main      # 或 git merge origin/main,依 repo 慣例
   ```
5. **在本機跑完整建置,確認通過,才往外送**。
6. **整合**:
   - 直接進 trunk:`git push origin main`。被拒絕(有人搶先)就回到第 4 步,**重新建置**後再推。
   - 短期 branch:推上去開 PR → review 與 CI 都通過 → 合併回 trunk → **立刻刪掉 branch**。
     ```bash
     git branch -d <branch> && git push origin --delete <branch>
     ```
7. **確認落地後 trunk 的 CI 是綠的**。這一步做完才算整合完成。看不到 CI 結果時(repo 沒有接 CI、remote 不會觸發、或沒有權限查看),改用最接近的替代:從 remote 重新 clone 一份乾淨的 trunk,在上面跑同一道建置。並在回報裡說明這是替代驗證,不是 CI 本身的結果。

### 收工時只有兩種合格的狀態

1. 這次的變更**已經在共用的 trunk 上**,建置是綠的,用過的短期 branch 已經刪掉。
2. 還沒整合 —— 而且你**明白告訴使用者**它現在在哪裡(哪一條 branch、有沒有 push)、為什麼停在這裡、還差哪一步。

把工作留在一條沒合回去的 branch 上,然後回報「做完了」,是這套做法最常見的失敗方式:對使用者來說看起來已經完成,實際上那段程式碼正在離 trunk 越來越遠。許多工具與 agent 的預設習慣是「先開一條 branch 比較安全」;在這套做法裡,開 branch 本身沒有問題,**開了卻沒有在同一段工作裡合回並刪除**才是問題。

整合是把變更推上共用的 remote,屬於會影響其他人的動作。使用者明確說先不要 push、或你沒有權限時,就停在「已帶入最新 trunk、建置為綠、隨時可以推」的狀態,並依上面第 2 種情況回報。

### 為什麼第 5 步不能省、也不能丟給 CI

兩筆改動碰到同一個檔案的不同區段時,git 會安靜地自動合併,不會跳出衝突。但那只代表**文字上**沒衝突:一邊把函式改了名,另一邊在別處新增了對舊名字的呼叫,兩邊的行從未重疊,合併演算法什麼都不會說。**這類語意上的破壞只有建置抓得到**。所以:

- 建置要在「已經帶入最新 trunk」之後跑,否則驗證的不是即將落地的那個狀態。
- 不要把 CI 當拐杖 —— 先在自己這邊確認是綠的,CI 只是第二道確認。
- 建置要快(原文的標準:一分鐘算快,十分鐘以上算慢)。建置慢是團隊放棄這套做法最常見的原因;發現建置很慢時要告訴使用者。

### trunk 壞了怎麼辦

- 自己剛推的 commit 弄壞了:**立刻 revert**,回到綠燈,再在自己這邊慢慢修。極小的團隊(三四人)可以選擇馬上補一筆修正,但前提是真的很快。
- 別人弄壞的:不要在紅燈上繼續疊 commit —— 之後很難分辨是誰的問題。同步時停在最後一個已知是綠的 commit,等 trunk 修好再往前。

## 短期 branch 的規矩

這幾條是它和 long-lived feature branch 的分界線,越過任何一條就不再是 Trunk-Based Development:

- **壽命**:一兩天。超過兩天就有變成長期 branch 的風險。
- **人數**:一個人(或一組 pair)。不是給多人共同開發用的。
- **合併方向**:只允許兩種 —— 把 trunk 合進來讓 branch 追上 HEAD;以及結束時合回 trunk。
- **合回之後刪掉**,作為已經收斂的證明。review 的留言保留在平台上,branch 本身不留。
- **不允許**:
  - 把做到一半、無法單獨上線的內容中途合進 trunk
  - 合到別人的短期 branch
  - 合到 release branch
  - 別人從你的 branch 拉變更(應該從 trunk 拉)
  - pair 以外的人加入你的 branch

## 長變更:做不完也不開長期 branch

### Feature flag

把還沒完成的功能包在開關後面,程式碼照常流進 trunk,在 production 保持關閉。

- 盡量用**抽象層**切換實作(在啟動處依 flag 選擇要注入哪一個實作),避免在各處散落 `if/else`。
- CI 要涵蓋有意義的 flag 組合:測試要能在開、關兩種狀態下都跑。
- 即使在 production 是關的,被包住的程式碼也要有單元測試。
- **flag 是技術債**。功能穩定後它很容易被遺忘。建立 flag 的當下就記錄「何時回來檢查並移除」(原文建議:上線一個月後;可以寫進 README 並附上日期)。

### Branch by Abstraction

要把一個既有實作換成另一個、預計耗時多日時用。兩條規則:不拖慢依賴這段程式碼的其他人;任何一筆推出去的 commit 都不得危及上線能力。

1. 在**要被取代**的程式碼外圍建立抽象層,把所有使用端改成依賴抽象層。提交。
2. 為抽象層寫**第二個實作**(新做法),在 trunk 上保持關閉。提交(可以分很多筆)。
3. 把開關從舊實作切到新實作。提交(一筆很小的 commit)。
4. 移除舊實作。
5. 移除抽象層(如果它對測試有用,也可以留著)。

每一步都可以拆成多筆 commit,每一筆都不得弄壞建置。附帶的好處:遷移可以隨時暫停再繼續,因為未完成的第二個實作一直被建置守著。

### Strangulation

新舊實作是**不相容的語言或不同的 process** 時(放不進同一個抽象層),改在前端的路由層依條件把請求導到新系統或舊系統,一個里程碑一個里程碑地搬。

細節與例子見 `references/techniques.md`。

## 發布

| 發布節奏 | 做法 |
|---|---|
| 很高(每天或更頻繁) | **Release from trunk**:直接從 trunk 發布(打 tag)。production 出問題就在 trunk 上修,往前發布(fix forward / roll forward)。 |
| 較低(例如每月) | **Branch for release**:發布前幾天才從 trunk 切出 release branch(just in time),在上面做最後的穩定化。 |

Release branch 的規矩:

- 開發者**不在 release branch 上做開發**,繼續全速往 trunk 提交。沒有 code freeze。
- **bug 一律先在 trunk 重現並修好**(附測試、CI 通過),再 **cherry-pick 到 release branch**。方向只有 trunk → release branch。反過來做,總有一天會有人忘記帶回 trunk,下一版就 regression。
- release branch **不合回 trunk**;確定不再從它發布後刪除(Git 要先在已發布的 commit 上打 tag,否則 commit 會被回收)。
- 不必預先開:可以先從 trunk 上的 tag 發布,等真的需要 patch 時再從那個 tag 回頭開 branch。
- 切點不必是 HEAD:可以從較早的、信得過的 commit 切。

## 這些情況代表做錯了

- 只是有一條叫 `trunk` / `main` 的 branch,但開發其實在別的 branch 上、多人共用、而且活超過幾天。
- 接近發布日就放慢或凍結提交(code freeze)。
- 把還沒準備好的 commit 從 trunk 退掉(unmerge)。沒準備好的東西本來就不該進來;要逐步累積就藏在 flag 後面。
- 在 release branch 上修 bug 再合回 trunk。
- 用一般 merge(而不是 cherry-pick)把 trunk 的內容帶到 release branch。
- 一條 release branch 一直活著,供好幾個大版本使用。
- release branch 之間互相合併。
- 發布後把 release branch 整條合回 trunk。

## 適用條件與例外

**前提**(缺了就先補,或先告訴使用者):

- 有夠快、夠完整、可以在本機重跑的自動化建置與測試。
- 工作可以切成小塊。做瀑布式開發、或迭代很長而且越接近發布越綁手綁腳的團隊,離這套做法還很遠。
- 版本控制系統的同步夠快(原文標準:已是最新時 3 秒內,落後時 15 秒內)。
- 超過三個人的團隊需要 CI 服務守著 trunk;極小的團隊靠「人人提交前都跑建置」可以晚一點再架。

**例外**:

| 情況 | 處理 |
|---|---|
| bug 在 trunk 上真的重現不出來(很罕見) | 可以在 release branch 上重現並修正,再合回 trunk —— 但要清楚這引入了 regression 的風險,並明確告知使用者 |
| 需要長期同時支援舊版 API 或舊版本(客戶自己決定何時升級) | Branch by Abstraction 不適用,它不是萬靈丹 |
| 開源專案收到外部 fork 的 PR | review 可能很慢、甚至不採用,談不上 continuous;這是志願性質的常態,不算違反 |
| repo 目前採用 GitFlow 或其他多條長期 branch 的模型 | 原文明說 GitFlow 與這套做法不相容。不要自行改變團隊的 branching model —— 說明差異,由使用者決定 |
| GitHub Flow | 非常接近,唯一的關鍵差別是它在合回 main **之前**就從 branch 發布;Trunk-Based Development 只從 trunk 或 release branch 發布 |

各種風格適用的人數範圍、與其他 branching model 的比較,見 `references/techniques.md`。

## 完成後的回報

每做完一次整合,向使用者回報:

1. **切法**:這次的工作怎麼切、每一塊多大;有沒有用到鋪路 commit、flag 或抽象層。
2. **整合風格**:直接進 trunk,或短期 branch(名稱、從開出到合回刪除經過多久)。
3. **建置證據**:跑了哪一道指令、是在帶入最新 trunk 之後跑的嗎、結果如何(附關鍵輸出,不是只說「通過」)。
4. **目前狀態**:trunk 上的 CI 是否為綠;還有沒有未合回、未刪除的 branch;trunk 現在是否可以發布。
5. **留下的債**:新增了哪些 flag 或暫時的抽象層、預計何時移除。

有任何一條規矩這次沒做到(例如 branch 活了三天、沒有可跑的測試),直接說出來並說明原因,不要略過。

## 資料來源

全部出自 <https://trunkbaseddevelopment.com/>(作者 Paul Hammant 與貢獻者)。本 skill 為摘要與轉述,原文版權屬原作者。整理日期:2026-10-05。

| 主題 | 頁面 |
|---|---|
| 定義、主張、注意事項 | <https://trunkbaseddevelopment.com/> |
| 距離、兩條承諾、基本流程 | <https://trunkbaseddevelopment.com/5-min-overview/> |
| 前提與上下層(CI / CD) | <https://trunkbaseddevelopment.com/context/> |
| 需求大小、建置時間等決定因素 | <https://trunkbaseddevelopment.com/deciding-factors/> |
| 三種風格與取捨、本機建置 | <https://trunkbaseddevelopment.com/styles/> |
| 直接進 trunk | <https://trunkbaseddevelopment.com/committing-straight-to-the-trunk/> |
| 短期 feature branch | <https://trunkbaseddevelopment.com/short-lived-feature-branches/> |
| CI | <https://trunkbaseddevelopment.com/continuous-integration/> |
| Code review | <https://trunkbaseddevelopment.com/continuous-review/> |
| Feature flags | <https://trunkbaseddevelopment.com/feature-flags/> |
| Branch by Abstraction | <https://trunkbaseddevelopment.com/branch-by-abstraction/> |
| Strangulation | <https://trunkbaseddevelopment.com/strangulation/> |
| Branch for release | <https://trunkbaseddevelopment.com/branch-for-release/> |
| Release from trunk | <https://trunkbaseddevelopment.com/release-from-trunk/> |
| 觀察到的習慣 | <https://trunkbaseddevelopment.com/observed-habits/> |
| 常見錯誤 | <https://trunkbaseddevelopment.com/youre-doing-it-wrong/> |
| 其他 branching model | <https://trunkbaseddevelopment.com/alternative-branching-models/> |
| 同時開發連續版本 | <https://trunkbaseddevelopment.com/concurrent-development-of-consecutive-releases/> |
| CD | <https://trunkbaseddevelopment.com/continuous-delivery/> |
