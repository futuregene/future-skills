# SOURCE

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction |
| 上游路径 | `1_DDC_Toolkit/BIM-Analysis/bim-validation-report/SKILL.md` |
| 固定 commit | `410ed1e71e4a5c6fd231afd0c8d1e586a9f546e8`（2026-10-19，MIT，Copyright (c) 2026 DataDrivenConstruction） |
| 许可证 | MIT（`LICENSE`）；技能说明与文档同属 MIT。注意：仓库内 CWICR 造价库为 **CC BY-NC 4.0 + 单独商用授权**，书籍 PDF 版权归作者，均未引入本技能 |
| 导入日期 | 2026-11-02 |
| 本库分类 | engineering（工程计算） |

## 抽取范围

整份 SKILL.md：ValidationRule/ValidationIssue/ValidationReport 数据模型、8 条默认规则（REQ-001…GEO-002）、按类别过滤的规则引擎、严重度汇总与 passed/warning/failed 判定、openpyxl 三页报表导出、Quick Start。

## 我们的改动

frontmatter 重写（去 openclaw 元数据、加 license/category/metadata）；正文原样保留（代码未改一行）；文件头加中文边界说明；补充 SOURCE.md。

正文（含全部 Python 代码）与上游 `SKILL.md` 逐字一致，仅：

1. 替换 frontmatter：`name` 去掉引号（本库要求 name 等于目录名），删去 openclaw 元数据块，
   补 `license` / `category` / `metadata`。
2. 文件头插入一段中文「来源与边界」引用块（不进入正文逻辑）。
3. 生成 `SOURCE.md`（本文件）。

## 使用边界

输入是已导出的元素表（xlsx/csv），不含模型文件解析——需要 Revit/IFC 导出器（DDC 转换器或 ifcopenshell）先出表；8 条默认规则是通用起点，必须替换为项目规则集；只覆盖属性/几何/命名层面，ISO 19650 与 IDS 仅被引用、未实现校验。依赖 pandas + openpyxl。

## 复核方式

- 上游为只读检出：`D:/future-os/.future/tmp/hdu-upstream/DDC_Skills_for_AI_Agents_in_Construction`，未做修改。
- 正文代码用 `python -m py_compile` 校验（抽取自 SKILL.md 的 python 代码块，结果见 stage `REPORT.md`）。
- 技能面向 Windows 场地流程；脚本本身是纯 Python + pandas，跨平台可读。
