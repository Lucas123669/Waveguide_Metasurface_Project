# 架构说明

## 1. 总览

仓库是"研究资料库 + 两条论文复现路线 + COMSOL 自动化代码 + 仿真产物"的混合仓库。核心代码遵循 **config → phase target → backend → result artifact** 流水线：

```text
config (seeds/calibrated) → design_with_params → build_phase_targets
      → backend (mock | comsol) → SimulationResult → candidate.json / phase_targets.csv / scored_result.json
```

## 2. 分层

- `src/gwm_workflow/config.py`：配置加载与校验（参数来源标记：`paper_exact` / `figure_estimate` / `assumption` / `derived`）。
- `src/gwm_workflow/phase_design.py`：偏转与金属透镜相位方程。
- `src/gwm_workflow/model_plan.py`：机器可读 COMSOL 构建计划。
- `src/gwm_workflow/backends.py`：`AnalyticMockBackend`（无 COMSOL 时验证调度/理论）与 `ExternalComsolBackend`（经 MPh adapter 调用 COMSOL）。
- `src/gwm_workflow/workflow.py`：候选生成与工件写入（candidate.json、phase_targets.csv、scored_result.json）。
- `scripts/simulation/`：建模与求解 CLI；`scripts/postprocess/`：结果重处理与绘图；`scripts/literature/`：文献下载、清单与统计。

## 3. 实验轨道

- `experiments/l01_huang_2023/`：L01 轨道（PMMA/Si₃N₄ qBIC），纯 Python 平板模 + 后续 COMSOL 元胞库。
- `experiments/l02_guo_2020/`：L02 轨道（Si 波导 Au/SiO₂/Au），COMSOL 自动化复现。

轨道之间物理模型、材料与目标互不混淆；共享的仅是工具型代码（src/gwm_workflow 属于 L02 复现，L01 轨道独立）。

## 4. 复现证据链

每个已接受结果目录含 `run_manifest.json`：配置 SHA、Git commit、环境版本、运行时长、输入/输出校验和。CLI 失败必须返回非零退出码（见 `scripts/simulation/run_single.py`）。

## 5. 状态同步

`project_config.json` 是唯一状态源；根 README 状态表人工同步维护。轨道级状态见 `experiments/*/README.md`。
