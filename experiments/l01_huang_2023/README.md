# L01 轨道：Huang et al. 2023（Leaky-wave metasurfaces for integrated photonics）

## 轨道状态

- 当前:**case_001 平板模分析已完成**(2026-08-04);**case_002 Dirac 方格基本模型已入库**(2026-09-04)
- 下一动作:**case_002 元胞库仿真**——基于 `case_002_qbic_cell/dirac_square_basic_model.mph` 核对几何/材料/边界后,扫描 D₀/δ/α,验证 Q=C/δ²(C=950 μm²)与 Jones 响应 (E_x,E_y)=δ(a_x sin2α, a_y cos2α),并加 σ=1/2/3 nm 加工容差展宽

## 结构与参数基线

- 堆叠：空气 / PMMA 300 nm（n≈1.48）/ PECVD Si₃N₄ 300 nm（n≈2.00）/ 熔融石英
- 波长：1.55 μm（1520–1580 nm）；导模 TM₀ n_eff≈1.5507
- 详细设计/工艺问题与文献依据：见 `docs/reports/design/2026-08-25_L01超表面波导综合分析与初步结构.md`

## 案例

| 案例 | 内容 | 状态 | 路径 |
| --- | --- | --- | --- |
| case_001 | 平板模 TM₀/TE₀ 有效折射率与色散 | 完成 | `case_001_slab_mode/` |
| case_002 | qBIC 元胞库(Q∝δ⁻²、Jones 矩阵、容差展宽) | 模型已入库 | `case_002_qbic_cell/` |

## 运行

```bash
python case_001_slab_mode/scripts/slab_mode_solver.py \
  --config case_001_slab_mode/params.json \
  --output case_001_slab_mode/results/result.json
```
