# NOTICE：第三方资产与许可边界

本仓库的原创代码以 MIT 许可发布（见 `LICENSE`）。以下资产不在 MIT 许可范围内，使用者须自行确认再分发与使用权限：

## 1. 论文（literature/）

`literature/` 下的出版商 PDF（Nature、ACS、Wiley、AIP/APS、De Gruyter、Optica、CLP 等）受各出版商版权保护。仓库内保存这些 PDF 仅为个人研究参考；**公开发布或再分发前须逐篇确认许可**（开放获取 CC-BY 的除外）。引用信息见 `references/references.bib`。

## 2. COMSOL 模型（experiments/l02_guo_2020/**）

`.mph` 文件受 COMSOL Multiphysics 许可约束。使用、分发或运行需要有效的 COMSOL 许可；导出的 Java/脚本仅描述模型结构。

## 3. 其他数据与图像

仿真输出（`.npz`、`.csv`、`.png`、`.pdf`）为本项目生成物，可在项目范围内自由使用；如对外发布请注明来源。

## 4. 建议

如需公开分发，建议：
- 论文 PDF 移出 Git（保留 `references.bib` + DOI）；
- 大型 `.mph`/`.npz` 迁至 Git LFS 或 Release；
- 在公开副本中排除受许可约束的资产。
