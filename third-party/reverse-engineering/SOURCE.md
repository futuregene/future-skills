# 来源与许可

- 上游仓库：https://github.com/zhaoxuya520/reverse-skill
- 上游路径：`skills/reverse-engineering`
- 固定提交：`cab634bd855fc287f6e420c1f36fd1a6b9245960`
- 许可证：MIT（全文见上游 LICENSE，随仓库分发时保留版权声明）
- 导入日期：2026-11-02
- 抽取范围：该技能目录整体导入（`SKILL.md` 及其 `scripts/`、`references/`、`assets/`）
- 我们的改动：仅补充本文件与 `skills.json` 元数据；`SKILL.md` 正文未改写

- 使用边界：仅限授权的目标。本技能不提供攻击利用步骤，仅用于授权范围内的分析与防御。

## 增量合并（2026-11-02）

本技能原有内容来自 reverse-skill；下列文件来自 ljagiello/ctf-skills 的 `ctf-reverse/`
（commit `a6106aaf5f1f4eeb6b95908f11c2314c7150dfac`，MIT），因其在本技能中没有对应物：

- `tools-mcp.md`（44.6 KB）—— 逆向/调试类 MCP 工具索引
- `unicorn-emulation.md`（50.8 KB）—— Unicorn 模拟执行
- `radare2-r2pipe.md`（17.8 KB）—— r2pipe 脚本接口
- `mba-simplification.md`（4.6 KB）—— 混合布尔算术化简

同时把 `ctf-malware`、`ctf-pwn` 中指向未导入的 `../ctf-reverse/` 的链接改指向本技能对应文件。

## 未导入的引用（2026-11-02 清理）

上游的 `field-journal/`、`ops/` 两个技能不在本库；`unicorn-emulation.md` 里指向的三个
ctf-reverse 兄弟文件也未导入。这些引用已改为指向本技能中**确实包含对应小节**的文件：

| 原引用 | 改为 |
| --- | --- |
| `tools-emulation.md#qiling-framework-cross-platform-emulation` | `tools-dynamic.md#qiling-framework-cross-platform-emulation` |
| `anti-analysis-ctf.md#instruction-trace-inversion-with-keystone-and-unicorn-meepwn-ctf-2017` | `anti-analysis.md#instruction-trace-inversion-with-keystone-and-unicorn-meepwn-ctf-2017` |
| `patterns-runtime.md#multi-stage-shellcode-loaders` | `field-notes.md#multi-stage-shellcode-loaders` |

`field-journal/`、`ops/` 本身刻意不导入，相关引用已去掉、只保留文字。
