# 体系：SiN（顶层超表面 = 氮化硅）

## 体系定位

顶层超表面材料为氮化硅（Si₃N₄，n≈2.0）。Si₃N₄ 兼具中等折射率、可见-NIR 低损耗、CMOS 兼容，是 L01 波导层的材料，也是本项目从 L01 延伸的核心体系之一。

## 主文献

| 编号 | SCI 分区 | 标题 | 在本体系中的角色 | PDF / 笔记 |
| --- | --- | --- | --- | --- |
| L03 | Q1 · 中科院一区 Top | Silicon Nitride Integrated Photonics from Visible to Mid-Infrared | Si₃N₄ 平台工艺综述(沉积/应力/损耗/耦合) | [PDF](../../L03_Buzaverov_2024_Silicon_Nitride_Integrated_Photonics.pdf) · [笔记](../../阅读笔记_L03_Buzaverov_2024.md) |
| Q1-03 | Q1 · 中科院一区 Top(OA) | Observation of trapped light within the radiation continuum | 介质 PhC 平板 BIC 实验奠基(Si₃N₄ 类) | [PDF](../../Q1_L01相关/Q1_03_Hsu_2013_Trapped_Light_Radiation_Continuum_Nature.pdf) · [笔记](../../Q1_L01相关/阅读笔记_Q1_03_Hsu_2013.md) |
| Q1-04 | Q1 · 中科院一区 Top(OA) | Merging BICs by harnessing higher-order topological charges | Si₃N₄ 平板 merged BIC(抗加工缺陷) | [PDF](../../Q1_L01相关/Q1_04_Kang_2022_Merging_BICs_Topological_Charges_Light_Sci_Appl.pdf) · [笔记](../../Q1_L01相关/阅读笔记_Q1_04_Kang_2022.md) |
| F-01 | Q1 · 中科院一区 Top | Wafer-Scale All-Dielectric Quasi-BIC Metasurfaces (DUV) | Si₃N₄ DUV 晶圆级 qBIC(Q≈150) | [PDF](../../Q1_工艺_L01相关/F_01_Yesilkoy_2026_WaferScale_qBIC_DUV_NanoLetters.pdf) · [笔记](../../Q1_工艺_L01相关/阅读笔记_F_01_Yesilkoy_2026.md) |
| F-02 | Q1 · 中科院一区 Top(OA) | An achromatic metasurface waveguide for AR displays | Si₃N₄ 波导超表面完整流程(PECVD+EBL+RIE) | [PDF](../../Q1_工艺_L01相关/F_02_2025_Achromatic_Metasurface_Waveguide_AR_LightSciAppl.pdf) · [笔记](../../Q1_工艺_L01相关/阅读笔记_F_02_Tian_2025.md) |
| F-04 | Q1 · 中科院一区(OA) | Robust ultrahigh-Q merging BIC in phase-change metasurface | Si₃N₄ + Sb₂S₃ PCM merged BIC | [PDF](../../Q1_工艺_L01相关/F_04_Ren_2025_Robust_Merging_BIC_PCM_Nanophotonics.pdf) · [笔记](../../Q1_工艺_L01相关/阅读笔记_F_04_Ren_2025.md) |
| F-07 | Q1 · 中科院二区 | Overcoming Si₃N₄ film stress limitations | Si₃N₄ 应力/开裂管理、高 Q 波导 | [PDF](../../Q1_工艺_L01相关/F_07_Luke_2013_Si3N4_Stress_HighQ_Ring_OptExpress.pdf) · [笔记](../../Q1_工艺_L01相关/阅读笔记_F_07_Luke_2013.md) |

## 相关文献（跨体系引用）

- L01 Huang 2023（Si₃N₄ 为波导层，顶层 PMMA）
- F-10 Shi 2024（Si₃N₄ 波导 + α-Si 顶层）

## 关键要点

- PECVD vs LPCVD：PECVD 300 °C 应力较高（F-02 用 PECVD；F-01 用 LPCVD 高均匀）。
- 应力管理：厚膜（>400 nm）开裂风险，必要时 trench 隔离（F-07）。
- 刻蚀配方：CHF₃/SF₆/N₂ RIE（F-02 模板）；DUV 量产可用 KrF/ArF（F-01）。

## 波段专题

- [1550波段](1550波段/README.md):C 波段 SiN 超表面/波导候选文献 **19 篇**(A 波导集成 7 / B 高Q·BIC 5 / C 综述制造 4 / D 自由空间 metalens 3),2026-09-04 经 CrossRef 核实入库;**2026-09-10 位置修正**:原 D4(1100/8000 nm)因波段不符已迁出本专题。

## 非波段文献（体系根 `pdfs/`，2026-09-10 迁入）

| 编号 | 分区 | 年份 · 期刊 | 文献 | 实际波段 | PDF / 笔记 |
| --- | --- | --- | --- | --- | --- |
| ⚠️ D4 | Q2 · 中科院三区 | **2026 · Journal of Optics 28(1), 015102** | Mekonnen Berhe *et al.*, *All-pass Si₃N₄ metasurface filter for advanced photonic applications: metalenses, vortex beams, and holography*; [DOI](https://doi.org/10.1088/2040-8986/ae292f) | **1100 nm(近红外) / 8000 nm(中红外)双波段，数值为主** | [PDF](pdfs/D4_MekonnenBerhe_2026_SiN_allpass_metasurface.pdf) · [笔记](阅读笔记_D4_MekonnenBerhe_2026.md) |

> ⚠️ **使用边界**:D4 的工作波段**不是 1550 nm**;仅可借鉴全通(All-pass)判据与效率–NA 权衡方法,**纳米柱几何不可搬用**。它原先按"SiN 自由空间超表面"主题归入 1550 nm 专题,2026-09-10 因波段不符迁至体系根目录(非波段位置),编号沿用原专题编号以便追溯。

## 待补充文献

- ~~Si₃N₄ 顶层超表面(非波导层)的专项设计/工艺文献。~~ → 已由 [1550波段专题](1550波段/README.md) 部分覆盖(D 组自由空间 metalens);仍待补:SiN 顶层超表面在 C 波段的固定焦 metalens 实验文献(目前为体系空档)。
