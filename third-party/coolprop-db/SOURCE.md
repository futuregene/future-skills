# coolprop-db — 来源与边界

- 上游仓库：https://github.com/Soljourner/claude-engineering-skills
- 上游路径：`skills/databases/coolprop-db`
- 固定 commit：`1c3340ba171b475fb0ecd7b1699e41dac6acd986`（导入时 `git log -1` 逐一核对）
- 许可：MIT（Copyright (c) 2025 Soljourner）。上游 LICENSE/LICENSE.md 随该仓库分发，本目录不再重复放置。
- 导入日期：2026-11-02
- 分类：engineering（工程与硬件）

## 抽取范围

导入 `SKILL.md`、`examples.py`、`reference.md` 三件；该目录在上游只有这三件。

## 我们的改动

仅在 frontmatter 之后插入「移植说明」块（记录实测版本、两处示例缺陷、维护状态），`SKILL.md` 其余正文、`examples.py`、`reference.md` 逐字节未动。

## 使用边界

需要 `pip install CoolProp`（实测 8.0.0）；它给的是纯组分/伪纯流体的 Helmholtz EOS 物性，不是混合物 VLE 求解器，含相互作用的混合物应改用 `thermo-package` 或流程模拟器。用 `(T,P)` 输入对查水前必须判相：101325 Pa/373.15 K 正好在饱和点，CoolProp 返回过热蒸汽支（ρ=0.5976 kg/m³），上游示例把它当液态水列出。0 °C/常压会因高于 Tmelt(101325 Pa)=273.153 K 而报错。

## 校验记录（导入时实际执行）

1) clone 并 `git log -1` 核对 commit = `1c3340ba`；`gh api` 核对 MIT、97 星、2025-11-07 最后推送（建库当天，此后无提交）。
2) `py_compile` 通过；`pip install --target` 装 CoolProp 8.0.0 后 `examples.py` 退出码 0、257 行输出，示例 1–6 数值合理（R134a 25 °C 饱和压力 6.65 bar、h_fg 177.79 kJ/kg）。
3) 单点复算确认 100 °C 相位跳变：373.15 K/101325 Pa → ρ=0.5976、Phase=5；373.00 K → ρ=958.46、Phase=0。
4) frontmatter `name` 等于目录名 `coolprop-db`。
