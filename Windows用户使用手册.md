# PyMotion Lite SDK Windows 用户使用手册

本文档适用于 `PyMotion Lite SDK 1.0.1` Windows x64 评估包。

请先阅读本手册，再连接设备并运行示例。完整 Python API 说明位于 SDK 解压目录的
`docs\SDK_USER_MANUAL.md`。

## 1. 用户会收到哪些文件

正常交付包含以下三个相互独立的文件：

- `PyMotion-Lite-SDK-1.0.1-windows-x64-EVALUATION-<发布编号>.zip`
- 与 ZIP 同名的 `.zip.sha256` 校验文件
- `Windows用户使用手册.md`

中文使用手册放在 ZIP 外部，不属于 SDK 签名包，也不会参与安装器的文件校验。
ZIP 解压后只有一个顶层目录：`pymotion_SDK_dev`。请保留该目录中的全部文件，
不要把外部中文手册复制进 `pymotion_SDK_dev`，也不要只复制 `install.bat`，否则
签名验证和离线安装可能失败。

## 2. 电脑要求

- 64 位 Windows 10 或 Windows 11。
- 普通用户账户可以安装，不要求管理员权限。
- 不要求电脑预先安装 Python。SDK 包内置经过签名清单保护的 64 位
  CPython 3.12 离线运行时。
- 使用 VS Code 运行课程时，电脑需要另行安装 VS Code。没有 VS Code 也可以
  使用 SDK 专用终端运行示例。
- USB 连接必须使用支持数据传输的 USB 线；仅供电线无法通信。

## 3. 校验下载文件

建议在解压前核对 ZIP 的 SHA-256。打开 ZIP 所在文件夹，在地址栏输入
`powershell` 并回车，然后执行：

```powershell
Get-FileHash -Algorithm SHA256 ".\PyMotion-Lite-SDK-1.0.1-windows-x64-EVALUATION-<发布编号>.zip"
```

输出的哈希值应与 `.zip.sha256` 文件中的值完全一致。若不一致，请停止安装并
重新获取 SDK 包。

安装器还会验证发布证书、清单签名和包内每个文件的哈希。任何验证失败都不应
通过手工删除清单或绕过脚本解决。

## 4. 安装 SDK

1. 将 ZIP 完整解压到本地磁盘，例如 `D:\PyMotionLiteSDK`。
2. 打开解压后的 `pymotion_SDK_dev` 目录。
3. 双击 `install.bat`。
4. 等待窗口显示 `Installation completed.`。
5. 安装窗口提示按键退出后，再进行下一步。

安装器默认在当前 Windows 用户目录创建隔离环境：

```text
%LOCALAPPDATA%\PyMotion\LiteSDK\venv-cp312
```

内置 Python 运行时和用户示例工作区也会放在
`%LOCALAPPDATA%\PyMotion\LiteSDK` 下，不会修改系统 Python，也不会要求用户
自己配置 `PATH`。

重复运行 `install.bat` 可以重新核验并更新同一 SDK 环境。如果安装失败，请保留
窗口中的完整错误信息，不要单独移动安装脚本后重试。

## 5. 在 VS Code 中运行示例

推荐使用以下方式：

1. 双击 `open-sdk-vscode.bat`。
2. 脚本会在用户目录创建与当前签名包对应的示例副本，并打开专用 VS Code
   工作区。
3. 在左侧打开 `examples\quick-start\01-pymotion-lite.py`。
4. 使用 VS Code 的 Python 运行按钮或 Code Runner 运行。

专用工作区会同时固定 Python 扩展和 Code Runner 使用的 SDK 解释器。请不要从
普通 VS Code 窗口直接打开原始 ZIP 目录并运行示例，否则可能调用系统 Python，
出现：

```text
ModuleNotFoundError: No module named 'pymotion'
```

如果 `open-sdk-vscode.bat` 提示找不到 VS Code，请先安装 VS Code，再重新运行该
脚本；也可以先使用下一节的 SDK 专用终端。

## 6. 在 SDK 专用终端中运行示例

双击 `open-sdk-terminal.bat`。窗口出现
`PyMotion Lite SDK environment activated.` 后，可执行：

```bat
python examples\quick-start\01-pymotion-lite.py
python examples\lite-learning-course\01-usb-connection.py
pymotion doctor
```

若必须在 PowerShell 中直接调用带空格路径的 Python 可执行文件，路径前要加调用
运算符 `&`：

```powershell
& "$env:LOCALAPPDATA\PyMotion\LiteSDK\venv-cp312\Scripts\python.exe" -u ".\example.py"
```

直接写 `"C:\...\python.exe" -u ...` 会被 PowerShell 当成字符串表达式，并报告
“意外的标记 `-u`”。

## 7. USB 首次连接

1. 给 PyMotion Lite 设备正常供电。
2. 使用支持数据传输的 USB 线连接电脑和设备。
3. 关闭串口助手、烧录工具以及其他可能占用同一 COM 端口的软件。
4. 等待 Windows 完成设备识别，并给设备留出启动时间。
5. 在 SDK 专用终端执行：

```bat
pymotion doctor
```

随后运行：

```bat
python examples\lite-learning-course\01-usb-connection.py
```

程序的正式导入方式是：

```python
import pymotion as pm

with pm.lite.connect(transport="usb") as lite:
    print(lite.connection.device_id)
```

`pm.lite.connect()` 默认最多等待 15 秒，以覆盖设备上电、USB 枚举和启动握手过程。
不要因为前几秒没有立即响应就反复拔插设备。

## 8. Wi-Fi 连接准备

设备和电脑需要位于可互通的局域网。电脑防火墙应允许 SDK 使用专用网络，设备
需要能够访问电脑的默认 TCP 端口 `8787`。

Token 必须与设备中配置的 Token 一致。只对当前 PowerShell 窗口设置 Token：

```powershell
$env:PYMOTION_AUTH_TOKEN = "设备的 Token"
```

然后从 SDK 专用环境运行：

```bat
python examples\lite-learning-course\02-wifi-connection.py
```

不要把真实 Token 写入准备公开或共享的示例代码。

## 9. 常见问题

### 9.1 提示安装目录不是签名包

典型错误：

```text
This directory is neither a signed customer bundle nor a complete source checkout.
```

原因通常是只复制了 `install.bat`、没有完整解压 ZIP，或者包内文件被移动。重新
完整解压原始 ZIP，并从 `pymotion_SDK_dev` 目录双击 `install.bat`。

### 9.2 找不到 `pymotion` 模块

当前程序使用了系统 Python，而不是 SDK 隔离环境。关闭普通终端，通过
`open-sdk-vscode.bat` 或 `open-sdk-terminal.bat` 重新运行。

### 9.3 找不到已验证的 USB 设备

典型错误：

```text
no verified PyMotion Lite device was found; check USB and power
```

依次检查：

1. 设备是否正常供电并完成启动。
2. USB 线是否支持数据传输。
3. Windows 设备管理器中是否出现对应串口。
4. 串口是否被烧录器或串口助手占用。
5. 执行 `pymotion doctor`，保存完整结果。
6. 若已经枚举到 Espressif 串口但仍没有有效握手，检查设备固件是否与 SDK
   发布版本匹配。

`doctor` 中“串口枚举成功”只说明 Windows 看到了端口，不等于该端口已经通过
PyMotion 协议验证。

### 9.4 双击安装窗口一闪而过

在解压目录的地址栏输入 `cmd` 并回车，然后执行：

```bat
install.bat
```

这样可以保留完整错误信息。向技术支持反馈时，请同时提供 Windows 版本、ZIP
文件名、SHA-256、安装器完整输出和 `pymotion doctor` 输出。

### 9.5 签名或哈希验证失败

不要继续使用该副本。删除当前解压目录，从确认可信的 ZIP 重新解压，并再次核对
SHA-256。杀毒软件隔离文件、网盘的按需同步或手工修改包内文件都可能导致验证
失败。

## 10. 示例学习顺序

建议按以下顺序学习：

1. `examples\quick-start`：完成安装、连接和基础控制验证。
2. `examples\lite-learning-course`：按编号学习 USB、Wi-Fi、电机、舵机、传感器、
   状态和实时控制。
3. `docs\SDK_USER_MANUAL.md`：查询完整 API、参数范围、返回对象和安全约束。

电机、舵机等执行器必须满足硬件供电要求。运行控制示例前应架空车轮或移除机械
负载，确保紧急情况下可以立即切断执行器电源。

## 11. 评估包说明

文件名含 `EVALUATION` 的包仅用于内部评估和功能验证。评估证书有有效期，且包内
`VERSION.json` 可能标记为 `development`、`HIL NOT_RUN`。此类包不是正式量产
发布物；对外正式交付前还需要完成硬件在环测试、正式证书签名和发布审批。
