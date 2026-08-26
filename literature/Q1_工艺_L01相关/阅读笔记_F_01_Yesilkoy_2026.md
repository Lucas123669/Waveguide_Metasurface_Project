# 阅读笔记 F-01 | Yesilkoy 2026：Wafer-Scale All-Dielectric Quasi-BIC Metasurfaces（DUV）

> 笔记日期：2026-08-25 ｜ PDF：`F_01_Yesilkoy_2026_WaferScale_qBIC_DUV_NanoLetters.pdf`（PMC 开放版）

## 1. 论文信息

- 编号：F-01
- 标题：Wafer-Scale All-Dielectric Quasi-BIC Metasurfaces: Bridging High-Throughput Deep-UV Lithography with Nanophotonic Applications
- 作者：Aidana Beisenova, Wihan Adi, Wenxin Wu, Shovasis K. Biswas, Samir Rosas, Biljana Stamenic, Demis D. John, Filiz Yesilkoy
- 期刊：Nano Letters 26(6), 2059–2067（一区）
- 年份：2026（2026-02-06）
- DOI：10.1021/acs.nanolett.5c05226
- 类型：量产工艺（DUV）+ qBIC 器件实验

## 2. 一句话总结

用半导体工业的 248 nm KrF DUV 步进光刻在 4 英寸晶圆上批量制造 Si₃N₄ qBIC 超表面，用"孔径扰动 Δr + 曝光剂量控制孔深"双参数调 Q，实测 Q≈150，并证明 qBIC 的非局域性使器件对随机工艺起伏天然均匀。

## 3. 核心内容

- **结构与材料**：LPCVD Si₃N₄ 160 nm 于 4 in 熔融石英晶圆；方孔阵基准（r=90 nm、P=510 nm），每两孔取一孔减小半径 Δr → 双孔元胞、周期倍增 P≈721 nm（Brillouin zone folding 引入 qBIC）。
- **工艺**：60 nm BARC + 230 nm DUV 化学放大胶；KrF 248 nm stepper 全片曝光 1–2 分钟（对比 EBL 2–5 mm²/数小时）；O₂ ICP 开 BARC，CF₄/O₂ 原位刻 Si₃N₄；显影后剂量矩阵校准 CD/侧壁/刻蚀。
- **新自由度**：曝光剂量 → 小孔刻深（浅孔=低 Q，全刻穿=高 Q），用"孔深"绕开 DUVL 200 nm 分辨率极限。
- **结果**：实测 Q≈150；非局域共振带来跨片空间均匀性（随机纳米起伏不劣化）；折射率传感 129 nm/RIU（CMOS 相机读出）。

## 4. 与 L01 的关联

- L01 的单元同样是"周期倍增 + 孔径扰动"（圆→椭圆、δ 扰动），本工作验证了同类设计的**工业化量产路径**：若我们后续从 EBL 转 DUV，双孔/椭圆孔 + 剂量控深策略可直接移植。
- L01 笔记中"量产路线：单层 PMMA 图案适合 DUV 转移"的设想，本工作提供了 DUV 版 qBIC 的完整工艺参数模板。

## 5. 对我们的启示

1. DUV 做 qBIC 的可行性已实证：若我们最终量产，248 nm DUV + 剂量矩阵是最现实的路线（EBL 仅用于研发）。
2. "非局域性 = 工艺容差"的定量证据：qBIC 的均匀性优于局域共振，支持 L01 的大孔径（500×500 元胞）设计。
3. 工艺参数可直接引用：BARC 60 nm、胶 230 nm、CF₄/O₂ 刻 Si₃N₄、O₂ ICP 开 BARC。

## 6. 待确认问题

- 其 DUV 最小 CD（亚 200 nm）与我们 L01 的 δ（±60–150 nm 扰动）匹配度：需要核对 DUV 下的椭圆孔取向控制能力。
