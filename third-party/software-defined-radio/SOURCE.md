# software-defined-radio — 来源与边界

- 上游仓库：https://github.com/briannasywa/sdr-skills
- 上游路径：`skills/software-defined-radio`
- 固定 commit：`f6aab2dfbe6d0b502ac30cba6f869684b7cfce6e`（导入时 `git log -1` 核对；该 commit 即默认分支 `main` 的 HEAD）
- 许可：MIT（Copyright (c) 2026 briannasywa）。上游 `LICENSE` 随仓库根目录分发，本目录不重复放置。
- 导入日期：2026-11-02
- 分类：engineering（工程与硬件）

## 仓库画像

`gh api repos/briannasywa/sdr-skills`：**0 star / 0 fork / 0 watcher**，MIT，`created_at` 与
`pushed_at` 同为 **2026-09-16**（06:11 建库、06:18 最后推送），全库 **2 个 commit**、100 KB。
也就是建库当天 7 分钟内一次性写完、此后无提交、无任何外部采用信号。内容质量不可依赖社区
背书，只以下面「校验记录」里的本机实测为准。

## 抽取范围

目录内全部 27 个文件原样导入：

| 组成 | 数量 | 说明 |
|---|---|---|
| `SKILL.md` | 1 | 303 行 / 19 KB，任务路由器 + 六个数（f_c、f_s、BW、gain、ppm、format）+ 公式表 + 标准工作流 |
| `references/*.md` | 14 | dsp-fundamentals、modulation、hardware、software-toolchain、gnuradio、python-sdr、protocols、signal-identification、antennas-rf-frontend、iq-formats、regulations、troubleshooting、transmission-lab-safety、advanced-topics（每篇 98–229 行） |
| `scripts/*.py` | 9 | 8 个可执行工具 + `_common.py`（共享读写/格式化库） |
| `assets/templates/` | 3 | `gr_wbfm_rx.py`、`gr_fsk_rx.py`（GNU Radio 3.10 无 GUI 流图）、`signal-report-template.md` |

未导入：仓库根目录的 `README.md`、`.gitattributes`、`.gitignore`、`LICENSE`（都属仓库层
而非技能层内容；README 的工具清单已在 `SKILL.md` §7 有等价表述）。

## 我们的改动

只在 frontmatter 之后插入一段「移植说明」块，记录本机实测的缺陷与验证边界。
`SKILL.md` 其余正文、14 篇 references、9 个脚本、3 个模板**逐字节未改**（导入时对
27 个文件做过 SHA-256 全量比对，除 `SKILL.md` 的这段插入外无任何差异）。

**没有替上游修 bug**：下面三处缺陷都保留原文，靠「移植说明」和本文件把正确用法写清楚。
理由是保持与上游可 diff、便于日后跟随上游更新；代价是使用者必须读到移植说明。

## 上游缺陷（全部本机复现）

1. **`--shift -250e3` 直接报错。** `SKILL.md` §7 与 `references/iq-formats.md` 都把
   `python scripts/iq_convert.py in.cu8 out.cf32 --fs 2.4e6 --shift -250e3 --decim 10`
   写成示例。argparse 把 `-250e3` 当成选项（只有纯数字 `-250000` 才被识别为负数），
   实测 `exit 2：argument --shift: expected one argument`。正确写法是 `--shift=-250e3`
   或 `--shift -250000`。同类风险在 `fm_demod.py --offset` 上同样存在。
2. **`--decim N` 静默少抽取。** `iq_convert.py` 的 `decimate()` 把因子拆成 ≤8 的整数连乘，
   但末尾没有处理余数：`--decim 10` 实际只做了 `/8`，同时仍然打印 `new fs 240.000 kHz`
   （真实输出速率 300 kHz）。实测 7,200,000 样本输入 → 输出 900,000（应为 720,000）。
   `references/python-sdr.md` §2 的 `decim()` 是同一段逻辑、同一 bug（`decim(x,10)` 返回 n/8）。
3. **`sdr_calc.py dbm` 单位重复**：`-50.00 dBm = 10.000 nW W = 707.107 uV V rms …`
   （`eng(w,"W")` 已带单位，格式串里又写了 `W`）。纯显示问题，数值正确。
4. `references/python-sdr.md` 的 `read_iq()` docstring 声明支持 `cs12`，但 dtype 表里没有，
   传 `cs12` 会 `KeyError`（实测）。
5. `references/python-sdr.md` §5 用 `dt.datetime.utcnow()`，Python ≥3.12 已弃用（能跑，
   SigMF 记录的 datetime 格式正确）。
6. `references/python-sdr.md` 同一节末尾关于 datatype 的一句自问自答
   （"`cu8` (as `cu8` non-standard; SigMF uses `cu8`? use `ci8`/` cf32_le`)"）把读者绕晕——
   按 SigMF 规范 `cu8` 是合法 datatype，`sigmf_write.py` 也照此输出。
7. `sigmf_write.py` 的示例 `cap.cs16 --hw "HackRF One"` 与硬件矛盾：HackRF 写的是 `cs8`
   （`SKILL.md` §8 自己也这么写）。
8. `references/software-toolchain.md` §1 的 UHD 行里留了自改痕迹：`` `pip install uhd`? no:
   use conda/radioconda``。
9. `iq_spectrum.py` docstring 说 ASCII 模式会给 "crude waterfall stats"，实际只打印 PSD。

## 使用边界

**不需要任何硬件即可用的（本机全部实跑过）**：`sdr_calc.py` 全部 12 个子命令、
`iq_info.py`、`iq_spectrum.py`（PNG 与 `--ascii` 两条路径）、`iq_convert.py` 格式互转、
`fm_demod.py`（WBFM/NBFM/AM）、`symbol_rate.py`、`sigmf_write.py`、`probe_devices.py`
（无设备时正确报告 9 类工具均未安装并 exit 0）。依赖只有 Python 3.9+ 与 numpy；
scipy/matplotlib 缺失时各脚本都有纯 numpy 退路（未在本机逐一断开验证退路质量）。

**需要硬件或额外软件栈、本机未验证的**：`probe_devices.py` 只验证了「工具不存在」这条
路径，没有真机；`references/python-sdr.md` §4 的 pyrtlsdr / SoapySDR / pyadi-iio / UHD 实流
代码块、2 个 GNU Radio 模板、`references/protocols.md` 的 dump1090-fa / rtl_433 / AIS-catcher /
multimon-ng / SatDump / grgsm 等外部解码器命令，本机既无 SDR 也无 GNU Radio，只做了语法
（`py_compile`）与参数形态核对，**没有跑通证据**。它们是「按上游叙述可执行」，不是「已核可执行」。

**内容属性**：以调参手册 + 命令行配方为主，任务路由器把 14 篇 references 按需加载。
协议部分给的是「频率 / 调制 / 速率 / 最小 f_s / 增益 / 工具 + 原样命令 / 法务提示」这一层，
不是比特级协议规范；真要自己写解析器仍需按 `references/modulation.md` §7 的九步走。
法规部分按 ITU 分区 + 美/英/印尼给，中国频段与执照要求未覆盖，用到时需另行核对。

**安全口径**：技能本身是 receive-first，明确拒绝 jam/spoof/解密私有通信，TX 只允许
持照业余、免照认证设备或有线屏蔽实验三类场景（`references/transmission-lab-safety.md`）。
导入后不需要额外限制。

## 校验记录（导入时实际执行）

1) `git clone` 后 `git checkout f6aab2d`，`git log -1` 核对 commit 与作者；`gh api` 核对
   MIT、0 star、2026-09-16 建库当天 2 个 commit。
2) **静态**：9 个脚本 + 2 个 GNU Radio 模板 `py_compile` **11/11 通过**；8 个工具 `--help`
   **8/8 exit 0**（`_common.py` 是库，无 CLI）。
3) **端到端**（合成 IQ，全部在 stage 目录内生成）：
   - 造 3 s / 2.4 MS/s cu8 WBFM（1 kHz 音调、75 kHz 频偏、偏移 +250 kHz）；
     `iq_info.py` 报 RMS 0.5001、占用带宽 160 kHz、最强谱线在 +322 kHz（250+75 kHz 边带，正确）；
   - `fm_demod.py --offset 250e3 --mode wbfm` → 48 kHz / 144,000 帧 WAV，FFT 主峰
     **999.8 Hz**（原始 1 kHz 音调被还原）；NBFM 与 AM 两条路径同样 exit 0；
   - `iq_spectrum.py` → 409,275 B PNG（magic 校验通过），`--ascii` 无 matplotlib 也可用；
   - `sdr_calc.py` 12 个子命令逐个跑：λ(433.92 MHz)=0.6909 m、FSPL(200 km,1090 MHz)=139.21 dB、
     噪声底(2 MHz,NF6)=-104.99 dBm、Carson(75k/15k)=180 kHz、Friis(1/0.8/6)=1.008 dB、
     doppler(137 MHz,7.5 km/s)=3.427 kHz、cu8@2.4 MS/s=4.8 MB/s —— 与手算一致；
   - `symbol_rate.py` 在合成 50 kBaud BPSK 上报 **50.000 kBaud**（包络线 prominence 48.8 dB）；
   - `sigmf_write.py` → `ci8` 元数据 + 字节级复制的 `.sigmf-data`，字段符合 SigMF 1.2.0；
   - `probe_devices.py` → 9 类工具全部 "not installed"，exit 0。
4) **文档代码**：`references/python-sdr.md` 的 9 个 python 块中，§1/§2/§3 三块原样 `exec` 通过
   （read/write、PSD、FM/AM/SSB 解调、Costas、Gardner 都能跑）；§5 SigMF 块装 `sigmf 1.14.0`
   后原样跑通并生成合法 1.2.0 元数据。
5) **结构**：25 个正文内引用的 `references/ scripts/ assets/` 路径**无悬空**（仅 `_common.py`
   无正文引用，属正常共享库）；frontmatter `name` = 目录名 `software-defined-radio`；
   `SKILL.md` 303 行，未超上游自定的 500 行上限。

## 出处强度（重要，读之前先看这一段）

- 上游仓库 **0 星**；
- **总共 2 个 commit，建库当天写完，此后再无提交**；
- 单一作者，无 issue、无 PR、无外部使用记录。

**本技能以内容实测收留，不是以出处强度收留。** 收留时的实测结论：9 个脚本全部 `py_compile` 通过，
8 个命令行工具 `--help` 全部 exit 0，正文给出硬件型号、采样率/中心频率/解调参数与协议解码步骤。

含义：它的可执行性经过验证，但**没有社区使用史背书**。若你读到与常识冲突的参数或结论，
优先相信手册与实测，并考虑用更可信的来源替换本技能。

固定的上游提交：`f6aab2dfbe6d`（不追 main，因为上游已无更新）。
