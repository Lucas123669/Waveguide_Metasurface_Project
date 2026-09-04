# 文档中心

本目录只保存“人需要阅读的知识”。仿真输入放 `configs/`，可执行入口放 `scripts/`，运行数据放 `experiments/`，论文与阅读笔记放 `literature/`。

## 按任务进入

| 任务 | 首选入口 | 内容 |
| --- | --- | --- |
| 接手项目 | [AI 接手指南](guides/AI_接手指南.md) | 当前状态、工作约定、下一动作 |
| 理解代码 | [架构说明](architecture.md) | config → design → backend → result 数据流 |
| 查历史选择 | [decisions/](decisions/README.md) | 带日期的决策、环境和工艺结论 |
| 查设计分析 | [reports/design/](reports/README.md#design设计分析) | 结构、参数和设计论证 |
| 查仿真结果 | [reports/simulation/](reports/README.md#simulation仿真与结果) | COMSOL 模型、结果与复现说明 |
| 查加工汇报 | [reports/fabrication/](reports/README.md#fabrication加工与汇报) | 工艺提纲、讲稿和汇报材料 |
| 查文献统计 | [reports/literature/](reports/README.md#literature文献分析) | 文献案例统计与专题汇总 |
| 新建仿真参数 | [仿真参数模板](templates/仿真参数模板.md) | 参数、边界、网格与验收项 |
| 查旧目录约定 | [archive/](archive/simulations-layout-v1.md) | 仅供追溯，不作为当前规范 |

## 文档边界

- `guides/`：告诉成员“如何进入和操作”。
- `decisions/`：记录“为何这样做”，结论不随报告改写而漂移。
- `reports/`：记录“分析和结果是什么”，按领域分层。
- `templates/`：新任务可复制的固定结构。
- `archive/`：已废弃但仍需追溯的旧约定。

新增文档时先判断其回答的是“怎么做、为什么、结果是什么、以后复用什么”中的哪一个问题，再选择目录。
