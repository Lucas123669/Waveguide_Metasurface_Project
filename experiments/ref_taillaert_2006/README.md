# ref_taillaert_2006（参考轨道：光栅耦合器 2D 模型）

> 来源：2026-09-08 师兄（孟乐天）微信提供，配套论文 PDF 由同一消息发送。
> 性质：**外部参考模型**（非本仓库自行搭建），作为波导‑光纤耦合/激励仿真的基准，不属于 L01/L02 复现主线。

## 配套论文

- Taillaert *et al.*, *Grating Couplers for Coupling between Optical Fibers and Nanophotonic Waveguides*, **Jpn. J. Appl. Phys. 45, 6071–6077 (2006)**（Invited Paper，Ghent University IMEC 团队）
- DOI: [10.1143/JJAP.45.6071]
- PDF 存档：`literature/材料体系分类/通用交叉/pdfs/Q1_12_Taillaert_2006_Grating_Couplers_JpnJApplPhys.pdf`（编号 Q1-12，阅读笔记同目录）

## 模型

- 文件：`grating_coupler_2d/Taillaert2006_2D_ready.mph`（COMSOL 2D，约 57 MB，"ready"状态）
- 内容（按论文 §2 参数推断，待打开核对）：SOI 220 nm Si 顶层、光栅周期 Λ≈630 nm、刻蚀深 70 nm、填充因子 0.5、中心波长 ~1550 nm、TE 偏振、光纤以 θ≈10° 倾斜耦合；论文仿真方法为 eigenmode expansion + PML（本文模型为 COMSOL 复现版）
- 用途：
  1. L01（Si₃N₄ 漏波超表面）与 L02（Si 波导驱动超表面）实验中把光耦合进/出波导的**激励端基准**
  2. 端面耦合 vs 光栅耦合的取舍参考（论文 §1：表面耦合可放在芯片任意位置、免抛光、支持晶圆级测试）
  3. 波导‑光纤耦合效率的 2D 快速估算模板

## 打开与核对

- COMSOL Multiphysics 打开后应先核对：几何尺寸（Si 厚度、光栅周期/占空比/刻蚀深度）、材料（Si、SiO₂、空气/匹配层）、激励与端口、波长范围；核对结果记录在本目录 README 或 results 中。
