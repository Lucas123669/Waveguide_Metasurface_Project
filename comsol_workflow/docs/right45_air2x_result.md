# 右上方 45°、双倍空气层模型

## 最终结构

- 超胞数量：15
- meta-atom 数量：45
- Au/SiO2/Au 薄层块：135
- 超胞周期：897.330998 nm
- 单元间距：299.110333 nm
- 超表面阵列长度：13.459965 µm
- 含端口缓冲的总长度：16.459965 µm
- 空气层高度：3.6 µm（原模型 1.8 µm 的两倍）
- 角谱监视面：z = 2.5 µm
- 波导：600 nm × 220 nm Si
- BOX：3 µm SiO2
- 每层 Au/SiO2/Au 厚度：30 nm

## 方向修正

保持论文中的负相位梯度：

```text
kx = beta - 2*pi/Lambda
```

由已有加载模型估计长周期下的 Bloch 有效折射率为 2.4344515，并选择：

```text
Lambda = lambda0/(n_Bloch - sin(45 deg))
       = 897.330998 nm
```

这使 `kx > 0`，因此自由空间光具有正 x 分量，朝右上方传播。

## COMSOL 全波结果

- 物理角谱主峰：+45.014702°
- 相对 +45° 目标误差：0.014702°
- 主瓣半高全宽：约 15.40°
- 反射率 `|S11|^2`：0.084992
- 透射率 `|S21|^2`：0.140988
- `1-R-T`：0.774021；该值同时包含辐射、金属吸收和开放边界泄漏
- 主频域求解时间：2770.2 s

## 输出文件

- `comsol_models/beam_deflector_right45_15cells_air2x/guided_wave_metasurface_45deg_solved.mph` (generated locally and intentionally excluded from GitHub because it is 923 MB)
- `comsol_models/beam_deflector_right45_15cells_air2x/GuidedWaveMetasurface45deg.java`
- `comsol_models/beam_deflector_right45_15cells_air2x/simulation_result.json`
- `comsol_models/beam_deflector_right45_15cells_air2x/angular_spectrum.png`
- `comsol_models/beam_deflector_right45_15cells_air2x/field_xz_Ey_paper_style.png`
- `comsol_models/beam_deflector_right45_15cells_air2x/field_xz_Ey_paper_style.pdf`

精简 Java 程序已通过 `comsolcompile`。

## 重跑命令

```powershell
..\bilayer-grating-workflow\bilayer-grating-workflow\.venv\Scripts\python.exe scripts\run_45deg_comsol.py `
  --cells 15 `
  --period-um 0.8973309975091556 `
  --phase-index 2.434451545050213 `
  --air-height-um 3.6 `
  --monitor-height-um 2.5 `
  --output comsol_models\beam_deflector_right45_15cells_air2x
```
