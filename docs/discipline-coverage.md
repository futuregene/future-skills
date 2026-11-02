# 学科覆盖与待评估清单

> **两处结构性空白，先说在前面：**
>
> 1. **中文语境没有现成来源。** 国内会计准则（CAS）与税务实务、全国大学生电子设计竞赛（NUEDC）流程、中国研究生数学建模竞赛（华为杯）规范、中文期刊与学位论文格式——这些在公开技能仓库里都找不到，需要自研。
> 2. **国产 EDA 没有替代路径。** 现有 EDA 技能全部建立在 Yosys / OpenROAD / KLayout / 商业 CST 之上；华大九天、概伦等国产工具链没有任何 agent 技能，而这正是集成电路设计教学与"国产替代"研究最需要的部分。

本文件记录技能库相对**杭州电子科技大学、浙江工业大学、浙江理工大学**学科布局的覆盖情况，以及已评估但未引入的上游仓库。

## 一、分类

| 分类 | 中文 | 说明 |
| --- | --- | --- |
| `engineering` | 工程与硬件 | PCB/EDA、嵌入式、机器人、机械、仿真工具 |
| `computing` | 数据与计算 | 数据科学、机器学习、统计、数值与优化、工作流 |
| `life-science` | 生命科学与医药 | 生物信息、临床、医学影像、神经科学、湿实验、药物化学 |
| `chemistry-materials` | 化学与材料 | 材料计算、分子动力学、谱图与化学信息学 |
| `research` | 科研与建模 | 文献、写作、评审、实验设计、数学建模 |
| `security` | 安全与取证 | 逆向、恶意样本、威胁情报、供应链与大模型安全 |
| `business` | 金融与管理 | 财务建模、会计审计、市场与运营 |
| `docs` | 文档与设计 | 文档解析、演示、图表、期刊模板、设计方法 |
| `platform` | 平台与工具 | Agent 自省、目标、任务、MCP、浏览器、检索、安装、版本 |

分类只有九类，新增技能必须落在其中一类；`tests/check_registry.py` 会拒绝白名单之外的分类。

## 二、三校学科与覆盖

| 学科 | 杭电 | 浙工大 | 浙理工 | 覆盖情况 |
| --- | --- | --- | --- | --- |
| 电子科学与技术 / 集成电路 | 博士点 | — | — | `kicad` 等 11 个硬件技能；**IC 设计与 EDA 仍空** |
| 信息与通信工程 | 博士点 | — | 硕士点 | 缺（仅通用 DSP 与仿真） |
| 控制科学与工程 | 博士点 | 博士点 | 硕士点 | 机器人 10 个技能；无控制器设计专用技能 |
| 计算机 / 软件工程 | 博士点 | 博士点 | 博士点 | 数据与计算 34 个；无软件工程流程技能 |
| 网络空间安全 | 博士点 | — | 硕士点 | 10 个安全与取证技能 |
| 机械工程 | 博士点 | 博士点 | 博士点 | 缺（机器人技能只覆盖控制侧） |
| 管理科学与工程 / 工商管理 | 博士点 | 博士点 | 硕士点 | 少量财务技能，待扩充 |
| 数学 | 博士点 | 博士点 | 硕士点 | 建模 2 个 + 统计与优化 |
| 材料科学与工程 | 硕士点 | 博士点 | 博士点 | `pymatgen` 等 14 个 |
| 化学工程与技术 | — | 博士点（A-） | 硕士点 | **空** |
| 环境科学与工程 | — | 博士点（A 类） | — | **空** |
| 动力工程及工程热物理 | — | 博士点 | 硕士点 | **空** |
| 土木工程 | — | 博士点 | 硕士点 | **空** |
| 药学 / 生物工程 | — | 博士点 | 硕士点 | 药物化学已覆盖，生物工程部分覆盖 |
| 纺织科学与工程 | — | — | 博士点（A 类） | **空** |
| 设计学 | — | — | 博士点（A 类） | **空** |

## 三、待评估（已查证，暂不引入）

| 上游 | 星 | 许可 | 不引入的原因 |
| --- | --- | --- | --- |
| `SDAI-institute/LCA-Skills` | 0 | 未声明（NOASSERTION） | 许可不明，无法确认可否再分发；LCA 方法学内容本身可用，需先谈许可 |
| `ChineduNlem/claude-structural-engineering` | 3 | MIT | 只覆盖国际规范（ASCE/AISC/Eurocode），与国内荷载规范不一致，教学会误导 |
| `flowful-ai/cad-skill` | 710 | PolyForm Noncommercial | 非商用许可，与 MIT 仓库不兼容 |
| `jihe520/MathModelAgent` | 6276 | 无许可证 | 不可再分发 |
| `JoelLewis/finance_skills` | 219 | MIT | 81 个投研/合规技能与 `anthropics/financial-services` 高度重叠 |
| `k-dense-ai/scientific-agents` | 234 | MIT | 503 个"以 X 专家思考"的 persona，1006 个文件里 1000 个不含任何命令，不可作为可执行技能 |
| `adriendelmas/pattern-making-skill` | 1 | MIT | 纺织打版，内容真实但仅单人维护，观察后再定 |
| `fdias78git/dwsim-claude-integration` | 23 | MIT | 化工流程模拟，依赖 DWSIM 桌面端，待环境验证 |
| `datadrivenconstruction/DDC_Skills_*` | 383 | MIT | 221 个土建技能，需逐条核对规范适用性 |
| `Owl-Listener/designer-skills` | 3214 | MIT | 设计学方法，需与国内设计教学口径对齐后引入 |

## 四、文档里刻意不提供的引用

技能正文里出现过、但本库**故意没有**对应物的引用，已去掉链接、保留文字（`tests/check_references.py` 会阻止这类引用再次长出来）：

| 技能 | 被去掉的引用 | 原因 |
| --- | --- | --- |
| `markdown-mermaid-writing` | `../../docs/project/{issues,kanban,pr}/…`、`../adr/…`、`../workflow_guide.md`、`../operational_readiness.md`、`mermaid_diagrams/kanban.md` | 上游仓库自己的项目管理文档与模板，不属于可复用技能内容 |
| `reverse-engineering` | `../field-journal/seed-014_unity-il2cpp-reverse.md`、`../../ops/analysis-*-*.md`、`tools-emulation.md`、`anti-analysis-ctf.md`、`patterns-runtime.md` | `field-journal` / `ops` / 其余 ctf-reverse 文件均未导入，刻意不提供 |
| `timesfm-forecasting` | `forecast_visualization.png` | 示例图未随技能导入 |
| `dwsim` | `LICENSE` | 许可证在上游仓库根目录，技能目录内没有 |

同目录下 `markdown-mermaid-writing` 的 `../markdown_style_guide.md`、`../mermaid_style_guide.md` 与 `mermaid_diagrams/*.md` 有对应物，改成了 `references/` 下的真实路径，属修正而非删除。

## 五、自研候补

1. **国内会计准则与税务**：CAS 收入确认、增值税、汇算清缴、合并报表口径差异。
2. **NUEDC 电子设计竞赛**：赛题流程、常用模块、测评与报告规范。
3. **华为杯研究生数学建模**：论文规范与评审偏好（与已有 CUMCM 技能区分）。
4. **国产 EDA 替代路径**：华大九天、概伦等工具链的操作与迁移流程。
5. **集成电路设计流程**：RTL→综合→布局布线→签核的可执行技能（开源链路或国产链路）。
6. **中文期刊与学位论文格式**：GB/T 7714 参考文献、学位论文模板与查重前自检。

自研技能请用 `future-skill-creator`，并沿用本仓库的 `SOURCE.md` 约定（自研技能注明"本仓库原创"）。

## 六、踩坑：守卫命令之前先取回 origin/main

不要直接跑 git diff --quiet origin/main dev-<user> 判断一个分叉分支能否收敛。本机实测：

`
git diff --quiet origin/main dev-huichen
fatal: Needed a single revision
`

因为本地根本没有 origin/main 这个 ref（CLI 的浅克隆/单分支配置下常见）。正确顺序是先把它取下来，**不 checkout**：

`ash
git fetch origin main:main
git diff --quiet origin/main dev-<user>   # 现在才成立
`

同理，任何"比较远端与本地分支"的守卫都应在 git fetch 之后写，否则守卫本身先失败，看起来像分支有问题。
