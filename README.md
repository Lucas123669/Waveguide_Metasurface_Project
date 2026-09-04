# Waveguide Metasurface Project（波导 + 超表面：辐射光控制）

> 本文件是项目入口。机器可读的单一状态源是 `project_config.json`；本文中的状态表由人工同步维护，若不一致以 `project_config.json` 为准。

## 快速导航

| 我要做什么 | 入口 |
| --- | --- |
| 接手项目 / 找下一步 | [AI 接手指南](docs/guides/AI_接手指南.md) |
| 了解文档体系 | [文档中心](docs/README.md) |
| 运行仿真或后处理 | [脚本入口](scripts/README.md) |
| 选择 seed / calibrated 参数 | [配置说明](configs/README.md) |
| 进入论文复现轨道 | [实验轨道](experiments/README.md) |
| 查论文、笔记和材料体系 | [文献库](literature/README.md) |

项目主链路为：**文献依据 → 决策 → 配置 → 代码/脚本 → 实验结果 → 报告 → 制备**。每类信息只在一个主目录维护，其余位置使用链接。

## 1. 项目目标

在波导结构上集成超表面（metasurface），实现对辐射光（radiated light）的调控：辐射方向（出射角度）、偏振状态、相位/波前整形、辐射效率。任务最终包含两部分：实现（设计 + 仿真）与制备（实验）。

## 2. 两条实验轨道（结构分轨）

仓库按论文复现路线分轨，物理模型、材料体系与仿真目标互不混淆：

| 轨道 | 论文 | 材料体系 | 目标 | 当前状态 |
| --- | --- | --- | --- | --- |
| `experiments/l01_huang_2023/` | Huang et al., Nat. Nanotechnol. 18, 580 (2023) | PMMA / Si₃N₄ 双层波导 + qBIC 椭圆孔 | 片上漏波超表面（LWM）全参量辐射控制 | case_001 平板模分析完成；下一动作 case_002 元胞库 |
| `experiments/l02_guo_2020/` | Guo et al., Sci. Adv. 6, eabb4142 (2020) | Si 波导 + Au/SiO₂/Au meta-atom | beam deflector + metalens（COMSOL 自动化复现） | 45° 偏转结果已接受（见 run_manifest）；metalens 待复现 |

## 3. 当前状态（2026-09-03）

- L01 轨道：case_001 平板模分析已完成（TM₀ n_eff≈1.5507、TE₀ n_eff≈1.6759 @1.55 μm，见 `experiments/l01_huang_2023/case_001_slab_mode/`）；下一动作 case_002（元胞库：δ/α/D₀ 扫描 + 容差展宽）。
- L02 轨道：Guo 2020 COMSOL 工作流已并入；45° 右上偏转结果已接受（15 supercell、897.331 nm 周期、模拟角谱峰 45.0147°，配置见 `configs/calibrated/`，结果见 `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/`）。
- 综合分析与初步结构报告：`docs/reports/design/2026-08-25_L01超表面波导综合分析与初步结构.md`。
- 文献：2026-09-02 新增 F-11~F-27（F08 制造综述案例论文 17 篇），按顶层材料体系收纳于 `literature/材料体系分类/<体系>/`（`pdfs/` + 阅读笔记）；15 篇已下载并精读，F-19/F-20 出版社反爬待浏览器下载。F08 案例统计汇报见 `docs/reports/literature/2026-09-02_F08制造案例统计与汇报.md`。
- Si 1550 nm 专题：29 篇已完成年份/期刊标注与逐篇项目笔记；本地 PDF 26 篇（专题目录 25 篇 + 复用 L02 1 篇），A7、B6、B7 待补档。专题索引见 `literature/材料体系分类/Si/1550波段/README.md`。

## 4. 目录结构

```text
Waveguide_Metasurface_Project/
├── README.md                  # 项目入口（本文）
├── project_config.json        # 机器可读单一状态源
├── pyproject.toml             # Python 包（src/gwm_workflow）与依赖
├── LICENSE / NOTICE.md        # 代码许可与第三方资产边界
├── CITATION.cff               # 引用信息
├── src/gwm_workflow/          # L02 复现核心模块（config/backend/workspace 流水线）
├── configs/
│   ├── schemas/               # 仿真配置 JSON Schema
│   ├── seeds/                 # 论文种子参数（paper_exact / figure_estimate）
│   └── calibrated/            # 已校准配置（最终接受结果所用）
├── experiments/
│   ├── l01_huang_2023/        # L01 轨道（case_001…）
│   └── l02_guo_2020/          # L02 轨道（beam_deflector / metalens）
├── scripts/
│   ├── simulation/            # 建模与求解 CLI
│   ├── postprocess/           # 结果重处理与绘图
│   └── literature/            # 文献下载、manifest 与统计
├── tests/
│   ├── unit/                  # 纯 Python 单元测试
│   ├── regression/            # 已知解回归测试
│   └── integration/           # 集成测试（占位）
├── docs/
│   ├── README.md              # 文档导航与边界
│   ├── architecture.md        # 架构说明
│   ├── guides/                # 接手与文献库指南
│   ├── decisions/             # 带日期的决策与工艺记录
│   ├── reports/               # design/simulation/fabrication/literature
│   ├── templates/             # 仿真与记录模板
│   └── archive/               # 失效但需追溯的旧约定
├── references/
│   ├── references.bib         # 论文 BibTeX
│   └── README.md              # 论文与资产策略
├── literature/                # 论文 PDF、阅读笔记与专题索引
│   └── 材料体系分类/          # 按顶层材料体系（Si/SiN/PMMA/TiO₂）分类的文献索引
├── artifacts/                 # 大型产物的索引与策略说明
└── fabrication/               # 工艺参考资料
```

## 5. 快速开始

```bash
# 安装 Python 包（src/gwm_workflow）
pip install -e .

# 无 COMSOL 时验证流水线/理论逻辑（mock backend）
python scripts/simulation/run_single.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json --backend mock

# L01 平板模（纯 Python，无需 COMSOL）
python experiments/l01_huang_2023/case_001_slab_mode/scripts/slab_mode_solver.py \
  --config experiments/l01_huang_2023/case_001_slab_mode/params.json \
  --output experiments/l01_huang_2023/case_001_slab_mode/results/result.json

# 运行测试
pytest tests/
```

## 6. 复现证据链（run_manifest）

每个已接受的结果目录包含 `run_manifest.json`，记录：输入配置 SHA、Git commit、运行环境/版本、结果校验和。任何已接受结果都可追溯到配置、代码提交与输入资产（见 `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/run_manifest.json`）。

## 7. 资产与许可策略

- 普通 Git 保存源代码、配置、文档与轻量数据。
- 大型二进制（`.mph`、`.npz`、论文 PDF）当前随仓库保存；如需瘦身可迁移至 Git LFS / Release（策略见 `artifacts/README.md` 与 `references/README.md`）。
- 第三方论文与 COMSOL 许可约束的资产不随代码授权，边界见 `NOTICE.md`。

## 8. 给未来 AI 助手的接手指引

1. 先读本文件与 `project_config.json`（单一状态源）。
2. 按实验轨道进入：L01 看 `experiments/l01_huang_2023/`，L02 看 `experiments/l02_guo_2020/`。
3. 读 `docs/README.md`，再按任务进入 `docs/decisions/` 或 `docs/reports/*/`。
4. 重要决策记录到 `docs/decisions/` 下带日期文件中，并同步更新 `project_config.json` 与本文状态表。
5. 中文交流；技术术语保留英文。
