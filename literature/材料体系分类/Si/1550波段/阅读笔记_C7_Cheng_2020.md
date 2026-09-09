# C7｜Cheng 2020｜Micromachines 11(7), 666

## 论文信息

- **题目**：Grating Couplers on Silicon Photonics: Design Principles, Emerging Trends and Practical Issues
- **期刊 / 年份**：*Micromachines* **11**(7), 666 (2020)
- **DOI**：[10.3390/mi11070666](https://doi.org/10.3390/mi11070666)（MDPI OA）
- **单位**：清华大学-伯克利深圳研究院（TBSI）；通讯 H. Y. Fu
- **本地原文**：[C7 PDF](pdfs/C7_Cheng_2020_Grating_Couplers_Silicon_Photonics_Review.pdf)
- **定位**：★C 组（综述 / 制造平台）。"1550 nm SOI 光栅耦合器"专题综述；与 A6（apodized GC）、Q1-12（Taillaert GC）、A10（SWG 无热化）同族，为本项目"波导光栅辐射"提供第一性框架（布拉格条件、损耗通道、方向性/模式重叠、SWG 等效介质）。[→ 精读笔记](精读笔记_C7_Cheng_2020_构思结构与术语.md)

## 一句话总结

以"性能短板"为主线的 GC 系统综述：从布拉格条件与损耗通道分解出发，把效率提升归结为**方向性 ↑（overlay/底部反射器/z 向复杂度）**与**模式重叠 ↑（apodization）**两条主线；再覆盖偏振分集（PSGC）、波长分集（宽带/双带）、新兴趋势（SDM/逆向设计/多层 SiN/等离激元）与工程实际（晶圆级测试/封装/应用）。

## 核心内容摘要

- **基础**：布拉格条件 $k_0\sin\theta + mG = \beta$；损耗通道 $P_w = P_{in} - P_{sub} - P_r - P_{w2}$；光纤倾斜 8–10° 打破对称；SWG 等效介质（Rytov TE/TM 公式）；聚焦 GC 省 taper。
- **CE**：多晶硅 overlay（−1.6 dB）；底部反射器（金属/DBR/Si 光栅；**迄今亚 dB 级 GC 均用底部反射器**）；apodization（变占空比/周期/蚀深）；双蚀刻（方向性 >95%）。
- **偏振**：1D/2D PSGC 偏振分集；SWG/厚 SOI 消双折射实现偏振不敏感。
- **波长**：1-dB 带宽公式 $\Delta\lambda_{1dB}=C·NA·\lambda_0 n_0\cos\theta_0/(n_{eff}-n_0\sin\theta_0)$；降 neff / 高 NA / Si 棱镜补偿；双波长带（PON 1310/1550）。
- **趋势**：FMF/MCF 空分复用（LP 模耦合）；逆向设计；多层 SiN、等离激元 GC。
- **工程**：晶圆级测试（Mueller 矩阵快速测 PDL）；g-Pack 垂直封装 vs 角度抛光光纤横向耦合；PIC / 生物传感 / LiDAR 应用。

## 对项目的启示

1. 布拉格条件 + 波矢图是"波导→自由空间辐射"的第一性检查工具。
2. 效率分析用"方向性 × 模式重叠 × 背反射 × 衬底泄漏"分解找瓶颈。
3. apodization（变占空比/周期/耦合强度）可迁移到项目辐射包络整形。
4. SWG 等效介质（Rytov）与 A10/L03 呼应，可入 SWG 元胞库理论文档。
5. 宽带三招（降 neff / 高 NA / 棱镜补偿）可直接评估。

## 待进一步处理

- Micromachines 为中科院三区（OA），引用时注意分区口径（专题综述用途，非一区顶刊）。
- Table 1/2/3 中各原始文献的峰值指标以原文为准；本文仅作索引。
