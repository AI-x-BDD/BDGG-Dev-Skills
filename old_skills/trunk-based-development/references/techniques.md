# Trunk-Based Development —— 技巧與細節

> 來源:<https://trunkbaseddevelopment.com/> 各頁(作者 Paul Hammant 與貢獻者)。以下為摘要與轉述,每節標明出處頁面,方便回頭核對。引號內為原文短句。整理日期:2026-10-05。

## 目錄

1. 關鍵字
2. 定義與主張
3. 三種風格與人數範圍
4. 建置與 CI
5. Code review
6. Feature flags
7. Branch by Abstraction
8. Strangulation
9. Release branch 與 cherry-pick
10. 觀察到的習慣
11. 與其他 branching model 的比較
12. 決定因素與前提

## 1. 關鍵字

| 關鍵字 | 意思 |
|---|---|
| trunk | 團隊集中開發的那一條共用 branch;Git 社群自 2020 年起多稱 `main` |
| distance(距離) | 尚未進入共用 branch 的程式碼,離整合有多遠 |
| short-lived feature branch | 壽命一兩天、單人(或一組 pair)使用、合回即刪的 branch;也叫 task / topic branch |
| long-lived feature branch | 短期 branch 的反面,這套做法所反對的 |
| the build | 開發者提交前與 CI 都執行的同一套建置腳本:編譯、單元測試、整合測試 |
| pre-integrate build | 往外推之前,在開發者自己的環境上跑的完整建置 |
| chasing HEAD | 一天多次從 trunk 同步 |
| facilitating commit | 為了讓後續變更更容易被隊友消化而先送出的鋪路 commit |
| feature flag / toggle | 控制功能開關的機制 |
| branch by abstraction | 透過抽象層在 trunk 上逐步替換實作的技巧 |
| strangulation | 以路由層在新舊系統之間逐步切換的技巧 |
| release branch | 發布前才從 trunk 切出、不承接開發工作的 branch |
| cherry-pick | 把特定 commit 合到目標 branch,略過其間其他 commit |
| fix forward / roll forward | 在 trunk 上修正後往前發布,而不是回退 |
| build cop | 負責處理建置失敗的角色 |
| thin vertical slice | 貫穿各層、可獨立完成的薄切片 |
| CI / CD | Continuous Integration / Continuous Delivery(或 Deployment) |

## 2. 定義與主張

出處:<https://trunkbaseddevelopment.com/>、<https://trunkbaseddevelopment.com/5-min-overview/>

- 一句話定義:一種 source-control branching model,開發者在單一條名為 trunk 的 branch 上協作,並藉由有文件記載的技巧,抗拒建立其他長期開發 branch 的壓力;因此避開 merge hell、不弄壞建置。
- 它是 Continuous Integration 的關鍵促成者,進而促成 Continuous Delivery。團隊成員一天多次提交到 trunk,自然滿足 CI 的核心要求:**所有成員至少每 24 小時提交到 trunk 一次**。
- 主張一:應該採用 Trunk-Based Development,而不是 GitFlow 或其他有多條長期 branch 的模型。
- 主張二:可以直接 commit/push 到 trunk(很小的團隊),也可以走 Pull Request 流程 —— 只要那些 feature branch 是短期的,而且是「單一開發工作站」的產物(單人、pair 或 mob 皆可)。
- 不論團隊規模,都要在往外推之前於開發者自己的環境上跑一次完整的 pre-integrate build(編譯、單元測試、整合測試)。
- 「Dev workstation」需要與時俱進地解讀:可能是 VM、dev container,在本機或雲端。
- 引言(Frank Compagner):"Branches create distance between developers and we do not want that"。
- "Trunk-Based Development will always be release ready";規則是 "never break the build, and always be release ready"。
- 提交粒度靠經驗累積,但 "commits are typically small"。

## 3. 三種風格與人數範圍

出處:<https://trunkbaseddevelopment.com/styles/>

| 風格 | 原文標示的適用人數(同一個 repo 的活躍提交者) |
|---|---|
| Committing straight to the trunk | 1–100 |
| Short-lived feature branches | 2–1000 |
| Coupled "patch review" system(Gerrit、Rietveld、Phabricator 等) | 2–40,000 |

- <https://trunkbaseddevelopment.com/short-lived-feature-branches/> 另提到:在 PR 與 code review 普及後,從「直接進 trunk」改走短期 branch 的分界點降到約 15 人;16 人以上的團隊用短期 branch 加上事前的 CI 驗證更有生產力。
- 選擇時的取捨清單:建置是否每次都得建全部、版本控制是否有 push/pull 瓶頸、建置時間的中位數相對於提交頻率、CI 多常落後、開發者能否不把自動建置當拐杖、能否接受以後續 commit 修正、是否擅長把 refactor 與功能 commit 分開(以及做出 "baby commits")、能否接受提交後才 review。
- 直接進 trunk 的節奏感:建置 10 秒、每五分鐘一筆 commit 是好位置;建置五分鐘、每十秒一筆 commit 就是地獄,該換做法。
- 短期 branch 的風險:PR 裡塞進比直接推更多的 commit、花更多時間。但不必如此 —— 可以把四筆鋪路 commit 分別送進 trunk,再送第五筆完成或啟用功能。
- 本機建置的重要性:所有變體都是先在本機看到完整建置通過,才宣稱完成並往外送。"They do not at all use build automation as a crutch"。

短期 branch 追上 trunk 的做法(<https://trunkbaseddevelopment.com/short-lived-feature-branches/>):

- 兩種工作流:先嘗試合回 trunk,被擋再從 trunk 拉;或在推之前先投機性地從 trunk 拉一次(沒東西可合時不留痕跡)。
- 個人偏好:`git stash` → `git pull` → `git stash pop`;或 `git rebase`。不論哪種都可能遇到衝突,要先在本機解決。
- 陷阱:一張需求卡只對應一個 PR 的想法。高產能的 XP 團隊每組 pair 一天向 trunk 送出數十筆 commit,每一筆都是可以單獨上線的一小步。

## 4. 建置與 CI

出處:<https://trunkbaseddevelopment.com/continuous-integration/>、<https://trunkbaseddevelopment.com/committing-straight-to-the-trunk/>

- 開發者提交前執行的建置腳本,就是 CI 服務執行的那一份。典型的關卡:編譯、測試編譯、單元測試、服務測試、功能測試(後兩者屬於整合測試)。
- 引言(Steve Smith):"individuals practice Trunk-Based Development, and teams practice CI"。
- 超過三個人的團隊都需要 CI daemon 守護程式碼庫,因為無法保證每個人提交前都跑了建置。
- 從提交到「這筆 commit 弄壞了建置」的通知,經過的時間是關鍵:壞掉之後疊上去的 commit 越多,修復成本越高。
- 最好的安排:commit 落地 trunk **之前**就有人的同意(code review)與機器的同意(CI 驗證)。落地之後仍要再跑一次 CI(時間差仍可能出錯),第二次失敗的機率很低,適合自動 revert 並通知。
- 掛在非 trunk branch(或 patch review 系統)上的自動化,**本身不是 Continuous Integration**。
- 建置速度:一分鐘算快,十分鐘以上算慢。把心力放在編譯與純單元測試(不碰 thread、socket、檔案 IO);整合測試在不犧牲有意義涵蓋率的前提下盡量少,最好的手法是把部分整合測試改寫成純單元測試。
- 語意衝突:小 commit 流進 trunk 時多數合併是安靜發生的;不同區段的改動會自動合併,文字上乾淨卻可能在語意上互相破壞(一邊改函式名、一邊新增呼叫)。合併演算法抓不到,只有建置抓得到 —— 這是「推之前人人跑完整建置、落地後 CI 立刻驗證 HEAD」不可妥協的真正原因。
- 建置壞了:多半立刻 revert(可能短暫鎖住 trunk);三四人的團隊可以讓人快速補一筆修正。
- "Tests are never green incorrectly":寫得好的測試不會錯誤地通過;反過來(產品程式碼沒問題但測試失敗)很常見。常常紅燈的 CI 價值大減。
- 工具:tbdflow(Claes Adamsson 的 CLI),為直接進 trunk 的團隊把 fetch → rebase、提交前的 CI 狀態檢查等步驟自動化。

## 5. Code review

出處:<https://trunkbaseddevelopment.com/continuous-review/>

- Continuous Code Review:團隊承諾迅速處理隊友送往 trunk 的 commit,不讓 review 堆積。
- 時間標準:幾分鐘最好,數十分鐘可接受;超過一兩個小時就開始拖累 cycle time。
- pair programming 在部分團隊可以算作 review。
- 退回必須基於客觀、公開的理由;不能以「這個 package 只有我能改」為由(common code ownership)。
- 是否 squash / rebase 成單一 commit 再送審,各團隊政策不同。

## 6. Feature flags

出處:<https://trunkbaseddevelopment.com/feature-flags/>

- 粒度可大(整個元件的 UI)可小(溫度顯示華氏或攝氏)。flag 不一定是 A/B 二選一,也可以是疊加的。
- 實作:盡量避免在程式碼各處以 if/else 選擇路徑,改以抽象層,在最早的啟動點依 flag 決定要用哪個實作(手動組裝或透過設定的 dependency injection)。
- CI:要守護合理預期的 flag 組合;單元測試之後,對每個有意義的組合 fan-out。
- 種類:啟動時設定的 flag;執行期可切換的 flag(狀態必須持久化,重啟後不應回到預設值,多節點時用 Consul / etcd 之類保存);build flag(建置時決定)。
- 用途延伸:把關閉的程式碼推進 production 後可做 A/B testing 與 beta。
- 陷阱(技術債):flag 會被遺忘。唯一的救贖是所有程式碼(包括在 production 實際上被關掉的)都有單元測試。建議爭取在發布一個月後清理 flag,或寫進 README 並附上 "review for delete" 日期。
- 警語(Brad Appleton):不喜歡 flag 的地方在於它們最後常常**不如預期地短命**。

## 7. Branch by Abstraction

出處:<https://trunkbaseddevelopment.com/branch-by-abstraction/>

適用:要在 trunk 上完成一個「需要較久」的變更(例如五天),而且有很多人依賴正要被改的那段程式碼。

規則:

1. 不讓依賴這段程式碼的其他開發者被拖慢。
2. "No commit pushed to the shared repository should jeopardize the ability to go live."

理想步驟:

1. 在要被取代的程式碼周圍引入抽象層,並提交讓所有人看到。必要時分多筆 commit,每一筆都不得弄壞建置。
2. 為抽象層寫第二個實作(新程式碼)並提交,但在 trunk 上保持關閉,讓其他人還不會依賴它。可以分多筆;抽象層偶爾需要微調,同樣不得弄壞建置。
3. 把開關從 off 切到 on,提交並推送。
4. 移除要被取代的舊實作。
5. 移除抽象層。

實例:ThoughtWorks 的 Go CI 把 ORM 從 iBatis 換成 Hibernate —— 先在直接使用 iBatis 的類別外圍建立抽象層;寫 Hibernate 的第二個實作;一筆很小的 commit 為所有人切到 Hibernate;移除 iBatis,再移除抽象層與開關。抽象層若有助於測試(多一個可以 mock 的接縫)也可以保留。

附帶好處:

- 遷移可以便宜地暫停與繼續,因為建置一直守著未完成的第二個實作。
- 取消專案的成本仍然低(只比刪掉一條長期 branch 稍貴)。

限制("Not a panacea"):必須長時間支援舊 API 與先前版本時(依賴你的客戶可以自己選擇升級時機)不適用。

## 8. Strangulation

出處:<https://trunkbaseddevelopment.com/strangulation/>

- 在應用程式中進行很大的破壞性變更,同時即使做到一半也不影響上線能力。名稱出自 Martin Fowler(絞殺榕)。
- 關鍵是有一個機制把呼叫導向新或舊的解法,例如由前端的 web server 依 URL 條件式路由。新舊兩邊要對 URL(與 cookie)有共識,並同步部署。
- 與 Branch by Abstraction 的差別:Strangulation 用在不相容的語言(不在同一個 process);Branch by Abstraction 用在來源與目標語言相同或相容時。

## 9. Release branch 與 cherry-pick

出處:<https://trunkbaseddevelopment.com/branch-for-release/>、<https://trunkbaseddevelopment.com/release-from-trunk/>、<https://trunkbaseddevelopment.com/youre-doing-it-wrong/>

- 引言(Wingerd & Seiwald, 1998):"Branch: only when necessary, on incompatible policy, late, and instead of freeze"。
- release branch 在發布前幾天才切(just in time);它「不應承接持續的開發工作」。
- 做 Continuous Delivery 的高產能團隊不用 release branch:production 出問題就 roll forward,在 trunk 上修、從 trunk 發布。
- 發布節奏很高的團隊不需要(也無法使用)release branch,必須從 trunk 發布;版號多半參照 commit 編號或日期時間。
- 一天發布一次(或更少)的團隊仍可能開一條 branch,用來 cherry-pick bug fix 並從那裡發布。
- **branch 可以事後才建立**:不必因為「將來可能需要」就先開;任何現代版本控制都能從過去的 revision 開 branch。
- 切點不必是 trunk 的 HEAD,可以回到較早、已知良好的 commit。被留在切點之後的好 commit 若後來需要,和 bug fix 一樣從 trunk cherry-pick 過來,不是反方向。
- 接近切點時,有些團隊更倚重 feature flag:未就緒的工作以關閉狀態落地,讓 branch 可以直接從 HEAD 切。
- **修 production bug 的最佳實務**:在 trunk 上重現,附測試修好,等 CI 驗證,再 cherry-pick 到 release branch,並等守護 release branch 的 CI 也驗證通過。
- **cherry-pick 只能從 trunk 到 release branch**。理由:反過來做,在壓力下會忘記帶回 trunk,幾週後 production 就 regression。真的無法在 trunk 重現時才反向操作,並接受因此引入的 regression 風險。
- Merge Meister:從 trunk cherry-pick 到 release branch 是單一開發者(或一組 pair)的兼職角色,可以輪值,並留下稽核紀錄。
- release branch 的刪除:確定該版本不再於 production 使用後刪除(不是立刻),**不合回 trunk**。Git 要先在已發布的 commit 建立 tag 再刪 branch。
- 不要讓單一 release branch 存活跨越多個大版本;cherry-pick 應隨時間遞減至零,活動轉移到新的 release branch。
- 只從 trunk 合到 release branch,且只用 cherry-pick;release branch 之間不互相合併。

## 10. 觀察到的習慣

出處:<https://trunkbaseddevelopment.com/observed-habits/>

| 習慣 | 內容 |
|---|---|
| No code freeze | 接近發布也不凍結、不放慢;每一天都一樣 |
| Quick reviews | 希望 review 提前而不是延後,所以可能偏好 pair,或在提交當下就請同事 review |
| Chasing HEAD | 一天多次從共用 trunk 同步 |
| Running the build locally | 提交前跑建置以免弄壞它;極小團隊因此可以晚一點才架 CI。被別人搶先時要再同步、再建置,才推出修訂後的 commit |
| Facilitating commits | 會造成大家不便的變更(如大規模目錄改名)先單獨送出,後續 commit 就相對小 |
| Powering through broken builds | 最好的做法是自動回退壞掉的 commit;其他人同步到最後一個已知良好的 commit,等修好再前進 |
| Build cop | CI 批次處理 commit 或建置很慢時,可能需要有人負責釐清是哪一筆弄壞的 |
| Shared nothing | 開發者可以在自己的環境把應用跑起來,並在本機跑完所有單元、整合、功能測試,不依賴共用的外部服務 |
| Common code ownership | 願意讓開發者修改自己沒參與過的區塊;伴隨的是標準、CI 檢查與迅速的 review |
| Always release ready | 不只不弄壞建置,還承諾能在短時間內上線(例如一小時);所以建置要附帶一批自動化測試 |
| Thin vertical slices | 需求應能由一人或一組 pair 在短時間、少量 commit 內完成,並貫穿各層;參考 INVEST |

## 11. 與其他 branching model 的比較

出處:<https://trunkbaseddevelopment.com/alternative-branching-models/>

| 模型 | 原文的評價 |
|---|---|
| GitHub Flow | 非常接近以 PR 為中心的 Trunk-Based Development。關鍵差別在發布從哪裡進行:GitHub Flow 在合回 main 之前先從 branch 發布,有下一版 regression 的小風險(branch 可能沒被合回,或缺少 trunk 上已發布的內容) |
| GitFlow 及類似模型 | "Git Flow is incompatible with Trunk-Based Development." 是多組開發者同時活躍在多條 branch 上的模型 |
| Mainline(ClearCase 時代) | "diametrically opposite to Trunk-Based Development - do not do this." |
| 多條 trunk | 看似可行但陷阱很多,建議不要 |

補充(<https://trunkbaseddevelopment.com/concurrent-development-of-consecutive-releases/>):Trunk-Based Development 加上 feature flag 與 branch by abstraction,是對「發布順序臨時要調整」的避險 —— 不必選擇性地 un-merge。但原文同時強調:依序開發依序發布(做完並發布一版,才開始下一版)遠優於同時開發多個連續版本。

## 12. 決定因素與前提

出處:<https://trunkbaseddevelopment.com/deciding-factors/>、<https://trunkbaseddevelopment.com/context/>

- **迭代長度**:四週以上、而且越接近發布每週的樣貌越不同,可以遵守 Trunk-Based Development 的原則,但走不到 Continuous Delivery。
- **Waterfall**:離「不弄壞建置」的要求很遠。
- **需求大小**:需要小的 story / task。最理想是開工後幾個小時內完成並送 review;超過兩天就會有把多人集中到非 trunk branch 上的壓力。整個團隊都該盡力把需求切小(INVEST)。
- **建置時間**:直接決定一天能提交幾次。幾分鐘的建置能維持高節奏;三十分鐘以上,開發者會降到一天只提交幾次。
- **版本控制**:要支援一天多次同步。已是最新時應在三秒內完成;trunk 領先時不超過十五秒。
- **提交尖峰**(race to push):有人搶先推時要先拉再推;極活躍的 repo 會找不到推送的空檔。PR 與 merge queue 可以緩解。
- **資料庫 migration**:schema 變更要納入版本控制,並處理既有資料(參考 *Refactoring Databases*)。
- **共用程式碼**:通常採 common code ownership;即使寫入權限有細分,讀取也不設限。
- **層次**(context 頁):下層前提是穩固的開發基礎設施;Trunk-Based Development 促成其上的 CI,再上是 CD,再上是 lean experiments。
