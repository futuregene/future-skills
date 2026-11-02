# 来源与许可

- 上游仓库：https://github.com/ljagiello/ctf-skills
- 上游路径：`solve-challenge`
- 固定提交：`a6106aaf5f1f4eeb6b95908f11c2314c7150dfac`
- 许可证：MIT（全文见上游 LICENSE，随仓分发时保留版权声明）
- 导入日期：2026-11-02
- 抽取范围：该技能目录整体导入：`SKILL.md` + 1 个技术参考 `*.md` + 1 个 shell 脚本（install_ctf_tools.sh 取自上游仓库根 `scripts/`）；共 3 个文件、59.6 KB；目录内无二进制/数据集。
- 我们的改动：仅新增本文件；`SKILL.md` 与全部参考文件正文与上游逐字节一致；另将上游仓库根的 `scripts/install_ctf_tools.sh` 收录为 `scripts/install_ctf_tools.sh` 以消除正文中的悬空引用（未改动脚本内容）

- 使用边界：仅用于 CTF 竞赛、教学靶场与明确授权的测试目标（自有虚拟机、赛事提供的实例、HackTheBox/TryHackMe 等合法演练平台）。不适用于未授权的真实系统；使用时须先确认目标属于上述范围，并遵守赛事规则与当地法律。竞赛/教学/授权靶场：本技能是调度器，其侦察与连接步骤只能指向赛事实例或自有靶场；不会自行扩大目标范围。

## 审计注记

- 与被导入的 9 个专项技能是「入口 vs 深度参考」关系，不构成重复（与全部 160 个既有技能实测相似度 ≤0.001）。
- `SKILL.md` 中 `/ctf-reverse` 指向的逆向技能本批未导入（重复度原因，见 REPORT）；该能力由已安装的 `reverse-engineering` 提供。
- 正文引用 `../scripts/install_ctf_tools.sh`（上游仓库根），为使引用不悬空，已把该脚本一并收录到 `scripts/install_ctf_tools.sh`；在上游它需要以仓库根为 cwd 运行，本目录下以技能目录为 cwd 运行即可。脚本为系统级安装器，只应在用户明确要求时执行。

## 增量合并（2026-11-02）

`scripts/install_ctf_tools.sh` 取自上游仓库根目录（commit `a6106aaf5f1f4eeb6b95908f11c2314c7150dfac`，MIT），
因为本技能正文按 `bash scripts/install_ctf_tools.sh <group>` 的方式调用它，而导入时只取了技能目录。
运行前请把工作目录切到本技能目录。
