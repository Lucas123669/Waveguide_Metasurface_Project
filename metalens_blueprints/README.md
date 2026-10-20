# 圆柱超透镜：独立版图工作流

这是独立于 `../blueprints` 六三角空气孔路线的新工作流。独立入口、参数、数据、测试、
输出和 Python 包名 `metalens_workflow`；不把圆柱分支塞回原 CLI/config。
通过显式 Python 包依赖仅复用原 `blueprint_core` 的中性 polygon、工艺修正、DRC、DXF工具。
因此本项目不是完全零依赖复制包，迁移时须同时提供该基础包；原三角孔源码保持不变。

## 运行

推荐从本目录创建/同步独立环境，不假定原三角孔环境仍可用：

```powershell
uv sync
uv run python main/run_metalens.py --preflight-only
uv run python main/run_metalens.py
```

只有确认原环境的解释器与依赖有效后，才可复用：

```powershell
../blueprints/.venv/Scripts/python.exe main/run_metalens.py --preflight-only
../blueprints/.venv/Scripts/python.exe main/run_metalens.py
New-Item -ItemType Directory -Force main/.out | Out-Null
../blueprints/.venv/Scripts/python.exe -B -m pytest tests -q -p no:cacheprovider --basetemp=main/.out/.test_tmp_run
```

本地依赖路径已在 pyproject 声明。默认参数唯一入口为 `main/parameter.json`，可用 `--config` 切换。
跨路线状态、外部矩形程序与Excel相位库的待接入边界见
[工作流总览](../docs/guides/版图生成工作流.md)；其他AI可复制
[接手提示词](../docs/guides/AI_版图工作流接手提示词.md)。

## 实现范围

圆柱 + 正方晶格 + 圆形口径 + 单波长轴上聚焦。不是同心圆环排布、矩形、椭圆或 PB 相位
生成器；不直接启动 CST/MATLAB/COMSOL，不附带整片器件全波求解。

数据流：外部 MATLAB/CST 单元库 → 物理条件/来源校验 → 聚焦相位 → 圆周最近相位选态 →
完整柱子口径筛选 → 独立工艺 bias/网格取整 → 几何 DRC → DXF/GDS → 真实轮廓预览和报告。

默认：1550 nm、周期0.8 um、口径100 um、焦距100 um、64边形圆柱、1024边形保守口径、
1 nm地址栅格。只有边缘不会截断的完整柱子才保留。首态相位偏移 -26.187541 deg，
聚焦相位符号 -1，二者均显式配置。`fabrication.edge_bias_nm` 正值扩大轮廓，负值收缩。
没有任何三角孔 SEM 修正字段。极性、剂量及生产尺寸阈值仍未标定。

## MATLAB 接口与输入安全

- `matlab_work10` 格式：`D,phase_deg,mag_dB`；来源统一记 unverified，需显式准入。
- `matlab_work11` 格式：`state_idx,D_um,actual_phase_deg,mag_dB,source`；读取真实传输相位，
  **不是**符号反转的 `actual_design_phase_deg` 绘图坐标。
- `canonical` 格式：`state_idx,D_um,phase_deg,transmission,source`；透射为0~1功率值。

仅接收准入来源且达到透射门限的状态。CSV和物理元数据JSON均固定SHA256，变化必须更新
哈希和revision。元数据与示例同结构，记录波长、周期、柱高、材料、偏振/入射、相位约定、
验证状态及provenance。波长或周期不匹配、哈希不符或不支持的物理通道会拒绝。
字节哈希包括换行；演示数据通过gitattributes固定LF。

数据源 `data/work11_demo.csv` 是用户提供的公众号“CST超表面工坊”第11期12态CSV。
12行均声明simulated，但原始CST工程/频谱未提供，故元数据为 **unverified_import**。
物理模型来自第10期：a-Si常数eps=12、无损、柱高0.94 um，石英eps=2.085、1 um有限层。
不是实际晶圆厚度或薄膜损耗标定。不得把单元功率透射率当作聚焦效率。

相位库只覆盖约298.56 deg连续跨度，环上最大空档约61.44 deg。默认62 deg空档门槛与
31 deg最大量化误差门槛仅保留教学示例，不是推荐生产标准。归一化或多分几个状态不会补齐2pi。

## 输出与验证边界

输出只进入 `main/.out/<显式参数和修订号>/`：DXF、可选层级GDS、`preview.png`、
`layout_report.json`。不同参数但同名case也拒绝覆盖，须改变revision。
GDS按实际修正后整数轮廓去重，标准BOUNDARY+SREF，回读展平与DXF输入几何核对；
数据库单位随writer grid，用户单位固定um。尚需独立版图查看器和加工平台转换软件验收。
报告记录每点选态、标称相位误差、输入哈希、圆柱及基础工具源码哈希、修正及DRC。
标称库响应不表示bias后重新求解的光学响应。

历史DRC字段 `min_hole_width_nm` 在此表示图元包络最小宽度，`min_bridge_nm` 表示图元间
间隙；`min_edge_nm` 是多边形单段边长，不是柱径。留空表示未标定，不表示生产已合格。

本路线强制 **engineering_preview**；填入剂量等字段也不能提升为released。实际焦距、
焦斑、聚焦效率、邻居耦合及工艺容差需另做验证。测试不启动昂贵外部仿真。

## 与原工作流的关系

`blueprints/main/run_blueprint.py` 与原 `parameter.json` 继续只负责原六三角空气孔，入口、
参数schema、命名和三文件合同恢复不变。前一阶段产生的圆柱试验case仍保留在原忽略输出
目录作为历史记录，不删除或覆盖；今后圆柱结果只进入本工作流。
