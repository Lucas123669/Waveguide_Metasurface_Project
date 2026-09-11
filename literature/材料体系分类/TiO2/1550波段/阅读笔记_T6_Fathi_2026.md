# 阅读笔记 T6｜Fathi 2026：Quantum-Well TiO₂ Metasurface

> **年份 · 期刊**：2026 · *Nature Nanotechnology*（2026-09-02 在线发表）  
> **DOI**：10.1038/s41565-026-02268-0 ｜ **证据等级**：实验 + RCWA/FDTD/量子阱建模  
> **本地 PDF**：[T6_Fathi_2026_Quantum_Well_TiO2_Metasurface.pdf](pdfs/T6_Fathi_2026_Quantum_Well_TiO2_Metasurface.pdf)（期刊正式版）

## 一句话总结

在 GaAs/AlGaAs multi-quantum-well（MQW）薄膜上制造 TiO₂ 纳米柱 guided-mode resonance（GMR），用谐振同时产生并增强泵浦场 Ex 与 Ez，使原本难以由自由空间正入射访问的 MQW χ² 张量变得可用；实测 1567 nm 泵浦处有效 χ² 约 14 nm/V。

## 结构与物理机制

- 非线性层：16 周期 GaAs/AlGaAs coupled quantum wells，总厚约 595 nm，转移并键合到 Al₂O₃/sapphire 基底。
- TiO₂ GMR 单元（RCWA 模型）：柱高 390 nm、半径 230 nm、x/y 周期 891/650 nm；TiO₂ 折射率来自同条件 ALD 薄膜 ellipsometry。
- 设计泵浦约 1.58 μm；弱辐射耦合的大面积周期阵列形成高 Q GMR，在 MQW 内同时增强面内 Ex 与面外 Ez，从而驱动 χ²xzx/χ²xxz。
- 正入射时场对称性使 nonlinear modal overlap β 消失；小角度约 0.3° 打破对称并保持两支 GMR 仍有谱重叠，获得最大二次谐波响应。

## 关键实验结果

- 实测主要 resonance B 位于泵浦 1.567 μm，相比仿真偏移 13 nm；作者估计可由异质结构厚度或折射率 <5% 偏差解释。
- 泵浦共振线宽 1.39 nm（0.3°），对应 Q≈1125；二次谐波线宽 0.89 nm。
- MQW 材料本征可用 χ² 在 1.57 μm 为约 1.6 nm/V；加入 TiO₂ metasurface 后有效 χ² 约 14 nm/V（若校正二次谐波吸收约 17 nm/V）。
- 谐振 metasurface 使 MQW 中 ExEz 场乘积相对裸 MQW 45° 入射约增强 57 倍；论文将有效 χ² 与 LiNbO₃ 最大张量元比较，约高 270 倍。

## 制备与测试

- **工艺流程图**：支持信息 **Figure S9 "Metasurface fabrication"**（衬底 → 旋涂 ZEP520A → EBL 写反图形 → **ALD 沉积 TiO₂ 填孔** → **回刻（etchback）** → 去胶）；本仓库截图见 [`docs/reports/fabrication/figures/fig_TiO2_T6_Fathi2026_ALD_gapfill.png`](../../../../docs/reports/fabrication/figures/fig_TiO2_T6_Fathi2026_ALD_gapfill.png)，用于汇报稿第 10 页的"**加法**"加工路线对比（2026-09-11 补）。
- ZEP 520A 正胶：3800 rpm 45 s；90 °C 3 min + 180 °C 3 min；ESPACER 300 防充电。
- 150 kV EBL、1 nA，o-xylene 显影；ALD 沉积 TiO₂，RIE 回刻过生长层，Remover PG 去胶。
- 非线性测试用中心约 1560 nm 的 erbium femtosecond laser（70 fs、100 MHz）；结合透射谱、二次谐波谱与相对 LiNbO₃ 标定提取 χ²。
- 电磁设计用 GRCWA；实验标定中的脉冲传播/界面反射用 Tidy3D FDTD。

## 对本项目的启示

- 这是最有价值的 TiO₂ 1550 nm 实验工艺基线：390 nm 高柱比 T1/T3/T5 的 1.3–1.8 μm 传播相位柱更易制造，但依赖窄带 GMR 与较大阵列相干性。
- 实测 13 nm 谱移把“厚度/折射率 <5%”如何转成通信波段失谐风险展示得很直观；高 Q 设计必须同时做膜厚、n、CD、周期的 Monte Carlo/容差扫描。
- 对 L01 qBIC/LWM，可直接借鉴“自由空间端口—弱泄漏导模—场重叠—外耦合”的建模链和 Q/带宽折中。
- 不能把 14 nm/V 归因于 TiO₂ 本征非线性；TiO₂ 负责 GMR 场工程，巨大 χ² 的材料来源是 MQW interband transition。

## 局限与待确认

- 混合 III–V/TiO₂ 工艺明显复杂于单一 TiO₂/SiO₂ metalens；若项目只做线性辐射控制，不必复制 MQW 部分。
- 高 Q 带来窄带宽：泵浦激光带宽约为 GMR 带宽的 100 倍，论文需在模型中显式校正谱接受度。
- 小角度最优响应意味着封装/角度漂移是系统级约束；应补充角度-波长联合容差图后再讨论器件化。
