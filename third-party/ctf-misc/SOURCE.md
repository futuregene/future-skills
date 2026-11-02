# 来源与许可

- 上游仓库：https://github.com/ljagiello/ctf-skills
- 上游路径：`ctf-misc`
- 固定提交：`a6106aaf5f1f4eeb6b95908f11c2314c7150dfac`
- 许可证：MIT（全文见上游 LICENSE，随仓分发时保留版权声明）
- 导入日期：2026-11-02
- 抽取范围：该技能目录整体导入：`SKILL.md` + 13 个技术参考 `*.md`；共 14 个文件、267.5 KB；目录内无二进制/数据集。
- 我们的改动：仅新增本文件；`SKILL.md` 与全部参考文件正文与上游逐字节一致

- 使用边界：仅用于 CTF 竞赛、教学靶场与明确授权的测试目标（自有虚拟机、赛事提供的实例、HackTheBox/TryHackMe 等合法演练平台）。不适用于未授权的真实系统；使用时须先确认目标属于上述范围，并遵守赛事规则与当地法律。竞赛/教学/授权靶场：jail 逃逸与提权步骤仅对题目容器、自有主机或合法演练环境（如 HTB 退役靶机）使用。

## 审计注记

- `linux-privesc.md` 是本文档集中双用程度最高的一份：内容取自 HackTheBox 退役靶机 writeup（Dump/Zero/Slonik/Bamboo/Watcher/Atlas 等），技术（sudo 通配符注入、PostgreSQL COPY TO PROGRAM、PaperCut、Zabbix 口令重置等）对真实未修补服务同样有效，使用前必须确认在 boundary 内。
- `ctfd-navigation.md` 需要用户在 CTFd 中自行生成 API token，本技能不内置任何凭据。
