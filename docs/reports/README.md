# 报告中心

报告按“设计依据、仿真证据、加工沟通、文献分析”分层；带日期文件表示当时的阶段性结论，未带日期文件多为持续维护的技术说明。

## design｜设计分析

| 文件 | 内容 |
| --- | --- |
| [2026-08-25_L01超表面波导综合分析与初步结构.md](design/2026-08-25_L01超表面波导综合分析与初步结构.md) | L01 波导、加工问题和初步结构，含逐条文献依据 |

## simulation｜仿真与结果

| 文件 | 内容 |
| --- | --- |
| [reproduction_plan.md](simulation/reproduction_plan.md) | L02 复现阶段与验收项 |
| [paper_parameter_register.md](simulation/paper_parameter_register.md) | 论文参数来源等级与登记 |
| [comsol_model_tree.md](simulation/comsol_model_tree.md) | 稳定 COMSOL tag / model tree 约定 |
| [comsol_structure_program.md](simulation/comsol_structure_program.md) | 结构构建脚本和输出说明 |
| [right45_air2x_result.md](simulation/right45_air2x_result.md) | 已接受 45° 结果与重建命令 |
| [45deg_simulation_result.md](simulation/45deg_simulation_result.md) | 45° 仿真过程记录 |
| [15_supercell_result.md](simulation/15_supercell_result.md) | 15-supercell 阶段记录 |

## fabrication｜加工与汇报

| 文件 | 内容 |
| --- | --- |
| [2026-08-30_项目汇报提纲_微纳加工技术整理.md](fabrication/2026-08-30_项目汇报提纲_微纳加工技术整理.md) | 加工技术汇报提纲 |
| [2026-08-30_项目汇报稿_微纳加工技术整理.md](fabrication/2026-08-30_项目汇报稿_微纳加工技术整理.md) | 配套讲稿 |
| [2026-08-31_PPT精炼版汇报稿.md](fabrication/2026-08-31_PPT精炼版汇报稿.md) | PPT 精炼稿 |

## literature｜文献分析

| 文件 | 内容 |
| --- | --- |
| [2026-09-02_F08制造案例统计与汇报.md](literature/2026-09-02_F08制造案例统计与汇报.md) | F08 综述 72 个制造案例统计；由 `scripts/literature/gen_f08_case_stats.py` 生成 |

原始运行数据和模型必须放在 `experiments/`，报告只保存解释、比较与复现入口，避免出现两份“最终结果”。
