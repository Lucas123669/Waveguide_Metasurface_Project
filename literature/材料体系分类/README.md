# 材料体系分类（超表面波导任务）

> 建立日期：2026-09-01 ｜ 更新：2026-09-02（约定修订：本目录开始收录 F08 综述案例原文 PDF）
> 分类维度：**顶层超表面材料体系**（Si / SiN / PMMA / TiO₂），即超表面图案层所用的材料。

## 存放约定（2026-09-02 修订）

- **初版约定（2026-09-01）**：PDF 保持原位（`literature/` 下 L/Q1/F 原结构），本目录只提供分类索引，不复制大文件。
- **修订（2026-09-02）**：自 F08（制造技术综述）案例文献下载起，本目录**同时收纳原文 PDF**（用户要求按体系直接存放）。PDF 放对应体系子目录 `pdfs/`；编号延续 F 系列（F-11 起，与 F-01~F-10 同性质：一区制造工艺文献）；阅读笔记放同体系子目录（`阅读笔记_F_编号_作者_年份.md`）。原「只索引不复制」原则仅对 L/Q1 系列与 F-01~F-10 继续适用。
- 文献编号全局唯一，登记在 `literature/文献清单.md` 与 `project_config.json`。

## 分类规则

- 每篇文献有一个**主体系**（最能指导该体系的设计/工艺）与若干**相关体系**（文中涉及）。
- 主体系详见对应子文件夹 README；相关体系仅在各子文件夹"相关文献"中列出编号。
- 物理/方法/综述类（BIC 物理、选择定则、逆设计、泄漏波、制造综述等）归入"通用交叉"。

## 四体系定位（顶层超表面材料）

| 体系 | 顶层材料 | 代表结构 | 当前主文献 |
| --- | --- | --- | --- |
| [Si](Si/README.md) | 硅（a-/m-/p-Si） | Si 纳米柱/纳米孔/梯形柱 | L02、Q1-05、Q1-11、F-03、F-05、F-10 |
| [SiN](SiN/README.md) | 氮化硅（Si₃N₄） | Si₃N₄ 孔阵/波导超表面 | L03、Q1-03、Q1-04、F-01、F-02、F-04、F-07 |
| [PMMA](PMMA/README.md) | 聚甲基丙烯酸甲酯 | PMMA 椭圆孔（qBIC）/聚合物波导 | L01、L04、L05、F-06 |
| [TiO2](TiO2/README.md) | 二氧化钛（TiO₂） | TiO₂ 纳米柱/金属透镜（ALD/EB 蒸发） | 暂无专属文献（见 F-08 相关工艺），待补充 |
| [通用交叉](通用交叉/README.md) | —（物理/方法/综述） | — | Q1-01、Q1-02、Q1-06、Q1-07、Q1-08、Q1-09、Q1-10、F-08、F-09 |

## 文献-体系归属总表

| 编号 | 主体系 | 相关体系 | 备注 |
| --- | --- | --- | --- |
| L01 Huang 2023 | PMMA | SiN | 顶层 PMMA 椭圆孔；波导层 Si₃N₄ |
| L02 Guo 2020 | Si | — | Si 波导；顶层为 Au/SiO₂/Au 金属三明治（非四体系，标注） |
| L03 Buzaverov 2024 | SiN | — | Si₃N₄ 集成光子学工艺综述 |
| L04 Hirler 2026 | PMMA | — | 全 PMMA qBIC，Q 最高 523 |
| L05 Rahman 2020 | PMMA | — | PMMA 光刻胶综述 |
| Q1-01 Hsu 2016 | 通用交叉 | — | BIC 物理综述 |
| Q1-02 Azzam 2021 | 通用交叉 | — | BIC 综述（应用） |
| Q1-03 Hsu 2013 | SiN | — | 介质 PhC 平板 BIC 实验（Si₃N₄ 类） |
| Q1-04 Kang 2022 | SiN | — | Si₃N₄ 平板 merged BIC |
| Q1-05 Koshelev 2018 | Si | — | qBIC 理论，示例为 Si 结构 |
| Q1-06 Overvig 2020 | 通用交叉 | Si | 选择定则（示例 Si 柱） |
| Q1-07 Lu & Zou 2026 | 通用交叉 | SiN/Si | 片上超表面综述（多体系） |
| Q1-08 Jackson 2011 | 通用交叉 | — | 泄漏波理论（微波/光学） |
| Q1-09 Molesky 2018 | 通用交叉 | — | 逆设计综述 |
| Q1-10 Overvig & Alù 2022 | 通用交叉 | — | 非局域超表面 Perspective |
| Q1-11 Kühne 2021 | Si | — | a-Si qBIC 制造鲁棒性 |
| F-01 Yesilkoy 2026 | SiN | — | Si₃N₄ DUV 晶圆级 qBIC |
| F-02 Tian 2025 | SiN | — | Si₃N₄ 波导超表面（AR） |
| F-03 Liao 2025 | Si | — | Si 梯形柱缺陷不敏感 BIC |
| F-04 Ren 2025 | SiN | — | Si₃N₄ + Sb₂S₃ PCM merged BIC |
| F-05 Campbell 2021 | Si | — | 深度学习容差（Si/SiO₂ 示例） |
| F-06 Sun 2008 | PMMA | — | PMMA 直接 EBL 写入波导 |
| F-07 Luke 2013 | SiN | — | Si₃N₄ 应力与高 Q 波导 |
| F-08 Yang 2024 | 通用交叉 | Si/TiO₂/Si₃N₄ | 制造综述（覆盖四体系） |
| F-09 Park 2019 | 通用交叉 | — | SiO₂ 全玻璃金属透镜（体系外，参考） |
| F-10 Shi 2024 | Si | SiN | α-Si 顶层 + Si₃N₄ 波导 |
| F-11 Devlin 2016 | TiO₂ | — | TiO₂ ALD 反向填充；可见光最高效率全息（F08 案例 C04） |
| F-12 Yang 2020 | Si | — | Si-on-sapphire 结构色纳米盘（F08 案例 C01） |
| F-13 Gorkunov 2018 | Si | — | FIB 直写 m-Si 手性可见超表面（F08 案例 C09） |
| F-14 Huang 2022 | 通用交叉 | — | 图案化脉冲激光光刻（PPL）大面积超表面（F08 案例 C20） |
| F-15 Zhan 2019 | 通用交叉 | — | 双光子逆设计 3D 光场（inverse Mie；F08 案例 C25） |
| F-16 Williams 2019 | 通用交叉 | — | EBL/UV 灰度光刻多光谱滤光阵列（F08 案例 C33） |
| F-17 Zhao 2021 | Si | — | a-Si 合成孔径 metalens（F08 案例 C35） |
| F-18 Hentschel 2023 | Si | — | FIB 灰度 Mie void 彩印（F08 案例 C31） |
| F-19 Xu 2019 | Si | — | 12 in ArF DUV Si 偏振带通滤波（F08 案例 C42；**PDF 待浏览器下载**） |
| F-20 Hu 2020 | Si | — | 12 in a-Si 940 nm metalens（F08 案例 C44；**PDF 待浏览器下载**） |
| F-21 Yoon 2020 | TiO₂ | — | TiO₂ 纳米颗粒树脂一步 UV-NIL metalens（F08 案例 C48） |
| F-22 Choi 2023 | TiO₂ | — | PVA 水溶模湿法 NIL 高深宽比 metalens（F08 案例 C50） |
| F-23 Zheng 2021 | Si | — | DMD 灰度 + 纳米球光刻大面积 metalens（F08 案例 C54） |
| F-24 Pan 2023 | 通用交叉 | — | 双光子 3D 打印多层消色差 metalens（F08 案例 C61） |
| F-25 Chen 2023 | TiO₂ | — | 倾斜扰动固有手性 BIC：CD 0.93、Q>2663（F08 案例 C67；Nature） |
| F-26 Wang 2021 | TiO₂ | — | 1.5 μm 高深宽比 TiO₂ 消色差 metalens（F08 案例 C69；F08 正文 [101]） |
| F-27 Kamali 2016 | Si | — | 共形柔性 a-Si/PDMS 超表面（F08 案例 C65） |

> F-11~F-27 为 2026-09-02 自 F08 综述案例论文下载（PDF 在本目录对应体系 `pdfs/`，笔记在同体系目录，均可点击跳转）。F-19/F-20 出版社反爬暂无法脚本下载，落地页 URL 见 [下载清单](../../scripts/literature/manifests/f08_download_manifest.json)。

## 使用建议

- **文献 PDF/笔记均可点击直达**：下方 5 个体系 README 的"主文献"表里，每篇文献都带 **[PDF]** 与 **[笔记]** 链接（相对本仓库路径，GitHub/本地预览均可点击跳转）。顶层归属总表只做归类概览。
- 快速入口：
  - [Si 体系（含 pdfs/）](Si/README.md) ｜ [SiN 体系](SiN/README.md) ｜ [PMMA 体系](PMMA/README.md) ｜ [TiO₂ 体系（含 pdfs/）](TiO2/README.md) ｜ [通用交叉（含 pdfs/）](通用交叉/README.md)
- 按"我要做哪个体系的顶层超表面"进入对应子文件夹查文献与笔记。
- 工艺/物理基础问题（BIC、泄漏波、逆设计、制造）先看"通用交叉"。
- 各体系 README 中列出"待补充文献"，可指导后续文献收集。
