# Waveguide Metasurface Project（波导 + 超表面辐射光控制）

> 项目入口。机器可读的当前状态以 [`project_config.json`](project_config.json) 为准；结构和口径变更见 [`CHANGELOG.md`](CHANGELOG.md)。

## 快速导航

| 任务 | 入口 |
| --- | --- |
| 接手项目 / 找下一步 | [AI 接手指南](docs/guides/AI_接手指南.md) |
| **改文档并推送到 GitHub** | [AI 文档更新与推送工作流](docs/guides/AI_文档更新与推送工作流.md)（🔧 附一键体检脚本 `scripts/maintenance/check_docs.ps1`） |
| 了解文档体系 | [文档中心](docs/README.md) |
| 运行仿真或后处理 | [脚本入口](scripts/README.md) |
| 选择 seed / calibrated 参数 | [配置说明](configs/README.md) |
| 进入论文复现轨道 | [实验轨道](experiments/README.md) |
| 咨询 EBL 加工与仿真设备 | [问题清单与回填表](docs/reports/consultation/2026-09-14_EBL加工与仿真设备咨询问题清单.md) |
| 查看近期文献筛选与项目影响 | [2026-09-14 文献筛选报告](docs/reports/literature/2026-09-14_近期相关文献筛选与项目影响.md) |
| 学习超表面设计并迁移到 SiN | [Q1-18 平面光学超表面教程精读报告](docs/reports/literature/2026-10-09_Q1-18_平面光学超表面教程精读报告.md)（逐章解读、公式核验、SiN/双波长执行计划） |
| 采购 HPFS 7980 衬底 | [面积推导与采购建议](docs/reports/fabrication/2026-09-21_HPFS7980衬底面积与采购建议.md) |
| 查看单面 a-Si / Cr 制备流程图 | [两种 Cr 硬掩膜方案](docs/reports/fabrication/2026-10-22_单面非晶硅_Cr硬掩膜两种工艺方案.md)（后沉积 lift-off / 预沉积刻蚀转移；待平台确认） |
| 生成微纳加工 DXF 版图 | [有限六角光子晶体三角空气孔版图工作流](blueprints/README.md) |
| 选择版图路线 / 交给其他 AI | [版图工作流总览](docs/guides/版图生成工作流.md) · [可复制接手提示词](docs/guides/AI_版图工作流接手提示词.md) |
| 生成圆柱超透镜 DXF/GDS | [独立圆柱相位库版图工作流](metalens_blueprints/README.md)（MATLAB/CST CSV 接口；工程预览） |
| 按元胞形状选择版图扩展路线 | [七类形状、超胞组合与工作流扩展说明](docs/reports/design/2026-10-14_超表面元胞形状分类与版图工作流扩展说明.md)（含原创示意图） |
| 按任务、材料、波段查文献 | [文献多维分类索引](literature/多维分类索引.md) |
| 查水下项目组的偏振结构光文献 | [UW01–UW03 精读专题](literature/水下项目组/README.md)（双通道融合、四路并行投影、TiO₂ 三步移相；水下迁移待验证） |
| 查编号、DOI 与入库状态 | [文献清单](literature/文献清单.md) |

项目主链路为：**文献依据 → 决策 → 配置 → 代码/脚本 → 实验结果 → 报告 → 制备**。每类信息只维护一个权威入口，其他位置通过链接复用。

## 1. 项目目标

在波导结构上集成超表面，实现对辐射方向、偏振、相位/波前和效率的调控。项目包含设计与仿真、微纳加工与实验验证两部分。

## 2. 实验轨道

| 轨道 | 论文与平台 | 目标 | 当前状态 / 下一步 |
| --- | --- | --- | --- |
| [`l01_huang_2023`](experiments/l01_huang_2023/) | Huang 2023；PMMA / Si₃N₄ 双层波导 + qBIC 椭圆孔 | 片上漏波超表面全参量辐射控制 | case_001 平板模完成；下一步 case_002 元胞库 |
| [`l02_guo_2020`](experiments/l02_guo_2020/) | Guo 2020；Si 波导 + Au/SiO₂/Au meta-atom | beam deflector + metalens | 45° 偏转已接受；下一步 metalens 与相位库 |

## 3. 当前状态

- **L01**：TM₀ `n_eff≈1.5507`、TE₀ `n_eff≈1.6759`（1.55 μm）的平板模分析已完成；进入 δ/α/D₀ 扫描与容差展宽。
- **L02**：15 个 supercell、周期 897.331 nm 的模型得到 `+45.0147°` 角谱峰；结果与配置已归档。
- **材料与制备**：已形成玻璃基 Si 起步路线，以及 SiN、TiO₂、PMMA 的分阶段迁移方案；HPFS 7980 常规研发片建议 20×20×0.5 mm，整片设备路线采用 D100；见 [fabrication 报告](docs/reports/fabrication/)。
- **DXF 版图工作流**：新增独立的有限六角光子晶体三角空气孔版图生成器，覆盖几何构建、SEM 修正接口、dose 接口、DRC、DXF 回读及 PNG 预览；当前仅为 `engineering_preview`，尚未绑定 L01/L02，剂量、极性和生产 DRC 阈值待标定。
- **圆柱版图路线（2026-10-20 整理）**：独立 `metalens_blueprints/` 已实现外部相位库选态、正方晶格聚焦、完整轮廓口径筛选、DXF/可选层级 GDS 与追溯报告，强制工程预览；矩形 Python 示例、XLSX 库与圆环/椭圆/PB 扩展尚未接入，不代表新增光学或加工结果。
- **合作演示路线（2026-09-28）**：先做 MOT、后拓展光镊；近期集中 Si/Si₃N₄，按 1064 nm → 852 nm 推进，TiO₂ 暂缓。工艺口头建议仍需平台确认与试片；见 [研讨纪要](docs/reports/consultation/2026-09-28_片上光波导与超表面工艺研讨纪要.md)。
- **文献库**：使用“稳定编号 + 多维标签”；Q1-13 至 Q1-17 覆盖全参量 Jones 矩阵、级联 qBIC 光谱路由、EBL/PMMA、多模容差与单向辐射；新增 Q1-18 教程精读，连接相位/非局域/设计/聚焦/全息与 SiN 1064→852 nm 路线，含原文公式与材料案例核验，不代表新增器件结果。
- **待补原文**：以 [文献清单](literature/文献清单.md) 和各专题 README 的状态为准，不在本页重复维护数量。
- **水下项目组文献**：三篇指定论文已有规范精读与题录，区分空气实验、水下迁移和原文疑点；公开保存 UW03 的 CC BY 4.0 PDF，UW01/UW02 仅保留笔记与 DOI。未改变主线波长、加工规格或已接受实验状态。

## 4. 目录边界

```text
Waveguide_Metasurface_Project/
├── README.md                  # 当前入口
├── CHANGELOG.md               # 影响使用方式的项目级变更
├── project_config.json        # 机器可读单一状态源
├── src/gwm_workflow/          # L02 复现核心模块
├── configs/                   # schemas / seeds / calibrated
├── experiments/               # 按论文拆分的复现轨道
├── blueprints/                # 独立 DXF 微纳加工版图生成器
├── metalens_blueprints/       # 独立圆柱超透镜相位库与 DXF/GDS 工作流
├── scripts/                   # simulation / postprocess / literature
├── tests/                     # unit / regression / integration
├── docs/                      # 指南、决策、报告与模板
├── references/                # BibTeX 与资产策略
├── literature/                # PDF、规范笔记与多维索引
├── artifacts/                 # 大型产物索引与存储策略
└── fabrication/               # 工艺参考资料
```

## 5. 快速开始

```bash
pip install -e .

# 无 COMSOL 时验证工作流
python scripts/simulation/run_single.py \
  --config configs/seeds/guo2020_beam_deflector_paper_seed.json \
  --backend mock

# L01 平板模
python experiments/l01_huang_2023/case_001_slab_mode/scripts/slab_mode_solver.py \
  --config experiments/l01_huang_2023/case_001_slab_mode/params.json \
  --output experiments/l01_huang_2023/case_001_slab_mode/results/result.json

pytest tests/
```

DXF 版图工作流使用独立环境，详见 [`blueprints/README.md`](blueprints/README.md)：

```powershell
cd blueprints
uv sync
uv run python main\run_blueprint.py --preflight-only
uv run python main\run_blueprint.py
```

## 6. 复现与资产规则

- 已接受结果使用 `run_manifest.json` 记录输入配置、Git commit、运行环境和结果校验和。
- 普通 Git 保存代码、配置、文档和轻量数据；大型二进制的策略见 [artifacts](artifacts/README.md) 与 [references](references/README.md)。
- 第三方论文和受 COMSOL 许可约束的资产不随代码授权，边界见 [NOTICE.md](NOTICE.md)。
- 新增文献时只保存一份 PDF、每个 DOI 只维护一份规范笔记；跨材料或专题用索引链接复用。

## 7. 接手约定

1. 先读本页和 `project_config.json`。
2. 按任务进入对应实验轨道，再阅读相关 decision/report。
3. 重要结构或口径变化写入 `docs/decisions/`，同步更新 `project_config.json`、本页与 `CHANGELOG.md`。
4. 文献分类遵循 [多维分类索引](literature/多维分类索引.md)，不要根据目录名推断唯一材料、波段或期刊分区。
