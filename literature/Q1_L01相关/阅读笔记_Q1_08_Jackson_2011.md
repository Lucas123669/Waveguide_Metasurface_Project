# 阅读笔记 Q1-08 | Jackson 2011：Directive Beaming and the Role of Leaky Waves

> 笔记日期：2026-08-25 ｜ PDF：`Q1_08_Jackson_2011_Directive_Beaming_Leaky_Waves_Proc_IEEE.pdf`

## 1. 论文信息

- 编号：Q1-08
- 标题：The Fundamental Physics of Directive Beaming at Microwave and Optical Frequencies and the Role of Leaky Waves
- 作者：David R. Jackson, Paolo Burghignoli, Giampiero Lovat, Filippo Capolino, Ji Chen, Donald R. Wilton, Arthur A. Oliner
- 期刊：Proceedings of the IEEE 99(10), 1780–1805（一区）
- 年份：2011
- DOI：10.1109/JPROC.2010.2103530
- 类型：泄漏波理论综述（邀请综述）

## 2. 一句话总结

用泄漏波（leaky wave）统一解释微波与光学频段的定向辐射现象（Fabry-Pérot 腔天线、EBG 天线、超材料、金属膜小孔增强透射等），给出复传播常数 β−jα 与波束方向/波束宽度的设计公式。

## 3. 核心内容

- **复波数**：泄漏模式 k_p = β − jα，β（相位常数）决定波束出射角 θ₀ ≈ arcsin(β/k₀)，α（衰减/泄漏常数）决定波束宽度与口径效率；弱衰减泄漏波（α 小）产生窄波束。
- **Fabry-Pérot 腔天线**：接地平行板 + 部分反射表面（PRS），腔厚按 h 满足 k₁·h·cosθ₀ 条件；宽边波束（θ₀=0）h = λ_d/2。
- **辐射场计算**：口径场傅里叶变换或互易定理；TM/TE 泄漏模组合决定辐射极化。
- **光学对应**：金属膜亚波长孔径 + 周期结构 → 增强透射与定向出射，同样由泄漏波解释。
- 提供"用泄漏波参数直接设计天线/器件"的公式集，并讨论频率扫描与波束扫描。

## 4. 与 L01 的关联

- L01 的本质就是"片上泄漏波天线"：波导导模被周期微扰变成泄漏模辐射到自由空间。Jackson 给出经典泄漏波理论框架（β、α 与辐射角、口径效率的关系）。
- L01 的 apodization（σ(x) 渐变控制辐射强度）对应 α(x) 渐变；Jackson 的公式可校验 L01 的口径效率与波束设计。

## 5. 对我们的启示

1. 仿真中提取泄漏模复波数（COMSOL 本征模的 k = β − jα）来预测辐射角与波束宽度，与 L01 的 n_ms/n_wg 有效折射率对照。
2. 用互易/口径场法计算远场方向图，作为 FDTD 远场投影的交叉验证。
3. 理解"泄漏常数 α ↔ 单位长度辐射率 σ"的换算，直接服务于 apodization 设计与工艺预算。

## 6. 待确认问题

- L01 中 σ_max ≈ 0.04/μm 与 α 的换算系数（模式重叠因子）需从补充材料 S.6 中确认。
