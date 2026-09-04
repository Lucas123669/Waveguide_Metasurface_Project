# 测试目录

- `unit/`：纯 Python 逻辑与工作流测试，不依赖 COMSOL。
- `regression/`：对已知论文参数/数值结果做回归检查。
- 需要 COMSOL 的测试后续放 `integration/`，并明确环境要求与跳过条件。

从项目根运行：

```bash
python -m pytest -q
```
