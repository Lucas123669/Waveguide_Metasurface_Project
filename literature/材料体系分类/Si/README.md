# 体系：Si（顶层超表面 = 硅）

## 体系定位

顶层超表面材料为硅（a-Si / m-Si / p-Si）。硅具有高折射率（n≈3.5）、CMOS 兼容、可见-NIR 低损耗，是超表面最常用的材料体系。本体系的任务：Si 波导 + Si 顶层超表面的设计、仿真与加工。

## 主文献

| 编号 | 标题 | 在本体系中的角色 | PDF / 笔记 |
| --- | --- | --- | --- |
| L02 | Molding free-space light with guided wave–driven metasurfaces | Si 波导 + Au/SiO₂/Au 顶层复现基准（45° 偏转已复现） | `literature/L02_Guo_2020_Molding_Free-Space_Light.pdf`；`阅读笔记_L02_Guo_2020.md` |
| Q1-05 | Asymmetric metasurfaces with high-Q resonances governed by BIC | qBIC 理论（Q∝α⁻²），示例为 Si 结构 | `literature/Q1_L01相关/Q1_05_Koshelev_2018_*.pdf`；`阅读笔记_Q1_05_Koshelev_2018.md` |
| Q1-11 | Fabrication robustness in BIC metasurfaces | a-Si qBIC 制造鲁棒性（椭圆最稳、σ 预算） | `literature/Q1_L01相关/Q1_11_Kuehne_2021_*.pdf`；`阅读笔记_Q1_11_Kuehne_2021.md` |
| F-03 | Defect-insensitive BIC in antisymmetric trapezoid metasurfaces | Si 梯形柱缺陷不敏感设计（磁偶极主导） | `literature/Q1_工艺_L01相关/F_03_*.pdf`；`阅读笔记_F_03_Liao_2025.md` |
| F-05 | Exhaustive metasurface robustness via deep learning | Si/SiO₂ 示例的穷尽容差方法 | `literature/Q1_工艺_L01相关/F_05_*.pdf`；`阅读笔记_F_05_Campbell_2021.md` |
| F-10 | On-chip meta-optics for arbitrary trajectories | α-Si 顶层 + Si₃N₄ 波导的片上轨迹整形 | `literature/Q1_工艺_L01相关/F_10_*.pdf`；`阅读笔记_F_10_Shi_2024.md` |
| F-12 | All-dielectric metasurface for high-performance structural color | Si-on-sapphire EBL 结构色（F08 案例 C01） | `pdfs/F_12_*.pdf`；`阅读笔记_F_12_Yang_2020.md` |
| F-13 | Chiral visible light metasurface patterned in m-Si by FIB | FIB 直写 m-Si 手性超表面（F08 案例 C09） | `pdfs/F_13_*.pdf`；`阅读笔记_F_13_Gorkunov_2018.md` |
| F-17 | Synthetic aperture metalens | a-Si 合成孔径 metalens（EBL+光刻，F08 案例 C35） | `pdfs/F_17_*.pdf`；`阅读笔记_F_17_Zhao_2021.md` |
| F-18 | Dielectric Mie voids: confining light in air | Si 中 FIB 灰度 Mie void 彩印（F08 案例 C31） | `pdfs/F_18_*.pdf`；`阅读笔记_F_18_Hentschel_2023.md` |
| F-19 | CMOS-compatible all-Si metasurface polarizing bandpass filters on 12-inch wafers | 12 in ArF DUV 偏振滤波（F08 案例 C42） | **PDF 待浏览器下载**；`阅读笔记_F_19_Xu_2019.md`（待补） |
| F-20 | CMOS-compatible a-Si metalenses on a 12-inch glass wafer for fingerprint imaging | 12 in a-Si 940 nm metalens（F08 案例 C44） | **PDF 待浏览器下载**；`阅读笔记_F_20_Hu_2020.md`（待补） |
| F-23 | Large-scale metasurfaces based on grayscale nanosphere lithography | DMD 灰度纳米球大面积 metalens（F08 案例 C54） | `pdfs/F_23_*.pdf`；`阅读笔记_F_23_Zheng_2021.md` |
| F-27 | Decoupling optical function and geometrical form using conformal flexible metasurfaces | 共形柔性 a-Si/PDMS（F08 案例 C65） | `pdfs/F_27_*.pdf`；`阅读笔记_F_27_Kamali_2016.md` |

## 相关文献（跨体系引用）

- Q1-06 Overvig 2020（选择定则，示例 Si 柱）
- Q1-07 Lu & Zou 2026（片上超表面综述，含 Si 案例）
- F-08 Yang 2024（制造综述，Si 工艺）

## 关键要点

- Si 高折射率对比 → 共振强，但对加工误差更敏感（Q1-11：σ≤1–2 nm 预算）。
- 可见光短波段 Si 有吸收；必要时加折射率匹配层或转 TiO₂。
- 刻蚀工艺（RIE/Bosch）是 Si 体系的核心加工手段。

## 待补充文献

- ~~Si 波导 + Si 顶层超表面的专项集成文献~~（F-10 已提供 α-Si/Si₃N₄ 波导案例；专项集成仿真仍属开放）
