# A4｜Doylend 2011｜Optics Express 19(22)

## 论文信息

- **题目**：Two-dimensional free-space beam steering with an optical phased array on silicon-on-insulator
- **期刊 / 年份**：*Optics Express* **19**(22), 21595–21604 (2011)
- **DOI**：[10.1364/OE.19.021595](https://doi.org/10.1364/OE.19.021595)
- **本地原文**：[A4 PDF](pdfs/A4_Doylend_2011_SOI_Optical_Phased_Array.pdf)
- **定位**：传统 SOI grating-emitter OPA 基线。

## 一句话总结

该工作演示 16 通道、独立调谐的 SOI 波导表面光栅 OPA，实现二维自由空间扫描，是评估后续导波驱动超表面能否改善视场、光束宽度和旁瓣的早期实验基线。

## 结构与机制

- 每个输出支路以表面光栅把导模耦合到离片光；通道间相位调节实现一个方向扫描，光栅色散/波长变化参与另一方向扫描。
- 阵列远场是各通道复振幅的相干叠加，因此通道振幅均衡、相位误差、单元间距共同决定主瓣和栅瓣。

## 原文关键指标

- **16-channel** independently tuned waveguide surface-grating OPA。
- 总视场 **20° × 14°**；光束宽度 **0.6° × 1.6°**。
- 全窗口背景峰值抑制约 **10 dB**。

## 对项目的启示

1. 它给出不可回避的系统级指标：通道数/有效孔径、通道间距和相位误差必须与出射单元设计同步优化。
2. 超表面若要证明优势，应在同孔径下比较 beamwidth、background/side-lobe、效率及二维扫描耦合方式。
3. 对 1550 nm SOI 平台，光栅发射的波长–角度色散既可用于扫描，也会形成 beam squint；需与 A2/A3 的抑制路径对照。

## 待确认

- 复现时从正文的相移器类型、功耗和天线间距提取系统约束，不把 2011 年器件工艺能力等同于当前平台。
