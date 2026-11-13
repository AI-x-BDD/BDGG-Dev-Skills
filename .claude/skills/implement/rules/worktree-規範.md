# Rule 1 [must] - 每個交給 subagent 的端點節開一個自己的 worktree
- 委派前,替每個端點節從目前的分支開一個 worktree:`git worktree add ../<repo 名稱>-wt-p<phase 序號>-E<端點序號> -b impl/p<phase 序號>-E<端點序號>`
- 被 gitignore、又是執行測試需要的相依(例如 `.venv`、`node_modules`),用 symlink 從主工作區連進 worktree,不在 worktree 裡重新安裝
- 端點指示的「你在…工作」寫這個 worktree 的路徑;主 agent 驗收這一節時,在同一個 worktree 裡跑測試、勾選與 commit
- 為什麼:subagent 共用一個工作區時,一個的對照組改壞會被另一個的測試跑到、被主 agent 一起 stage,撤回後還可能跑到舊的 `.pyc`;colab-gpu-bridge 002 的 E2 subagent 斷在改壞的半途,三行錯誤實作就留在大家共用的檔裡

## good example
- E8、E2 兩節平行;**各開一個 worktree,`.venv` 用 symlink 連進去**
```
git worktree add ../colab-gpu-bridge-wt-p3-E8 -b impl/p3-E8
git worktree add ../colab-gpu-bridge-wt-p3-E2 -b impl/p3-E2
ln -s /home/dev/projects/colab-gpu-bridge/.venv ../colab-gpu-bridge-wt-p3-E8/.venv
ln -s /home/dev/projects/colab-gpu-bridge/.venv ../colab-gpu-bridge-wt-p3-E2/.venv
```

## bad example
- 同兩節,**都在主工作區做**;E2 暫時改壞 `services/library.py` 跑對照組時,E8 的快速層剛好跑到那個版本而變紅
```
subagent E8:/home/dev/projects/colab-gpu-bridge
subagent E2:/home/dev/projects/colab-gpu-bridge
```

## good example
- 邊界:這個 phase 只有一個端點節有任務;**照樣開 worktree**,主 agent 同時在主工作區做跨端點驗收的準備時不會互相干擾
```
git worktree add ../colab-gpu-bridge-wt-p4-E2 -b impl/p4-E2
```

## bad example
- 邊界:同一個情況,因為「只有一個 subagent」就**讓它在主工作區做**;主 agent 在同一時間跑全部測試,和它的對照組改壞撞在一起
```
subagent E2:/home/dev/projects/colab-gpu-bridge(主 agent 同時在這裡跑 uv run pytest)
```

# Rule 2 [must] - 依編號順序合併回目前的分支,有衝突就停下
- 每個 worktree 的 commit 驗收過之後,依端點序號由小到大,用 `git merge --ff-only` 合併回目前的分支;前一個合併之後,後面的分支先在它的 worktree 裡 `git rebase <目前的分支>` 再合併
- rebase 或合併有衝突時,不自己挑一邊解;`git rebase --abort` 退回,停下這個端點節,在 Checkpoint 報告列出衝突的檔
- 合併完成後,移除 worktree 與它的分支:`git worktree remove <路徑>`、`git branch -d impl/p<phase>-E<端點>`
- 合併之後由主 agent 在主工作區跑一次全部測試,才進 Checkpoint
- 為什麼:fast-forward 合併讓每一筆 commit 都保持驗收過的樣子;衝突時自己挑一邊,等於沒驗收就改了別人的程式;不移除 worktree,下一個 phase 開同名的分支會失敗

## good example
- E8 先合併;**E2 在自己的 worktree rebase 之後才 fast-forward 合併**,最後移除兩個 worktree
```
git merge --ff-only impl/p3-E8
git -C ../colab-gpu-bridge-wt-p3-E2 rebase main
git merge --ff-only impl/p3-E2
git worktree remove ../colab-gpu-bridge-wt-p3-E8 && git branch -d impl/p3-E8
git worktree remove ../colab-gpu-bridge-wt-p3-E2 && git branch -d impl/p3-E2
uv run pytest -q   (背景執行)  628 passed
```

## bad example
- 同一次合併,**直接 `git merge impl/p3-E2` 產生合併 commit**,衝突時手動挑了 E8 的版本;E2 的一個綠燈改動不見了,測試照樣綠
```
git merge impl/p3-E8
git merge impl/p3-E2   → CONFLICT (content): src/cgb/domain/errors.py
(保留 E8 的版本,git commit)
```

## good example
- 邊界:E2 rebase 時衝突在 `tasks.md` 的勾選列;**照樣 abort 停下**,在 Checkpoint 報告列出,由使用者決定怎麼併
```
git -C ../colab-gpu-bridge-wt-p3-E2 rebase main   → CONFLICT: specs/002-library-error-handling/tasks.md
git -C ../colab-gpu-bridge-wt-p3-E2 rebase --abort
Checkpoint 報告:E2 未合併,衝突檔 tasks.md
```

## bad example
- 邊界:同一個衝突,因為「只是勾選列,兩邊都勾就好」就**自己合併兩邊的勾選**;其中一列在 E2 是停下的任務,被合成已勾
```
(手動把兩邊的 [X] 都留下,git rebase --continue)
```
