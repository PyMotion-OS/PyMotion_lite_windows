# PyMotion Lite Python SDK

PyMotion Lite 的正式用户 API 统一从 `pymotion` 导入：

```python
import pymotion as pm

lite = pm.lite.connect()
print(lite.device_id)
lite.close()
```

当前 SDK 版本为 1.0.1，支持 CPython 3.10～3.14。正式目标平台为
Windows 10/11 x64、Ubuntu 22.04/24.04 LTS amd64/arm64。当前Ubuntu适配与验收
以PC Ubuntu 24.04 amd64和系统默认的CPython 3.12为主；保留22.04兼容，arm64作为
后续树莓派硬件阶段。

## 安装

用户只能安装经过原生编译、发布签名和完整性校验的对应平台正式交付包。

Windows x64：

```powershell
.\install.bat
```

安装器会自动选择 64 位 CPython 3.10～3.14，并在当前用户目录建立隔离虚拟环境；
也可用 `install.bat -Python C:\Python312\python.exe -VenvPath D:\PyMotionVenv`
明确指定解释器和环境目录。

安装完成后，双击 `open-sdk-vscode.bat` 打开 SDK。该入口会为当前签名包生成独立
VS Code 工作区，并把 Python 扩展和 Code Runner 都固定到安装器创建的 SDK 环境；
首次启动时还会把可编辑示例复制到当前用户的工作区，避免修改签名交付目录。
不要直接从普通 VS Code 窗口使用系统 `python` 运行示例。没有 VS Code 时，可双击
`open-sdk-terminal.bat`，再从已激活的终端运行示例。

Ubuntu：正式包先由管理员独立部署 PyMotion 发布 CA；内部评估包会显示醒目警告，
但不作为正式可信发布。解压对应架构交付包后执行：

```bash
bash ./setup-ubuntu.sh
bash ./open-sdk-vscode.sh
```

`setup-ubuntu.sh` 会一次完成签名校验、SDK 安装、USB udev 规则、`dialout`
用户组配置、示例工作区创建和诊断。必须以普通桌面用户运行，不要在命令
前加 `sudo`；脚本仅在系统包、udev 和用户组步骤中单独请求管理员权限。
如果用户首次被加入 `dialout`，执行后需要拔插设备并完全注销、重新登录。

`setup-ubuntu.sh` 内部调用的 `install.sh` 会检查隔离环境中的 `pip`。如果上次创建环境时因系统缺少
`python3-venv` 而留下半成品，安装器会先将其可恢复地备份为 `.broken-*`，
然后在 Ubuntu 上提示 `sudo` 并安装 `python3-venv`后自动继续。不要用
`sudo bash ./install.sh`；只有系统包安装和 udev 规则需要管理员权限。

安装器会先验证受信任的发布证书、签名清单、全部文件 SHA-256、Python 版本和
平台 wheel，再从签名包内离线安装依赖。`src/` 源码、测试、HIL 验证、历史 wheel
和内部合同不属于用户交付物。

Ubuntu安装完成后运行 `./open-sdk-vscode.sh`。它会使用安装器记录的虚拟环境，
并把可编辑示例复制到当前用户工作区，避免VS Code或Code Runner误用系统Python。

在完整源码仓库中运行 `pymotion_SDK_dev\install.bat` 会自动建立项目 `.venv` 并
挂载 `src/`，此路径只用于授权开发环境，不是产品安装方式。可附加
`-IncludeBuildTools` 安装构建工具，或用 `-Python` / `-VenvPath` 指定解释器和目录。
Ubuntu 22.04/24.04源码环境使用隔离的开发虚拟环境，不要向系统Python安装依赖：

```bash
bash tools/setup_ubuntu_dev.sh --include-build-tools
source .venv/bin/activate
```

当前纯 Python `pymotion_lite-1.10.0-py3-none-any.whl` 仅为历史冻结证据，正式
`1.0.1` 安装器会明确拒绝它。

## 连接与 Token

连接和控制设备需要使用该设备的 Token。Windows PowerShell：

```powershell
$env:PYMOTION_AUTH_TOKEN = "设备的 Token"
```

Ubuntu Bash：

```bash
export PYMOTION_AUTH_TOKEN='设备的 Token'
```

存在多台设备或使用 Wi-Fi 时，还应明确指定设备 ID：

```python
import pymotion as pm

lite = pm.lite.connect(
    "90E5B1D51380",
    transport="wifi",
)
```

也可以通过 `auth_token=` 直接传入 Token。不要把真实 Token 写入准备分享或提交的代码。

## 正式学习入口

- [Quick Start](pymotion_SDK_dev/pymotionlite/01-quick-start/code)：4 个快速入门例程。
- [Lite Learning Course](pymotion_SDK_dev/pymotionlite/02-lite-learning-course/code)：26 个完整课程例程。
- [SDK 用户手册](pymotion_SDK_dev/docs/SDK_USER_MANUAL.md)：正式 API、参数、默认行为和注意事项。
- [SDK 开发诊断手册](pymotion_SDK_dev/docs/SDK_DEVELOPER_DIAGNOSTICS_MANUAL.md)：原始 ADC、状态证据、安全证据、实时任务与字段验证等级；仅供开发联调。
- [功能与老化测试项](pymotion_SDK_dev/docs/PYMOTION_LITE_TEST_ITEMS.md)：已完成测试、代表性证据、覆盖边界和后续老化计划。

Quick Start 和 Lite Learning Course 使用的接口构成当前正式用户 API。`pymotion_lite` 包中的传输、协议和数据解析代码属于 SDK 内部实现，用户程序不应直接依赖。

## Validation

[`validation`](pymotion_SDK_dev/validation) 保存硬件在环验证脚本和证据，用于开发、回归与故障诊断，不属于用户教程或稳定公开 API。

## 通信方式

- USB：自动发现或按设备 ID 选择设备。
- Wi-Fi：应明确指定设备 ID；普通操作由认证 RPC 完成，实时传感器使用持久数据通道，实时命令使用带序号和认证的 UDP 通道。传输选择由 SDK 完成。

USB 与 Wi-Fi 对外使用同一套 `pm.lite` API。连接、认证、控制权、安全停止和实时流的详细用法请参阅用户手册与课程例程。
