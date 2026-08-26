# 15 超胞 45° 超表面仿真结果

## 最终采用的模型

- 超胞数量：15
- meta-atom 数量：45
- Au/SiO2/Au 三维薄层块数量：135
- 超胞周期：505.395255 nm
- meta-atom 间距：168.465085 nm
- 阵列长度：7.580929 µm
- 含两端端口缓冲的模型总长度：10.580929 µm
- 波导：600 nm × 220 nm Si
- BOX：3 µm SiO2
- 每层 Au/SiO2/Au 厚度：30 nm

## 为什么将周期从 478.717 nm 修正到 505.395 nm

裸波导模式给出 `neff=2.530714`，据此得到的 478.717 nm 周期在 6 超胞短阵列中产生很宽的主瓣，峰值约为 45.5°。扩展到 15 超胞后，加载超表面的传播常数累积效应变得明显，主瓣移动到 61.4°。

由第一次 15 超胞结果反推出加载结构的 Bloch 有效折射率：

```text
n_Bloch = lambda0/Lambda - sin(61.4045°)
        = 2.3597997
```

重新要求 45° 相位匹配：

```text
Lambda_corrected = lambda0/(n_Bloch + sin(45°))
                 = 505.395255 nm
```

修正周期后的第二次 15 超胞全波求解得到 `|theta|=46.496°`，相对目标误差为 1.496°。

## COMSOL 结果

- 角谱峰值：-46.496°，即朝 -x 方向斜向上 46.496°
- 目标绝对角度误差：1.496°
- 反射率 `|S11|^2`：0.010320
- 透射率 `|S21|^2`：0.099435
- `1-R-T`：0.889245；包含自由空间辐射、金属吸收和开放边界泄漏，不能直接视为向上辐射效率
- 主频域求解时间：1475.0 s
- 15 超胞主瓣半高全宽：约 20.83°
- 原 6 超胞主瓣半高全宽：约 46.65°

15 超胞将角谱半高全宽缩小约 55%，因而 x-z 场图中的斜向波前明显更连续。

## 最终文件

- `comsol_models/beam_deflector_45deg_15cells_corrected/guided_wave_metasurface_45deg_solved.mph`
- `comsol_models/beam_deflector_45deg_15cells_corrected/GuidedWaveMetasurface45deg.java`
- `comsol_models/beam_deflector_45deg_15cells_corrected/simulation_result.json`
- `comsol_models/beam_deflector_45deg_15cells_corrected/angular_spectrum.png`
- `comsol_models/beam_deflector_45deg_15cells_corrected/field_xz_Ey_paper_style.png`
- `comsol_models/beam_deflector_45deg_15cells_corrected/field_xz_Ey_paper_style.pdf`

精简 Java 文件已通过 `comsolcompile`。

## 重跑命令

```powershell
..\bilayer-grating-workflow\bilayer-grating-workflow\.venv\Scripts\python.exe scripts\run_45deg_comsol.py `
  --cells 15 `
  --period-um 0.5053952548466464 `
  --phase-index 2.3597997343293557 `
  --output comsol_models\beam_deflector_45deg_15cells_corrected

..\bilayer-grating-workflow\bilayer-grating-workflow\.venv\Scripts\python.exe scripts\plot_paper_style_field.py `
  --directory comsol_models\beam_deflector_45deg_15cells_corrected
```
