# Blueprints：有限六角光子晶体三角空气孔 DXF 工程版图

> **版图类型**：面向 EBL 图形化与后续刻蚀的二维 DXF 工程版图。当前结构为有限六角边界的三角晶格光子晶体腔；每个元胞包含六个三角空气孔，并附带六段外围大面积刻蚀开窗及七段式参数标记。
>
> **当前状态**：`engineering_preview`。当前配置中的曝光剂量、图形极性和生产 DRC 阈值尚未完成平台标定，不能直接标作可投片生产版。
>
> **项目归属边界**：该生成器目前未绑定 L01 或 L02 论文复现轨道，`source_trace` 为 `null`。在建立仿真参数来源与加工标定证据前，应把它视为独立的光子晶体微纳加工版图工作流。

`blueprints/` 是独立、无 COMSOL 运行依赖的微纳加工版图项目。外层项目目录使用
`blueprints/`，内部 Python 包的公开导入名为 `blueprint_core`，避免与项目名混淆。

当前 v1 从显式六角晶格参数构建完整 finite-cavity 孔阵列，依次执行局部孔形修正、
全局空间包络修正、dose/process 接口、地址栅格取整、DRC、DXF 写入回读和综合预览。
官方工程配置还生成围绕 finite boundary 的 6 个分段大面积空气开窗，以及位于完整结构
下方、由 cavity/cladding 参数自动派生的七段式空气孔标记。
几何源以独立接口接入；修正、dose、DRC、DXF 和预览均只消费中性 polygon layout，
便于后续增加其他晶格或把整个目录迁出当前 COMSOL 仓库。

## 形状分类与扩展说明

[跨路线工作流总览](../docs/guides/版图生成工作流.md)区分本目录三角孔路线、独立圆柱路线与尚未接入的矩形/Excel输入；[AI接手提示词](../docs/guides/AI_版图工作流接手提示词.md)可直接复用。本目录入口、参数与输出合同不因圆柱路线加入而改变。

[七类超表面元胞形状及版图扩展说明](../docs/reports/design/2026-10-14_超表面元胞形状分类与版图工作流扩展说明.md)给出圆形、矩形、椭圆形、三角形、梯形、环形和特殊结构的库内文献例子、建议参数、超胞组合标签及原创示意图。

该文档是分类与扩展设计依据。当前生成器仍只实现六三角空气孔路线；闭合环的内孔、其他形状的严格配置、通用组合与文件命名尚需实现和验证。

## 目录

- `main/parameter.json`：唯一正式参数源；几何、修正、dose、layout、DRC 和 export 参数均在此显式给出。
- `main/run_blueprint.py`：仓库内直接运行的入口。
- `main/.out/`：按用户可读的显式参数名称分 case 保存结果；完整 identity 保留在报告内。
- `workflow/`：核心工作流包文件；物理目录扁平，但公开导入名仍为 `blueprint_core`。
  - `geometry/`：晶格、孔形、外围开窗和参数标记；
  - `fabrication/`：局部/包络修正及 dose/process 接口；
  - `quality/`：DRC 和加工质量门禁；
  - `output/`：DXF、PNG 预览、报告和源码 provenance；
  - 根层 `cli.py`、`config.py`、`models.py`：流水线编排、严格参数和共享 layout 合同。
- `tests/`：配置、几何一致性、修正、dose、DRC、DXF 和 CLI 合同测试。
- `AGENTS.md`：独立项目的目录、参数、加工安全和验证约束。

## 运行

在本项目根目录同步独立环境：

```powershell
uv sync
```

先执行不写文件的完整预检：

```powershell
uv run python main\run_blueprint.py --preflight-only
```

预检通过后生成工程版图：

```powershell
uv run python main\run_blueprint.py
```

成功 case 严格只包含三个文件：

- 参数化 DXF，例如
  `dxf_15-15_cav(245-0.96-1.156)_clad(242-0.98-0.93)_shift(0-0)_sem-air-hole-220nm-radial-v1-unassigned-r1_(-10,1).dxf`；
- `preview.png`：包含整体版图、中心/cavity 边界/cladding 边界三个共享局部尺度的三角孔、沿同一径向带实际施加的三角形边长修正函数，以及从 shell 0 到最外层、一个 cell 宽的径向放大带；右侧纵轴为 `Triangle side-length correction (nm)`，直接绘制 `global_delta_nm + 2√3 × envelope_modulation_strength × envelope edge offset`；
- `layout_report.json`。

CLI 不覆盖已存在的 case。完整配置仍产生稳定 identity 并写入 `layout_report.json`，但
最终名称不显示哈希；case 文件夹末尾直接显示
`(global_delta_nm,envelope_modulation_strength)`，例如
`dxf_15-15_cav(245-0.96-1.156)_clad(242-0.98-0.93)_shift(0-0)_(-10,1)/`。
若其他未显示参数不同却映射到同名 case，no-overwrite gate 会拒绝覆盖。

## 外围开窗与参数标记

`outer_etch_windows` 当前正式类型为 `segmented_hex_ring_windows_v2`。六个开窗逐边从
finite 六边形边界派生：`inner_clearance_um` 给出靠近结构底边的法向净距，
`radial_width` 给出梯形沿边界外法线高度的显式层数规则，当前关系为
`height_um = 0.4 * (cavity_layers + cladding_layers) - 3.0`。因此 15-15 对应 `9 um`，
20-20 对应 `13 um`；非对称层数也按 cavity/cladding 总层数计算。
`parallel_side_gap_um` 独立给出相邻梯形两条径向平行斜边的法向净距。构造器在每个共享
顶点两侧对称收短底边以满足该净距；当前净距参数为 `inner_clearance_um=3.8 um`、
`parallel_side_gap_um=5.0 um`。零间距拼环不属于 v2 正式合同。圆角只施加在靠结构的
两个内角，两个外角保持尖角；圆角半径和离散数均在
`main/parameter.json` 显式给出。设置
`{"kind": "none"}` 可关闭；开窗作为 `outer_etch_window` region 进入 dose、按 region
局部修正、grid snap、通用 DRC 和 DXF，但不参加仅针对内部纳米孔的
finite-footprint containment。

`markers` 使用 `seven_segment_parameter_label_v1` 时，从
`geometry.unit_cell.cavity/cladding` 自动生成当前显示字符串，默认结果是
`245.0 0.96 1.156 — 242.0 0.98 0.93`。字符高宽、棍宽、段间隙、倒角、小数点、数字/
参数/分组间距、长横线和相对位置全部在 `main/parameter.json` 显式给出。每一段均为闭合
polygon；DXF 中不会出现 `TEXT` 或 `MTEXT`。设置 `{"kind": "none"}` 可关闭标记。

`fabrication.triangle_side_correction` 是等边三角孔的显式边长修正接口：
`global_delta_nm` 表示单个三角孔每条边的统一修正，负值缩小；
`envelope_modulation_strength` 是无量纲 SEM 包络强度，`0` 关闭、`1` 使用当前标定幅度；
`regions` 给出两者共同作用域。当前正式值为 `global_delta_nm=-10.0`、
`envelope_modulation_strength=1.0`、`regions=[cavity, cladding]`。内部几何按
`edge_offset = global_delta_nm/(2√3)` 换算，不要求用户写入低层平行边偏移。

`fabrication.local_correction` 保留为通用 region 级 edge bias/scale 接口，当前 default
为零；`by_region` 可分别标定 `outer_etch_window` 和 `parameter_marker`。SEM 包络和整体
边长修正都不会改变开窗与参数标记。上述工艺值仍是工程方案，不代表生产标定。

## 工程版与生产版

仓库内的 `main/parameter.json` 有意保持为工程预览配置：几何与 writer grid 已显式，当前
启用目标边长 `220 nm` 的 SEM 径向修正方案，但 `process_gain=1.0` 尚未经过二次 SEM
闭环验证，dose、极性和加工 DRC 阈值也尚未赋值。因此它只能生成
`release_status=engineering_preview` 的参数化 DXF。只有设置经过标定的 fabrication
profile/revision/provenance、标量 dose、明确极性及全部 DRC 阈值，并把 project/export
状态同时改为 `released`，配置校验才允许把参数化 DXF 标记为生产发布。release gate
由严格配置与报告状态控制，不依赖固定文件名。

`source_trace` 只用于记录当前 COMSOL 参数源的哈希，不参与几何构建；目录迁出仓库后可
将它设为 `null`。生产源码不导入 `scripts`、`comsol_workflow`、`mph`，也不会启动 COMSOL。

## SEM 三角孔修正数据

`data/SEM_air_hole_size.csv` 保存未施加空间包络修正的真实 SEM 三角孔边长。以下入口会
从 `main/parameter.json` 读取当前 finite 总壳层数和晶格周期，以显式目标 CD `220 nm`
和内区实测平台共同确定中心补偿，生成完整壳层修正表和三面板 QA 图：

```powershell
uv run python main\build_sem_correction.py --target-cd-nm 220 --overwrite
```

默认产物为 `data/SEM_air_hole_correction.csv` 和
`data/SEM_air_hole_correction.png`。CSV 同时保留逐壳层表格补偿和可供
`radial_even_polynomial` 接口使用的平滑 edge-offset 系数。当前正式方案 ID 为
`sem-air-hole-220nm-radial-v1`，其系数和 `regions=["cavity", "cladding"]` 已显式写入
`main/parameter.json`；数据生成器本身仍不会隐式修改参数文件。当前结果使用
`process_gain=1.0`，在二次 SEM 闭环验证前不得当作生产工艺标定。
