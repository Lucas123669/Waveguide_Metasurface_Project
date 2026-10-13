# AGENTS.md

本文件约束在 `blueprints/` 独立项目内工作的 coding agent。默认使用中文与用户沟通。

## 项目定位

`blueprints` 将已经确定的光子晶体几何参数转换为微纳加工版图。它负责显式几何构建、
局部加工修正、全局空间包络修正、dose 接口、DRC、DXF 导出和 PNG 快速预览。

该项目必须能够从外层 COMSOL 仓库直接迁出。生产源码不得导入 `scripts`、
`comsol_workflow`、`mph`，也不得启动 COMSOL。`main/parameter.json` 中可选的
`source_trace` 仅记录外部参数源及摘要，不参与版图几何构建；独立迁出时允许设为
`null`。

## 目录与入口

- `workflow/cli.py`、`workflow/config.py`、`workflow/models.py`：流水线编排、严格参数和共享 layout 合同；
- `workflow/geometry/`：晶格、孔形、外围开窗、参数标记及可扩展 geometry source；
- `workflow/fabrication/`：局部/包络修正和 dose/process 接口；
- `workflow/quality/`：DRC 与加工质量门禁；
- `workflow/output/`：DXF、PNG 预览、报告和源码 provenance；
- `main/run_blueprint.py`：仓库内直接运行入口；
- `main/parameter.json`：唯一正式参数入口；
- `main/.out/`：运行时结果根目录，不纳入版本控制；
- `tests/`：独立项目测试；
- `pyproject.toml`、`uv.lock`：独立安装与可复现环境。

不要恢复 `src/`、根目录 `parameter.json`、根目录 `run_blueprint.py` 或根目录 `.out/`。
Python 包名保持 `blueprint_core`，不要改成与项目目录同名的 `blueprints`。

## 运行

从本项目根目录执行：

```powershell
uv sync
uv run python main\run_blueprint.py --preflight-only
uv run python main\run_blueprint.py
```

也可在环境安装后使用 `blueprint-generate`。CLI 默认读取
`main/parameter.json`。

## 参数与几何规则

- 所有独立几何自由度必须在 `main/parameter.json` 显式给出；不得在源码中增加隐藏的
  尺寸、间距、圆角、离散数、layer 或工艺 bias；
- 当前正式几何源是六角晶格 finite cavity，但新结构必须通过几何接口接入，并继续输出
  中性的 `LayoutPlan`/polygon feature；不得在 DXF、DRC 或修正模块硬编码六角特例；
- cavity、cladding、外围开窗和参数标记使用明确的 region。局部修正按 region 标定，
  空间包络修正在完整布局上统一应用；
- 参数标记必须由当前几何参数派生，并展开为闭合 polygon；DXF 不写 `TEXT` 或
  `MTEXT`；
- dose 保持显式接口。未标定时使用 `unassigned`，不得猜测或隐式填入生产剂量；
- writer grid、单位、polarity、最小线宽/间距/桥宽、边界安全距离和 release 信息必须
  来自配置并经过严格校验。

`parameter.json` 必须是无注释的标准 UTF-8 JSON。新增参数时同步更新严格 schema、示例
配置、identity 和测试。不得为了兼容拼写错误而静默接受未知字段。

## 输出与 release gate

成功 case 只能位于参数化目录
`main/.out/dxf_<layers>_cav(<...>)_clad(<...>)_shift(<...>)_(<global_delta_nm>,<envelope_modulation_strength>)/`，并严格包含：

- 参数化 DXF，文件名必须包含 cavity/cladding 层数、cavity/cladding 紧凑参数、shift、
  fabrication profile、dose kind、revision、整体边长修正和包络调制强度；最终名称不得
  显示 identity 短哈希，完整 identity 只写入 `layout_report.json`；
- `preview.png`；
- `layout_report.json`。

不得生成冗余 JSON、CSV、中间 DXF、单独面板图或调试副本。临时写入只允许出现在
case-local staging 中，最终化后必须清除。已存在 case 不得覆盖；参数变化应生成新的稳定
identity。若未显示在名称中的参数变化映射到同一显式名称，必须拒绝覆盖，不得复用旧结果。

在 fabrication profile/revision/provenance、dose、polarity 和全部生产 DRC 阈值完成
标定前，只能生成 engineering preview。不得降低或绕过 release gate；发布状态以严格
配置校验和 `layout_report.json.release_status` 为准，不依赖 DXF 固定文件名。

## 修改与验证

- 开始前检查 `git status -sb`，保留外层仓库及本项目中用户已有修改；
- 跨模块重构或数据流变化应先在外层 `docs/spec/` 建立或更新中文
  `plan-execute_YYYYMMDD_*.md`，结束时回填实际改动与验证；
- 优先复用 `workflow/` 底层模块，不复制几何或数值实现；
- 修改后按风险运行完整独立测试、相关 `py_compile`、CLI preflight 和
  `git diff --check`；测试和 preflight 不得启动 COMSOL；
- 生成实际 PNG 时必须查看图像，确认几何、开窗、七段标记、边界和裁切正确；
- 任务结束前删除 `.pytest_cache/`、`__pycache__/`、`*.pyc`、`.test_tmp_*`、staging 和
  其他验证临时文件；除非用户明确要求，不删除 `.venv/` 或已确认需要保留的正式 case；
- 只暂存当前任务文件；不要自动 commit 或 push，除非用户明确要求。

## 安全边界

DXF 是加工输入，不把工程预览默认值描述为已标定工艺。交付时明确说明 release 状态、
仍未标定的工艺接口、是否生成或删除结果、测试结果以及是否启动 COMSOL。
