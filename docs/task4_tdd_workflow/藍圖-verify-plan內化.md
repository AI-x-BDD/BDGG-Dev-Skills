# 藍圖:verify-plan 退場,替身、護欄與判定者內化進 testplan

- 要你回答:這份藍圖可不可以寫入;要修改的話是哪一項
- 根因報告:落差 1~3 在 testplan,歸類為「缺」(原本由 verify-plan R1、R3、R4 管,退場後沒有人接手);落差 4 在 tasks 與 analyze,歸類為「多」(指向已移除的 verify-plan)
- 同意之後會改到的檔(`.claude/skills/` 與 `.agents/skills/` 兩份同步):
  - testplan:`SKILL.md`、`rules/待測端點-規範.md`、`rules/測試案例-規範.md`、`templates/testplan.md`、`templates/testplan.example.md`、`scripts/check_testplan.py`
  - tasks:`SKILL.md`、`rules/任務-規範.md`
  - analyze:`SKILL.md`、`rules/問題-規範.md`、`scripts/check_analysis.py`
  - implement:`templates/完成報告.md`、`templates/完成報告.example.md`
  - 刪:`verify-plan/` 整個資料夾
  - 文件:根 `README.md`、`.claude/skills/README.md`、`.agents/skills/README.md`、`docs/task3_sdd_workflow/README.md`(verify-plan 連結改指 tag `task3-v1`)
  - CI:`ci/test_testplan_coverage.py`(加替身檢查的測試)
- 產出鏈:spec.md + plan.md + 既有測試的替身 → 待測端點(含替身清單)→ testplan.md(含每個替身的實跑案例、📏 案例的護欄與判定者)→ tasks.md 的 📏 實跑任務(帶護欄)→ 完成報告(SC 標判定者;無法實跑的替身列未驗證)

## 主幹

只有 testplan 的主幹有變更,其餘三支的主幹只拿掉 verify-plan 的字樣。

### testplan(變更只有 Phase 1 Step 1、Phase 2 Step 3)

```
## Phase 1: 提出待測端點
1. Read **這次規劃的依據**:spec.md、plan.md 的端點盤點與它指到的規格檔與原型、techstack.md、research.md,以及範疇內已經有的程式碼與測試,包含測試裡代替真元件的替身;若 spec.md 所在的資料夾沒有 plan.md → 結束。
2. Think 依 `rules/待測端點-規範.md` **照抄端點盤點列出待測端點**:每個端點的代號、介面規格檔、公開接縫、受測操作與規格錨點、接縫的取捨、替身,以及上游沒寫到的待決問題。
3. Ask 依骨架 `templates/testplan.md` 與範例 `templates/testplan.example.md` **提出待測端點與待決問題**,問使用者是否同意只在這些端點與操作上規劃測試、每一題怎麼決定;若使用者要修改 → 跳至 Phase 1 Step 2。
4. Write 把使用者的決定**登記到 plan.md 的待決問題**。

## Phase 2: 寫出測試計劃
1. Write 依 `rules/測試案例-規範.md` 照確認過的待測端點,把每個使用者故事的端點節、跨端點驗收與全域測試區的測試案例**寫成 `specs/<功能>/testplan.md`**。
2. Delegate 依 `rules/腳本執行-規範.md` 執行 `uv run scripts/check_testplan.py --spec <spec.md 的路徑> --plan <testplan.md 的路徑>` **取得覆蓋檢查的結果**;若有不過 → 跳至 Phase 2 Step 1。
3. Ask **提出測試計劃與會碰到正式資料或共用服務的實跑案例**,問使用者是否同意照它交給 `/tasks`、這些案例可不可以照寫的護欄執行;若使用者要修改 → 跳至 Phase 2 Step 1。
```

### tasks Phase 1 Step 1

```
1. Read **任務的依據**:spec.md、testplan.md、research.md、techstack.md、plan.md,以及 plan.md Documentation 樹列出的每一個規格檔與原型;若 testplan.md 不存在 → 結束。
```

### analyze Phase 2 Step 1

```
1. Read **全部產出物與憲法**:spec.md、research.md、techstack.md、plan.md,plan.md Documentation 樹列出的每一個規格檔與原型,testplan.md,tasks.md,`<專案根目錄>/constitution/` 底下的條文,以及既有的 analysis.md。
```

(analyze 原本就沒有讀 testplan.md。它是 tasks 的依據,verify-plan 的位置由它補上,analyze 才對得到實跑案例和 📏 任務。)

## 變更

| 處置 | 對象 | 現況 | 終態 | 依據 |
|---|---|---|---|---|
| 換 | testplan 步驟 P1 S1 | 「…以及範疇內已經有的程式碼與測試」 | 句尾加「,包含測試裡代替真元件的替身」 | 根因 1:不讀替身就列不出替身 |
| 換 | testplan 步驟 P1 S2 | 列到「接縫的取捨,以及上游沒寫到的待決問題」 | 加「、替身」 | 根因 1 |
| 換 | testplan 步驟 P2 S3 | 「**提出測試計劃**,問使用者是否同意照它交給 `/tasks`」 | 「**提出測試計劃與會碰到正式資料或共用服務的實跑案例**,…、這些案例可不可以照寫的護欄執行」 | 根因 2:原 verify-plan P2 S1 的同意點 |
| 加 | testplan 規則 `待測端點-規範` Rule 4 [must]〈每個替身至少有一個不用它的實跑案例〉 | 沒有 | 待測端點表的「替身」欄列出這個端點的測試用哪個替身代替哪個真元件,並指到接真元件的實跑案例 ID;實跑案例的驗證方式是 📏,假如/當要寫明接真的哪個元件,不能是同一個替身換個環境跑;拿不到真元件寫「無法實跑:原因」,implement 列為未驗證 | 根因 1,搬自 verify-plan R1 |
| 加 | testplan 規則 `測試案例-規範` Rule 8 [must]〈📏 案例寫出副作用與護欄〉 | 沒有 | 每個 📏 案例寫出會寫到哪裡、呼叫哪些服務,以及防止碰到正式資料的具體做法;碰到正式資料或共用服務的,在 P2 S3 交給使用者同意 | 根因 2,搬自 verify-plan R3 |
| 加 | testplan 樣板 `testplan.md` | 待測端點表 6 欄;非功能案例與全域案例 9 欄 | 待測端點表加「替身」欄(`替身(代替的真元件)→ 實跑案例 ID`,沒有替身寫「無」);非功能案例與全域案例加「副作用與護欄」「判定者與樣本」兩欄(🔴🟢 寫 —;判定者是 AI 時固定寫「使用者尚未複核」;樣本寫是否用來調整過規則) | 根因 1~3;判定者與樣本是固定格式,依部位判定表放樣板,不另立 rule |
| 換 | testplan 樣板 `testplan.example.md` | 範例沒有替身 | 補上替身欄與一個實跑案例的範例 | 同上 |
| 加 | testplan 腳本 `check_testplan.py` 第 10 項 | 檢查 9 項 | 第 10 項:待測端點表「替身」欄不是「無」或「—」時,要指到至少一個有定義、驗證方式是 📏 的案例 ID,或寫「無法實跑:」加原因 | 根因 1:替身有沒有對到案例,每次都該得到同樣的結果,所以交給腳本 |
| 刪 | tasks 步驟 P1 S1 | 「…以及 spec.md 所在資料夾的 verify-plan.md(有的話)」 | 拿掉這一段 | 根因 4 |
| 換 | tasks 規則 `任務-規範` Rule 12 | 〈verify-plan.md 的每一項都有任務〉 | 〈testplan 的每個實跑案例都有帶著護欄的任務〉:替身欄指到的每個實跑案例,📏 任務照抄它的副作用與護欄、判定者;good/bad example 換成 testplan 的案例 ID | 根因 4;原規則的「為什麼」(護欄不抄進任務,subagent 看不到)仍然成立,所以換不刪 |
| 換 | analyze 步驟 P2 S1 | 讀「verify-plan.md(有的話)」 | 改讀 testplan.md | 根因 4 |
| 刪 | analyze 規則 `問題-規範` Rule 4 表格 | `verify-plan.md` → `/verify-plan` 一列 | 拿掉;加一列 `testplan.md` → `/testplan` | 根因 4;testplan 已在流程中,原表卻沒有它 |
| 換 | analyze 腳本 `check_analysis.py` | `SKILLS` 有 `/verify-plan` | 換成 `/testplan` | 根因 4 |
| 換 | implement 樣板 `完成報告.md` | SC 表 3 欄;未驗證只寫「範圍內所有標了未驗證的項目」 | SC 表加「判定者」欄(AI 判定寫「使用者尚未複核」);未驗證加上「testplan 替身欄寫無法實跑的替身」 | 根因 3 的症狀位置;判定者要一路帶到報告,使用者才分得出誰判的 |
| 刪 | `verify-plan/` | 整支 Skill | 沒有;歷史留在 tag `task3-v1` | 本人與分身拍板 |

**拿掉測試**:testplan 範圍內既有的 Rule(待測端點 1~3、測試案例 1~7、腳本執行 1~3)與原有 9 項檢查,逐一問過。它們都不是這次根因指到的對象,拿掉後各自的「為什麼」要防的後果都還會發生,所以全部保留原文。

## 驗收

| 根因 | 驗收輸入 | 驗收產出 | 依據的文字 |
|---|---|---|---|
| 1 | watchlater-notes `specs/005-correction-coverage` 的複本(沒有 verify-plan.md 與 testplan.md),交給終態的 testplan | testplan.md 的待測端點表有「替身」欄,至少列出 `FakeOpenAI`(代 asr-gateway)、`fake_tesseract`(代 Tesseract)、假 DOM(代 htmx 與瀏覽器);每個替身都指到一個 📏 實跑案例,或寫「無法實跑:原因」;`check_testplan.py` 第 10 項通過 | `待測端點-規範` Rule 4;`check_testplan.py` 第 10 項 |
| 1 | 把上面的 testplan.md 改壞:刪掉一個替身指到的實跑案例 | `check_testplan.py` 第 10 項不過,指出那個替身 | `check_testplan.py` 第 10 項 |
| 2 | 同上的 testplan.md | 接 asr-gateway 的實跑案例在「副作用與護欄」寫出只寫暫存 volume、服務位址走環境變數之類的具體做法;P2 S3 把它列為要使用者同意的項目 | `測試案例-規範` Rule 8;testplan P2 S3 |
| 3 | 同上的 testplan.md | 要逐筆判定正確率的 📏 案例,「判定者與樣本」寫「Claude,使用者尚未複核」與樣本是否調過規則 | `templates/testplan.md` 非功能與全域案例的「判定者與樣本」欄 |
| 4 | `grep -rn verify-plan .claude/skills .agents/skills` | 沒有結果;`ci/check_skills.sh` 與 `ci/test_testplan_coverage.py` 全過 | tasks P1 S1、analyze P2 S1、`問題-規範` Rule 4、`check_analysis.py` |
