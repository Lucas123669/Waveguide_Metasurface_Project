# 脚本入口

所有命令均建议从项目根目录执行。脚本内部通过文件位置解析项目根，不依赖调用时的当前目录。

## simulation｜建模与求解

| 脚本 | 用途 |
| --- | --- |
| `simulation/run_single.py` | 运行单个候选；支持 mock / COMSOL backend |
| `simulation/plan_model.py` | 生成机器可读 COMSOL 构建计划 |
| `simulation/build_phase_targets.py` | 生成元原子位置与目标相位表 |
| `simulation/build_comsol_structure.py` | 构建并保存 COMSOL 结构 |
| `simulation/comsol_adapter.py` | 将候选参数写入已校准 COMSOL 模板 |
| `simulation/solve_waveguide_mode.py` | 求解 L02 SOI 波导模式 |
| `simulation/run_45deg_comsol.py` | 运行 45° 偏转器件级 COMSOL 仿真 |

## postprocess｜结果处理

| 脚本 | 用途 |
| --- | --- |
| `postprocess/reprocess_45deg_results.py` | 从复场监视器重算角谱与指标 |
| `postprocess/plot_paper_style_field.py` | 从 COMSOL/缓存渲染论文风格场图 |

## literature｜文献维护

| 脚本/数据 | 用途 |
| --- | --- |
| `literature/download_f08_refs.py` | 按 manifest 下载 F08 案例文献 |
| `literature/download_si_1550_refs.ps1` | 下载或复核 Si 1550 nm 专题 PDF |
| `literature/gen_f08_case_stats.py` | 生成 F08 制造案例统计报告 |
| `literature/manifests/f08_download_manifest.json` | F08 下载来源与状态 |

## 常用命令

```bash
python scripts/simulation/run_single.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json --backend mock
python scripts/simulation/plan_model.py --config configs/seeds/guo2020_beam_deflector_paper_seed.json
python scripts/postprocess/reprocess_45deg_results.py
powershell -File scripts/literature/download_si_1550_refs.ps1 -NoNetwork
```

可复用的计算逻辑应放 `src/gwm_workflow/`；`scripts/` 只负责参数解析、调用和输入输出编排。
