# 配置目录

配置按成熟度分层，避免论文原始参数、推断值与校准结果混用。

| 目录 | 含义 | 修改规则 |
| --- | --- | --- |
| `schemas/` | 配置结构和字段约束 | 修改时同步代码与测试 |
| `seeds/` | 论文参数种子；允许 `paper_exact`、`figure_estimate`、`assumption` | 保留来源标签，不覆盖成校准值 |
| `calibrated/` | 已被接受结果使用的校准配置 | 新版本新文件，保持旧结果可追溯 |

配置进入执行流程后，解析值和输入哈希写入对应实验结果目录的 `resolved_config.json` / `run_manifest.json`。历史 run 的 resolved config 属于证据链，不因目录调整而回写。
