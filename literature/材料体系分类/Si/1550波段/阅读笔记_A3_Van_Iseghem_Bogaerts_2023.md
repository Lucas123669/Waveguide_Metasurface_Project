# A3｜Van Iseghem & Bogaerts 2023｜Photonics Research 11(9)

## 论文信息

- **题目**：Optical leaky fin waveguide for long-range optical antennas on high-index contrast photonic circuit platforms
- **期刊 / 年份**：*Photonics Research* **11**(9), 1570–1584 (2023)
- **DOI**：[10.1364/PRJ.490085](https://doi.org/10.1364/PRJ.490085)
- **本地原文**：[A3 PDF](pdfs/A3_Van_Iseghem_2023_Optical_Leaky_Fin_Waveguide.pdf)
- **定位**：★A 组；长口径、低发散片上 LiDAR 天线方案。

## 一句话总结

论文用“渐变波导 + 顶部窄 fin”的连续漏泄结构替代弱 apodized surface grating，在高折射率对比平台上产生大直径、近 Gaussian 的 1.55 μm 离片光束，目标是远距离 LiDAR 所需的低发散口径。

## 结构与机制

- 常规弱光栅需极小且连续变化的散射系数，容易受刻蚀和线宽误差限制；leaky-fin 以渐变横截面调节导模向顶部窄 fin 的耦合与泄漏。
- 作者先以 mode solver 扫描横截面参数、再用该设计空间构造长天线，从而分开处理“局部泄漏率”和“全器件孔径包络”。
- 目标应用要求约 **30 mm** 级有效孔径以投射 200–300 m 量级的准直束，故重点不是紧凑，而是可扩展与可制造。

## 关键结果

- 设计工作在 **λ≈1.55 μm**；给出发射图样、波长色散与关键截面参数敏感性分析。
- 论文结论是该方案对关键尺寸具有内在鲁棒性，并可在高折射率对比 PIC 上扩展到长距离光天线。
- 文本核心为设计/仿真与制造可行性讨论；使用时需区分“设计预测”与已实测性能。

## 对项目的启示

1. 若目标是低束散，优先反推所需有效孔径和目标泄漏率分布，再开始元原子相位设计。
2. 连续 taper 可承担 amplitude apodization，超表面可保留给相位/偏振调控；这是一条降低离散单元工艺压力的混合路线。
3. 容差表应包含 fin 宽度、波导 taper、层厚和波长漂移，而不能只扫描周期。

## 待确认

- 将实际工艺最小线宽与可做的天线长度代入后，复算本项目目标发散角和传播损耗。
