# 1550 nm Si 体系候选文献

> 范围:1.5–1.6 μm(C 波段 / 1550 nm)的 a-Si、c-Si、SOI 超表面与片上辐射器件。  
> 整理日期:2026-09-03(初版)/ 2026-09-07(增补 B9 + 全 30 篇 SCI 分区列)/ 2026-09-08(增补 A9、A10 两篇,并补齐两篇阅读笔记)/ 2026-09-09(增补 C7、A11、D8、D9 与 E1；C2 更新为正式期刊 PDF)/ **2026-09-10(波段位置修正:B9、D8 因波段不符迁出本专题)**。现有原文均已补上**年份 · 期刊**标签和项目笔记;PDF 统一采用 `编号_第一作者_年份_短标题.pdf`。
> 2026-09-07 起,A/B/C/D 表新增 **SCI 分区** 列(中科院升级版 + JCR Q)。
> **2026-09-11 补**:★A8(Guo 2020,即项目 L02)新增 [精读笔记](精读笔记_A8_Guo_2020_构思结构与术语.md)(构思 · 结构 · 递进 · 术语 + 本项目 45° 复现状态)。
> **2026-09-10 波段位置修正**:原 **B9 Eyvazi 2025**(激射中心 ~800–850 nm)与 **D8 Yao 2017**(工作波段 600–800 nm)已迁出本专题,移至 **Si 体系根目录(非波段位置)**,不再计入本专题条目与 PDF 审计:
> - `材料体系分类/Si/pdfs/B9_Eyvazi_2025_Si_flatband_lasing_BIC.pdf` + `材料体系分类/Si/阅读笔记_B9_Eyvazi_2025.md`
> - `材料体系分类/Si/pdfs/D8_Yao_2017_Heterogeneous_Metasurface_Broadband_Reflector.pdf` + `材料体系分类/Si/阅读笔记_D8_Yao_2017.md`
>
> 编号沿用原专题编号以便追溯,登记见 [`../README.md`](../README.md);引用时仍须写明其实际波段。

## 波段适用性（先读）

> **专题目标波段 = 1.55 μm / C 波段（1.5–1.6 μm）。经 2026-09-10 位置修正后,本专题条目全部工作在目标波段内。**
>
> 原按主题归入、但波段不符的两个条目已**迁出**本专题,移至 Si 体系根目录(非波段位置):

| 编号 | 实际波段 | 现位置 | 允许的使用方式 |
| --- | --- | --- | --- |
| ⚠️ B9 Eyvazi 2025 | 激射中心 ~800–850 nm | [`../pdfs/`](../pdfs/) + [`../阅读笔记_B9_Eyvazi_2025.md`](../阅读笔记_B9_Eyvazi_2025.md) | 仅借"波导集成 + flat-band + BIC"机制框架;数值不可用于 1550 nm |
| ⚠️ D8 Yao 2017 | 600–800 nm | [`../pdfs/`](../pdfs/) + [`../阅读笔记_D8_Yao_2017.md`](../阅读笔记_D8_Yao_2017.md) | 仅借异质叠层/超薄壳层设计思想;几何参数不可套用 |

> 引用上述条目时,正文必须写明实际波段。

## 入库与标注规则

- 编号:A=波导集成/片上辐射,B=高 Q / BIC,C=综述与制造,D=自由空间 Si metalens,E=材料参数、损耗与工艺窗口。
- 文件名:专题 `pdfs/` 内统一为 `编号_第一作者_年份_短标题.pdf`,仅用 ASCII 字母、数字和下划线;短标题保留可检索关键词,不重复期刊信息。A8 复用项目全局 L02,保留其现有主文献名。
- 年份 · 期刊:以正式出版年份和期刊卷(期)/文章号为准;预印本用 arXiv 号。
- **SCI 分区列**:采用"**JCR Q? · 中科院X区 [Top]**"格式(中科院 2025 升级版)。Q1 Top = 学科前 5%,Q1 = 前 5–10%,Q2 = 前 10–25%,Q3 = 前 25–50%,Q4 = 后 50%。若作者发表时该刊为 OA 出版,额外标 **OA**。
- PDF 审计(2026-09-10):专题目录检出 **31 份** PDF(A1–A6、A9–A11、B1–B5/B8、C1–C7、D1–D7/D9、E1；B9 与 D8 已迁出本专题),项目根文献已有 A8(L02)1 份,合计 **32 份**在库；A7、B6、B7 仍待补档。C2 已用正式期刊版替换原 arXiv 版，E1 已补入出版社 PDF。两份出版社 PDF 仅适用于当前 Private 仓库，重新公开前必须复核或移除。
- 笔记口径:数值优先取本地 PDF;综述记录可直接用于本项目的设计/工艺路线。

## A 组｜Si 波导集成 / 片上辐射

| 编号 | SCI 分区 | 年份 · 期刊 | 文献与 DOI | 本地 PDF | 笔记 |
| --- | --- | --- | --- | --- | --- |
| ★A1 | Q1 · 中科院二区 | **2023 · Optics Express 31(8), 12487–12496** | Hsieh *et al.*, *Metasurfaces on silicon photonic waveguides for simultaneous emission phase and amplitude control*;[DOI](https://doi.org/10.1364/OE.487589) | [PDF](pdfs/A1_Hsieh_2023_Waveguide_Phase_Amplitude_Control.pdf) | [阅读笔记](阅读笔记_A1_Hsieh_2023.md) |
| ★A2 | Q2 · 中科院三区(OA) | **2025 · Scientific Reports 15, 19964** | Tanhayivash *et al.*, *Phase and amplitude gradient waveguide coupled metasurfaces*;[DOI](https://doi.org/10.1038/s41598-025-05141-7) | [PDF](pdfs/A2_Tanhayivash_2025_Phase_Amplitude_Gradient_Waveguide_Metasurfaces.pdf) | [阅读笔记](阅读笔记_A2_Tanhayivash_2025.md) |
| ★A3 | Q1 · 中科院一区 Top | **2023 · Photonics Research 11(9), 1570–1584** | Van Iseghem & Bogaerts, *Optical leaky fin waveguide for long-range optical antennas*;[DOI](https://doi.org/10.1364/PRJ.490085) | [PDF](pdfs/A3_Van_Iseghem_2023_Optical_Leaky_Fin_Waveguide.pdf) | [阅读笔记](阅读笔记_A3_Van_Iseghem_Bogaerts_2023.md) |
| A4 | Q1 · 中科院二区 | **2011 · Optics Express 19(22), 21595–21604** | Doylend *et al.*, *Two-dimensional free-space beam steering with an optical phased array on silicon-on-insulator*;[DOI](https://doi.org/10.1364/OE.19.021595) | [PDF](pdfs/A4_Doylend_2011_SOI_Optical_Phased_Array.pdf) | [阅读笔记](阅读笔记_A4_Doylend_2011.md) |
| A5 | Q1 · 中科院一区 Top | **2013 · Nature 493, 195–199** | Sun *et al.*, *Large-scale nanophotonic phased array*;[DOI](https://doi.org/10.1038/nature11727) | [PDF](pdfs/A5_Sun_2013_Large_Scale_Nanophotonic_Phased_Array.pdf) | [阅读笔记](阅读笔记_A5_Sun_2013.md) |
| A6 | Q1 · 中科院二区 | **2015 · Optics Express 23(12), 16289–16304** | Bozzola *et al.*, *Optimising apodized grating couplers in a pure SOI platform to −0.5 dB coupling efficiency*;[DOI](https://doi.org/10.1364/OE.23.016289) | [PDF](pdfs/A6_Bozzola_2015_Apodized_Grating_Couplers.pdf) | [阅读笔记](阅读笔记_A6_Bozzola_2015.md) |
| A7 | Q3 · 中科院四区(OA) | **2024 · Engineering Research Express 6(1), 015044** | Chen, *Subwavelength grating waveguide antenna based on interleaved groove structure*;[DOI](https://doi.org/10.1088/2631-8695/ad1d21) | 待补档 | [笔记(待原文核对)](阅读笔记_A7_Chen_2024.md) |
| A8 | Q1 · 中科院一区 Top(OA) | **2020 · Science Advances 6, eabb4142** | Guo *et al.*, *Molding free-space light with guided wave-driven metasurfaces*;[DOI](https://doi.org/10.1126/sciadv.abb4142) | [项目已有 PDF](../../../L02_Guo_2020_Molding_Free-Space_Light.pdf) | [阅读笔记](阅读笔记_A8_Guo_2020.md) · [精读笔记](精读笔记_A8_Guo_2020_构思结构与术语.md) |
| A9 | Q1 · 中科院一区 Top | **2023 · Nano Letters 23(6), 2094–2099** | Mikhin *et al.*, *Coherent control of topological states in an integrated waveguide lattice*;[DOI](https://doi.org/10.1021/acs.nanolett.2c04182)([arXiv:2210.01648](https://arxiv.org/abs/2210.01648)) | [PDF](pdfs/A9_Mikhin_2023_Coherent_Control_Topological_States.pdf) | [阅读笔记](阅读笔记_A9_Mikhin_2023.md) |
| A10 | Q1 · 中科院二区 | **2011 · Optics Letters 36(11), 2110–2112** | Schmid *et al.*, *Temperature-independent silicon subwavelength grating waveguides*;[DOI](https://doi.org/10.1364/OL.36.002110) | [PDF](pdfs/A10_Schmid_2011_Temperature_Independent_SWG_Waveguides.pdf) | [阅读笔记](阅读笔记_A10_Schmid_2011.md) |
| A11 | Q1 · 中科院一区 | **2019 · Advanced Optical Materials 7(4), 1801191** | Wang *et al.*(上海交大 张永/苏翼凯), *Compact Silicon Waveguide Mode Converter Employing Dielectric Metasurface Structure*;[DOI](https://doi.org/10.1002/adom.201801191) | [PDF](pdfs/A11_Wang_2019_Silicon_Mode_Converter_Dielectric_Metasurface.pdf) | [阅读笔记](阅读笔记_A11_Wang_2019.md) |

## B 组｜高 Q / qBIC / BIC

| 编号 | SCI 分区 | 年份 · 期刊 | 文献与 DOI | 本地 PDF | 笔记 |
| --- | --- | --- | --- | --- | --- |
| ★B1 | Q1 · 中科院一区 Top(OA) | **2023 · Nature Communications 14, 3433** | Huang *et al.*, *Ultrahigh-Q guided mode resonances in an all-dielectric metasurface*;[DOI](https://doi.org/10.1038/s41467-023-39227-5) | [PDF](pdfs/B1_Huang_2023_Ultrahigh_Q_Guided_Mode_Resonances.pdf) | [阅读笔记](阅读笔记_B1_Huang_2023.md) |
| ★B2 | Q1 · 中科院一区 Top | **2025 · Nano Letters 25(7), 2777–2784** | Watanabe *et al.*, *Low-Contrast BIC Metasurfaces with Quality Factors Exceeding 100,000*;[DOI](https://doi.org/10.1021/acs.nanolett.4c05880) | [PDF](pdfs/B2_Watanabe_2025_Low_Contrast_BIC_Metasurfaces.pdf) | [阅读笔记](阅读笔记_B2_Watanabe_2025.md) |
| ★B3 | Q1 · 中科院一区 Top | **2024 · Advanced Functional Materials 34(11), 2309982** | Huang *et al.*, *Realizing Ultrahigh-Q Resonances Through Harnessing Symmetry-Protected BICs*;[DOI](https://doi.org/10.1002/adfm.202309982) | [PDF](pdfs/B3_Huang_2024_Symmetry_Protected_BIC.pdf) | [阅读笔记](阅读笔记_B3_Huang_2024.md) |
| B4 | Q1 · 中科院一区 Top | **2026 · Nano Letters 26(14), 4822–4829** | Zhu *et al.*, *Observation of Dual-Band Intrinsic Chirality in Underetched Silicon Metasurfaces via Quasi-BICs*;[DOI](https://doi.org/10.1021/acs.nanolett.6c00556) | [PDF](pdfs/B4_Zhu_2026_Underetched_Silicon_Chiral_qBIC.pdf) | [阅读笔记](阅读笔记_B4_Zhu_2026.md) |
| B5 | Q2 · 中科院三区(OA) | **2017 · Sensors 17(8), 1861** | Liu *et al.*, *Optical Refractive Index Sensing Based on High-Q BICs in Free-Space Coupled Photonic Crystal Slabs*;[DOI](https://doi.org/10.3390/s17081861) | [PDF](pdfs/B5_Liu_2017_BIC_Refractive_Index_Sensing.pdf) | [阅读笔记](阅读笔记_B5_Liu_2017.md) |
| B6 | Q1 · 中科院二区 | **2014 · Optics Express 22(8), 9271–9280** | Lee *et al.*, *Resonant grating polarizers made with silicon nitride, titanium dioxide, and silicon*;[DOI](https://doi.org/10.1364/OE.22.009271) | 待补档 | [笔记(待原文核对)](阅读笔记_B6_Lee_2014.md) |
| B7 | Q1 · 中科院一区 Top | **2023 · ACS Photonics 10(2), 534–543** | Kalinic *et al.*, *Quasi-BIC Modes in All-Dielectric Slotted Nanoantennas for Enhanced Er³⁺ Emission*;[DOI](https://doi.org/10.1021/acsphotonics.2c01703) | 待补档 | [笔记(待原文核对)](阅读笔记_B7_Kalinic_2023.md) |
| B8 | Q1 · 中科院二区 | **2025 · Optics Express 33(5), 11853–11862** | Zhou *et al.*, *Efficient silicon-erbium photonic hybrids with flexible spatial control of light via BICs*;[DOI](https://doi.org/10.1364/OE.555348) | [PDF](pdfs/B8_Zhou_2025_Silicon_Erbium_BIC_Hybrids.pdf) | [阅读笔记](阅读笔记_B8_Zhou_2025.md) |

> **易混提示(2026-09-10 补)**:本专题 ★B1 是 **Huang et al., Nat. Commun. 14, 3433 (2023)**(SOI 上全介质 GMR 超表面,Q_rad∝δ⁻²);项目主文献 **L01** 是 **Huang et al., Nat. Nanotechnol. 18(6), 580–588 (2023)**(PMMA/Si₃N₄ qBIC 泄漏波超表面)。两篇第一作者同姓、同年,但材料体系(SOI vs PMMA/Si₃N₄)、结构机制(全介质 GMR vs 椭圆孔 qBIC 漏波)与 δ 的定义都不同,**Q 值与 δ 标度不可跨文互用**;引用时务必写全期刊与卷页。
>
> **编号完整性说明**:原 B9(非 1550 nm)已于 2026-09-10 迁出本专题,故 B 组现为 B1–B8;其文件位置见本页"波段适用性(先读)"。

## C 组｜综述 / 制造平台

| 编号 | SCI 分区 | 年份 · 期刊 | 文献与 DOI | 本地 PDF | 笔记 |
| --- | --- | --- | --- | --- | --- |
| ★C1 | Q1 · 中科院一区 Top | **2026 · Advanced Photonics 8(2), 024003** | Li *et al.*, *Metasurface-empowered integrated silicon photonics: foundational principles, representative applications, and fabrication strategies*;[DOI](https://doi.org/10.1117/1.AP.8.2.024003) | [PDF](pdfs/C1_Li_2026_Metasurface_Empowered_Integrated_Silicon_Photonics.pdf) | [阅读笔记](阅读笔记_C1_Li_2026.md) · [精读笔记](精读笔记_C1_Li_2026_构思结构与术语.md) |
| ★C2 | Q1 · 中科院一区 Top(OA) | **2015 · Nature Communications 6, 7069** | Arbabi *et al.*, *Subwavelength-thick lenses with high numerical apertures and large efficiency based on high contrast transmitarrays*;[DOI](https://doi.org/10.1038/ncomms8069) | [PDF](pdfs/C2_Arbabi_2015_High_Contrast_Transmitarray_Lens.pdf) | [阅读笔记](阅读笔记_C2_Arbabi_2015.md) |
| ★C3 | Q1 · 中科院一区 Top(OA) | **2024 · Nature Communications 15, 8271** | Ji *et al.*, *On-chip multifunctional metasurfaces with full-parametric multiplexed Jones matrix*;[DOI](https://doi.org/10.1038/s41467-024-52476-2) | [PDF](pdfs/C3_Ji_2024_On_Chip_Full_Parametric_Jones_Matrix.pdf) | [阅读笔记](阅读笔记_C3_Ji_2024.md) · [精读笔记](精读笔记_C3_Ji_2024_构思结构与术语.md) |
| C4 | Q1 · 中科院一区(OA) | **2020 · Nanophotonics 9(10), 3071–3087** | Li *et al.*, *Large-area metasurface on CMOS-compatible fabrication platform: driving flat optics from lab to fab*;[DOI](https://doi.org/10.1515/nanoph-2020-0063) | [PDF](pdfs/C4_Li_2020_Large_Area_CMOS_Metasurface_Platform.pdf) | [阅读笔记](阅读笔记_C4_Li_2020.md) |
| C5 | Q1 · 中科院一区 Top | **2018 · Nanophotonics 7(6), 1041–1066** | Kamali *et al.*, *A review of dielectric optical metasurfaces for wavefront control*;[DOI](https://doi.org/10.1515/nanoph-2017-0129) | [PDF](pdfs/C5_Kamali_2018_Dielectric_Metasurface_Wavefront_Control_Review.pdf) | [阅读笔记](阅读笔记_C5_Kamali_2018.md) |
| C6 | Q1 · 中科院一区 Top(OA) | **2024 · ACS Photonics 11(3), 816–955** | Kuznetsov *et al.*, *Roadmap for Optical Metasurfaces*;[DOI](https://doi.org/10.1021/acsphotonics.3c00457) | [PDF](pdfs/C6_Kuznetsov_2024_Roadmap_for_Optical_Metasurfaces.pdf) | [阅读笔记](阅读笔记_C6_Kuznetsov_2024.md) |
| C7 | Q2 · 中科院三区(OA) | **2020 · Micromachines 11(7), 666** | Cheng *et al.*(清华-伯克利深圳研究院 TBSI), *Grating Couplers on Silicon Photonics: Design Principles, Emerging Trends and Practical Issues*;[DOI](https://doi.org/10.3390/mi11070666) | [PDF](pdfs/C7_Cheng_2020_Grating_Couplers_Silicon_Photonics_Review.pdf) | [阅读笔记](阅读笔记_C7_Cheng_2020.md) · [精读笔记](精读笔记_C7_Cheng_2020_构思结构与术语.md) |

## D 组｜自由空间 Si metalens @1550 nm

| 编号 | SCI 分区 | 年份 · 期刊 | 文献与 DOI | 本地 PDF | 笔记 |
| --- | --- | --- | --- | --- | --- |
| D1 | Q1 · 中科院一区 Top(OA) | **2016 · Optica 3(6), 628–633** | Arbabi *et al.*, *Multiwavelength polarization-insensitive lenses based on dielectric metasurfaces with meta-molecules*;[DOI](https://doi.org/10.1364/OPTICA.3.000628) | [PDF](pdfs/D1_Arbabi_2016_Multiwavelength_Meta_Molecule_Lenses.pdf) | [阅读笔记](阅读笔记_D1_Arbabi_2016.md) |
| D2 | Q1 · 中科院一区 Top(OA) | **2018 · Light: Science & Applications 7, 85** | Shrestha *et al.*, *Broadband achromatic dielectric metalenses*;[DOI](https://doi.org/10.1038/s41377-018-0078-x) | [PDF](pdfs/D2_Shrestha_2018_Broadband_Achromatic_Dielectric_Metalenses.pdf) | [阅读笔记](阅读笔记_D2_Shrestha_2018.md) |
| D3 | Q1 · 中科院二区 | **2022 · Optics Express 30(22), 39860–39866** | Liu *et al.*, *Broadband behavior of quadratic metalenses with a wide field of view*;[DOI](https://doi.org/10.1364/OE.466321) | [PDF](pdfs/D3_Liu_2022_Quadratic_Metalens_Wide_FOV.pdf) | [阅读笔记](阅读笔记_D3_Liu_2022.md) |
| D4 | Q2 · 中科院三区(OA) | **2025 · Scientific Reports 15, 43343** | Cao *et al.*, *Single-layer silicon metalens for broadband achromatic focusing and wide field of view*;[DOI](https://doi.org/10.1038/s41598-025-27208-1) | [PDF](pdfs/D4_Cao_2025_Single_Layer_Silicon_Achromatic_Wide_FOV_Metalens.pdf) | [阅读笔记](阅读笔记_D4_Cao_2025.md) |
| D5 | Q1 · 中科院一区(OA) | **2022 · Nanophotonics 11(2), 405–413** | Li *et al.*, *Flat telescope based on an all-dielectric metasurface doublet enabling polarization-controllable enhanced beam steering*;[DOI](https://doi.org/10.1515/nanoph-2021-0609) | [PDF](pdfs/D5_Li_2022_Flat_Telescope_Metasurface_Doublet.pdf) | [阅读笔记](阅读笔记_D5_Li_2022.md) |
| D6 | Q1 · 中科院一区 Top | **2024 · Advanced Optical Materials 12(18), 2400191** | Matiushechkina *et al.*, *Perfect Mirror Effects in Metasurfaces of Silicon Nanodisks at Telecom Wavelength*;[DOI](https://doi.org/10.1002/adom.202400191) | [PDF](pdfs/D6_Matiushechkina_2024_Silicon_Nanodisk_Perfect_Mirror.pdf) | [阅读笔记](阅读笔记_D6_Matiushechkina_2024.md) |
| D7 | arXiv 预印本(未正式出版) | **2017 · arXiv:1711.01430** | Vasilantonakis *et al.*, *Refractive index contrast enhanced metalens on an SOI platform for large angle deflection*;[arXiv](https://arxiv.org/abs/1711.01430) | [PDF](pdfs/D7_Vasilantonakis_2017_SOI_Large_Angle_Deflector.pdf) | [阅读笔记](阅读笔记_D7_Vasilantonakis_2017.md) |
| D9 | Q1 · 中科院二区(OA) | **2010 · Optics Express 18(16), 16973–16988** | Karagodsky *et al.*(UC Berkeley), *Theoretical analysis of subwavelength high contrast grating reflectors*;[DOI](https://doi.org/10.1364/OE.18.016973) | [PDF](pdfs/D9_Karagodsky_2010_HCG_Reflector_Theory.pdf) | [阅读笔记](阅读笔记_D9_Karagodsky_2010.md) |

> **编号完整性说明**:原 D8(600–800 nm,非目标波段)已于 2026-09-10 迁出本专题,故 D 组现为 D1–D7、D9;其文件位置见本页"波段适用性(先读)"。

## E 组｜材料参数 / 损耗与工艺窗口

| 编号 | SCI 分区 | 年份 · 期刊 | 文献与 DOI | 本地 PDF | 笔记 |
| --- | --- | --- | --- | --- | --- |
| E1 | 分区待统一核验 | **2025 · Physical Review Materials 9, 105602** | Molina-Ruiz *et al.*, *Revealing the role of hydrogen in reducing optical absorption and mechanical loss in magnetron-sputtered amorphous silicon for gravitational-wave detectors*;[DOI](https://doi.org/10.1103/5n1c-tjhq) | [PDF](pdfs/E1_Molina_Ruiz_2025_Hydrogenated_Amorphous_Silicon_Loss.pdf) | [阅读笔记](阅读笔记_E1_Molina_Ruiz_2025.md) |

> **E1 适用边界**:原文研究磁控溅射 a-Si:H 镜膜，而非 PECVD 超表面；其 1550 nm 吸收数据用于建立“沉积与热历史决定损耗”的材料证据，不能直接作为本项目纳米柱效率或 PECVD 验收值。

## 使用建议

1. 优先研读 ★A1–A3、★B1–B3、★C1–C3:分别对应导模出射、容差/高 Q、集成与工艺路线。
2. 做器件设计时,把 A6 的 apodization、A3 的长口径低散射、B1–B4 的辐射损耗工程并行比较;不要只比较峰值效率或理论 Q。
3. A7、B6、B7 原文补入前,预备笔记中的参数不可直接进入仿真规格或立项结论。
4. **B9 适配评估**:B9 已于 2026-09-10 迁出本专题(现位于 `Si/pdfs/`)。若项目目标在 1550 nm,仅借鉴其"长程耦合 flat-band + guided mode + BIC"机制框架;若波段适配 800–850 nm,可直接作为光源原型,但**引用时必须写明波段**。
5. E1 用于回答“a-Si:H 为什么不能笼统称为低损耗”：先核对沉积方法、氢化方式和热处理状态，再引用吸收系数；不要把镜膜 QWL 吸收 ppm 直接换成超表面器件效率。
6. **条目与分区口径**:本专题现为 **35 条**(A×11 + B×8 + C×7 + D×8 + E×1;B9、D8 已迁出),其中 **32 份 PDF** 已在项目内可用,A7、B6、B7 待补原文。器件文献的分区只用于初筛；E1 暂标“分区待统一核验”，避免把未经统一年份/学科口径核验的分区写成定论。
7. **器件横向对比**:A2(辐射端·波导驱动超表面)与 Q1-12(激励端·光栅耦合器)的参数、利弊与应用差异,以及"器件类型 × 衬底(SOI/SiOG)"判据,见 [对比分析文档](../../../../docs/reports/literature/2026-09-11_对比_Q1-12光栅耦合器_vs_A2波导超表面.md)。
8. **加工方式对比(2026-09-11 补)**:本专题 **D5 Li 2022** 的补充其支持信息 Figure S10 是"**熔融石英 + 两面 PECVD a-Si:H + ZEP520A/EBL + 60 nm Al 硬掩模 + 氟基 ICP-RIE + 翻面套刻**"的完整流程卡(已补入其[阅读笔记](阅读笔记_D5_Li_2022.md)),即四类材料加工对比中 **Si = 减法** 的代表;Si₃N₄、TiO₂、PMMA 的对应路线与"第一轮继承/延后"清单见 [四类材料加工工艺路线对比](../../../../docs/reports/fabrication/2026-09-11_四类材料加工工艺路线对比.md)(汇报稿第 10 页)。
