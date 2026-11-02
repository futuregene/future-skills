# SOURCE

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/adriendelmas/pattern-making-skill |
| 上游路径 | `skills/pattern-making/`（`SKILL.md`、`scripts/`、`references/`、`examples/`） |
| 固定 commit | `6587004c4c0495592d0a3947553b52e72f1e354c`（2026-10-10，HEAD） |
| 许可证 | MIT License，Copyright (c) 2026 Adrien Delmas（见上游 `LICENSE`） |
| 导入日期 | 2026-11-02 |
| 上游规模 | 仓库仅 1 个技能；本目录 1.89 MB（`references/kb/` 知识库约 1.3 MB） |
| 本库分类 | engineering（参数化几何 + CAD 文件导出） |

## 抽取范围

整目录复制，未删减：`SKILL.md`、`scripts/pattern.py`（102 KB）、`scripts/garment.py`（53 KB）、
`scripts/sheet.py`（5.6 KB）、`references/`（含 `kb/` 九册知识库、`techniques/` 七册工艺表、
`reference-analysis.md`、`design-from-sketch.md`、`piece-format.md`、`garment-spec.md`、`clo3d.md`、
`blocks.md`、`transformations.md`、`measurements.md`、`ease.md`、`finishes.md`）、
`examples/notched-lapel-jacket/`、`examples/velvet-coat/`。

未取：`.claude-plugin/`（Claude 插件清单，与本库无关）、仓库根 `README.md`。

## 我们的改动

1. `SKILL.md` frontmatter：`description` 末尾追加中文触发词；新增 `license` / `category` / `metadata`。
   正文一字未改。
2. `SKILL.md` 正文前插入中文「来源与边界」引用块。
3. 新增本 `SOURCE.md`。
4. 未改任何 `.py` 与 `references/` 内容。

## 使用边界

- 领域是**服装/纺织打版**，不是工业产品设计（工业设计/CMF/结构设计在本库仍为空，见 stage `REPORT.md`）。
- 输入单位为厘米；SVG / DXF / CLO3D 输出为毫米。CAD 侧是 DXF 图层（CUT/SEAM/NOTCHES/GRAIN/TEXT），
  不是参数化的 SolidWorks/Fusion 模型。
- 引擎为纯标准库（Python 3.8+）；`scripts/sheet.py` 出 PNG 需 Pillow；CLO3D 导出需外部
  `clo3d-mcp-extended` 插件与 MCP server，本库不含。
- 知识库中标记 "unverified" 的造型必须在真实纸样上核对后才能使用；引擎的自检报告只覆盖可计算的
  几何定律（对缝等长、褶量、90° 折边、缝长匹配），不覆盖合体度与面料手感。
- 不产出生产级排料/放码公差表；量产前须由打版师复核。

## 复核方式（本次导入实测）

```
python scripts/pattern.py test                        -> All tests pass.
python scripts/pattern.py --help                      -> 子命令 block/measurements/garment/piece/pivot/smooth/clo3d/kb/test
python scripts/pattern.py measurements --body women --size 38           -> 打印全部量体值
python scripts/pattern.py block skirt --body women --size 38 --out ...  -> 4 项自检全 OK，产出 SVG/DXF/CLO3D/pieces
python scripts/pattern.py block bodice --body women --sizes 36,38,40 --out ... -> 三码放码，自检全 OK
python scripts/pattern.py block glove --size 7 --length 40 --end-girth 26 --out ... -> 64 条缝零失败
python scripts/pattern.py garment examples/notched-lapel-jacket/jacket_fitted.json --out ...
                                                      -> 42 条缝 0 失败，产出 pattern.svg / pattern_38.dxf /
                                                         pieces_38.json / clo3d_38.{json,py}
python scripts/sheet.py pieces_38.json                -> pieces_38_shell.png / pieces_38_lining.png
python scripts/pattern.py kb search collar            -> 命中 notched-lapel / shawl-collar 等 12 条
python -m py_compile scripts/*.py                     -> OK
```
