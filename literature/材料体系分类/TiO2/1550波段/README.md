# TiO₂ 超表面｜1550 nm / 通信波段代表文献

> 范围：TiO₂ 作为主要纳米结构材料、波导/谐振层，且工作波段覆盖 1.5–1.6 μm 或明确包含 1550 nm。  
> 整理日期：2026-09-08。PDF 统一命名为 `编号_第一作者_年份_短标题.pdf`；每篇均有中文项目笔记。

## 波段适用性（先读）

> **本专题范围 = 1.5–1.6 μm / 1550 nm，收录 T1–T6。** 两处容易混用的边界:
>
> 1. **T7(Gao 2025,晶圆级倾斜 TiO₂ 光栅)不属于本专题**:其工作波段为**可见光 532 nm**,按材料体系存放在体系根目录,见 [`../README.md`](../README.md) 的 T7 章节。引用时须写明波段,**不得与 T1–T6 的 C 波段结论混用**。
> 2. T1 是多材料横向对照(TiO₂ 为基准之一)、T2 是光纤集成综述:两者本身跨材料/跨波段,只能用于方法定位,不作为单器件性能记录。

## 入库口径与证据等级

- **实验**：包含实际器件制备与光学测量，可用于建立工艺和实测性能基线。
- **数值设计**：参数来自 RCWA/FDTD 等仿真，不能直接当作实验效率或制造容差。
- **综述**：用于建立 fiber-integrated metasurface 的方法和工艺导航，不作为单一器件性能记录。
- T1 是 1550 nm 多材料 metalens 对照研究，TiO₂ 是其中一个基准材料；T2 是光纤集成综述。两篇均保留，因为它们分别回答“为什么选 TiO₂”和“怎样集成到导模平台”。

## 代表文献清单

| 编号 | 年份 · 期刊 | 文献与 DOI | 波段 / 证据 | 对项目的直接价值 | PDF / 笔记 |
| --- | --- | --- | --- | --- | --- |
| T1 | **2019 · Applied Optics 58(6), 1460–1466** | Bayati *et al.*, *Role of refractive index in metalens performance*；[DOI](https://doi.org/10.1364/AO.58.001460) | 1550 nm；数值对照 | TiO₂（n=2.4）与 Si/GaN/SiN 等统一口径比较；给出 TiO₂ 元胞初值 | [PDF](pdfs/T1_Bayati_2019_Refractive_Index_Metalens_Performance.pdf) · [笔记](阅读笔记_T1_Bayati_2019.md) |
| T2 | **2022 · Nanomaterials 12(5), 793** | Zhao *et al.*, *Optical Fiber-Integrated Metasurfaces: An Emerging Platform for Multiple Optical Applications*；[DOI](https://doi.org/10.3390/nano12050793) | 800–1550 nm 相关；综述 | 光纤端面/纤芯集成、相位机制和 FIB/EBL/NIL 等工艺路线图 | [PDF](pdfs/T2_Zhao_2022_Optical_Fiber_Integrated_Metasurfaces_Review.pdf) · [笔记](阅读笔记_T2_Zhao_2022.md) |
| ★T3 | **2021 · Micromachines 12(2), 219** | Zhao *et al.*, *Endless Single-Mode Photonic Crystal Fiber Metalens for Broadband and Efficient Focusing in Near-Infrared Range*；[DOI](https://doi.org/10.3390/mi12020219) | 800–1550 nm；数值设计 | TiO₂ 柱直接放在 LMA-PCF 纤芯区，最接近“导模驱动 + TiO₂ 波前整形” | [PDF](pdfs/T3_Zhao_2021_Broadband_PCF_TiO2_Metalens.pdf) · [笔记](阅读笔记_T3_Zhao_2021.md) |
| T4 | **2022 · Nanomaterials 12(4), 653** | Guo *et al.*, *Multifunctional Optical Vortex Beam Generator via Cross-Phase Based on Metasurface*；[DOI](https://doi.org/10.3390/nano12040653) | 1550 nm；数值设计 | 给出 TiO₂/SiO₂ 方柱库和 vortex/OAM 多功能相位拼接示例 | [PDF](pdfs/T4_Guo_2022_Multifunctional_Optical_Vortex_Generator.pdf) · [笔记](阅读笔记_T4_Guo_2022.md) |
| ★T5 | **2023 · Photonics 10(1), 28** | Li *et al.*, *Achromatic Flat Metasurface Fiber Couplers within Telecom Bands*；[DOI](https://doi.org/10.3390/photonics10010028) | 1330–1550 nm；数值设计 | TiO₂/SiO₂/PDMS 平面光纤耦合器；给出固定高度、变直径的消色差优化流程 | [PDF](pdfs/T5_Li_2023_Achromatic_Flat_Metasurface_Fiber_Coupler.pdf) · [笔记](阅读笔记_T5_Li_2023.md) |
| ★T6 | **2026 · Nature Nanotechnology，在线发表** | Fathi *et al.*, *Quantum-well metasurface for free-space-accessible enhanced nonlinear polarization*；[DOI](https://doi.org/10.1038/s41565-026-02268-0) | 实测谐振 1567 nm；实验 | TiO₂ 纳米柱 GMR 与 MQW 混合集成；提供 1550 nm 附近高 Q、ALD+EBL 制造及非线性增强实测基线 | [PDF](pdfs/T6_Fathi_2026_Quantum_Well_TiO2_Metasurface.pdf) · [笔记](阅读笔记_T6_Fathi_2026.md) |

## 按项目问题选文献

1. **先建 TiO₂ 元胞库**：T1 给出材料横向基准；T3、T4、T5 给出传播相位型圆柱/方柱的几何初值。
2. **做导模或光纤集成**：先读 T2 的平台/制造综述，再用 T3 与 T5 比较“直接在纤芯区布柱”和“独立薄片贴合端面”两条路线。
3. **做高 Q 或非线性升级**：T6 是本专题唯一实验论文，应优先用于谐振线宽、加工流程和实验可达性判断。
4. **做 OAM / vortex 功能**：T4 可复用 cross-phase 相位构造，但其器件效率和容差未形成实验基线。

## 使用边界

- T1、T3、T4、T5 的性能是仿真结果；设计进入本项目参数表前，应在统一 TiO₂ 色散、基底和网格下复算。
- T3 正文 Fig. 8 给出焦距随 800→1550 nm 由约 380→310 μm；结论段出现“310→280 μm”的内部笔误，笔记以图和正文结果为准。
- T5 的“平均耦合效率 0.43”是计算值，且作者明确指出端面装调误差仍待研究。
- T6 为 TiO₂ GMR + GaAs/AlGaAs MQW 混合体系；增强非线性主要来自 MQW，TiO₂ 的角色是提供可由自由空间访问的谐振场，而非自身产生巨大 χ²。

## 尚未本地化的扩展候选

- Lee *et al.*, *Resonant grating polarizers made with silicon nitride, titanium dioxide, and silicon*, Optics Express 22(8), 9271–9280 (2014)，[DOI](https://doi.org/10.1364/OE.22.009271)：C-band TiO₂ GMR 器件；本次出版社验证页阻断自动获取。
- Dong *et al.*, *On-chip trans-dimensional plasmonic router*, Nanophotonics 9 (2020)，[DOI](https://doi.org/10.1515/nanoph-2020-0078)：1550 nm TiO₂ meta-wall 片上路由；本次下载端点受验证页限制。

## 文件审计

- 本地 PDF：**6/6**；阅读笔记：**6/6**。
- 六份 PDF 均已验证 `%PDF` 文件头、页数、非加密状态，并完成首页渲染目检。
- 下载来源、许可声明、文件大小与 SHA-256 见 [download_manifest.json](download_manifest.json)。
