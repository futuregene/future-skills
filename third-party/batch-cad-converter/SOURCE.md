# SOURCE

| 项目 | 内容 |
|---|---|
| 上游仓库 | https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction |
| 上游路径 | `1_DDC_Toolkit/CAD-Converters/batch-cad-converter/SKILL.md` |
| 固定 commit | `410ed1e71e4a5c6fd231afd0c8d1e586a9f546e8`（2026-10-19，MIT，Copyright (c) 2026 DataDrivenConstruction） |
| 许可证 | MIT（`LICENSE`）；技能说明与文档同属 MIT。注意：仓库内 CWICR 造价库为 **CC BY-NC 4.0 + 单独商用授权**，书籍 PDF 版权归作者，均未引入本技能 |
| 导入日期 | 2026-11-02 |
| 本库分类 | engineering（工程计算） |

## 抽取范围

整份 SKILL.md：CADFormat/ConversionStatus/ConversionResult/BatchResult 模型、转换器路径解析与 PATH 回退、单文件转换、并发批量执行、进度回调、汇总报表。

## 我们的改动

frontmatter 重写（原 openclaw 元数据声明 win32 + anyBins，本库改为正文边界说明）；正文原样保留；文件头加中文边界说明；补充 SOURCE.md。

正文（含全部 Python 代码）与上游 `SKILL.md` 逐字一致，仅：

1. 替换 frontmatter：`name` 去掉引号（本库要求 name 等于目录名），删去 openclaw 元数据块，
   补 `license` / `category` / `metadata`。
2. 文件头插入一段中文「来源与边界」引用块（不进入正文逻辑）。
3. 生成 `SOURCE.md`（本文件）。

## 使用边界

真正的格式转换依赖 DDC 闭源导出器（RvtExporter/DwgExporter/DgnExporter/RVT2IFCconverter），本技能不含这些二进制，只有编排/重试/报表这一层；没有转换器时可用桩程序验证流程，但不会产生真实数据。DDC 导出器为 Windows 工具，跨平台批次需自备 LibreDWG/ODA/IfcOpenShell 替代实现并改 DEFAULT_CONVERTERS。

## 复核方式

- 上游为只读检出：`D:/future-os/.future/tmp/hdu-upstream/DDC_Skills_for_AI_Agents_in_Construction`，未做修改。
- 正文代码用 `python -m py_compile` 校验（抽取自 SKILL.md 的 python 代码块，结果见 stage `REPORT.md`）。
- 技能面向 Windows 场地流程；脚本本身是纯 Python + pandas，跨平台可读。
