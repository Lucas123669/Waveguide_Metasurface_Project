# artifacts：大型资产策略

本目录保存大型产物的**策略与索引**（当前不直接存放大文件）。

## 现状

- 普通 Git 已跟踪：论文 PDF（`literature/`）、COMSOL `.mph`（`experiments/l02_guo_2020/**`）、`.npz` 等二进制。
- 仓库当前约 200 MB（历史演进中），单文件最大约 36.8 MB。

## 建议的资产分层

| 资产 | 存储方式 |
| --- | --- |
| 源代码、配置、文档、轻量 JSON/CSV、小型基准结果 | 普通 Git |
| `.mph`、`.npz`、大图、PDF | Git LFS 或 GitHub Release / 本地机构存储 |
| 已求解超大型 COMSOL（如 923 MB） | 永不入库；记录重新生成命令 |

## 迁移方式（如需）

```bash
git lfs track "*.mph" "*.npz" "*.pdf"
git add .gitattributes
git lfs migrate import --include="*.mph,*.npz,*.pdf" --everything
```

迁移前请确认 GitHub 配额与论文再分发许可（见 `NOTICE.md`）。论文 PDF 更推荐移出 Git，仅保留 `references.bib` + DOI。
