# 660 nm 小口径超透镜 FDTD 参考数据

本案例在 2026-11-23 至 2026-11-24 使用 Lumerical FDTD 2026 R1（8.35.4413）求解。名义口径 22 μm，目标焦距 100 μm。整片模型采用 3,125 根圆柱，计算的焦点距柱顶 76.87 μm。图和数值来自本次运行，单元结构图用于检查模型设置。

- [六步仿真操作、结果与局限](../../docs/reports/simulation/2026-11-24_Ansys_FDTD_小口径超透镜.md)
- [运行清单与文件校验值](run_manifest.json)
- [相位库](phase_library.json)载明半径、相对相位和零级透射率。相位以半径 50 nm 为零点，透射率以 0–1 表示。
- [整片排布](lens_design.json)载明列名及逐柱坐标、半径和相位。位置用 μm，半径用 nm。逐柱透射率和相位由单元库估算。
- [焦点测量值](focus_metrics.json)和[原始投影数组](focusing_fields.npz)用于核对测量和绘图。NPZ 的 `spot_intensity_xy` 按 x、y 排列，`section_intensity_xz` 按 x、z 排列。
- `figures/` 保存单元结构、电场对比、相位库、排布和聚焦五张 PNG。

从官方入口下载 Lumerical 示例工程。在具备许可证的环境中，按六步报告重建模型。 [Ansys 原始案例和下载入口](https://optics.ansys.com/hc/en-us/articles/360042097313-Small-Scale-Metalens-Field-Propagation)
