# 体系：TiO2（顶层超表面 = 二氧化钛）

## 体系定位

顶层超表面材料为二氧化钛（TiO₂，n≈2.87–2.31）。TiO₂ 兼具高折射率与可见-NIR 低损耗，是可见光高效超透镜/超表面的代表材料（Capasso 组等）。

## 当前状态

**2026-09-02 起已有专属文献**(原为空缺,本轮自 F08 案例补入 5 篇):

| 编号 | SCI 分区 | 标题 | 在本体系中的角色 | PDF / 笔记 |
| --- | --- | --- | --- | --- |
| F-11 | Q1 · 中科院一区 Top(OA) | Broadband high-efficiency dielectric metasurfaces for the visible spectrum | EBL 反向结构 + ALD 填 TiO₂ + 平面化 RIE;粗糙度 <1 nm、可见全息 82/81/78%(F08 案例 C04) | [PDF](pdfs/F_11_Devlin_2016_TiO2_ALD_Metasurface_PNAS.pdf) · [笔记](阅读笔记_F_11_Devlin_2016.md) |
| F-21 | Q1 · 中科院一区 Top(OA) | Single-step manufacturing of hierarchical dielectric metalens in the visible | TiO₂ 纳米颗粒树脂(PER)一步 UV-NIL(F08 案例 C48) | [PDF](pdfs/F_21_Yoon_2020_TiO2PER_SingleStep_Metalens_NatCommun.pdf) · [笔记](阅读笔记_F_21_Yoon_2020.md) |
| F-22 | Q1 · 中科院一区(OA) | High aspect ratio metalenses by NIL with water-soluble stamps | PVA 水溶模湿法脱模高深宽比 PER metalens(F08 案例 C50) | [PDF](pdfs/F_22_Choi_2023_PVA_WaterSoluble_NIL_HighAR_Metalens_PhotoniX.pdf) · [笔记](阅读笔记_F_22_Choi_2023.md) |
| F-25 | Q1 · 中科院一区 Top(arXiv 录用前) | Observation of intrinsic chiral bound states in the continuum | 倾斜扰动 TiO₂ 固有手性 BIC:CD 0.93、Q>2663(F08 案例 C67) | [PDF](pdfs/F_25_Chen_2023_Intrinsic_Chiral_BIC_Nature.pdf) · [笔记](阅读笔记_F_25_Chen_2023.md) |
| F-26 | Q1 · 中科院一区 Top(OA) | High-efficiency broadband achromatic metalens for near-IR biological imaging | 1.5 μm 高深宽比 TiO₂ 消色差 metalens(F08 案例 C69) | [PDF](pdfs/F_26_Wang_2021_HighAR_TiO2_Achromatic_Metalens_NatCommun.pdf) · [笔记](阅读笔记_F_26_Wang_2021.md) |

> F-08 制造综述(含 TiO₂ ALD/蒸发/RIE 工艺总参照,Q1 · 中科院一区 Top):[PDF](../../Q1_工艺_L01相关/F_08_Yang_2024_Advanced_Manufacturing_Metadevices_PhotonicsInsights.pdf) · [笔记](../../Q1_工艺_L01相关/阅读笔记_F_08_Yang_2024.md)

## TiO₂ 专题文献

### 1550 nm 专题（T1–T6，PDF 全齐）

> 入口与逐篇说明见 [`1550波段/README.md`](1550波段/README.md)：T1 Bayati 2019、T2 Zhao 2022、T3 Zhao 2021、T4 Guo 2022、T5 Li 2023、T6 Fathi 2026。

- 定位：TiO₂ 在 C 波段的材料/器件证据链——T1 给出不同折射率材料的统一仿真比较；T3/T5 为"导模驱动 + 光纤/波导集成"；**T6（Fathi 2026）是本体系唯一 1550 nm 附近的实验工作**（实测 1567 nm、Q≈1125，衬底为 MQW/蓝宝石而非熔融石英）。
- 边界：材料 n 取值分散（2.05 / 2.4 / 2.55-n_eff），**不能作为同一薄膜在 1550 nm 的材料范围**；进参数表前须用本项目同炉见证片实测色散复算。

### 可见光倾斜光栅 T7（2026-09-10 新增）

| 编号 | SCI 分区 | 标题 | 在本体系中的角色 | PDF / 笔记 |
| --- | --- | --- | --- | --- |
| T7 | Q1 · 中科院一区 Top | Scalable Wafer-Level Fabrication of Slanted TiO₂ Gratings for Directional Visible Light Control | 晶圆级倾斜 TiO₂ 光栅制造：干涉光刻 + NIL 一步复制 + ICP + RIBE 定斜角；AR 衍射光波导应用（F08 §4.3 "斜刻蚀"的最新可量产方案） | [PDF](pdfs/T7_Gao_2025_Slanted_TiO2_Gratings_NanoLett.pdf) · [笔记](阅读笔记_T7_Gao_2025.md) |

- 元数据：Gao, X. *et al.*, Nano Letters **25**(41), 15055–15061 (2025)；[DOI](https://doi.org/10.1021/acs.nanolett.5c04104)。
- **PDF 许可**：本 PDF 为 ACS 出版社正式版（订阅内容），仅适用于当前 Private 仓库；**重新公开仓库前必须复核或移除**（与 Si/1550 专题已标注的两份出版社 PDF 同一处理原则）。
- 关键指标（取自原文）：周期 550 nm、高 350 nm、占空比 0.32、斜角 30°（左右对称）、532 nm TM 正入射、目标 +1 级约 75°；RCWA+PSO 仿真 T₁=80%，**实测绝对效率 39.1%**；斜角失配 10° 时 T₁ 相对下降约 40%；分段 out-coupler 仿真平均均匀性 92%。
- **使用边界：工作波段为可见光（532 nm），非 1550 nm**——不能作为本项目 C 波段的性能依据；可迁移的是"母版单点定义 + 一次 RIBE 全局定斜角"的制造逻辑与 NIL 复制思路。
- 与既有文献的关系：F-25（楔形衬底 + Al₂O₃ 离子准直器实现 φ≈0.1 的高 Q 手性 BIC）与 T7（RIBE 30°、晶圆级）在"面外倾斜 TiO₂"上互补；F-08 §4.3 的斜刻蚀路线在 T7 中被 RIBE 替代（**注意 F-08 笔记记 89.5%、T7 引 83.6%，属引用口径冲突，二者不可混用**）。

## 关键要点（来自主文献）

- TiO₂ 制造高度依赖 ALD（慢、厚度 <600 nm、深宽比 <15，F-11 证明反向填充可达 600 nm 高、间隙 6 nm）；EB 蒸发为更快替代（F-26：1500 nm、0.6 Å/s）。
- 直接刻蚀 TiO₂ 需专用 RIE 配方（F-26：SF₆/CHF₃/O₂、侧壁 89–90°、AR≥37.5）；F-11 走"负结构 + 保形填充 + 回刻"免直刻路线。
- 低缺陷量产：UV-NIL + TiO₂ 纳米颗粒树脂（F-21 一步成型、F-22 PVA 水溶模免脱模应力）。
- 手性升级路线：斜刻蚀 + 面内/面外联合破缺 → 固有手性 BIC（F-25，CD 0.93、Q>2663）。

## 待补充文献（建议优先收集）

- TiO₂ 更宽波段（蓝紫/UV）专项 metalens 效率数据与 NIL 母版长期稳定性。
