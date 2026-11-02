# 来源与许可 — stm32f411-blackpill

- 上游仓库：https://github.com/alexex1993/mcu-skills
- 上游路径：`skills/stm32/stm32f411-blackpill`
- 固定提交：`816967f30a7dbdf4759ad585b822eda3575f720c`（2026-10-30，仓库仅此一个 squash 提交）
- 许可证：MIT（Copyright (c) 2026 Alex New，全文见上游 `LICENSE`；再分发需保留版权与许可声明）
- 导入日期：2026-11-02
- 抽取范围：该技能目录整体导入，即 `SKILL.md`、`reference/board-hardware.md`、`reference/recipes.md`、
  `assets/IMAGE.md`、`template/`（可直接 `pio run` 的参考工程，含 `template/variants/new-project.sh`
  脚手架与 `lib/USBDevice/` 里 vendored 的 ST USB CDC 栈）。共 32 个文件。
- 我们的改动：**只新增本文件**。`SKILL.md` 正文、`reference/`、`template/` 一字未改，
  逐文件 MD5 与上游一致（导入时比对 32/32 相同）。因此上游正文里的「verified on hardware」陈述
  是**上游作者**的验证结论，不是我们在本机的实测结论——本机只做了构建级验证（见下）。
- 本机实跑记录（导入时）：用该目录自带 `template/variants/new-project.sh` 生成 `--minimal` 与
  `--full` 两个工程，`pio run` 均 SUCCESS（PlatformIO Core 6.2.0，`ststm32` 20.0.0，
  `framework-stm32cubef4` 1.28.3，`toolchain-gccarmnoneeabi` 7.2.1）；体积与正文所写数字相符
  （minimal 3476 B flash / 44 B RAM 完全一致；full 实测 19816 B / 4840 B，正文写 19808 B，差 8 B）。
  正文「规则」逐条在 `template/src/main.c` 里落地（`SysTick_Handler`、PLLM25/N192/P2/Q4、
  `FLASH_LATENCY_3`、`PWR_REGULATOR_VOLTAGE_SCALE1`、`HAL_PWR_EnableBkUpAccess()`、
  `GetTime` 先于 `GetDate`、`ADC_CHANNEL_TEMPSENSOR` + `ADC_SAMPLETIME_480CYCLES`）。

## 使用边界（硬件与工具链）

- **必需要有对应的实物板**才有意义：WeAct Studio "Black Pill" V3.x（STM32F411CEU6，25 MHz HSE +
  32.768 kHz LSE 已焊）。没有板子时，本技能只能当**板级知识手册**读（引脚/时钟/USB/DFU/F4 陷阱），
  构建可跑但任一条「已在硬件上验证」的结论都不可复现。
- **必须是 F411CEU6**：同款 PCB 也有 STM32F401CCU6 版本（256 KB flash / 64 KB RAM / 84 MHz，
  温度传感器在 ADC 通道 **16** 而非 18）。丝印确认芯片再照抄；正文的时钟树在 F401 上仍成立，
  温度传感器与 96 MHz 上限则不能照搬。
- 工具链：PlatformIO（本机实测 Core 6.2.0 + `ststm32` 20.0.0 + `framework-stm32cubef4` 1.28.3），
  首次构建需联网下载平台与 `toolchain-gccarmnoneeabi`（本机约 3.5 分钟）。**不需要** CubeIDE/CubeMX；
  也可用 CubeIDE 读同一份 HAL 代码，但 `platformio.ini` 与 `template/` 的构建路径只对 PlatformIO 成立。
- 烧写：走板载 USB-C 的 ROM DFU（`0483:DF11`，手动 BOOT0 + NRST），`pio run -t upload` 调 `dfu-util`
  并传 `:leave`；需要断点时用 4 针 SWD 与 ST-Link（`debug_tool = stlink`）。无任何商业授权依赖。
- 已知与当前版本不符的一处：正文规则 11 说 `framework-stm32cubef4` 里没有 `STM32_USB_Device_Library`，
  实测 1.28.3 的 `Middlewares/ST/STM32_USB_Device_Library/` 是存在的（只是框架不会自动加入编译路径），
  所以「必须自己 vendor」这句在本版本下是过时表述；`template/lib/USBDevice/` 的做法本身可用。

图片来源：`assets/IMAGE.md` 里是 GitHub user-attachments 的外链照片，**未随技能打包**；离线环境只能看到
alt 文本，不能当作看图识别板子的依据。
