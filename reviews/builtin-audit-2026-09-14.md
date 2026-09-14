# Builtin 技能审查 — 2026-09-14

## 结论与范围

审查了 14 个 builtin 技能的入口，并检查相关脚本、关键参考资料和现有测试。
按要求不审改 `future-slides`；通用元数据检查仍会枚举它，但没有执行其生成流程或修改其文件。

入口文档整体已具备较好的权限、证据和重试边界。本轮主要问题集中在**残留脚本与参考资料未同步遵守入口契约**，而非入口措辞。修正 6 个技能及相关校验器；其余 8 个未发现需要立即修改的明确问题。

这不是所有数据库端点的全面认证，也不是模型行为的端到端评测。代码变更位于 skills 子仓库的隔离分支 `claude/builtin-audit`，没有覆盖用户安装目录，也没有修改 FutureOS Rust/桌面代码。

## 逐项结论

| 技能 | 结论 | 本轮检查与处理 |
|---|---|---|
| future-account | 保留 | 入口与 `future account --help` 相符；未读取个人资料或余额，无需为技能审查访问账户数据。 |
| future-browser | 保留 | 核对 CLI 描述、导航/ref 生命周期、敏感输入与操作授权边界；未启动浏览器或干扰现有标签页。 |
| future-database-lookup | 修正至 0.1.1 | 重做有明确错误的 ID helper；修正 ClinVar 标识符与映射文档；限制顺序请求 pacer 的能力声明；第三方 gget 改为可选。 |
| future-deep-research | 保留 | 入口、检索/报告参考及离线契约通过；已有证据链、资源预算、继承授权和失败引用处理，无需为本轮审查重写。 |
| future-document | 保留 | 核对 parse_doc 接口；本地/远程解析边界、部分结果与视觉核验限制清楚。未上传文件。 |
| future-experimental-design | 修正至 0.0.5 | 拒绝重复/缺失 cluster ID、非法 crossover 参数和静默补造/丢弃的处理标签；澄清 cyclic Latin 不等于 carryover-balanced Williams；完善随机分配及隐藏分配序列的说明。 |
| future-image | 保留 | 核对 image_gen/image_edit/read_image 参数；现有超时、授权、付费重试不确定性和文件验证契约合理。未执行付费图片调用。 |
| future-loop | 保留 | 本机 help 支持 `steer --interrupt`、`supervisor watch`、相对 goal cwd 的 write scopes；静态契约测试通过。未建立 goal、启动 worker 或改动 ledger。 |
| future-paper | 保留 | 核对 search_paper/get_paper 参数；明确摘要不等于全文、生成摘要不等于原文证据。未额外发起论文检索。 |
| future-peer-review | 修正至 0.1.1 | 退役有错误接口和“审图失败算通过”逻辑的历史画图器，保留无外部调用的迁移提示入口；独立绘图请求转 future-image；更新报告规范指向。 |
| future-scientific-writing | 修正至 0.1.1 | 将过期的“最新版”更新为 CONSORT 2025、SPIRIT 2025、TRIPOD+AI；区分参考摘要与完整官方 checklist。 |
| future-skill-creator | 修正至 1.1.1 | 修正 SemVer 对 prerelease+build 的误拒绝及非法版本误接受；统一 builtin/custom 的名字长度、调用策略 flag 校验。 |
| future-software-install | 保留 | 检查入口及平台/镜像参考；已有权限复用、来源校验、任务局部安装和回滚说明。本轮不安装软件、不改镜像。 |
| future-web | 修正至 1.1.1 | 公共 URL 与本地/内网/签名/认证资源分流，避免默认交给远程 fetch；实测 count 并非硬结果上限，增加实际响应检查与本地限额说明。 |

## 高影响问题及修正

### 1. 数据库解析不能把失败或候选当确定结果

旧 `id_resolver.sh` 的明确缺陷：

- SMILES 的 `.get(key, default)` 默认表达式再次 `json.load(sys.stdin)`；默认表达式会先求值，造成读取已耗尽的输入，最终被吞成 `N/A`。
- 给完整 `CHEMBL25` 再加 `CHEMBL` 前缀。
- 名称直接插入 URL/GraphQL，空格、斜线、引号会破坏查询；ChEMBL 使用名称正则第一条命中不能证明化合物身份。
- 将 rsID 直接用作 ClinVar ESummary ID；参考资料还混淆 rsID、Allele ID、Variation ID 和 VCV。
- 默认人类、取第一条候选、缺乏超时、HTTP/schema 错误被静默吞掉。

新 Python 标准库实现对参数编码，GraphQL 使用 variables，通过 InChIKey 查 ChEMBL；显式要求 gene taxon；返回候选及完整性标记和请求时间/参数；HTTP/API/schema 错误非零退出且不自动重试。ClinVar 使用 ELink，再用实际返回的 numeric UID 获取摘要并对齐 UID 集。

兼容性变化：shell 入口仍可调用，但输出改为 JSON；gene 查询需 `--taxon`，不再返回未核实的 Ensembl 一对一映射。每次 HTTP 请求 30 秒上限；不是整个多请求任务的硬总时限。helper 不保证穷尽所有数据库结果。

旧 rate limiter 的负 jitter 可能缩短最小间隔，现改为正 jitter，并明确它只对单个顺序调用者有效，不能控制多进程总速率。

### 2. 实验单位与设计标签不能静默改变

修复前本地反例：

- `cluster_randomization(["clinic1", "clinic1"], seed=1)` 把同一个 clinic 分到 treatment 和 control。
- `latin_square_design(["A", "B"], n_levels=3)` 自动生成不存在的 `T3`；更小的 n_levels 会丢弃已指定处理。
- `crossover_design(..., balance="typo")` 静默走随机分支。

现在均显式拒绝。另补充 crossover 的全体 subject 序列分配随机化、周期平衡和精确样本数测试。说明 cyclic Latin 只在完整组数下保证周期平衡，不保证一阶携带效应平衡；重复测量应使用能处理依赖的方法，不能声称只有混合模型可用。

新版 crossover 同一 seed 的排程可能与旧版不同，真实研究必须保留既有排程并记录脚本版本，不应以升级为由重分已入组受试者。

### 3. 审稿不应悄悄进入付费图片重生成

历史脚本使用错误的 `--args` / `image_path` 调用方式；审图错误或空响应被赋予 7.5 分并视为 acceptable；生成失败还可能自动继续下一轮。因为绘图不是审稿职责，未重新维护第二套图片流水线，而将两个历史命令改成退出码 2 的退役提示；无需网络、不会生成文件或消耗绘图额度。

### 4. 参考资料的版本与官方清单应分开

官方站点核验：

- [SPIRIT–CONSORT](https://www.consort-spirit.org/)：CONSORT 2025 为 30 项，SPIRIT 2025 为 34 项。
- [官方出版记录](https://www.consort-spirit.org/published-statements)：2025 statement 的出版信息。
- [TRIPOD 官方页面](https://www.tripod-statement.org/tripod-ai/)：TRIPOD+AI 为 27 项，替代 TRIPOD-2015，同时覆盖回归与机器学习模型。

保留参考中的核心主题摘要，但不把简化列表冒充官方编号或完整提交表。BMJ 正文 fetch 遇到安全验证页，没有把它算作读到原文；一个推测的 `/spirit-2025` 地址返回 404，也未用于支持结论。最终依据为可读取的官方页面内容。

## 实测记录

运行环境：macOS、Python 3.14，NumPy 2.4.3、pandas 3.0.3、pyDOE3 1.6.2；CLI `future v0.0.2-c18d1063+local`。未新增依赖。

### 公开数据库 smoke tests

| 输入 | 实际结果 |
|---|---|
| compound-name aspirin | PubChem CID 2244；ConnectivitySMILES 可读；InChIKey 精确过滤返回 CHEMBL25，计数 1/1。 |
| gene-symbol TP53 --taxon 9606 | NCBI Gene 7157；UniProt reviewed candidate P04637。 |
| variant-rsid rs334 | ELink 返回 10 个 ClinVar UID；ESummary 的 10 个 UID 与之相符。不是单一临床结论。 |
| disease-name cystic fibrosis | Open Targets 返回三个候选，第一条 MONDO_0009061。初次因缺少 pagination index 返回 HTTP 400；按现有参考补 `index: 0` 后通过，并加回归断言。 |

另外验证了 ClinVar 查询语义：`rs334[RS]` 被翻译为 All Fields，`334[RS]` 更产生宽泛命中；因此未采用这种字段猜测，改为显式跨库 ELink。计数只反映本次查询时点。

Web smoke test 的 `--count 3` 实际返回 10 条结果；请求参数不能冒充硬覆盖/费用上限。fetch 的退出码 0 也不保证获得目标正文。

### 离线验证

以下全部通过：

```text
python3 -W error::ResourceWarning -m unittest discover -s tests -v
  27 tests
python3 -m unittest discover -s builtin/future-experimental-design/tests -v
  18 tests
python3 tests/check_builtin.py
python3 tests/check_orchestration.py
python3 builtin/future-deep-research/tests/check_skill.py
python3 builtin/future-skill-creator/scripts/validate_skill.py builtin/future-skill-creator
sh -n builtin/future-database-lookup/scripts/id_resolver.sh
bash -n builtin/future-database-lookup/scripts/rate_limiter.sh
git diff --check
```

合计 45 项 Python 单元测试；编排检查为 fixture/契约检查，不代表跑过模型决策。没有运行包含 slides 测试的统一 runner，而按范围分别执行上述检查。

## 仍需保留的限制与后续建议

1. 78 个数据库参考的目录一致性已检查，但没有逐一认证全部 API；本轮只实测上述公开数据路径。其余引用尤其旧 GraphQL/REST 示例仍应在使用时验证。
2. 未运行实际论文全文检索、文档上传解析、图片生成/编辑/视觉分析、浏览器交互或 loop worker；相应“保留”结论是静态审查与接口核对，不是全流程通过。
3. 未执行 Windows/Linux 平台实测。新解析器使用标准库跨平台接口；shell 兼容层仍仅适用于 POSIX 环境，原生 Windows 应直接调用 Python。
4. 新增测试覆盖确定性缺陷与失败语义，不证明模型会总是触发正确技能，也不证明临床试验设计足以直接实施。
5. 值得后续单独做的是按领域的**少量可选择的 live contract 测试**，而不是在离线检查里强制联网或付费，也不建议为本轮审查再重写整体技能架构。
