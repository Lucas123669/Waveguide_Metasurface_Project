# 体系：PMMA（顶层超表面 = PMMA）

## 体系定位

顶层超表面材料为聚甲基丙烯酸甲酯（PMMA，n≈1.48）。PMMA 可同时作为电子束胶与超表面/波导图案层（无刻蚀路线），是本项目主论文 L01 的核心体系，也是加工友好性最强的体系。

## 主文献

| 编号 | 标题 | 在本体系中的角色 | PDF / 笔记 |
| --- | --- | --- | --- |
| L01 | Leaky-wave metasurfaces for integrated photonics | 主论文：PMMA 椭圆孔 qBIC + Si₃N₄ 波导，单层 PMMA 无刻蚀工艺 | [PDF](../../L01_Huang_2023_Leaky-Wave_Metasurfaces.pdf) · [SI](../../L01_Huang_2023_补充材料.pdf) · [笔记](../../阅读笔记_L01_Huang_2023.md) |
| L04 | Accessible, All-Polymer Metasurfaces: Low Effort, High Quality Factor | PMMA 直接做 qBIC 谐振材料（三步工艺，Q 最高 523）；配方与 L01 一一对应 | [PDF](../../L04_Hirler_2026_All-Polymer_Metasurfaces.pdf) · [SI](../../L04_Hirler_2026_补充材料.pdf) · [笔记](../../阅读笔记_L04_Hirler_2026.md) |
| L05 | A review of PMMA as a versatile lithographic resist | PMMA 光刻胶机制综述（曝光/显影/剂量标定） | [PDF](../../L05_Rahman_2020_PMMA_Lithographic_Resist.pdf) · [笔记](../../阅读笔记_L05_Rahman_2020.md) |
| F-06 | Direct electron beam writing of electro-optic polymer microring resonators | PMMA 直接 EBL 写入波导（30 kV/700 μC/cm²） | [PDF](../../Q1_工艺_L01相关/F_06_2008_Direct_EBL_PMMA_Microring_OptExpress.pdf) · [笔记](../../Q1_工艺_L01相关/阅读笔记_F_06_Sun_2008.md) |

## 相关文献（跨体系引用）

- F-08 Yang 2024（制造综述中的聚合物/灰度工艺）

## 关键要点

- PMMA 950K（AR-P 679.04）300 nm；剂量随电压换算（100 keV 750 ↔ 20 kV 200–250 μC/cm²）。
- 显影家族：3:1 或 7:3 IPA:水（高对比水稀释路线）。
- 绝缘衬底需 Espacer 300Z 电荷泄放；版图避免尖角（L04 SI：膜易在尖角撕裂）。
- 低折射率弱约束 = 容错设计；但 Q 上限受材料限制（Q≈500 量级）。

## 待补充文献

- PMMA 在 1.55 μm 的精确 n/k 实测（SI Fig. S1 为图形数据，建议椭偏实测）。
