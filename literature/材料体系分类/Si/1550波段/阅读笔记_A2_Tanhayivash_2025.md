# A2｜Tanhayivash 2025｜Scientific Reports 15

## 论文信息

- **题目**：Phase and amplitude gradient waveguide coupled metasurfaces
- **期刊 / 年份**：*Scientific Reports* **15**, 19964 (2025)
- **DOI**：[10.1038/s41598-025-05141-7](https://doi.org/10.1038/s41598-025-05141-7)
- **本地原文**：[A2 PDF](pdfs/A2_Tanhayivash_2025_Phase_Amplitude_Gradient_Waveguide_Metasurfaces.pdf)
- **定位**：★A 组；Si bar 覆盖一维 slab waveguide 的导波驱动 metalens。

## 一句话总结

通过在 Si 平板波导上布置 Si-bar 梯度超表面，论文将导模整形成自由空间聚焦场，并提出以元原子参数而非换工作波长来控制主瓣指向、降低 1550 nm 附近 beam squint 的思路。

## 结构与机制

- 平台为硅基一维 slab waveguide，表面 Si bars 既提供散射耦合，也承担相位和振幅梯度。
- 设计逻辑是把目标自由空间相位减去导模沿传播方向累积的相位，得到每个 bar 所需的局部补偿；散射强度用于孔径加权。
- 相对传统光栅，该方法的优点是元原子可同时参与波前与耦合强度设计，适合片上 beam deflection / focusing。

## 关键结果

- 标称工作波长 **1550 nm**；示例 metalens 焦距 **7.5 μm**。
- 末级设计在焦平面给出约 **893 nm FWHM** 的光斑。
- 文中扫描 1550 nm 周边波长，报告主束 squint 较小；并提出利用 Si-bar 参数工程获得目标指向，而非仅靠波长扫描。
- 结果以数值电场分布为主，工程采用前须独立做效率、背反射和工艺容差验证。

## 对项目的启示

1. 把“波导传播相位 + 元原子散射相位”写入优化目标，是从自由空间 metalens 迁移到片上发射器的必需步骤。
2. 波束指向设计应同时报告 `dθ/dλ`、孔径长度和出射效率；只看焦点 FWHM 不足以评价 LiDAR/通信发射器。
3. Si-bar 的几何扫描可作为第一版全介质单元库，但应加入 3D 全波与侧壁/线宽偏差。

## 待确认

- 论文给出的高性能主要基于仿真；需从方法部分提取边界条件、入射模式及效率定义后再作横向比较。
