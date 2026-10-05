# Conventional Commits 1.0.0 —— 規範原文與整理

> 來源:<https://www.conventionalcommits.org/en/v1.0.0/>(CC BY 3.0)。
> 「規範原文」一節為逐條照錄,方便回頭核對;其餘為整理與翻譯。整理日期:2026-10-05。

## 目錄

1. 關鍵字
2. 規範原文(16 條)
3. 逐條白話對照
4. 官方範例
5. FAQ 整理
6. type 定義的出處
7. 與 SemVer 的關係
8. 相關工具

## 1. 關鍵字

| 關鍵字 | 意思 |
|---|---|
| type | header 開頭的名詞,標示這筆變更的性質(`feat`、`fix`…) |
| scope | 括號裡的名詞,標示影響的程式碼區塊 |
| description | 冒號與空格之後的簡短摘要 |
| body | 選用的詳細說明,與 description 隔一行空行 |
| footer | 選用的中繼資料,格式近似 git trailer |
| BREAKING CHANGE | 破壞性的 API 變更,對應 SemVer MAJOR |
| `!` | 放在 `:` 之前,標示 breaking change |
| SemVer | Semantic Versioning,`MAJOR.MINOR.PATCH` |
| RFC 2119 | 定義 MUST / SHOULD / MAY 等字眼強度的文件 |

## 2. 規範原文(16 條)

> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

1. Commits MUST be prefixed with a type, which consists of a noun, `feat`, `fix`, etc., followed by the OPTIONAL scope, OPTIONAL `!`, and REQUIRED terminal colon and space.
2. The type `feat` MUST be used when a commit adds a new feature to your application or library.
3. The type `fix` MUST be used when a commit represents a bug fix for your application.
4. A scope MAY be provided after a type. A scope MUST consist of a noun describing a section of the codebase surrounded by parenthesis, e.g., `fix(parser):`
5. A description MUST immediately follow the colon and space after the type/scope prefix. The description is a short summary of the code changes, e.g., *fix: array parsing issue when multiple spaces were contained in string*.
6. A longer commit body MAY be provided after the short description, providing additional contextual information about the code changes. The body MUST begin one blank line after the description.
7. A commit body is free-form and MAY consist of any number of newline separated paragraphs.
8. One or more footers MAY be provided one blank line after the body. Each footer MUST consist of a word token, followed by either a `:<space>` or `<space>#` separator, followed by a string value (this is inspired by the git trailer convention).
9. A footer's token MUST use `-` in place of whitespace characters, e.g., `Acked-by` (this helps differentiate the footer section from a multi-paragraph body). An exception is made for `BREAKING CHANGE`, which MAY also be used as a token.
10. A footer's value MAY contain spaces and newlines, and parsing MUST terminate when the next valid footer token/separator pair is observed.
11. Breaking changes MUST be indicated in the type/scope prefix of a commit, or as an entry in the footer.
12. If included as a footer, a breaking change MUST consist of the uppercase text BREAKING CHANGE, followed by a colon, space, and description, e.g., *BREAKING CHANGE: environment variables now take precedence over config files*.
13. If included in the type/scope prefix, breaking changes MUST be indicated by a `!` immediately before the `:`. If `!` is used, `BREAKING CHANGE:` MAY be omitted from the footer section, and the commit description SHALL be used to describe the breaking change.
14. Types other than `feat` and `fix` MAY be used in your commit messages, e.g., *docs: update ref docs*.
15. The units of information that make up Conventional Commits MUST NOT be treated as case-sensitive by implementors, with the exception of BREAKING CHANGE which MUST be uppercase.
16. BREAKING-CHANGE MUST be synonymous with BREAKING CHANGE, when used as a token in a footer.

## 3. 逐條白話對照

| # | 強度 | 白話 |
|---|---|---|
| 1 | MUST | 開頭一定是 type;scope 與 `!` 選用;最後一定要有 `: `(冒號+空格) |
| 2 | MUST | 新增功能就用 `feat` |
| 3 | MUST | 修 bug 就用 `fix` |
| 4 | MAY / MUST | scope 可有可無;有的話必須是名詞、用括號包起來 |
| 5 | MUST | description 緊接在 `: ` 之後,是變更的簡短摘要 |
| 6 | MAY / MUST | body 可有可無;有的話必須與 description 隔一行空行 |
| 7 | MAY | body 格式自由,可以多段 |
| 8 | MAY / MUST | footer 可有可無;有的話與 body 隔一行空行,形式為 `Token: value` 或 `Token #value` |
| 9 | MUST | footer token 的空白以 `-` 取代;`BREAKING CHANGE` 是唯一例外 |
| 10 | MAY / MUST | footer 的值可以含空白與換行;遇到下一組合法的 token/分隔符就結束 |
| 11 | MUST | breaking change 一定要標,標在 header 或 footer |
| 12 | MUST | 標在 footer 時:全大寫 `BREAKING CHANGE` + 冒號 + 空格 + 說明 |
| 13 | MUST / MAY / SHALL | 標在 header 時:`!` 緊貼 `:` 之前;此時 footer 可省略,但 description 要負責說明破壞了什麼 |
| 14 | MAY | 可以用 `feat`、`fix` 以外的 type |
| 15 | MUST NOT / MUST | 工具實作不得區分大小寫;唯獨 `BREAKING CHANGE` 必須大寫 |
| 16 | MUST | footer 裡的 `BREAKING-CHANGE` 與 `BREAKING CHANGE` 同義 |

## 4. 官方範例

description + breaking change footer:

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

用 `!` 標示:

```
feat!: send an email to the customer when a product is shipped
```

scope 加 `!`:

```
feat(api)!: send an email to the customer when a product is shipped
```

`!` 與 footer 並用:

```
feat!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

沒有 body:

```
docs: correct spelling of CHANGELOG
```

有 scope:

```
feat(lang): add Polish language
```

多段 body 加多個 footer:

```
fix: prevent racing of requests

Introduce a request id and a reference to latest request. Dismiss
incoming responses other than from latest request.

Remove timeouts which were used to mitigate the racing issue but are
obsolete now.

Reviewed-by: Z
Refs: #123
```

## 5. FAQ 整理

| 問題 | 官方回答(摘譯) |
|---|---|
| 初期開發階段的 commit 訊息怎麼處理? | 建議當作產品已經發布。通常總有人在用你的軟體(即使只是其他開發者),他們想知道什麼被修了、什麼壞了。 |
| type 用大寫還是小寫? | 都可以,但最好保持一致。 |
| 一個 commit 符合不只一種 type 怎麼辦? | 盡可能回頭拆成多個 commit。Conventional Commits 的好處之一,就是驅使我們做出更有條理的 commit 與 PR。 |
| 這不會妨礙快速開發與迭代嗎? | 它妨礙的是「沒有條理地求快」。它讓你在多個專案、不同貢獻者之間長期維持速度。 |
| 會不會讓開發者只在既有的 type 裡思考、限制了 commit 的種類? | 它鼓勵我們多做某幾類 commit(例如 fix)。除此之外規範很有彈性,團隊可以自訂 type,並隨時間調整。 |
| 和 SemVer 的關係? | `fix` → PATCH;`feat` → MINOR;含 `BREAKING CHANGE` 的 commit 不論 type → MAJOR。 |
| 自己擴充的規範要怎麼定版號? | 建議用 SemVer 發布你的擴充(也鼓勵你擴充)。 |
| 用錯了 type 怎麼辦?—— 用了規範內但不正確的 type(該 `feat` 卻寫 `fix`) | 在合併或發布之前,建議用 `git rebase -i` 修改歷史。發布之後,清理方式取決於你使用的工具與流程。 |
| 用錯了 type 怎麼辦?—— 用了規範外的 type(`feet`) | 最壞的情況下,一筆不符規範的 commit 落地也不是世界末日,只代表依規範運作的工具會漏掉它。 |
| 所有貢獻者都必須遵守嗎? | 不必。採用 squash 流程時,主要維護者可以在合併時整理訊息,不增加臨時貢獻者的負擔。常見做法是讓 git 平台自動 squash PR,並由維護者填寫最終的 commit 訊息。 |
| revert 怎麼處理? | 還原很複雜(還原多筆?還原功能後下一版該是 patch 嗎?)。規範不明確定義 revert 行為,交給工具作者利用 type 與 footer 的彈性處理。一項建議:使用 `revert` type,並在 footer 引用被還原的 commit SHA。 |

## 6. type 定義的出處

規範本身只定義 `feat` 與 `fix`。其餘 type 規範只舉例並指向兩個來源:

**Angular Commit Message Guidelines**(規範的靈感來源,見 About 頁)
<https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines>

| type | Angular 的定義 |
|---|---|
| build | Changes that affect the build system or external dependencies |
| ci | Changes to our CI configuration files and scripts |
| docs | Documentation only changes |
| feat | A new feature |
| fix | A bug fix |
| perf | A code change that improves performance |
| refactor | A code change that neither fixes a bug nor adds a feature |
| style | Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc) |
| test | Adding missing tests or correcting existing tests |

Angular 另外規定(**非 Conventional Commits 規範要求**):

- subject 用祈使句現在式、首字不大寫、結尾不加句點。
- body 同樣用祈使句現在式,寫出變更的動機,並與先前的行為對照。
- 訊息的任何一行都不超過 100 個字元。
- revert 以 `revert: ` 開頭,後接被還原 commit 的 header;body 寫 `This reverts commit <hash>.`

**`@commitlint/config-conventional`**
<https://github.com/conventional-changelog/commitlint/tree/master/%40commitlint/config-conventional>

- `type-enum`:`build`、`chore`、`ci`、`docs`、`feat`、`fix`、`perf`、`refactor`、`revert`、`style`、`test`
- `type-case`:小寫;`type-empty` / `subject-empty`:不得為空
- `subject-case`:不得是 sentence-case、start-case、pascal-case、upper-case;`subject-full-stop`:結尾不得有 `.`
- `header-max-length`、`body-max-line-length`、`footer-max-line-length`:100(含 URL 的 body / footer 行不受限)
- `body-leading-blank`、`footer-leading-blank`:前面要有空行(warning 等級)

該 README 自己的說明:這些風格規則是在規範之上**收窄**,不與規範衝突;想只照規範走可以在設定裡覆寫。

## 7. 與 SemVer 的關係

| commit | 版號 |
|---|---|
| `fix` | PATCH |
| `feat` | MINOR |
| 任何帶 `BREAKING CHANGE`(footer 或 `!`)的 commit | MAJOR |
| 其他 type | 沒有隱含的版號影響(除非帶 BREAKING CHANGE) |

## 8. 相關工具

About 頁列出大量工具,常用的幾類:

- 檢查:commitlint、gitlint、Conventional Commits Linter、commitsar
- 互動式撰寫:commitizen(cz-cli / Python 版)、cz-git
- 產生 changelog 與版號:conventional-changelog、semantic-release、standard-version、git-cliff、Cocogitto

完整清單:<https://www.conventionalcommits.org/en/about/>
