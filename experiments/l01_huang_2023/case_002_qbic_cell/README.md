# case_002：qBIC 元胞库仿真（Dirac 方格基本模型）

## 目标

复现主论文(L01)的超表面元胞响应:0.8×0.8 μm 元胞、4 椭圆孔(p2 对称),扫描 D₀/δ/α,验证:

- Q = C/δ²(C ≈ 950 μm²)
- 半元胞 Jones 响应 (E_x, E_y) = δ(a_x sin2α, a_y cos2α)
- σ = 1/2/3 nm 加工容差展宽

物理背景:能带折叠形成 1D Dirac 点,使器件可在正入射(broadside)附近工作(见 `literature/阅读笔记_L01_Huang_2023.md`)。

## 模型

- `dirac_square_basic_model.mph` —— Dirac 方格基本 COMSOL 模型(2026-09-04 入库,2.1 MB,未求解基底模型)
- 来源:微信接收的 `dirac_squre-basic model.mph`,重命名为项目 snake_case 约定

## 状态

- 2026-09-04:基本模型已入库,待打开核对几何/材料/边界条件与论文参数基线(空气 / PMMA 300 nm / Si₃N₄ 300 nm / SiO₂,λ₀ = 1.55 μm,TM₀ n_eff ≈ 1.5507,见 case_001)是否一致
- 待办:参数化扫描 D₀/δ/α → Q 因子拟合 → Jones 响应提取 → 容差展宽

## 复现说明

- 模式基线:先运行 case_001(`python case_001_slab_mode/scripts/slab_mode_solver.py`)确认 n_eff
- 结果产出归档至 `results/`;求解后的大型 .mph 不入库(参照 L02 约定,仅保留未求解模型 + 重生成说明)
