# 来源与许可 — nrf52840-promicro

- 上游仓库：https://github.com/alexex1993/mcu-skills
- 上游路径：`skills/nrf/nrf52840-promicro`
- 固定提交：`816967f30a7dbdf4759ad585b822eda3575f720c`（2026-10-30）
- 许可证：MIT（Copyright (c) 2026 Alex New，全文见上游 `LICENSE`）
- 导入日期：2026-11-02
- 抽取范围：该技能目录整体导入：`SKILL.md`、`reference/board-hardware.md`、`reference/recipes.md`、
  `assets/IMAGE.md`、`template/`（`--full` / `--minimal` / `--ble` 三个变体、`new-project.sh`、
  以及 vendored 的板定义 `template/boards/promicro_nrf52840.json` + `template/boards/variants/`）。共 15 个文件。
- 我们的改动：**只新增本文件**；正文与资源未改写（逐文件 MD5 与上游一致）。
- 本机实跑记录（导入时，PlatformIO Core 6.2.0 + `nordicnrf52` **11.0.0** +
  `framework-arduinoadafruitnrf52` 1.10700.0）：三个变体 `pio run` 全部 SUCCESS，体积与正文相符——
  `--minimal` 20196 B / 3092 B（完全一致）、`--full` 55320 B / 8772 B（完全一致）、
  `--ble` 128692 B / 15588 B（正文写 128676 B，差 16 B）。构建产物含 Nordic DFU 包 `firmware.zip`。
- 顺手复核了正文里几条可证伪的断言（均成立）：
  - 规则 10：Adafruit core 的 `cores/nRF5/nordic/nrfx/mdk/system_nrf52840.c` 只 `#if defined
    (CONFIG_NFCT_PINS_AS_GPIOS)`（复数）。把板定义的 `extra_flags` 改成单数后重编，
    flash 从 20196 B 掉到 20092 B，**差 104 B**，与正文数字一致。
  - 规则 12：平台自带 `adafruit_feather_nrf52840.json` 的 `maximum_ram_size` 是 248832，
    模板的 JSON 改成 237568（链接脚本给小 11 KB），实测进度条分母确实是 237568。
  - 规则 7：Adafruit core 1.7.0 只带 `nrf52840_s140_v6.ld`，没有 v7 的脚本。
  - 规则 1：Adafruit core 的 14 个 variant 里没有任何 Pro Micro / nice!nano 引脚映射，
    平台 45 个板定义里也没有 nice/promicro/supermini——「必须自己 vendor 板定义」成立。
  - 版本漂移（正文写 `nordicnrf52` 10.11.0，实测解析到 11.0.0，板数 45 而非 44）：体积仍完全对得上，
    所以正文的数字结论不依赖那个旧版本号，但 `platform = nordicnrf52` 未 pin 版本这一点要自己注意。

## 使用边界（硬件与工具链）

- **需要实物 ProMicro nRF52840 V1940 / nice!nano v2 兼容板**（nRF52840 QIAA + 出厂 Adafruit UF2
  bootloader + SoftDevice S140 6.1.1）。没有板子时只能当手册读；BLE、USB CDC、低功耗这些结论
  全都无法复现。
- 无 BLE 硬件也能构建：`--minimal` 与 `--full` 不需要任何无线电即可编译；`--ble` 只是把 Bluefruit 链进来。
- 工具链：PlatformIO（`platform = nordicnrf52`、`framework = arduino`、Adafruit nRF52 core 1.7.0）
  + `adafruit-nrfutil`，无商业授权依赖。ZMK/QMK 键盘固件不是这条路——正文明确要求改用 Zephyr 的
  `nice_nano_v2` / `promicro_nrf52840` 板目标。
- 烧写：双击 RESET 进 UF2 bootloader（出现 `NICENANO`/`PROMICRO` 盘），`pio run -t upload` 走
  `adafruit-nrfutil dfu serial --singlebank`；也可把 `uf2conv.py` 转出的 `.uf2` 拖到盘上。
  bootloader 自身丢失时只能用 SWD（J-Link / CMSIS-DAP / pyOCD / OpenOCD）`nrf5 mass_erase` 后重烧。
- 上游明确未验证、不要在工程里当结论用的部分：V1940 **没有公开原理图**，电池充电器、电池检测分压、
  稳压器静态电流、某些修订的第二颗 LED 都未证实；本机也没有仪器测电流/时序/模拟量。
- 克隆板上的 32.768 kHz LSE 晶振常常**没有焊**：`USE_LFXO` 会让 SoftDevice 永久等时钟，
  USB 仍枚举、LED 不闪，看起来像刷坏了。默认保持 `USE_LFRC`。

图片来源：`assets/IMAGE.md` 是 GitHub 外链照片，未随技能打包。
