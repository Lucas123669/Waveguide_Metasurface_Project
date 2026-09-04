# Waveguide Metasurface Project｜接手指南

> 更新：2026-09-03  
> 原则：先确认状态与证据链，再修改配置或运行模型；本地路径不固定到某个盘符。

## 1. 五分钟接手顺序

1. 读根目录 `README.md`，确认项目目标和当前两个实验轨道。
2. 读 `project_config.json`；它是机器可读的单一状态源。
3. 读 `docs/README.md` 和 `docs/architecture.md`，确认信息应放在哪一层。
4. 进入 `experiments/l01_huang_2023/` 或 `experiments/l02_guo_2020/` 的轨道 README。
5. 查看 `docs/decisions/` 最新记录，以及与任务对应的 `docs/reports/<category>/`。

## 2. 项目一句话

在 waveguide 上集成 metasurface，控制辐射光的方向、偏振、相位/波前和效率；工作链分为设计/仿真和制造/实验，并以论文复现轨道推进。

## 3. 信息流与目录边界

```text
literature/             论文、阅读笔记、材料/波段专题
        ↓
docs/decisions/         已确认的选择、假设与工艺结论
        ↓
configs/                schema → paper seeds → calibrated inputs
        ↓
src/gwm_workflow/       可复用计算逻辑
scripts/                simulation / postprocess / literature 入口
        ↓
experiments/            按论文轨道保存输入快照、模型、数据和 run manifest
        ↓
docs/reports/           design / simulation / fabrication / literature 解释与汇报
        ↓
fabrication/            后续版图、工艺卡和表征记录
```

边界规则：

- `src/` 不放一次性参数；`scripts/` 不复制核心算法。
- `configs/seeds/` 保留论文值/估读值/假设的来源标签；校准值另存 `configs/calibrated/`。
- `experiments/` 是运行证据源，`docs/reports/` 只解释它，不复制结果数据。
- `literature/` 保存 PDF 和笔记；`references/` 保存规范化 BibTeX 与许可策略。
- 历史 `resolved_config.json` 和 `run_manifest.json` 不因目录重构回写。

## 4. 实验轨道

### L01｜Huang 2023｜PMMA / Si₃N₄ qBIC

- 路径：`experiments/l01_huang_2023/`
- 当前：case_001 slab mode 已完成；TM₀ `n_eff≈1.5507`、TE₀ `n_eff≈1.6759` @ 1.55 μm。
- 下一步：case_002 unit-cell library，扫描 `D₀ / δ / α`，验证 `Q∝δ⁻²`、Jones 响应与 `σ=1/2/3 nm` 容差展宽。
- 设计分析：`docs/reports/design/2026-08-25_L01超表面波导综合分析与初步结构.md`。

### L02｜Guo 2020｜Si waveguide + Au/SiO₂/Au

- 路径：`experiments/l02_guo_2020/`
- 当前：45° beam deflector 已接受；15 supercells、897.331 nm 周期、角谱峰 +45.0147°。
- 证据：`experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/run_manifest.json`。
- 下一步：metalens 复现和 Au/SiO₂/Au phase/amplitude library 校准。
- 结果说明：`docs/reports/simulation/right45_air2x_result.md`。

## 5. 文献组织

- `L01–L05`：主线与辅助论文，位于 `literature/` 根部。
- `Q1-01–Q1-11`：L01 相关物理/设计，位于 `literature/Q1_L01相关/`。
- `F-01–F-10`：L01 相关加工，位于 `literature/Q1_工艺_L01相关/`。
- `F-11–F-27`：F08 制造案例，按材料放在 `literature/材料体系分类/<体系>/`。
- Si 1550 nm A/B/C/D 专题：29 篇已建索引与笔记，本地 PDF 26 篇；入口 `literature/材料体系分类/Si/1550波段/README.md`。
- 总清单：`literature/文献清单.md`；BibTeX：`references/references.bib`。

命名：PDF 使用 `编号_第一作者_年份_短标题.pdf`；笔记使用 `阅读笔记_编号_作者_年份.md`。

## 6. 常用命令

```bash
pip install -e .

# 无 COMSOL：验证 config → workflow → result
python scripts/simulation/run_single.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json --backend mock

# 生成模型计划 / 相位表
python scripts/simulation/plan_model.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json
python scripts/simulation/build_phase_targets.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json

# 测试
python -m pytest -q
```

脚本总表见 `scripts/README.md`。COMSOL 工作依赖本机安装与相应许可证，不把可执行程序路径写死到说明文档中。

## 7. 证据链规则

每个“已接受”结果至少应包含：

- 执行时的 resolved config；
- 输入配置 SHA-256；
- 代码版本或明确的源文件校验信息；
- 环境与软件版本；
- 关键输出及其校验和；
- `run_manifest.json` 中的验收结论。

大型已求解 COMSOL 文件若不入库，必须留下可重新生成的命令、未求解 seed/model 和关键输出。

## 8. 更新约定

- 里程碑、下一动作、文献集合统计改变：先更新 `project_config.json`，再同步根 README 和轨道 README。
- 设计取舍或目录规则改变：在 `docs/decisions/` 新建 `YYYY-MM-DD_主题.md`。
- 结果解释进入 `docs/reports/<category>/`；原始数据始终进入对应 `experiments/` 轨道。
- 新 CLI 按职责进入 `scripts/simulation/`、`scripts/postprocess/` 或 `scripts/literature/`。
- 不删除已有证据；确需迁移时同步更新活动配置和文档引用，并验证链接与测试。

## 9. 当前优先级

1. L01 case_002 qBIC unit-cell library。
2. L02 metalens 复现与 meta-atom phase/amplitude library。
3. 将制造约束（CD、侧壁角、粗糙、层厚偏差）前置到参数扫描。
4. 补齐 Si 1550 nm 专题 A7、B6、B7 PDF，并把预备笔记升级为原文精读。
