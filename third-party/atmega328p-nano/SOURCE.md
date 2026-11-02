# 来源与许可 — atmega328p-nano

- 上游仓库：https://github.com/alexex1993/mcu-skills
- 上游路径：`skills/avr/atmega328p-nano`
- 固定提交：`816967f30a7dbdf4759ad585b822eda3575f720c`（2026-10-30）
- 许可证：MIT（Copyright (c) 2026 Alex New，全文见上游 `LICENSE`）
- 导入日期：2026-11-02
- 抽取范围：该技能目录整体导入：`SKILL.md`、`reference/board-hardware.md`、`reference/recipes.md`、
  `assets/IMAGE.md`、`template/`（`--full` / `--minimal` 两个变体 + `new-project.sh`）。共 11 个文件。
- 我们的改动：**只新增本文件**；`SKILL.md` 与 `reference/`、`template/` 未改写（逐文件 MD5 与上游一致）。
  上游正文里标注「hardware-verified」的只有 Blink（`--minimal`）一项，其余 ADC 参考、中断、Timer1 PWM、
  Servo/tone、sleep、PROGMEM 上游自己标为「**compile-checked only**」——这个区分在本机没有被推翻，
  也没有被升级成实测结论。
- 本机实跑记录（导入时）：`template/variants/new-project.sh` 生成两个工程后 `pio run` 均 SUCCESS
  （PlatformIO Core 6.2.0 + `atmelavr`，`toolchain-atmelavr` 首次构建约 86 s），体积与正文数字**完全一致**：
  `--minimal` 924 B flash / 9 B RAM，`--full` 2874 B flash / 201 B RAM。上游说的烧写熔丝位也核对过：
  平台自带的 `platforms/atmelavr/boards/nanoatmega328new.json` 里正是 `lfuse 0xFF / hfuse 0xDA /
  efuse 0xFD`、`maximum_size 30720`，与正文 §8/§12 一致。

## 使用边界（硬件与工具链）

- **需要实物 Arduino Nano（A000005）或其克隆**：ATmega328P @16 MHz、5 V。没有板子时只能当手册读
  （引脚修正表、定时器归属、2 KB SRAM 预算、熔丝与 ICSP 恢复流程仍是可用的知识）。
- **克隆板必须分清 bootloader 代际**：2018 年前的正品与多数克隆是 ATmegaBOOT @57600，对应
  `board = nanoatmega328`；Optiboot 板用 `nanoatmega328new`。选错在上传期报 `not in sync`。
  克隆板多用 CH340，需要 WCH 驱动才会出现 COM 口。
- 工具链：PlatformIO（`platform = atmelavr`、`framework = arduino`）+ `avrdude`，无商业授权依赖；
  也可用 Arduino IDE（`arduino:avr:nano`）。ICSP 恢复需要第二块 Arduino 作 ArduinoISP、USBasp 或
  `avrdude` + 任意 ISP 编程器。
- 烧写/调试：Mini-B USB 线，DTR 自动复位进 bootloader；没有 SWD/JTAG，只能用 6 针 ICSP。
- 与上游无关的版本敏感点：正文写「PlatformIO 6.1 + atmelavr 5.3.0」，本机实际装的是 6.2.0 + 平台最新版，
  构建体积仍逐字节对上，说明该技能对这些版本不敏感。

图片来源：`assets/IMAGE.md` 是 GitHub 外链照片，未随技能打包。
