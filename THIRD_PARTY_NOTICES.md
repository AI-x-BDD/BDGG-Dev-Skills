# 第三方聲明

本 repo 部分 skill 參考或改寫自下列開源專案。各 skill 資料夾裡的 `NOTICE.md` 寫明該 skill 與來源的關係。

## 參考來源

| 專案 | 授權 | 本 repo 的使用方式 |
|---|---|---|
| [github/spec-kit](https://github.com/github/spec-kit) | MIT | `specify` 的 `templates/spec.template.md` 譯自其 `templates/spec-template.md`;其餘列出的 skill 參考其流程與產出檔(spec.md、research.md、plan.md、tasks.md)的概念,文字為重新撰寫 |
| [dceoy/speckit-agent-skills](https://github.com/dceoy/speckit-agent-skills) | AGPL-3.0 | 只作為設計參考閱讀(`speckit-implement`、`speckit-clarify`),未複製其文字;該專案的 skill 內容本身轉寫自 github/spec-kit 的 `templates/commands/` |

## 涉及的 skill

| skill | 關係 | 來源 |
|---|---|---|
| `specify` | 樣板翻譯 | github/spec-kit `templates/spec-template.md` |
| `tasks` | 概念參考 | github/spec-kit `templates/tasks-template.md` |
| `implement` | 概念參考 | dceoy/speckit-agent-skills `skills/speckit-implement`(源自 github/spec-kit `templates/commands/implement.md`) |
| `clarify` | 概念參考 | dceoy/speckit-agent-skills `skills/speckit-clarify`(源自 github/spec-kit `templates/commands/clarify.md`) |
| `clarify-over-specs` | 概念參考 | dceoy/speckit-agent-skills `skills/speckit-clarify`(源自 github/spec-kit `templates/commands/clarify.md`) |
| `technical-research` | 概念參考 | github/spec-kit 的 Phase 0 `research.md` |
| `system-analysis` | 概念參考 | github/spec-kit 的 `plan.md` |

## github/spec-kit 授權全文

```
MIT License

Copyright GitHub, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
