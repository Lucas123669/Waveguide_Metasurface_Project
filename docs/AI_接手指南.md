# Waveguide_Metasurface_Project —— AI 接手指南（完整项目简介）

> 编写日期：2026-09-02 ｜ 面向：接手的 AI 助手（任何模型版本）与项目成员
> 仓库：https://github.com/Lucas123669/Waveguide_Metasurface_Project （本地：`E:\Waveguide_Metasurface_Project`）
> 总原则：**先读本文件 → 再读 `project_config.json`（单一状态源）与 `README.md`，然后按轨道进入。**

---

## 1. 项目一句话概述

在波导结构上集成超表面（metasurface），实现对**辐射光**（出射方向、偏振、相位/波前、效率）的精确控制；任务分**设计+仿真**与**制备（微纳加工）**两大部分，按"论文复现轨道"（L01/L02）与"顶层材料体系"（Si/SiN/PMMA/TiO₂）双维度组织。

## 2. 接手前 5 分钟（必读顺序）

1. 本文件（AI 接手指南）——全局地图；
2. `project_config.json` —— **机器可读单一状态源**（轨道状态、文献、配置，改动先更新它）；
3. `README.md` —— 人类/AI 共用的项目入口；
4. `docs/architecture.md` —— 代码流水线架构；
5. `docs/decisions/` 最新决策笔记、`docs/reports/` 综合报告与汇报稿；
6. 按任务进入 `experiments/` 对应轨道。

## 3. 目录结构

```text
Waveguide_Metasurface_Project/
├── README.md                  # 项目入口（状态表以 project_config.json 为准）
├── project_config.json        # 单一状态源（schema v2）
├── pyproject.toml / requirements.txt
├── LICENSE / NOTICE.md / CITATION.cff
├── src/gwm_workflow/          # L02 复现核心模块（config/backend/workspace 流水线）
├── configs/
│   ├── schemas/               # 仿真配置 JSON Schema
│   ├── seeds/                 # 论文种子参数（paper_exact / figure_estimate）
│   └── calibrated/            # 已校准配置（最终接受结果所用）
├── experiments/
│   ├── l01_huang_2023/        # L01 轨道（case_001…）
│   └── l02_guo_2020/          # L02 轨道（beam_deflector / metalens）
├── scripts/                   # CLI：建模、求解、后处理
├── tests/                     # unit / regression / integration
├── docs/
│   ├── architecture.md
│   ├── decisions/             # 决策与工艺记录（原 notes/，带日期）
│   ├── reports/               # 综合报告、结果说明、汇报稿/提纲
│   ├── literature-notes/      # 文献笔记索引
│   └── references/            # 参数模板等
├── references/                # references.bib + 论文/资产策略
├── literature/                # PDF 与阅读笔记（L/Q1/F 系列）
│   └── 材料体系分类/           # Si/SiN/PMMA/TiO₂/通用交叉 索引（PDF 不复制）
├── artifacts/                 # 大型产物策略（LFS 建议）
└── fabrication/               # 版图/工艺/测试记录（预留）
```

> 注意：本地磁盘顶层可能残留 `comsol_workflow/、notes/、reports/、simulations/、workspaces/、.pytest_cache/` 等**空壳或被忽略目录**（重构迁移后遗留，`.gitignore` 已忽略，git 不跟踪），可忽略，不必清理或操作。

## 4. 两条实验轨道（状态与下一步）

### 4.1 L01 轨道（Huang 2023, Nat. Nanotechnol.）—— PMMA/Si₃N₄ qBIC 漏波超表面

- 器件：PMMA 300 nm（顶层超表面 + EBL 胶）/ PECVD Si₃N₄ 300 nm / 180 μm 熔融石英；λ=1.55 μm；椭圆孔对 qBIC；Q=C/δ²（C=950 μm²）。
- **状态**：case_001 平板模分析完成（TM₀ n_eff≈1.5507、TE₀≈1.6759）。
- **下一步（优先）**：case_002 元胞库仿真——0.8×0.8 μm 元胞、4 椭圆孔（p2），扫 D₀/δ/α，验证 Q∝δ⁻² 与 Jones 公式 (E_x,E_y)=δ(a_x sin2α, a_y cos2α)，加 σ=1/2/3 nm 容差展宽。
- 加工关键结论：PMMA 950K（AR-P 679.04）300 nm；100 keV 750 μC/cm²（20 kV 200–250）；3:1 或 7:3 IPA:水显影；Espacer 300Z 防充电；**孔径 400 μm 与 4.8 mm 锥形为 L01 原文给出，孔数为"数十万–百万量级"估算（勿当文献数据）**。

### 4.2 L02 轨道（Guo 2020, Sci. Adv.）—— Si 波导 + Au/SiO₂/Au

- **状态**：45° 右上偏转结果**已接受**（15 supercell、897.331 nm 周期、模拟角谱峰 +45.0147°），证据链见 `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/run_manifest.json`。
- **下一步**：metalens 复现 + Au/SiO₂/Au 相位库校准。
- 代码：`src/gwm_workflow`（config→phase target→backend→artifact），`scripts/` CLI，无 COMSOL 时 `--backend mock` 可验证流程。

## 5. 材料体系任务组织（2026-09-01 起）

按**顶层超表面材料**建立任务维度，索引在 `literature/材料体系分类/`：

| 体系 | 顶层材料 | 主文献 |
| --- | --- | --- |
| Si | 硅 | L02、Q1-05、Q1-11、F-03、F-05、F-10 |
| SiN | 氮化硅 | L03、Q1-03、Q1-04、F-01、F-02、F-04、F-07 |
| PMMA | PMMA | L01、L04、L05、F-06 |
| TiO2 | 二氧化钛 | 暂无专属文献（F-08 含工艺案例），待补充 |
| 通用交叉 | 物理/方法/综述 | Q1-01/02/06/07/08/09/10、F-08、F-09 |

每体系 README 含：定位、主文献表（角色+路径）、关键工艺要点、待补充文献。

## 6. 文献库体系

- **L 系列（L01–L05）**：主论文与辅助文献，PDF+笔记在 `literature/` 根（L03=SiN 参考、L04/L05=PMMA 参考）。
- **Q1 系列（Q1-01~11）**：一区/与 L01 强相关设计物理，在 `literature/Q1_L01相关/`（**11 篇 PDF 全部到位、笔记全部完成**）。
- **F 系列（F-01~10）**：一区/微纳加工工艺，在 `literature/Q1_工艺_L01相关/`（10 篇 PDF 全部到位、笔记全部完成）。
- 总清单：`literature/文献清单.md`；BibTeX：`references/references.bib`。
- 命名规范：PDF `L编号/Q1编号/F编号_作者_年份_简短标题.pdf`；笔记 `阅读笔记_编号_作者_年份.md`；补充材料 `编号_作者_年份_补充材料.pdf`。

## 7. 状态管理与更新约定（重要）

- `project_config.json` 是**唯一状态源**（schema v2）；README 状态表人工同步并在开头注明"以 project_config 为准"。
- 任何里程碑变化（case 完成、结果被接受、新文献）→ 先更新 project_config.json → 再同步 README 与轨道 README → 提交推送。
- 文档引用文献用 `编号@出处`（如 `L01@S.6`），编号速查见各文献笔记与 `references/references.bib`。

## 8. 复现与证据链

- 每个已接受结果目录含 `run_manifest.json`：配置 SHA256、Git commit、环境、输入文件 SHA256——结果可追溯到源头。
- 生成/更新 calibrated 配置与 run_manifest 的脚本思路见 `work/gen_artifacts.py`（本机工作目录，非仓库内）。

## 9. 关键技术结论速查（工艺）

- PMMA：950K / AR-P 679.04；300 nm 厚度=波导层=孔深；剂量随电压换算；水稀释 IPA 显影；Espacer 防充电；版图避免尖角（膜易撕裂）。
- Si₃N₄：PECVD 300 °C（L01/F-02）vs LPCVD（F-01 高均匀）；应力管理（trench）；刻蚀 CHF₃/SF₆/N₂。
- 制造技术体系：见 F-08（标准/先进/大规模/极端四层；"分辨率-吞吐-成本"三角；DUV 为量产答案）。
- Q/容差：Q∝δ⁻² 且 Q∝σ⁻²；工艺几何标准差预算 σ≤1–2 nm；椭圆单元最鲁棒；merged BIC 可降敏。

## 10. 环境与工具

- 本机：Python 3.13（系统）+ Codex bundled Python 3.12（numpy/pytest 等）；COMSOL 6.3（`D:\comsol.6.3\bin\win64\comsol.exe`）。
- GitHub：仓库走本机代理 `http://127.0.0.1:7897`（已配置在 `.git/config`）；推送失败多为瞬时网络问题，重试即可。
- 识图：无原生视觉模型请用技能 `claude-vision-skill`（`node .../scripts/vision.js <图片路径> <问题>`）；图片须以**本地文件路径**形式传入。
- 文件编辑：统一用 `apply_patch`；批量机械改写可用脚本；不用 `cat` 写文件。

## 11. 工作规范

- 中文交流；技术术语保留英文（metasurface、waveguide、EBL、qBIC 等）。
- 提交信息用英文、描述性，一个主题一次提交。
- 不删除已有内容；重命名/移动先说明。
- 遇到网络推送失败：检查 7897 代理端口 → 重试。
- 大二进制（PDF/.mph/.npz）继续留在 Git（用户要求）；如需瘦身按 `artifacts/README.md` 走 LFS（需用户确认）。

## 12. 常见任务 SOP

### A. 新增一篇文献
1. 按命名规范放 PDF（L/Q1/F 系列或补充材料）；
2. 写 `阅读笔记_编号_作者_年份.md`（按 `literature/阅读笔记模板.md`）；
3. 更新 `literature/文献清单.md` 与 `project_config.json`（对应系列数组）；
4. 若属于四体系，更新 `literature/材料体系分类/对应体系/README.md`；
5. 提交推送。

### B. 推进仿真 case
1. 在轨道目录建 `case_XXX/`（含 README、params.json、scripts/、results/）；
2. 跑通后把结果写入 result.json / results.md（程序生成，勿手编）；
3. 更新 project_config.json 的 cases 状态与"下一动作"；
4. 结果若"接受"，补 `run_manifest.json`；
5. 提交推送。

### C. 汇报相关
- 综合报告/提纲/汇报稿均在 `docs/reports/`（带日期命名）；修改后同步推送。

## 13. 当前待办/开放问题

- case_002 元胞库仿真（L01 轨道最高优先）。
- L02 metalens 复现 + 相位库校准。
- TiO₂ 体系专属文献收集（metalens/高深宽比刻蚀）。
- PMMA 1.55 μm 精确 n/k 实测（L04 SI Fig. S1 为图形数据）。
- 确认 EBL 设备/电压与 AEMD 平台条件（工艺开工前提）。
