# 45° 斜向上出射：COMSOL 仿真结果

## 结论

600 nm × 220 nm SOI 波导在 1550 nm 的 COMSOL TE00 模式有效折射率为

```text
neff = 2.530713934
```

采用论文三相位超胞的相位匹配关系

```text
sin(theta) = neff - lambda0/Lambda
```

得到 45° 设计周期

```text
Lambda = 478.717056 nm
atom_pitch = Lambda/3 = 159.572352 nm
```

6 超胞有限三维 COMSOL 模型的监视线复电场角谱主瓣为

```text
theta_peak = -45.523°
abs(theta_peak) = 45.523°
abs(angle error) = 0.523°
```

角度以 +z 为 0°；负号仅表示光束朝 -x 方向倾斜。因此模型实现的是向左上方 45.523° 出射。

## 使用的几何和材料参数

- 真空波长：1550 nm
- Si 波导：宽 600 nm、高 220 nm
- BOX：3 µm SiO2
- 超胞：3 个 Au/SiO2/Au meta-atom
- 每个 Au/SiO2/Au 层：30 nm
- 6 个超胞，共 18 个 meta-atom、54 个三维薄层块
- 超表面长度：2.872302 µm
- 端口缓冲后总长度：5.872302 µm
- 相位种子尺寸（由论文图读数，需做单元扫描精标）：
  - +2pi/3：110 nm × 190 nm
  - 0：100 nm × 275 nm
  - -2pi/3：110 nm × 295 nm
- 折射率种子：Si 3.48、SiO2 1.444、Au n=0.55、k=11.5

## 求解结果

- 三维主求解时间：560.9 s
- 反射率 `|S11|^2`：0.009391
- 透射率 `|S21|^2`：0.405796
- 端口未计入功率 `1-R-T`：0.584812

`1-R-T` 同时包含自由空间辐射、金属吸收以及开放边界泄漏，不能在未做上表面功率积分前直接当作向上辐射效率。

## 可直接运行的程序

在项目目录执行：

```powershell
# 1. 求波导模式并反算 45° 周期
..\bilayer-grating-workflow\bilayer-grating-workflow\.venv\Scripts\python.exe scripts\solve_waveguide_mode.py

# 2. 建模、网格、端口模态、三维频域求解和场采样
..\bilayer-grating-workflow\bilayer-grating-workflow\.venv\Scripts\python.exe scripts\run_45deg_comsol.py --cells 6

# 3. 从已保存的复电场重新生成高密度角谱（无需重跑 COMSOL）
..\bilayer-grating-workflow\bilayer-grating-workflow\.venv\Scripts\python.exe scripts\reprocess_45deg_results.py
```

主要程序：

- `src/gwm_workflow/comsol_mode.py`：二维 SOI 模式模型
- `src/gwm_workflow/comsol_structure.py`：三维波导驱动超表面模型
- `scripts/run_45deg_comsol.py`：完整求解和后处理入口

## 数值模型说明

- 输入、输出端口均为 Numeric Port，并各自配置一个 Boundary Mode Analysis，再运行 Frequency Domain。
- 监视线位于 `y=0, z=1.25 µm`，保存 Ex、Ey、Ez 的实部和虚部，共 1024 个采样点。
- 角谱用三个电场分量的加窗复场 FFT 功率和；65536 点零填充用于平滑定位有限孔径主瓣中心，不会虚构额外的物理角分辨率。
- 为避免有限截断的高折射率 Si handle 在端口截面产生非物理平板模，三维验证模型保留完整 3 µm BOX，但将 BOX 底面作为开放截断面。真实器件的 Si handle 与 BOX 相隔 3 µm，对波导 TE00 的影响很小。
- 当前采用散射边界而非 PML；当前结果适合确认出射方向。要报告严格的辐射效率和旁瓣，应增加 PML、做网格/超胞数收敛，并用单 meta-atom 周期模型重新标定三种相位尺寸。

## 输出文件

- `experiments/l02_guo_2020/beam_deflector/waveguide_mode_1550nm/soi_waveguide_mode.mph`
- `experiments/l02_guo_2020/beam_deflector/waveguide_mode_1550nm/mode_result.json`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/guided_wave_metasurface_45deg_solved.mph`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/GuidedWaveMetasurface45deg.java`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/simulation_result.json`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/monitor_field_complex.csv`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/angular_spectrum.csv`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/angular_spectrum.png`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/field_xz_normE.png`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/field_xz_Ey_paper_style.png`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/field_xz_Ey_paper_style.pdf`
- `experiments/l02_guo_2020/beam_deflector/right45_15cells_air2x/field_xz_Ey_complex.npz`

论文风格的 `Re(Ey)` 场图可用下面的命令重新绘制。首次执行读取 COMSOL，之后默认复用 NPZ 场缓存：

```powershell
..\bilayer-grating-workflow\bilayer-grating-workflow\.venv\Scripts\python.exe scripts\plot_paper_style_field.py
```
