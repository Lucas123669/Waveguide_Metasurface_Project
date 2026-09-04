# COMSOL 超表面波导结构程序

## 已生成模型

程序按照论文图 2-3 的无源直波导偏转器建立三维模型：

- 1550 nm 工作波长；
- 600 nm 宽、220 nm 高的硅脊波导；
- 3 um SiO2 BOX 和截断的硅衬底；
- 575 nm 超胞，每个超胞包含三个相位原子；
- 每个原子为 30 nm Au / 30 nm SiO2 / 30 nm Au；
- 12 个超胞，共 36 个纳米棒、108 个材料层块；
- 阵列长度 6.9 um，总波导计算长度 10.9 um；
- 空气、硅、二氧化硅和金材料选择；
- 左右数值端口、顶部/底部/横向散射边界；
- 体网格与金属局部网格控制；
- 1550 nm 频域研究节点，尚未执行求解。

三组纳米棒尺寸来自论文图 2B 的图读初值：

| 相位目标 | lx | ly |
|---|---:|---:|
| +2pi/3 | 110 nm | 190 nm |
| 0 | 100 nm | 275 nm |
| -2pi/3 | 110 nm | 295 nm |

这些尺寸必须在单原子相位扫描后重新标定。当前金的 `n=0.55`、
`k=11.5` 也是用于建模启动的光学常数初值，不是论文明确给出的数据。

## Python/MPh 生成程序

主程序是 `scripts/simulation/build_comsol_structure.py`，实际 COMSOL Java API 建模
逻辑位于 `src/gwm_workflow/comsol_structure.py`。

```powershell
python scripts\build_comsol_structure.py
```

常用选项：

```powershell
# 只建立一个超胞并跳过物理场，用于快速检查几何
python scripts\build_comsol_structure.py --supercells 1 --geometry-only

# 建立正式模型并实际划分网格；内存需求会明显增加
python scripts\build_comsol_structure.py --build-mesh
```

默认输出目录为 `experiments/l02_guo_2020/beam_deflector/structure/`。

## 原生 COMSOL Java 程序

生成的 `GuidedWaveMetasurfaceStructure.java` 是 COMSOL 6.3 导出的完整
原生程序，可以独立编译和运行：

```powershell
cd comsol_models\beam_deflector_structure
comsolcompile GuidedWaveMetasurfaceStructure.java
comsolbatch -inputfile GuidedWaveMetasurfaceStructure.class -outputfile rebuilt.mph
```

本次已验证 Java 文件能被 `comsolcompile` 编译，并能由 `comsolbatch`
重新构建模型。

## 在 COMSOL GUI 中首先检查

1. 检查 `sel_air`、`sel_si`、`sel_sio2`、`sel_au` 是否无重叠或漏选。
2. 检查两个端口是否为完整的共面截面，输入端口 TE00 模式方向是否正确。
3. 用 COMSOL 材料库或有出处的插值表替换金、硅和 SiO2 初始光学常数。
4. 建立单原子扫参模型，重新获得相位/振幅库后更新 `lx_p/z/m`、`ly_p/z/m`。
5. 检查局部金属网格、空气域尺寸和开放边界收敛，再执行 `std1`。
6. 求解后增加上方功率积分面和远场变换，计算偏转角及功率守恒。
