# AI 工作流｜文档更新与推送（GitHub）

> 更新：2026-09-13
> 目的：把"读完 → 改哪几个文件 → 校验什么 → 怎么提交与推送 → 怎么确认真到远端了"固化成可复制的步骤，**让任何 AI（或人）在 10 分钟内完成一次规范更新**。
> 适用：新增/修订文献笔记、精读笔记、汇报稿、工艺说明、衬底/材料资料、索引入口等**一切文档类改动**。
> 配套：
> - 接手顺序与项目状态 → [`AI_接手指南.md`](AI_接手指南.md)
> - 文献库组织与编号 → [`文献库指南.md`](文献库指南.md)
> - 一键体检脚本 → [`scripts/maintenance/check_docs.ps1`](../../scripts/maintenance/check_docs.ps1)

---

## 0. TL;DR（给 AI 的最短路径）

```powershell
# ① 定位：先读，不要猜
Get-Content project_config.json -Raw            # 单一状态源
Get-Content README.md                            # 状态行
Get-Content docs/guides/AI_接手指南.md          # 接手顺序与优先级

# ② 改：权威文件优先（config → 正文 → 索引）
# ③ 体检：一条命令跑完 JSON/链接/结构/术语（本机无 pwsh，且执行策略禁止直接跑 .ps1）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\maintenance\check_docs.ps1

# ④ 提交：提交信息写文件，禁止多行 -m
git add -A
git commit -F <临时文件路径>                      # 见 §5
git push origin main                             # 若是 22 端口被重置 → §6 的 443 回退

# ⑤ 确认：远端 SHA == 本地 SHA
git ls-remote origin refs/heads/main
```

**硬规则三条**：① 改完必须跑体检脚本且**断链为 0**；② 提交信息**英文**、说明"改了什么 + 为什么 + 边界"；③ 推送后**必须核对远端 SHA**，不要只看 `git push` 的输出。

---

## 1. 先定位：这次改动属于哪一层

| 改动类型 | 权威文件（先改这里） | 必须同步的索引 |
| --- | --- | --- |
| 里程碑 / 状态 / 文献集合统计 / 规格与报价 | `project_config.json` | 根 `README.md` 状态行、轨道 README |
| 文献新增、笔记新增、PDF 补档 | `literature/<专题>/` 下 README + 笔记本体 | `literature/文献清单.md`、`literature/分区全景索引.md`、体系 README |
| 设计/仿真/工艺汇报稿 | `docs/reports/<category>/<日期>_<主题>.md` 正文 | `docs/reports/README.md`、相关配套文档的交叉链接 |
| 术语/口径澄清 | 对应说明文档 + 汇报稿术语表 | 所有引用该口径的笔记（用 grep 找） |
| 决策与目录规则 | `docs/decisions/<日期>_<主题>.md`（新建） | `project_config.json`、`docs/README.md` |

**规律：一次改动通常要动 3–6 个文件**（正文 + 2~4 个索引）。只改正文、不更索引，是这个仓库最容易犯的错。

---

## 2. 标准执行序列（八步）

1. **读**：`project_config.json` → 根 `README.md` → `docs/guides/AI_接手指南.md` → 与任务相关的**目录级 README**（如 `literature/材料体系分类/Si/1550波段/README.md`）。
2. **搜**：用 grep 找**已有的权威表述**，避免重复定义或与旧口径冲突；同时找出**所有需要同步的位置**（同一术语/统计出现在哪些文件）。
3. **定**：明确这次改动的**证据等级与边界**（见 §4）；文献类改动要写清"是原文值还是预备笔记、是实验还是仿真"。
4. **改权威文件**：先 `project_config.json`（若涉及状态），再正文。
5. **改索引**：按 §1 的表逐项补齐；报告正文顶部加 `> 更新（YYYY-MM-DD，主题）：...` 一行。
6. **做一致性检查**：跑体检脚本 + §4 的"易错口径"清单。
7. **提交**：`git add -A` → `git commit -F <文件>`（见 §5）。
8. **推送与验证**：`git push origin main` → `git ls-remote origin refs/heads/main` 与 `git rev-parse main` 比对（见 §6）。

---

## 3. 一键体检：`scripts/maintenance/check_docs.ps1`

```powershell
# 本机（Windows PowerShell 5.1，无 pwsh；执行策略禁止直接运行 .ps1）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\maintenance\check_docs.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\maintenance\check_docs.ps1 -Quiet   # 只看失败项
```

> **为什么要带 `-ExecutionPolicy Bypass`**：本机执行策略为 Restricted，直接 `& .\xxx.ps1` 会报 `UnauthorizedAccess`；`pwsh` 未安装，所以用 `powershell`（5.1）。已实测通过。
> 脚本**自解析仓库根**（`$PSScriptRoot` 上两级），可在任意工作目录运行；也可显式传 `-Repo <路径>`。

一次性检查（本机当前实测值见括号）：

| 检查 | 判定 | 本机当前值（2026-09-13） |
| --- | --- | --- |
| `project_config.json` 与所有 `configs/**/*.json`、`experiments/**/{run_manifest,simulation_result,resolved_config}.json` 的 JSON 合法性 | **失败即阻断** | 8 个全部合法 |
| 全库 Markdown **相对链接**（排除 http/mailto/锚点） | **断链必须为 0** | 182 个 md、499 条链接、**0 断链** |
| 汇报稿结构计数（页数 / 证据条目 / 待办勾选项 / Q 条数） | 供人工比对，异常说明改动漏了 | 873 行 / **10 页** / 18 条证据 / 23 项待办 / 9 个 Q |
| `figures/` 下图片的**被引用次数**（找出孤儿图片） | 孤儿图片需处理或说明 | 2 张图、0 孤儿 |
| 术语残留扫描（如把 `metalens` 误写成"金属透镜"） | **提示项**，需人工确认（说明性文字允许出现） | 2 个文件命中，**均为"术语易错提示"的解释性文字** |
| Git 状态（分支 / HEAD / 未提交文件数） | 信息项 | main / HEAD=最新 / 0（提交前会显示待提交数） |

> 脚本源码**保持纯 ASCII**（正则用 `\uXXXX` 转义写中文），避免中文编码在不同 PowerShell 版本下被误读。

**手动版（脚本不可用时）**：链接审计的核心逻辑是——遍历所有 `*.md`，用 `\]\(([^)\s]+)\)` 抓取链接目标，跳过 `http:/mailto:/#`，去掉 `#` 锚点与 `<>`，`UnescapeDataString` 解码 `%20` 等，再相对**该文件所在目录**解析并 `Test-Path`。

---

## 4. 一致性检查清单（本仓库的高频易错口径）

改完文档、提交前逐条自查（这些都是历史上真实出过错的点）：

| # | 口径 | 正确写法 |
| --- | --- | --- |
| 1 | **基片尺寸** | 一律用**直径**：`直径 ≤250 mm`／`D100/D150/D200/D300`；早期文档写的"基片长度 `L ≤ 250 mm`"**实指晶圆直径**（引用旧文档时要加这句说明） |
| 2 | **术语 `metalens`** | 中文写 **超透镜**（meta + lens），**不是"金属透镜"**；`metasurface` = 超表面。全库已统一更正 |
| 3 | **两个 "Huang 2023"** | L01 = *Nat. Nanotechnol.* 18(6) 580（PMMA/Si₃N₄ qBIC 漏波）；Si/1550 ★B1 = *Nat. Commun.* 14, 3433（SOI 全介质 GMR）。**Q 值与 δ 标度不可跨文互用** |
| 4 | **效率口径** | 必须写清是"每超胞提取率 `η_e`"、"总耗散 `η_t`"、"上限 `η_e/η_t`"、还是"出耦合/入射"、"光纤–波导 CE"；**不同口径不可比大小** |
| 5 | **FWHM** | 写清是**空间**（焦斑，µm）还是**光谱**（线宽，nm）还是**时间**（脉宽，fs） |
| 6 | **带隙** | 材料选型说**电子/光学带隙 `E_g`**；共振/能带/BIC 说**光子带隙**——两者不同层（材料 vs 结构） |
| 7 | **波段边界条目** | Si **B9/D8**、SiN **D4**、TiO₂ **T7** 不在 1550 专题内（已迁出）；引用时必须写明实际波段 |
| 8 | **效率 92% / 16% / 9% / 80%** | 92%＝Q1-12 光栅耦合器理论层叠值；16%＝A2 波导超表面**仿真**出耦合；9%/80%＝L02 金属/纯介质的**理论上限**——都不是同一件事 |
| 9 | **报价与规格** | 引用厂商报价必须带**日期（2026-09-11）+ 批量（0.3/0.5 mm 各 10 片）+ "不做其他处理"**；且注明是**询价估算（V）**不是成交价 |
| 10 | **素材版权** | **OA**（如 *Sci. Rep.*、*Nanophotonics*、PMC）图可入库；**非 OA**（*Nat. Nanotechnol.* SI、ACS、De Gruyter 出版版等）**仅限当前 Private 仓库**，且必须在文中标注"公开前移除或替换" |
| 11 | **待补档条目的笔记** | `A7 / B6 / B7 / SiN B4 / F-19 / F-20` 等**原文未入库者**，其"预备笔记"**不得**作为规格或结论引用 |
| 12 | **大文件** | 已求解 `.mph`（如 923 MB）**不入库**；只留可重生成命令 + 未求解 seed + 关键输出 + `run_manifest.json` |

---

## 5. 提交信息：写文件，不要用多行 `-m`

**坑（本仓库已踩过）**：在 `pwsh -Command` 包装里传多行 here-string 给 `git commit -m`，会被**按词拆开**成 pathspec，报一堆 `error: pathspec '...' did not match any file(s)`。

**正确做法**（把信息写到仓库外的临时文件）：

```powershell
$msg = 'C:\Users\Liu\AppData\Local\Temp\dsh_commit_msg.txt'
@'
Short imperative subject line (English, <= 72 chars)

Body: what changed, why, which files/sections are affected, and any
evidence boundary that must be quoted with the change (e.g. "efficiencies
are simulated upper bounds", "figure is private-repo only").

Keep it a plain-English changelog; no need to list every index file.
'@ | Set-Content -Path $msg -Encoding UTF8

git add -A
git commit -F $msg
if ($LASTEXITCODE -ne 0) { Write-Error 'COMMIT FAILED'; exit 1 }
```

**约定**：subject 用**英文祈使句**；正文说清"改了什么 / 为什么 / 边界"；涉及 Private-only 素材或未验证结论时**必须在正文写明**。

---

## 6. 推送与远端验证

### 6.1 正常路径

```powershell
git push origin main
```

远端配置：`origin = git@github.com:Lucas123669/Waveguide_Metasurface_Project.git`（**SSH**，分支 `main`）。仓库里配了 HTTPS 代理 `http://127.0.0.1:7897`，**SSH 推送不走它**。

### 6.2 22 端口被重置时的回退（本会话实测通过）

症状：`git push` 报 `Connection reset by 20.205.243.166 port 22` / `Could not read from remote repository`。

```powershell
# 走 GitHub 官方的 SSH-over-443
git -c 'core.sshCommand=ssh -i C:/Users/Liu/.ssh/id_ed25519_github -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -p 443' `
    push 'ssh://git@ssh.github.com:443/Lucas123669/Waveguide_Metasurface_Project.git' main:main
```

> 用显式 URL 推送**不会**更新本地的 `refs/remotes/origin/main`，所以推送后要手动同步：

```powershell
$remote = git -c 'core.sshCommand=ssh -i C:/Users/Liu/.ssh/id_ed25519_github -o IdentitiesOnly=yes -p 443' `
    ls-remote 'ssh://git@ssh.github.com:443/Lucas123669/Waveguide_Metasurface_Project.git' refs/heads/main
$remoteSha = ($remote -split '\s+')[0]
"remote = $remoteSha"; "local  = $(git rev-parse main)"
if ($remoteSha -eq (git rev-parse main)) { git update-ref refs/remotes/origin/main $remoteSha }
```

### 6.3 多写入者协作（本仓库已真实发生过）

这个仓库**不止一个 AI/人在推**：2026-09-13 有协作者推入了两个项目汇报 PPTX，导致本工作流的推送被拒（non-fast-forward）。规则：

1. **推送被拒时不要 force push**，按顺序处理：

```powershell
$url = 'ssh://git@ssh.github.com:443/Lucas123669/Waveguide_Metasurface_Project.git'
$ssh = 'core.sshCommand=ssh -i C:/Users/Liu/.ssh/id_ed25519_github -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -p 443'

# ① 抓远端到临时 ref（22 端口不通时必用 443；包较大时会花 1-3 分钟，建议后台执行）
git -c $ssh fetch --no-tags $url 'main:refs/remotes/upstream-tmp/main'

# ② 先确认双方改动的文件是否重叠（有重叠才需要手工合并）
git diff --name-status (git merge-base HEAD upstream-tmp/main) upstream-tmp/main   # 对方改了什么
git diff --name-status (git merge-base HEAD upstream-tmp/main) HEAD                # 自己改了什么

# ③ 只把自己的提交搬到对方之上（不改写他人历史）
git rebase upstream-tmp/main

# ④ 重推 + 清理临时 ref
git -c $ssh push $url main:main
git update-ref -d refs/remotes/upstream-tmp/main
```

2. **绝不 `git push --force`**；**绝不 rebase/amend 别人的提交**——只搬自己的。
3. 真冲突时以"**两边内容都保留**"为目标手工合并，**不要**用 `-X ours/theirs` 粗暴取舍；合并后重跑体检脚本。
4. 对方提交信息若为中文，**不要为了统一语言去改写历史**；只要求自己用英文提交。
5. 推送成功后再跑一次 §6.5 的远端校验；若又被人抢先，重复 ①–④。

### 6.4 永久修复（可选，需用户同意）

在 `~/.ssh/config` 的 `Host github.com` 段加入 `HostName ssh.github.com` 与 `Port 443`，此后 `git push` 直接可用。**改用户级配置前先问。**

### 6.5 完成判定

- `git status --short --branch` → 无未提交文件；
- `git rev-parse main` == 远端 SHA；
- 体检脚本**断链 0**、JSON 全通过；
- 报告/索引中的计数与 `project_config.json` 一致。

---

## 7. 常用工具路径（本机实测，2026-09-13）

| 工具 | 路径 | 用途 |
| --- | --- | --- |
| `pdftotext` / `pdftoppm` | `D:\texlive\2024\bin\windows\` | 抽 PDF 文本 / 渲染页面成图（读图表轴、核对数字） |
| Python 3.13 | `C:\Users\Liu\AppData\Local\Programs\Python\Python313\python.exe` | 批量替换、统计、脚本化检查（**中文批量改写优先用 Python 脚本文件**，见 §8） |
| COMSOL 6.3 | `D:\comsol.6.3\bin\win64\comsol.exe` | 仿真（求解产物不入库） |
| 仓库 | `E:\Waveguide_Metasurface_Project` | 工作目录 |
| AI 附件（只读） | `C:\Users\Liu\.dsh\attachments\...` | 用户贴图的规范化副本 |

---

## 8. 已知坑与对策（全部为真实踩坑记录）

| 坑 | 现象 | 对策 |
| --- | --- | --- |
| 多行 `-m` 提交信息 | pathspec 报错、提交失败 | 写文件 + `git commit -F`（§5） |
| 编辑前未读文件 | 工具报 "file changed since read" / 拒绝写入 | 先 `read` 再 `edit`；文件被其它步骤改过后**重新读** |
| 锚点不唯一 / 含不可见字符 | `edit` 报多处匹配或匹配失败 | 用**更长且唯一**的锚点；必要时先 grep 行号再定位 |
| 控制台中文乱码 | `Get-Content` 输出变成"闈㈠舰" | **不一定是文件坏了**：用 `read` 工具确认；只有 `read` 也乱码才需修 |
| pwsh 命令里的中文正则 | 有时静默匹配不到 | 把中文匹配/替换写成 **Python 脚本文件**（用 `write` 落盘再执行），或正则用 `\uXXXX` 转义 |
| CRLF 警告 | `LF will be replaced by CRLF` | **无害**，不需处理 |
| SSH 22 被重置 | `Connection reset ... port 22` | 走 443 回退（§6.2） |
| 图片未被引用 | 入库后没有任何 md 引用 | 体检脚本会列出孤儿图片 |
| 目录迁移 | 迁移后出现 6 处断链（历史事故） | 迁移后**必须**重跑链接审计 |
| 前端/服务器误解 | 误以为改了要"重启服务" | 本仓库是**纯文档+代码仓库**，无网络服务；改动只影响 git 内容 |
| 术语误译扩散 | "金属透镜"曾散落 24 个文件 69 处 | 批量修正后用体检脚本的术语扫描复查 |
| **执行策略禁止跑脚本** | `& .\x.ps1` 报 `UnauthorizedAccess`（Restricted） | 加 `powershell -NoProfile -ExecutionPolicy Bypass -File` 前缀 |
| **`pwsh` 不存在** | `pwsh : 无法将"pwsh"项识别为...` | 本机只有 Windows PowerShell 5.1，用 `powershell` 调用 |
| **PS 5.1 的 `$PSScriptRoot` 陷阱** | 写在 `param()` 默认值里会取到空串 | 在脚本体里解析根路径（`check_docs.ps1` 已按此实现） |
| 脚本里写中文路径 | 单引号字符串里的 `\uXXXX` **不会**被解码成中文 | 用**ASCII 前缀**定位文件（如 `-Filter '2026-09-09_1550nm*.md'`），中文只出现在 `\uXXXX` 正则里 |

---

## 9. 精读/阅读笔记的模板与命名

| 类型 | 文件名 | 内容骨架 |
| --- | --- | --- |
| 速览笔记 | `阅读笔记_<编号>_<作者>_<年份>.md` | 论文信息 / 一句话总结 / 结构与方法 / 关键结果 / 对项目的启示 / 局限 |
| **精读笔记** | `精读笔记_<编号>_<作者>_<年份>_构思结构与术语.md` | ①作者的构思（问题意识、推导链、论证策略、作者自报边界）②结构安排（章节地图 + 图表清单 + 可借鉴的结构特点）③内容的递进（逐节逻辑 + 关键数字）④专业术语表（面向项目读者）⑤关键数字速查 ⑥本项目复现/使用状态 ⑦对项目的启示 ⑧局限与待核对 ⑨术语易错提示 |
| 专题对比 | `docs/reports/literature/<日期>_对比_<甲>_vs_<乙>.md` | 对象确认 / 共同点 / 参数逐项对照 / 各自利弊 / 应用差异 / 对项目的结论 / 证据边界 / 来源 |

**精读笔记的额外要求**：凡发现**原文内部不一致**（例如正文写 `f = 5 µm`、SI 图注写 `3 µm`；或按公式核算与图中方向矛盾），**必须在"局限与待核对"里显式记录**，不要把矛盾悄悄抹平。

---

## 10. Definition of Done

- [ ] 权威文件已改（`project_config.json` 若涉及状态；正文如常）
- [ ] §1 表中的**所有索引**已同步（含报告顶部"更新（日期）"行）
- [ ] 新增笔记/文档的**命名**符合 §9；旧笔记加了指向新文档的链接
- [ ] §4 的 12 条口径逐条自查通过
- [ ] 体检脚本：**JSON 全通过、断链 0**；结构计数与预期一致
- [ ] 提交信息（英文）说明了"改了什么 + 为什么 + 边界"
- [ ] 已推送，且 `local SHA == remote SHA`；工作区干净
