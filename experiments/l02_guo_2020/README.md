# L02 轨道：Guo et al. 2020（Molding free-space light with guided wave-driven metasurfaces）

## 轨道状态

- 当前：**45° 右上偏转结果已接受**（beam_deflector_right45_air2x）
- 下一动作：metalens 复现 + Au/SiO₂/Au meta-atom 相位库校准

## 已接受结果

- 15 supercells、45 meta-atoms、135 Au/SiO₂/Au 层；目标辐射方向 +45°（x-z 面）；模拟角谱峰 +45.0147°；supercell 周期 897.331 nm；air 域高度 3.6 μm（相对初版 1.8 μm 翻倍）
- 证据链：`beam_deflector/right45_15cells_air2x/run_manifest.json`
- 923 MB 已求解 COMSOL 文件刻意不入库；重新生成命令见 `docs/reports/simulation/right45_air2x_result.md`

## 复现里程碑（Figs. 2–4）

1. 校准 Au/SiO₂/Au meta-atom 相位/振幅库 @1550 nm；
2. 复现 575 nm 三单元 supercell beam deflector；
3. 复现 5 μm 焦距数值 metalens。

## 布局（重构后）

```text
src/gwm_workflow/            # 核心模块（config/backend/workspace 流水线）
configs/seeds/               # 论文种子参数
configs/calibrated/          # 已校准配置（最终结果所用）
scripts/simulation/          # 建模与求解 CLI
scripts/postprocess/         # 结果重处理与绘图
tests/                       # 单元/回归/集成测试
docs/reports/simulation/     # 参数登记、复现计划、结果说明
experiments/l02_guo_2020/
  beam_deflector/
    right45_15cells_air2x/   # 45° 偏转结果（模型、Java、数据、图、run_manifest）
    structure/               # 结构构建模型
    waveguide_mode_1550nm/   # SOI 波导模式求解
  metalens/                  # metalens 轨道（待复现）
```

## 无 COMSOL 快速检查

```bash
pip install -e .
python scripts/simulation/run_single.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json --backend mock
python scripts/simulation/run_single.py --config configs/seeds/guo2020_metalens_1550nm_seed.json --backend mock
python scripts/simulation/plan_model.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json
python scripts/simulation/build_phase_targets.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json
pytest tests/
```
