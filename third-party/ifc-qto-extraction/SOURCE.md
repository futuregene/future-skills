# SOURCE

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction |
| 上游路径 | `1_DDC_Toolkit/BIM-Analysis/ifc-qto-extraction/SKILL.md` |
| 固定 commit | `410ed1e71e4a5c6fd231afd0c8d1e586a9f546e8`（2026-10-19，MIT，Copyright (c) 2026 DataDrivenConstruction） |
| 许可证 | MIT（`LICENSE`）；技能说明与文档同属 MIT。注意：仓库内 CWICR 造价库为 **CC BY-NC 4.0 + 单独商用授权**，书籍 PDF 版权归作者，均未引入本技能 |
| 导入日期 | 2026-11-02 |
| 本库分类 | engineering（工程计算） |

## 抽取范围

整份 SKILL.md：QTO 流水线图、转换器 CLI 调用（RvtExporter/IfcExporter/DwgExporter）、QuantityItem 数据模型、BIMQuantityExtractor.convert_model/load_bim_data/extract_quantities、分组与导出。

## 我们的改动

frontmatter 重写；正文原样保留；文件头加中文边界说明（转换器为闭源外部二进制）；补充 SOURCE.md。

正文（含全部 Python 代码）与上游 `SKILL.md` 逐字一致，仅：

1. 替换 frontmatter：`name` 去掉引号（本库要求 name 等于目录名），删去 openclaw 元数据块，
   补 `license` / `category` / `metadata`。
2. 文件头插入一段中文「来源与边界」引用块（不进入正文逻辑）。
3. 生成 `SOURCE.md`（本文件）。

## 使用边界

转换器（RvtExporter.exe / IfcExporter.exe / DwgExporter.exe）是 DDC 闭源 Windows 工具，本技能不带二进制，缺它时只有 pandas 分组这一半可跑（任何元素表都能喂进去）；不得改用 DDC CWICR 价格库——该库为 CC BY-NC 4.0，商用需另行授权。产出的工程量仍需造价人员复核，尤其面积/体积单位与净毛面积口径。

## 复核方式

- 上游为只读检出：`D:/future-os/.future/tmp/hdu-upstream/DDC_Skills_for_AI_Agents_in_Construction`，未做修改。
- 正文代码用 `python -m py_compile` 校验（抽取自 SKILL.md 的 python 代码块，结果见 stage `REPORT.md`）。
- 技能面向 Windows 场地流程；脚本本身是纯 Python + pandas，跨平台可读。
