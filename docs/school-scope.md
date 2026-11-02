# 服务对象与 scope

本仓库的**默认集合是"学科通用 + 杭州电子科技大学"**，其余学校的口径单独标注，不混在默认视图里。

## 三种 scope

| scope | 含义 | 数量 |
| --- | --- | --- |
| `general` | 学科通用技能，与具体学校无关（原有科研/数据/文档类） | 144 |
| `hdu` | 按杭州电子科技大学 9 个一级学科博士点选取 | 53 |
| `cross-school:multi` | 多个学校的经管学科共用（会计/财务口径） | 18 |
| `cross-school:zjut` | 浙江工业大学口径（化工、动力工程及工程热物理、土木） | 7 |
| `cross-school:zstu` | 浙江理工大学口径（设计学、纺织、土木工程管理） | 10 |

**默认视图 = `general` + `hdu`**。取法：

```bash
python -c "import json;d=json.load(open('skills.json'));print('\n'.join(k for k,v in d.items() if v['scope'] in ('general','hdu')))"
```

`tests/check_scope.py` 会拒绝缺失或非法的 scope，并要求每个 `cross-school:*` 条目在本文件里出现，防止跨校内容悄悄混进默认集合。

## 杭州电子科技大学（53）

| 学科（层次） | 技能 | 数 |
| --- | --- | --- |
| 电子科学与技术 / 集成电路（博士点，省一流 A） | `kicad` `spice` `emc` `bom` `datasheets` `jlcpcb` `pcbway` `lcsc` `digikey` `mouser` `element14` | 11 |
| 控制科学与工程（博士点，机器人方向） | `ros2` `ros1` `robot-bringup` `robot-perception` `robotics-testing` `robotics-security` `robotics-design-patterns` `robotics-software-principles` `docker-ros2-development` `ros2-web-integration` | 10 |
| 网络空间安全（博士点，省属唯一） | 逆向：`malware-analysis` `ida-reverse` `radare2` `binary-diff` `reverse-engineering` `protocol-reverse` `threat-intelligence` `supply-chain-security` `llm-security` `dotnet-reverse`<br>竞赛：`ctf-web` `ctf-pwn` `ctf-crypto` `ctf-forensics` `ctf-misc` `ctf-osint` `ctf-malware` `ctf-ai-ml` `ctf-writeup` `solve-challenge` | 20 |
| 管理科学与工程（数字化管理 / 运营） | `sop-builder` `supplier-scorecard` `inventory-forecasting` `incident-postmortem` `job-description-writer` `interview-kit-builder` `compensation-benchmarking` `seo-content-optimizer` `email-marketing` `brand-voice-enforcement` | 10 |
| 数学（博士点，数模传统强项） | `math-modeling-solver` `math-modeling-paper` | 2 |

## 跨校共用：会计与财务（18，`cross-school:multi`）

按杭电工商管理（会计学为浙江最早设硕士点）口径选取，同时服务浙理工会计专硕（1253）与浙工大工商管理、应用经济学博士点：

`dcf-model` `3-statement-model` `comps-analysis` `audit-xls` `roll-forward` `unit-economics`
`revenue-recognition` `lease-accounting` `deferred-tax` `corporate-consolidation` `inventory-costing`
`fixed-asset-accounting` `audit-checklist` `variance-analysis` `budget-forecast`
`working-capital-analysis` `close-management` `intercompany-accounting`

## 浙江工业大学（7，`cross-school:zjut`）

| 学科 | 技能 |
| --- | --- |
| 化学工程与技术（第四轮 A-，博士点） | `dwsim` |
| 动力工程及工程热物理（博士点） | `coolprop-db` `thermo-package` |
| 土木工程（博士点） | `bim-validation-report` `ifc-qto-extraction` `bim-to-schedule-4d` `batch-cad-converter` |

## 浙江理工大学（10，`cross-school:zstu`）

| 学科 | 技能 |
| --- | --- |
| 设计学（省一流 A，博士点，全国前八） | `design-debt-audit` `survey-design` `motion-system` `form-design` `heuristic-evaluation` `platform-conventions` `service-blueprint` `critique-color` |
| 纺织科学与工程（博士点，A 类） | `pattern-making` |
| 土木工程（硕士点，工程管理方向） | `labor-allocation` |

## 仍然空着的方向

公开仓库里没有可信来源，因此**没有接入、也不打算硬凑**：

- 工业设计 / 产品造型（浙理工设计学的另一半）
- 纺织国标与染整工艺
- 生物工程发酵

需要时走 `future-skill-creator` 自研，见 `docs/discipline-coverage.md` 第五节。
