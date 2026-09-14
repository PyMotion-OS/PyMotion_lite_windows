# PyMotion Lite Python SDK 用户手册

本文档适用于 `pymotion-lite 1.0.1`，汇总当前面向用户的 Python API、参数范围、默认行为、返回数据和安全注意事项。

正式入口只有：

```python
import pymotion as pm
```

后续全部通过 `pm.lite` 使用。`pymotion_lite` 包中的传输、协议和解析模块属于 SDK 内部实现，用户程序不要直接调用。

## 0. 阅读约定

本文只记录 Quick Start 和 Course 已采用的正式 API。方法签名中的 `/` 之前是仅限位置参数，`*` 之后是仅限关键字参数，`-> 类型` 表示返回对象类型。例如：

```python
pm.lite.connect("90E5B1D51380", transport="wifi")
```

这里 `device_id` 可以按位置传入；`transport`、`timeout` 等必须写出参数名。关键字参数写出名称后，彼此没有顺序要求。形如 `参数=None` 或 `timeout=5.0` 的内容是默认值，不是必须原样填写的文字。

文档中的字段表遵循以下规则：

- 标为“用户字段”的表格列出应用程序可以依赖的稳定字段。设备内部可能携带额外协议证据，但它们不是正式用户合同。
- `None` 表示设备没有提供、当前无效或不能确认，不能当作数字 0。
- 控制方法未注明返回对象时，成功返回 `None`，失败抛出 `pm.lite.LiteError` 的具体子类或参数校验异常。
- 电机、PWM 舵机和 GPIO 均使用板上印刷编号；M1～M4、S1～S6 不需要用户手工加 1。
- 带 `max_age` 的读取会拒绝超过允许年龄的数据；带 `timeout` 的参数限制本次等待时间，两者含义不同。

## 1. 安装与首次连接

### 1.1 环境要求

- CPython 3.10～3.14。
- Windows 10/11 x64，或 Ubuntu 22.04/24.04 LTS amd64/arm64。当前优先验收
  Ubuntu 24.04 PC amd64及其系统默认CPython 3.12，保留22.04兼容。
- USB 通信需要可用的串口驱动。
- Wi-Fi 通信要求电脑与设备处于可互通的局域网，并允许设备访问电脑的 SDK 服务端口（默认 TCP 8787）。
- 电机、舵机等负载应使用满足硬件要求的外部电源；USB 供电不能替代执行器电源。

用户应解压与操作系统、CPU 架构匹配的正式 SDK 交付包并运行签名安装器。

Windows：

```powershell
.\install.bat
```

Windows 安装器会自动选择 64 位 CPython 3.10～3.14，并在当前用户目录建立隔离
虚拟环境。需要固定解释器或安装位置时，可使用
`install.bat -Python C:\Python312\python.exe -VenvPath D:\PyMotionVenv`。

安装完成后应双击 `open-sdk-vscode.bat` 打开示例。该入口生成与当前签名包对应的
独立 VS Code 工作区，将示例复制到用户目录，并为 Python 扩展和 Code Runner 配置
安装器实际创建的解释器；编辑工作区副本不会破坏交付包的签名和文件哈希。
直接在普通 VS Code 窗口点击 Code Runner 的“Run Code”可能调用系统 Python，导致
`ModuleNotFoundError: No module named 'pymotion'`。不使用 VS Code 时，可双击
`open-sdk-terminal.bat` 后在已激活的 SDK 终端运行示例。

Ubuntu（正式包的发布 CA 必须由管理员提前独立部署；内部评估包不代表正式可信发布）：

```bash
bash ./setup-ubuntu.sh
bash ./open-sdk-vscode.sh
```

`setup-ubuntu.sh` 会完成签名校验、SDK 安装、udev 规则安装、`dialout` 用户组
配置、示例工作区创建和诊断。以普通桌面用户运行它，不要在整条命令前
加 `sudo`。首次加入 `dialout` 后，必须拔插设备并完全注销、重新登录。

Ubuntu 安装器会自动检查虚拟环境中的 `pip`。如果检测到上次因
缺少 `python3-venv` 而留下的半成品环境，它会先备份该环境，必要时
通过 `sudo apt-get` 安装系统的 `python3-venv`，然后继续离线安装 SDK。
请始终以普通用户执行 `bash ./install.sh`，不要对整个安装器使用 `sudo`。

Ubuntu的VS Code入口会打开用户目录中的示例副本，并同时固定Python扩展与Code Runner
所使用的解释器；不要从普通VS Code窗口直接使用系统Python运行SDK示例。

安装器会在写入 Python 环境前验证发布证书、签名清单、文件哈希、Python 版本和
原生 wheel 平台标签。不要安装来源不明或完整性校验失败的 wheel。

### 1.2 首次初始化与 AP 配网

全新设备先完成一次初始化：

1. 给设备上电，电脑连接 `PyMotion-Lite-XXXX` 热点；出厂热点密码为 `pymotionlite`。
2. 若热点没有出现，在设备运行时单次按下并释放板上的 `CFG` 按键，等待设备重启并进入 AP 配网模式。
3. 浏览器打开 `http://192.168.4.1:8787/wifi/setup`，填写 2.4 GHz Wi-Fi 名称、Wi-Fi 密码和设备 Token。
4. “服务器地址”首次不会预填某台电脑的地址。请填写运行 SDK 的电脑在目标局域网中的地址，例如 `http://192.168.1.100:8787`；电脑 IP 改变后应重新配网更新。
5. 若要修改设备自己的 AP 热点密码，必须连续输入两遍相同的新密码；不修改时保持两个密码框为空。
6. 保存并连接，等待设备加入目标局域网。

Wi-Fi 密码、Token 和新热点密码在页面中均采用密码输入框，不会明文显示。修改热点密码只是更改下一次进入 AP 配网模式时使用的密码，不等于恢复出厂设置。

### 1.3 Token

设备连接需要使用与设备一致的 Token。Token 可以直接传给 `connect()`，也可以放入当前终端的环境变量。

Windows PowerShell：

```powershell
$env:PYMOTION_AUTH_TOKEN = "设备的 Token"
```

Ubuntu Bash：

```bash
export PYMOTION_AUTH_TOKEN='设备的 Token'
```

Python：

```python
import pymotion as pm

with pm.lite.connect(auth_token="设备的 Token") as lite:
    print(lite.connection.device_id)
```

Wi-Fi Token 必须为 1～16 个 UTF-8 字节。Token 不匹配时会抛出 `AuthenticationError`。

### 1.4 USB 连接

```python
import pymotion as pm

with pm.lite.connect(
    transport="usb",
    timeout=15.0,
) as lite:
    print(lite.connection.device_id)
    print(lite.connection.transport)
```

只有一台设备时，`device_id=None` 可以自动选择。连接多台设备时，应明确传入设备 ID：

```python
with pm.lite.connect(
    "90E5B1D51380",
    transport="usb",
) as lite:
    pass
```

### 1.5 Wi-Fi 连接

```python
import pymotion as pm

with pm.lite.connect(
    "90E5B1D51380",
    transport="wifi",
    auth_token="设备的 Token",
    timeout=8.0,
) as lite:
    print(lite.connection.transport)  # wifi
```

Wi-Fi 连接不要求预先通过 USB 保存设备 ID。未传 `device_id` 时，SDK 以通过 Token/HMAC 认证并首先建立会话的设备所报告的 ID 为准；显式传入 12 位设备 ID 时，SDK 仍会在握手结束时校验实际设备是否一致。多台设备同时在线时，建议为每台设备配置不同 Token，并在运行前设置目标设备对应的 Token。

Wi-Fi 模式下，设备会按配网时保存的服务器地址连接电脑上的 SDK 服务。电脑局域网 IP 改变、防火墙阻止 TCP 8787 或两端网络互相隔离时，Wi-Fi 连接会超时；此时应先更新配网地址和防火墙规则。传感器持久数据通道由 SDK 再主动连接设备的 TCP 8789，不要求额外开放电脑入站端口。

### 1.6 `connect()` 完整签名

```python
pm.lite.connect(
    device_id=None,
    *,
    timeout=15.0,
    auth_token=None,
    transport="usb",
    wifi_host="0.0.0.0",
    wifi_port=8787,
)
```

最简写法就是：

```python
lite = pm.lite.connect()
```

它等价于选择 USB、连接总时限 15 秒，并自动选择设备。只有一台可用设备时无需填写 `device_id`；发现多台设备时会抛出 `MultipleDevicesFoundError`，此时必须明确填写设备 ID。`auth_token=None` 表示从环境变量 `PYMOTION_AUTH_TOKEN` 读取，而不是跳过认证。`wifi_host` 和 `wifi_port` 只在 `transport="wifi"` 时参与连接。

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `device_id` | `None` | 设备 ID；多设备或 Wi-Fi 使用时建议明确填写 |
| `timeout` | `15.0` 秒 | SDK 发现、认证、握手、首份状态和能力确认共享的总时限 |
| `auth_token` | `None` | 设备 Token；省略时读取 `PYMOTION_AUTH_TOKEN` |
| `transport` | `"usb"` | `"usb"` 或 `"wifi"` |
| `wifi_host` | `"0.0.0.0"` | Wi-Fi 本机监听地址，通常无需修改 |
| `wifi_port` | `8787` | Wi-Fi 本机监听端口，范围 1～65535 |

`connect()` 只建立连接，不申请控制权，也不会让执行器动作。

### 1.7 发现设备

```python
devices = pm.lite.list_devices(timeout=6.25)

for device in devices:
    print(device.device_id)
    print(device.transports)
    print(device.preferred_transport)
```

`list_devices()` 只发现设备，不需要 Token。默认扫描 6.25 秒，同时查找 USB 和 Wi-Fi，并按设备 ID 合并；同一设备同时存在两种链路时，`preferred_transport` 优先为 `usb`。

`LiteDeviceInfo` 完整字段和属性：

| 字段/属性 | 类型 | 含义 |
| --- | --- | --- |
| `device_id` | `str` | 12 位设备 ID |
| `transports` | `tuple[str, ...]` | 当前发现到的链路，元素为 `usb`、`wifi` |
| `usb_port` | `str \| None` | USB 串口名称；未发现 USB 时为 `None` |
| `wifi_address` | `str \| None` | 设备局域网地址；未发现 Wi-Fi 时为 `None` |
| `wifi_port` | `int \| None` | 设备 Wi-Fi 服务端口；未发现 Wi-Fi 时为 `None` |
| `preferred_transport` | `str`，只读属性 | 同时存在两种链路时返回 `usb`，否则返回现有链路 |

## 2. 连接对象与生命周期

推荐始终使用 `with`：

```python
with pm.lite.connect() as lite:
    print(lite.closed)       # False
    print(lite.connection)

print(lite.closed)           # True
```

也可以手动关闭：

```python
lite = pm.lite.connect()
try:
    print(lite.connection.device_id)
finally:
    lite.close()
```

`close()` 可以重复调用。关闭后，原来取得的电机、舵机等对象也不能继续使用。

`lite.connection` 用于确认当前连接对象。用户程序只应依赖以下稳定属性：

| 字段/属性 | 类型 | 含义 |
| --- | --- | --- |
| `device_id` | `str` | 当前设备 ID |
| `transport` | `str` | 当前实际链路：`usb` 或 `wifi` |

启动周期、内部端点、状态结构版本和各处理器固件信息供 SDK 协商及开发诊断使用，不作为用户业务逻辑的稳定字段。

## 3. 控制权与通用安全规则

所有会改变电机、舵机或数字输出的操作都应放在控制上下文中：

```python
with pm.lite.connect() as lite:
    with lite.control(timeout=5.0):
        lite.motor(1).set_speed(20, duration=1.0)
```

控制上下文会维护控制心跳，并在退出时执行停止和释放。一个连接只能存在一个控制上下文，不支持嵌套：

```python
with lite.control():
    # 这里再次 with lite.control() 会抛出 ControlUnavailableError
    pass
```

通用规则：

- 端口号、舵机 ID 和电机号在公开 API 中均从 1 开始。
- 带 `duration` 的普通控制方法会阻塞当前 Python 线程，时间到后停止对应输出。
- 不带 `duration` 的命令会持续生效，直到下一条命令、显式停止、安全事件或控制上下文退出。
- 命令被确认只表示设备接受了命令，不等于已经由独立传感器确认机械体完全停止或到位。
- 对执行结果不确定的运动命令，不要直接重复发送；先停止并检查状态。

## 4. 数字输出

当前允许用户控制的板卡输出 GPIO：

```python
pm.lite.DIGITAL_OUTPUT_GPIOS
# (9, 10, 14, 38, 39, 40)
```

示例：

```python
with pm.lite.connect() as lite:
    io14 = lite.digital_output(14)

    with lite.control():
        io14.set_high()
        io14.set_low()
```

接口：

- `lite.digital_output(gpio)`：取得白名单 GPIO 对象。
- `output.gpio`：GPIO 编号。
- `output.set_high()`：输出高电平。
- `output.set_low()`：输出低电平。

数字输出仅提供高、低电平，不提供输入、PWM、上拉或中断配置。控制释放、急停或安全事件会把用户数字输出恢复为低电平。

## 5. 直流电机

### 5.1 取得电机对象

```python
motor = lite.motor(1)   # M1；范围 M1～M4
print(motor.port)       # 1
```

当前版本的电机支持边界必须先说明：官方闭环参数只针对当前已经完成实测的标配电机，
其默认编码器参数为 PPR 13、减速比 20.0。SDK 当前没有向用户公开电机 PI/PID、前馈、
输出限制或加减速参数调节接口。因此，更换其他型号电机后，即使正确填写 PPR 和减速比，
也不能认为闭环 RPM、位置控制或里程计已经可用。当前发布版本只承诺标配测试电机的
闭环功能。

其他型号电机在额定电压、电流、驱动能力和接线均符合要求时，可以先用
`set_speed()` 做低速、架空的开环验证；开环百分比不是实际转速，也不代表该型号已经
得到产品支持。需要正式支持新电机时，必须先增加闭环参数配置或对应固件参数组，再完成
转速阶跃、正反转、堵转/饱和、位置和底盘实测。

### 5.2 开环速度百分比

```python
with lite.control():
    motor.set_speed(30)                 # 持续运行
    motor.set_speed(-30, duration=1.0)  # 反向运行 1 秒后停止
    motor.stop()
```

`motor.set_speed(speed, duration=None)`：

- `speed`：`-100～100`，单位为百分比。
- 正负号表示方向，绝对值表示输出比例。
- `speed=0` 等价于停止本路电机。
- 调用后使用开环模式；如果电机此前处于闭环 RPM 模式，会切回开环。

### 5.3 闭环 RPM

本节只适用于当前已测试的标配电机。`-360～360 RPM` 是接口允许范围，不表示任意电机
接上后都能在整个范围内稳定达到目标。

```python
with lite.control():
    motor.set_rpm(120)
    print(motor.status().measured_rpm)
    motor.stop()
```

`motor.set_rpm(rpm, duration=None)`：

- `rpm` 必须为整数，范围 `-360～360 RPM`。
- 直接请求设备进入闭环模式，然后写入目标 RPM；不会为了准备模式先读取一次电机状态。
- 重复设置闭环模式是幂等操作；编码器能力、设备故障和安全状态仍由固件校验并拒绝无效命令。
- 不带 `duration` 时持续保持目标 RPM。
- 带 `duration` 时运行指定时间，之后把目标 RPM 设为 0；电机仍保持闭环模式。
- `motor.stop()` 把当前模式的目标设为 0，不主动更改控制模式。

多路闭环 RPM 使用批量接口：

```python
with lite.control():
    lite.motors.set_rpms({
        1: 120,
        2: 120,
        3: -80,
        4: -80,
    }, duration=2.0)
```

`lite.motors.set_rpms(rpms, duration=None)`：

- 接受 1～4 路非空映射，端口为 M1～M4，RPM 均为整数 `-360～360`。
- 只使用一次 USB/Wi-Fi 主机 RPC；设备先准备所有指定端口的闭环模式，再写入各路目标。
- 设备内部仍会依次应用各路目标，因此不是硬件级原子同步，但不会产生多次 Wi-Fi 请求造成的明显间隔。
- `duration` 到时后逐路停止所列端口，端口继续保留闭环模式。
- 任一路准备或写入失败时，设备请求聚合停止，避免只留下部分电机运行。
- 这是低频闭环目标接口；需要连续高频更新时，使用实时命令流的 `motor_rpms` 目标。

### 5.4 多电机开环控制

```python
with lite.control():
    lite.motors.set_speeds({
        1: 30,
        2: 30,
        3: -20,
        4: -20,
    }, duration=2.0)

    lite.motors.stop()
```

- `set_speeds()` 接受 1～4 路非空字典。
- 速度范围仍为 `-100～100%`。
- 如果目标端口之前由 `set_rpm()` 保持在闭环模式，SDK 会在设备拒绝首次批量命令后识别这些端口、切回开环并完整重试一次。
- SDK 使用一条批量请求提交目标，但设备内部仍会逐路应用，因此不保证四路在完全相同的物理时刻改变。
- 中途失败时 SDK 会尝试停止本次涉及的电机。

### 5.5 位置控制

位置控制依赖编码器比例和电机闭环参数同时正确，当前同样只承诺标配测试电机。

先建立当前位置零点，再执行位置运动：

```python
with lite.control():
    motor.zero_position()
    result = motor.move_to(
        360,
        speed=20,
        tolerance=2,
        timeout=8.0,
    )
    print(result.completed, result.verified)

    motor.move_by(-90, speed=15)
```

接口与范围：

| API | 参数与语义 |
| --- | --- |
| `zero_position()` | 电机静止且编码器有效时，把当前位置设为 0° |
| `move_to(angle, ...)` | 移动到相对零点的绝对角度 |
| `move_by(angle, ...)` | 从当前位置移动指定相对角度 |

零点保留在设备本次运行的 RAM 中。需要更换零点时，让电机静止后再次调用
`zero_position()`；SDK 不公开“清除零点”接口。该零点只用于位置角度参考，不改变
`set_speed()` 的开环百分比控制和 `set_rpm()` 的闭环转速控制。

位置命令参数：

- `angle`：`-3600～3600°`。
- `speed`：默认 `20`，范围 `(0, 100]`。
- `tolerance`：默认 `2°`，范围 `(0, 30]`。
- `timeout`：默认 `8.0` 秒，范围 `0.1～60` 秒。
- 位置命令为阻塞调用，返回 `MotionResult(completed, verified)`。

### 5.6 电机状态

```python
state = motor.status(max_age=0.5)

print(state.port)
print(state.control_mode)
print(state.commanded_speed)
print(state.target_rpm)
print(state.measured_rpm)
print(state.encoder_count)
```

`max_age` 默认 0.5 秒，允许范围 0～10 秒；设为 0 表示要求最新状态。

`MotorState` 完整基础字段和属性：

| 字段/属性 | 类型 | 含义 |
| --- | --- | --- |
| `port` | `int` | 产品端口号 1～4 |
| `control_mode` | `str` | `open_loop` 或 `closed_loop` |
| `has_encoder` | `bool` | 当前端口是否声明编码器能力 |
| `commanded_speed` | `float \| None` | 开环目标百分比；闭环时为 `None` |
| `target_rpm` | `float \| None` | 闭环目标 RPM；开环时为 `None` |
| `measured_rpm` | `float \| None` | 编码器实测 RPM；无编码器能力时为 `None` |
| `encoder_count` | `int \| None` | 当前启动周期内累计编码器计数；可正可负 |
| `controller_enabled` | `bool` | 当前电机控制器是否启用 |
| `running` | `bool` | 设备报告的“命令或实测速度非零”状态；不是堵转判断 |
| `output_saturated` | `bool` | 闭环输出是否已经达到可用输出上限 |
| `age_s` | `float` | 状态样本年龄，秒 |
| `feedback_valid` | `bool`，只读属性 | 位置反馈是否有效；普通状态能力不足时为 `False` |
| `actual_angle` | `float \| None`，只读属性 | 相对软件零点的输出轴角度；未设零点或不可用时为 `None` |
| `fault` | `str \| None`，只读属性 | 位置控制故障；没有时为 `None` |

支持位置状态的固件返回对象还增加两个公开字段：`zeroed: bool` 表示软件零点是否已建立，`position_active: bool` 表示位置运动是否正在执行。读取前可先用 `hasattr(state, "zeroed")` 判断当前固件是否提供。

`has_encoder=True` 表示端口具备编码器能力，不等于能够独立判断编码器线缆一定正常；`running` 也不是堵转检测结果。

读取全部电机：

```python
states = lite.motors.status(max_age=0.5)
for port, state in states.items():
    print(port, state.measured_rpm)
```

### 5.7 编码器参数与配置边界

当前正式 API 已公开编码器参数读取和设备本次启动期间的临时配置。所有产品端口都使用板上印刷编号 M1～M4，不需要换算为内部通道号。

读取单路当前配置不需要控制权：

```python
motor = lite.motor(1)
config = motor.encoder.configuration()

print(config.ppr)
print(config.gear_ratio)
print(config.counts_per_revolution)
```

按照电机或编码器铭牌设置 PPR 和减速比：

```python
with lite.control():
    actual = motor.encoder.configure(
        ppr=13,
        gear_ratio=20.404,
    )
```

设备按照 `PPR × 4 × gear_ratio` 计算输出轴每圈计数，并将减速比量化到 0.001。SDK 会在写入后立即回读；回读值与请求不一致时抛出 `ProtocolError`，不会把仅收到写入 ACK 当作配置成功。

已通过实测得到输出轴每圈计数的高级用户，也可以直接配置计数：

```python
with lite.control():
    actual = motor.encoder.configure_counts(
        counts_per_revolution=1061,
    )
```

两个配置方法互相替代，不要同时使用。`configure()` 保留铭牌 PPR 和减速比；`configure_counts()` 只保留实测每圈计数，因此其返回对象的 `ppr` 和 `gear_ratio` 为 `None`。

`EncoderConfiguration` 完整字段：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `port` | `int` | 产品端口号 1～4 |
| `source` | `str` | `nameplate` 表示由 PPR/减速比推导；`counts` 表示直接指定每圈计数 |
| `ppr` | `int \| None` | 铭牌配置时为 1～65535；直接计数配置时为 `None` |
| `gear_ratio` | `float \| None` | 铭牌配置时为 0.001～1000.000；直接计数配置时为 `None` |
| `counts_per_revolution` | `int` | 输出轴每圈四倍频计数，范围 1～1000000 |
| `persistent` | `bool` | 当前实现始终为 `False`；设备重启后恢复固件默认值 |

写配置需要 `with lite.control():`。设备在修改比例前会停止目标电机；调用前仍应确保机械机构处于安全状态。配置改变以后，闭环 RPM、位置角度和里程计距离都会采用新比例。若配置发生实际变化，应重新建立位置零点，并重新开始需要连续性的里程计任务。

编码器反馈和依赖编码器的控制能力包括：

- `motor.status()`：读取 `has_encoder`、`measured_rpm` 和 `encoder_count`。
- `motor.set_rpm()`：使用编码器执行闭环转速控制。
- `zero_position()`、`move_to()`、`move_by()`：使用编码器执行输出轴位置控制。
- `lite.odometry`：使用选定左右轮的编码器累计距离。

编码器相关术语：

| 名称 | 含义 |
| --- | --- |
| `PPR` | 编码器输入轴每转、每相输出的脉冲数（以电机/编码器铭牌为准） |
| 四倍频 | 对 A/B 两相信号的上升沿和下降沿都计数，因此一圈计数是基础脉冲数的 4 倍 |
| `gear_ratio` | 电机轴到输出轴的减速比 |
| 输出轴每圈计数 | `PPR × 4 × gear_ratio`；设备会按固件的整数规则量化 |
| `encoder_count` | 从当前启动/计数基准开始累积的有符号计数，不是角度值 |

当前边界仍需明确：

- 编码器方向仍由设备固件按固定硬件接线管理，尚无运行时用户 API；方向会同时影响闭环 RPM、位置控制和里程计，不能只为改变显示正负号而翻转。
- `motor.status().encoder_count` 可以读取累计计数，但没有任意写入或清零原始累计计数的 API；`zero_position()` 建立的是位置控制软件零点。
- 编码器配置只解决转速、角度和距离的换算比例，不会自动调整不同电机所需的 PI/PID、前馈、输出限制和加减速参数。
- 当前没有公开上述闭环参数的用户调节 API；非标配电机只能把开环低速试运转作为接线和基本驱动检查，不能使用或宣称闭环 RPM、位置控制及里程计已经受支持。
- `lite.odometry.configure()` 仍只配置左右轮端口、轮径和轮距；应先配置电机编码器，再配置底盘几何参数。

## 6. PWM 舵机

同一个物理 PWM 端口可以接连续旋转舵机或位置舵机，但 SDK 无法自动识别型号。
两种类型统一通过 `lite.pwm_servo(port, mode=...)` 获取；`mode` 必须与实际硬件一致，
可以填写字符串 `"speed"`、`"position"`，也可以使用 `PwmServoMode` 枚举。

### 6.1 连续旋转 PWM 舵机

```python
servo = lite.pwm_servo(1, mode="speed")  # S1～S6

with lite.control():
    servo.set_speed(40, duration=1.0)
    servo.stop()
```

- `set_speed(speed, duration=None)`：`-100～100%`。
- `stop()` 会关闭本路 PWM 输出，不是发送 1500 μs 中立脉冲。
- 带 `duration` 时，时间到后关闭本路输出。
- 因此正常执行完带 `duration` 的调用后不必再调用 `stop()`；在异常处理、提前退出或不带 `duration` 的持续控制结束时显式调用，可让清理意图更清楚。

多路控制：

```python
with lite.control():
    lite.pwm_servos.set_speeds(
        {1: 30, 2: -30},
        duration=2.0,
    )
    lite.pwm_servos.stop()
```

多路速度由 SDK 按端口依次下发，不保证原子同步。

### 6.2 位置 PWM 舵机

```python
servo = lite.pwm_servo(2, mode="position")

with lite.control():
    servo.move_to(90)
    servo.stop()
```

- `move_to(angle)`：范围 `0～180°`，只发送目标角度。
- PWM 协议不提供运动时间参数；如需等待观察，可在用户程序中使用 `time.sleep()`，但等待结束不代表有到位反馈。
- 普通 PWM 位置舵机没有位置回传，因此 SDK 只能确认目标已下发，不能确认实际到达角度。
- `stop()` 会关闭 PWM，舵机不再主动保持目标角度。
- 位置模式调用 `set_speed()`、连续旋转模式调用 `move_to()` 会在发送前直接报错。

多路角度：

```python
with lite.control():
    lite.pwm_servos.move_to({
        1: 0,
        2: 45,
        3: 90,
        4: 135,
        5: 180,
        6: 90,
    })
```

设备会逐路应用角度，不承诺机械上的绝对同步。若操作中途失败，SDK 会尝试关闭本次列出的端口。

### 6.3 状态与统一多路对象

```python
speed_servo = lite.pwm_servo(1, mode="speed")
position_servo = lite.pwm_servo(2, mode="position")

single = position_servo.status(max_age=0.5)
all_ports = lite.pwm_servos.status(max_age=0.5)
print(single.port, single.mode, single.output_enabled)
print(all_ports[1], all_ports[2])
```

- `lite.pwm_servos` 同时提供 `set_speeds()`、`move_to()`、`stop()` 和 `status()`，不再按位置/速度拆成两套批量对象。
- `status()` 是只读操作，不需要控制权；`max_age` 范围为 `0～10` 秒。
- `mode` 来自本次连接中创建对象或执行批量命令时的用户声明，SDK 不会自动识别实际接入的舵机类型。
- `PwmServoState` 只有 `port`、`mode`、`commanded_angle_deg`、`commanded_speed` 和 `output_enabled`。它描述最近命令与输出开关，不把目标角度误称为实测角度。

## 7. TTL 总线舵机

当前正式支持飞特 `SCS0002` 和 `SCS125`。用户只填写舵机 ID；SDK 首次创建对象时读取版本指纹、识别型号并缓存结果，不再要求用户选择型号。`mode` 默认是位置模式，需要连续旋转时才显式填写 `"speed"`：

```python
position_servo = lite.ttl_servo(1)
speed_servo = lite.ttl_servo(2, mode="speed")
```

范围与默认行为：

- ID：1～253。
- `mode="position"` 是默认值；位置模式调用 `move_to()`，速度模式调用 `set_speed()`。公开 API 不使用底层协议的 `motor` 名称。
- SDK 自动识别后，`SCS0002` 允许 `0～270°`，`SCS125` 允许 `0～220°`；越界命令会在发包前被拒绝。
- 正常运行统一使用 `500000` 波特率；位置模式使用 `0～1023` 原始限位，速度模式在底层按飞特协议使用 `0/0` 限位。其他非标准端点配置会提示先执行配置，而不是在运动时产生含糊的通信错误。
- `servo.model` 是自动识别后的只读 `TtlServoModel`，仅用于查看结果，不能在构造对象时手工指定。

### 7.1 新舵机首次配置

新购舵机或 ID、波特率、限位状态未知时，必须逐只配置：

```python
with lite.control():
    result = lite.ttl_servos.configure(new_id=1)

print(result.model, result.id, result.baudrate, result.verified)
```

调用前必须执行以下步骤：

1. 完全断开设备和舵机电源，禁止带电插拔；
2. TTL 总线上只连接一只待配置舵机；
3. 接通稳定的外部舵机电源并等待设备启动；
4. 取得控制权后调用 `configure(new_id=...)`；
5. 成功后断电，取下并标记舵机，再配置下一只；
6. 所有舵机 ID 唯一后，断电并将它们串联使用。

配置过程会自动尝试两种已知出厂波特率（`500000`、`1000000`），识别支持的型号，设置目标 ID，并把运行波特率和位置限位统一为 `500000`、`0～1023`，最后重新读取并校验。它会写舵机非易失配置，只用于安装或维护，不得放入循环中反复调用。

`TtlServoConfigurationResult` 字段：

| 字段 | 含义 |
| --- | --- |
| `old_id` / `id` | 配置前 ID / 配置后的目标 ID |
| `model` / `max_angle` | 自动识别型号及其最大机械角度 |
| `baudrate` | 校验后的运行波特率，成功时为 `500000` |
| `min_position` / `max_position` | 校验后的原始限位，成功时为 `0` / `1023` |
| `verified` | ID、波特率、限位和型号是否已完整读回确认 |

若总线上有两只相同 ID 的舵机，它们会同时应答，协议无法区分“哪一只是新接入的”。因此配置接口不支持多只舵机同时接入，也不提供任意寄存器写入能力。通信中断或指纹不在支持白名单时会报错，不应把舵机当作已经配置成功。

### 7.2 位置模式

```python
with lite.control():
    position_servo.move_to(135, duration=1.0)
    status = position_servo.status()
    print(status.angle_deg, status.online)
```

- 仅 `POSITION` 模式可以调用 `move_to()`。
- `servo.max_angle` 是自动识别型号对应的最大角度；角度范围为 `0～servo.max_angle`。
- `duration` 是舵机原生运动时间，不是 Python 端等待后再停止；允许 `0.001～65.535` 秒。

### 7.3 速度模式

```python
with lite.control():
    speed_servo.set_speed(30, duration=1.0)
    speed_servo.stop()
```

- 仅 `mode="speed"` 的对象可以调用 `set_speed()`。
- 速度范围 `-100～100%`。

### 7.4 模式读取和配置

```python
actual_mode = position_servo.read_mode()

with lite.control():
    position_servo.configure_mode()
```

`configure_mode()` 会把对象声明的模式写入舵机。实际发生模式变化时可能写入舵机非易失存储器，不应放在高频循环中反复调用，也不应把模式切换当作运动控制命令。

SCS0002 和 SCS125 的速度模式在底层使用飞特协议的电机模式，允许连续旋转；位置反馈只包含当前角度周期内的原始计数，不包含可靠的完整圈数。舵机在速度模式下越过位置模式的有效角度区间以后，再切回位置模式时可能重新寻找规范区间并产生较大转动；即使切换前后的原始位置数字相同，也不能据此认定机械位置属于同一个角度周期。因此：

- 正常应用应为每只舵机固定选择位置模式或速度模式，不在动作流程中来回切换。
- 必须切换时，先拆除连杆并清空完整活动范围；不能承诺切回位置模式后保持速度模式停止位置。
- 位置模式程序应先以较长运动时间到达一个已知安全角度，再开始后续位置动作。
- 当前公开 API 不提供 SCS0002/SCS125 机械零点校准。通用 SCS 协议虽然定义了 `0x0B` 位置校准指令，但本项目资料的支持型号表未包含这两款 SCSCL 舵机，不应发送未经型号确认的校准命令。

`status()` 返回的 TTL 状态完整字段：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `online` | `bool` | 本次读取是否收到舵机响应 |
| `id` | `int` | TTL 舵机 ID |
| `angle_deg` | `float` | 由原始位置计数换算的角度，显示精度限制为两位小数 |
| `voltage_v` | `float \| None` | 舵机反馈电压；型号或本次反馈不支持时为 `None` |
| `temperature_c` | `float \| None` | 舵机反馈温度；不支持时为 `None` |
| `moving` | `bool` | 舵机反馈的运动标志 |
| `fault_code` | `int` | 舵机故障码；0 表示没有报告故障 |
| `model` | `str` | 解析时使用的型号：`scs0002` 或 `scs125` |
| `raw_position` | `int \| None` | 原始位置计数；未取得位置反馈时为 `None` |
| `feedback_valid` | `frozenset[str]` | 本次真正有效的反馈项，可包含 `position`、`voltage`、`temperature`、`moving` |

`online=True` 不代表每一个可选反馈字段都有效；判断电压、温度或位置时，应同时检查相应值是否为 `None` 或是否出现在 `feedback_valid` 中。

### 7.5 TTL 批量控制

```python
with lite.control():
    lite.ttl_servos.move_to({
        position_servo: 90,
    }, duration=1.0)

    lite.ttl_servos.set_speeds({
        speed_servo: 20,
    }, duration=1.0)

    lite.ttl_servos.stop()
```

批量接口一次支持 1～8 个同一连接中的 TTL 对象，并使用总线同步写。这里的 8 是单次 SDK 批量命令和实时订阅的上限，用于约束总线占用时间和一帧数据量，并不是 TTL 协议只能存在 8 个 ID；更多舵机需要按不超过 8 个分批控制。`ttl_servos.stop()` 只停止当前连接中已经登记使用的 TTL ID。

`lite.ttl_servos.status()` 会读取本连接中已经创建或配置的 TTL 舵机，返回只读的 `ID -> BusServoStatus` 映射；它不需要控制权。若尚未创建或配置任何 TTL 对象，则返回空映射。

## 8. 传感器快照

### 8.1 一次读取多个来源

```python
observation = lite.observe(
    max_age=0.5,
    refresh=True,
)

print(observation.imu)
print(observation.ultrasonic)
print(observation.line_tracker)
print(observation.ambient_light)
print(observation.color)
```

`lite.observe()`：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `max_age` | `0.5` 秒 | 允许的数据年龄，范围 0～10 秒 |
| `refresh` | `True` | `True` 请求一次新快照；`False` 复用缓存 |
| `timeout` | `None` | 本次读取超时；`None` 使用连接默认值 |
需要多种传感器的同一代数据时，调用一次 `observe()` 再取各字段，不要连续调用多个便利方法。

### 8.2 单传感器便利方法

```python
imu = lite.imu(max_age=0.5)
ultrasonic = lite.ultrasonic(max_age=0.5)
line = lite.line_tracker(max_age=0.5)
light = lite.ambient_light(max_age=0.5)
color = lite.color(max_age=0.5)
```

每个便利方法都会单独取得一次快照，适合只需要一种数据的程序。

### 8.3 数据单位

| 传感器 | 主要字段 | 单位/含义 |
| --- | --- | --- |
| IMU | `acceleration_mm_s2` | mm/s² |
| IMU | `angular_velocity_rad_s` | rad/s |
| IMU | `orientation_deg.roll/pitch` | 度；不提供温度 |
| 超声波 | `distance_mm` | mm |
| 五路循迹 | `levels` | 5 路原始 0/1 电平 |
| 五路循迹 | `detected` | 按 `black_is_low` 换算的检测结果 |
| 环境光 | `illuminance_lux` | lux |
| 颜色 | `red/green/blue/clear` | RGBC 原始计数，不是校准后的颜色名称 |

### 8.4 有效性

每个读数都提供三个统一的有效性属性：

```python
if imu.valid:
    print(imu.orientation_deg)
else:
    print("IMU state:", imu.state)
```

`state` 是下列固定小写字符串之一：

- `"valid"`：数据有效，`valid=True`。
- `"no_echo"`：超声波未收到回波，通常表示目标超出量程或没有合适反射面，不是通信故障。
- `"stale"`：数据年龄超过 `max_age`。
- `"unavailable"`：传感器未安装、未启用或当前不可用。
- `"error"`：传感器报告错误。

只有 `valid=True` 时，数值字段才应参与业务计算。`age_s` 是样本年龄（秒），无法确定时为 `None`。来源序号、底层错误码和链路证据属于开发诊断，不进入用户读数对象。

### 8.5 传感器返回对象完整字段

`SensorObservation`：

| 字段 | 类型 | 含义 |
| --- | --- | --- |
| `imu` | `ImuReading` | IMU 读数 |
| `ultrasonic` | `UltrasonicReading` | 超声波读数 |
| `line_tracker` | `LineTrackerReading` | 五路循迹读数 |
| `ambient_light` | `AmbientLightReading` | 环境光读数；未安装时对象仍存在但 `valid=False` |
| `color` | `ColorReading` | 颜色读数；未安装时对象仍存在但 `valid=False` |

所有具体传感器读数都含 `valid`、`state`、`age_s`，并含下列测量字段：

| 返回类型 | 测量字段 |
| --- | --- |
| `UltrasonicReading` | `distance_mm`；只读别名 `distance` 与它相同 |
| `ImuReading` | `acceleration_mm_s2`、`angular_velocity_rad_s`、`orientation_deg` |
| `LineTrackerReading` | `levels`、`detected`、`black_is_low` |
| `AmbientLightReading` | `illuminance_lux` |
| `ColorReading` | `chip_id`、`clear`、`red`、`green`、`blue` |

IMU 的加速度和角速度是带 `x`、`y`、`z` 的三维向量；姿态对象只有 `roll`、`pitch`，当前不提供 yaw。读数无效时，上述可选测量字段为 `None`，不要使用上一次数值自行冒充本次有效读数。

## 9. 电源测量

### 9.1 用户电源接口

```python
power = lite.power(max_age=1.0)

print(power.motor_1_2_current)  # A，M1/M2 共用供电组
print(power.motor_3_4_current)  # A，M3/M4 共用供电组
print(power.pwm_servo_current)  # A，S1～S6 共用供电组
print(power.battery_voltage)    # V
```

当前板卡只提供以上四项真实电源测量：

- M1/M2 供电组电流，不是两路分别测量。
- M3/M4 供电组电流，不是两路分别测量。
- S1～S6 PWM 舵机供电组总电流。
- 电池电压。

TTL 舵机没有单独公开的电流测量。电流值是约 1 秒平均值，并在用户接口中规范为非负数。某项无有效数据时返回 `None`，不是虚构的 0。

电池测量当前上限为约 12.5 V；读数恰好长期停在上限时，可能是采样满量程，不能把上限值当成更高精度的实际电压。硬件采样排查由开发诊断工具完成。

`PowerReading` 只有以下四个字段，没有电量百分比、功率、TTL 电流或分路电机电流等隐藏字段：

| 字段 | 类型 | 单位 |
| --- | --- | --- |
| `motor_1_2_current` | `float \| None` | A |
| `motor_3_4_current` | `float \| None` | A |
| `pwm_servo_current` | `float \| None` | A |
| `battery_voltage` | `float \| None` | V |

原始 ADC 码、ADC 引脚电压、校准状态和硬件映射不属于用户 API。开发人员排查采样问题时参见 [SDK 开发诊断手册](SDK_DEVELOPER_DIAGNOSTICS_MANUAL.md)。

## 10. 雷达

### 10.1 最近一帧

```python
frame = lite.lidar.frame(max_age=0.5)

print(frame.sequence)
print(len(frame.points))       # 有效 LD14P 帧通常为 12 点
```

### 10.2 一整圈扫描

```python
scan = lite.lidar.scan(max_age=0.5)

print(scan.sequence)
print(scan.complete)
print(len(scan.points))
```

### 10.3 连续扫描流

```python
with lite.lidar.stream() as stream:
    while True:
        scan = stream.next_scan(timeout=3.0, max_age=0.5)
        print(scan.sequence, len(scan.points))
```

还可以使用 `stream.latest_scan(max_age=0.5)` 和 `stream.stats`。务必使用 `with` 或显式关闭流。

`LidarPoint`：

- `angle_deg`：角度，度。
- `distance_mm`：距离，mm。
- `confidence`：原始置信度，0～255。

雷达返回对象完整字段：

| 类型 | 完整字段 |
| --- | --- |
| `LidarFrame` | `sequence`、`points`、`age_s`、`speed_dps` |
| `LidarScan` | `sequence`、`points`、`frame_count`、`complete`、`age_s`、`speed_dps` |
| `LidarPoint` | `angle_deg`、`distance_mm`、`confidence` |
| `LidarStreamStats`（由 `stream.stats` 返回） | `active`、`batches`、`frames`、`points`、`frame_gaps`、`raw_crc_errors`、`driver_dropped_frames`、`last_batch_age_ms` |

`frame()` 返回一个协议帧，不等于一整圈；`scan()`/`next_scan()` 返回聚合扫描。`complete=False` 表示本圈数据不完整，绘图可以选择显示，但测量算法应自行决定是否接受。`frame_gaps` 或 `driver_dropped_frames` 增加表示链路/驱动丢帧；`raw_crc_errors` 增加表示收到但校验失败。

## 11. 里程计

### 11.1 读取状态

```python
odom = lite.odometry.status(max_age=0.5)

print(odom.x_mm, odom.y_mm, odom.heading_deg)
print(odom.linear_speed_mm_s)
print(odom.angular_speed_deg_s)
```

坐标约定：

- X 轴正方向：车体前方。
- Y 轴正方向：车体左侧。
- Z 轴正方向：车体上方。
- 航向角正方向：从上方看逆时针左转。

`OdometryState` 用户字段：

| 字段 | 单位/含义 |
| --- | --- |
| `x_mm`、`y_mm` | 相对当前里程计原点的平面坐标，单位 mm；例如 `x_mm=500` 表示向车头方向前进约 500 mm，`y_mm=100` 表示向车体左侧偏移约 100 mm |
| `heading_deg` | 航向角，度 |
| `linear_speed_mm_s` | 线速度，mm/s |
| `angular_speed_deg_s` | 角速度，度/s |
| `left_distance_mm`、`right_distance_mm` | 左右轮累计距离，mm |
| `configured` | 当前是否有有效几何配置 |
| `pose_valid` | 当前位姿是否有效 |
| `left_encoder_valid`、`right_encoder_valid` | 左右编码器数据是否有效 |
| `age_s` | 状态年龄，秒 |

位姿、左右轮累计距离、配置读回和有效性标志已进行硬件链路验证。线速度与角速度已完成协议解析和单位测试，但当前证据库还缺少“非零动态速度”的专项硬件验证，因此在依赖它们做闭环导航前，应先针对实际电机和底盘补做动态验证。

返回对象当前还携带 `left_motor_port`、`right_motor_port`、`stale`、`update_period_s` 和 `update_count`，它们用于配置一致性、时序和链路诊断，不作为普通用户算法的稳定输入；说明见开发诊断手册。

### 11.2 配置

```python
config = lite.odometry.configuration()
print(config)

with lite.control():
    new_config = lite.odometry.configure(
        left_motor=3,
        right_motor=4,
        wheel_diameter_mm=67.5,
        track_width_mm=160.0,
    )
```

范围：

- 左右电机端口：1～4，且不能相同。
- 轮径 `wheel_diameter_mm`：1～1000 mm。
- 轮距 `track_width_mm`：10～2000 mm。

当前默认后驱配置为左轮 M3、右轮 M4、轮径 67.5 mm、轮距 160 mm；实际运行值以 `configuration()` 返回为准。硬件布局约定是左侧使用 M1/M3，右侧使用 M2/M4。

配置只在当前运行周期的 RAM 中生效，`persistent=False`，设备重启后恢复默认值。配置时所有直流电机必须停止；成功配置会把里程计坐标原点重置为零。

`configuration()` 和 `configure()` 都返回 `OdometryConfiguration`，其完整字段为 `left_motor`、`right_motor`、`wheel_diameter_mm`、`track_width_mm`、`persistent`。

轮胎宽度不参与标准差速里程计公式；计算使用轮子滚动直径和左右轮中心间距。编码器每圈计数属于电机/编码器配置，不在里程计 API 中重复设置。

## 12. OLED

OLED 当前支持文本和设备本地动态字段，不支持图片。

限制：

- 最多 8 页。
- 每页 1～4 行。
- 每行最多 21 个字符。
- 当前只支持可打印 ASCII 字符。

### 12.1 临时文字

```python
lite.oled.show(
    ["Welcome to", "PyMotion"],
    duration_seconds=5.0,
)
```

`duration_seconds` 默认 5 秒，范围 0.1～60 秒。时间结束后恢复此前页面。

### 12.2 多页仪表盘

```python
pages = {
    "device": [
        "PyMotion Lite",
        "{status.state}",
        "{wifi.ip}",
    ],
    "sensors": [
        "{ultrasonic.distance_cm}",
        "{imu.roll_pitch_deg}",
        "{line_tracker.levels}",
    ],
    "power": [
        "{power.battery_voltage_v}",
        "{power.m1_m2_current_a}",
        "{power.m3_m4_current_a}",
        "{power.pwm_servo_current_a}",
    ],
}

lite.oled.show_pages(
    pages,
    refresh_interval_seconds=0.5,
    page_interval_seconds=3.0,
)
```

- `refresh_interval_seconds` 默认 0.5 秒，范围 0.2～5 秒。
- `page_interval_seconds` 默认 3 秒，范围 1～60 秒。
- 动态字段由设备本地刷新，不要求 Python 不断发送 RPC，也不需要重启设备。
- 页面保存在 RAM 中，重启后恢复默认页面。

选择一页或恢复轮播：

```python
lite.oled.show_page("sensors")
lite.oled.show_slideshow("device")
lite.oled.show_default()
```

使用命名字典配置页面后，可以直接传页面名；使用普通列表时可传从 0 开始的页索引。`show_default()` 恢复默认欢迎页面。

### 12.3 动态字段

| 字符串占位符 | 显示内容与单位 |
| --- | --- |
| `"{ultrasonic.distance_cm}"` | 超声波距离，cm |
| `"{ambient_light.lux}"` | 环境光，lux |
| `"{color.rgb_raw}"` | RGB 原始值 |
| `"{color.clear_raw}"` | Clear 原始值 |
| `"{imu.roll_pitch_deg}"` | Roll/Pitch，度 |
| `"{line_tracker.levels}"` | 五路循迹电平 |
| `"{wifi.ip}"` | Wi-Fi IP |
| `"{wifi.rssi_dbm}"` | Wi-Fi RSSI，dBm |
| `"{system.uptime_s}"` | 运行时间，秒 |
| `"{status.state}"` | 设备状态 |
| `"{motors.1.measured_rpm}"`～`"{motors.4.measured_rpm}"` | 电机实测 RPM |
| `"{power.battery_voltage_v}"` | 电池电压，V |
| `"{power.m1_m2_current_a}"` | M1/M2 组电流，A |
| `"{power.m3_m4_current_a}"` | M3/M4 组电流，A |
| `"{power.pwm_servo_current_a}"` | PWM 舵机组电流，A |

课程和普通用户程序推荐使用以上小写字符串占位符。需要 IDE 自动补全时，也可以使用等价的枚举写法，例如：

```python
"{ultrasonic.distance_cm}"
pm.lite.OledField.ULTRASONIC_DISTANCE_CM
```

这两种写法表示同一个动态字段，不要在字符串中填写枚举名称。

## 13. 设备状态、停止与锁存安全

### 13.1 状态

```python
status = lite.status(max_age=1.0)

print(status.device_id)
print(status.state)
print(status.age)
print(status.lease_active)
print(status.estop_latched)
print(status.fault_latched)
```

`max_age` 默认 1 秒。状态年龄显示为 `0.000 s` 可能只是刚收到的新快照并经过三位小数格式化，不表示通信完全没有延迟。

`ProductStatus` 用户字段和属性：

| 字段/属性 | 含义 |
| --- | --- |
| `device_id` | 设备身份 |
| `lease_active` | 普通控制租约是否活动 |
| `estop_latched`、`fault_latched` | 急停/故障是否锁存 |
| `estop_reason`、`fault_reason` | 锁存原因文本 |
| `state` | 只读汇总属性：`IDLE`、`CONTROLLED`、`STOPPING`、`MAINTENANCE`、`ESTOP` 或 `FAULT` |
| `age` | 只读属性，状态在主机侧的年龄（秒） |

设备状态内部还携带启动周期、序号、命令代次、命令影子、停止域确认和安全来源等证据。这些字段用于 SDK 一致性校验与开发验证，不属于应用层稳定合同，也不再从 `pymotion.lite` 导出对应类型。需要排查安全链路时参见开发诊断手册。

### 13.2 普通停止

```python
report = lite.stop()
print(report.ok)
```

`lite.stop()` 是直流电机、PWM 和受支持 TTL 的聚合普通停止，不要求先取得控制权。用户程序判断返回对象的 `ok` 即可；停止域确认和协议错误码属于开发诊断信息。

确认命令成功不等于有独立物理传感器证明机械体已经完全静止。

单独停止某类执行器时，使用其自身 `stop()`。

### 13.3 紧急停止

```python
report = lite.emergency_stop()
print(report.estop_latched)
```

急停会锁存，设备进入 `ESTOP`。解除前必须先人工确认现场安全：

```python
report = lite.reset_estop()
```

复位急停不会恢复之前的运动，用户必须重新申请控制并重新发送命令。

### 13.4 故障清除

```python
status = lite.status()
if status.fault_latched:
    report = lite.clear_fault()
```

`fault_latched=True` 表示设备已经锁存故障。只有在排除故障并完成物理安全检查后才调用 `clear_fault()`。无故障时不需要清除。

## 14. 实时数据流

实时流由设备主动推送数据，适合连续采集，避免循环频繁调用普通读取 RPC。

### 14.1 可用数据源

传感器类：

```python
pm.lite.REALTIME_SENSOR_SOURCES
# status, imu, ultrasonic, line_tracker,
# ambient_light, color, lidar, power
```

执行器状态类：

```python
pm.lite.REALTIME_ACTUATOR_SOURCES
# motors, pwm_servos, ttl_servos
```

### 14.2 读取数据流

```python
with lite.realtime.open(
    data_sources=("imu", "ultrasonic", "power"),
    frequency="low",
    data_queue_size=32,
) as session:
    try:
        while True:
            event = session.data.read(timeout=1.0)
            if event is not None:
                print(event.source, event.sequence, event.data)
    except KeyboardInterrupt:
        pass

    print(session.data.stats())
```

`realtime.open()` 默认值：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `data_sources` | 空 | 要订阅的数据源 |
| `command_targets` | `None` | 要启用的实时命令目标 |
| `frequency` | `low` | `low`、`medium` 或 `high` |
| `data_queue_size` | `32` | Python 本地队列，范围 1～1024 |
| `ttl_servos` | 空 | 订阅 TTL 状态时声明具体对象 |
| `pwm_servos` | 空 | 订阅 PWM 状态时声明各端口实际类型 |

默认频率：

`frequency` 表示实时数据发送频率档位，三档只按频率由低到高命名：

- `low`：普通传感器与电源约 5 Hz，适合仪表盘、记录和一般监视，链路负担最低。
- `medium`：普通传感器与电源约 10 Hz，适合避障、遥控和多数“读取后立即控制”的程序。
- `high`：普通传感器与电源约 20 Hz（目标周期 50 ms），适合循迹、姿态融合等快速反馈；CPU、USB/Wi-Fi 和用户程序必须能持续消费数据。
- 三档的 `status` 都约 0.5 Hz，雷达整圈都约 6 Hz；切换档位不会提高这两个来源的频率。
- 电机、PWM 和 TTL 状态由设备主动推送；TTL 有效频率还会随订阅的舵机数量分配。

USB 与 Wi-Fi 的上传方式不同，但向用户返回相同的事件类型：

- USB：设备通过二进制串口帧主动推送。
- Wi-Fi：使用经过 HMAC 认证、带流编号和批次序号的持久 TCP 数据流。该连接由 SDK 主动连接设备，因此不要求电脑开放入站监听端口；数据通道的建立、恢复和关闭由 SDK 管理。
  `low` 目标周期约 200 ms，`medium` 目标周期约 100 ms，`high` 目标周期约 50 ms。
- `status`：复用设备已有状态快照缓存，目标约 0.5 Hz，也就是约 2 秒才出现一条。

因此，Wi-Fi 传感器实时数据通道不是两秒状态上报。前者在 `medium` 下约每
100 ms 产生一批，后者才是约 2 秒更新一次。Wi-Fi 到达时间允许有少量网络抖动；控制
算法不应把每个传感器事件直接当作唯一的命令刷新时钟，而应保存最新目标、按固定
周期刷新实时命令，并为传感器数据设置独立的过期停车时间。

队列满时，SDK 丢弃最旧事件并增加 `dropped`，不会让设备发送线程无限阻塞。应用程序应持续消费队列，并通过 `session.data.stats()` 检查丢包。

`RealtimeSession` 完整公开属性和方法：

- `session.sources`：实际订阅的数据源元组。
- `session.effective_rate_hz`：来源名到有效目标频率的只读映射。
- `session.motor_speed_command_ports`：开环百分比命令端口元组；未启用时为空。
- `session.motor_rpm_command_ports`：闭环 RPM 命令端口元组；未启用时为空。
- `session.command_ports(target)`：返回指定命令目标的端口元组。
- `session.data`：`RealtimeData` 读取入口。
- `session.commands`：`RealtimeCommands` 命令入口。
- `session.close()`：关闭会话；推荐由 `with` 自动调用。

`session.data.read()` 返回 `RealtimeDataEvent`，完整字段如下：

| 字段 | 含义 |
| --- | --- |
| `source` | 数据来源名 |
| `data` | 按来源解析后的强类型数据，见下表 |
| `sequence` | 本来源事件序号；用于判断重复或跳号 |
| `received_monotonic` | 主机单调时钟接收时刻，只用于计算时间差，不能当作日期时间 |
| `age_s` | 样本年龄；来源不能提供时为 `None` |

`session.data.stats()` 返回 `RealtimeDataStats(received, dropped)`：`received` 是进入本地队列的事件总数，`dropped` 是队列满时被 SDK 丢弃的最旧事件数。

各数据源的 `event.data` 类型和完整业务字段：

| `source` | `event.data` | 字段 |
| --- | --- | --- |
| `status` | `RuntimeStatus` | `state`、`uptime_ms`、`api_version`、`firmware_version`、`queue_depth`、`task_id`、`metrics`、`config` |
| `imu` | `ImuReading` | 见 8.5 |
| `ultrasonic` | `UltrasonicReading` | 见 8.5 |
| `line_tracker` | `LineTrackerReading` | 见 8.5 |
| `ambient_light` | `AmbientLightReading` | 见 8.5 |
| `color` | `ColorReading` | 见 8.5 |
| `lidar` | `LidarScan` | 见第 10 节 |
| `power` | `PowerReading` | 四个电源字段，见第 9 节 |
| `motors` | `tuple[RealtimeMotorState, ...]` | 每个元素见下表 |
| `pwm_servos` | `tuple[RealtimePwmServoState, ...]` | 每个元素见下表 |
| `ttl_servos` | `tuple[BusServoStatus, ...]` | 每个元素见第 7 节 |

实时电机 `RealtimeMotorState` 字段：

| 字段/属性 | 含义 |
| --- | --- |
| `port` | 产品端口 M1～M4 对应的 1～4；用户代码使用此属性 |
| `commanded_speed` | 开环命令百分比；闭环时为 `None` |
| `control_mode` | `open_loop` 或 `closed_loop` |
| `target_rpm`、`measured_rpm` | 闭环目标和编码器实测 RPM |
| `encoder_count` | 编码器累计计数；无有效反馈时为 `None` |
| `feedback_valid` | 本次编码器反馈是否有效 |
| `running` | 当前命令或实测速度是否非零；只表示正在运动，不用于判断堵转 |
| `saturated` | 输出是否饱和 |

实时 PWM `RealtimePwmServoState` 字段：

| 字段/属性 | 含义 |
| --- | --- |
| `port` | 产品端口 S1～S6 对应的 1～6；用户代码使用此属性 |
| `mode` | `position`、`speed` 或 `unknown`；类型来自用户声明 |
| `output_enabled` | PWM 输出是否启用 |
| `commanded_speed` | 连续旋转舵机命令百分比 |
| `commanded_angle_deg` | 位置舵机最近一次已知命令角度 |

### 14.3 PWM 与 TTL 状态类型声明

PWM 接口没有硬件自动识别能力。订阅状态时声明每个端口实际接入的类型：

```python
s1 = lite.pwm_servo(1, mode="speed")
s2 = lite.pwm_servo(2, mode="position")

ttl1 = lite.ttl_servo(1, mode="position")

with lite.realtime.open(
    data_sources=("pwm_servos", "ttl_servos"),
    pwm_servos=(s1, s2),
    ttl_servos=(ttl1,),
) as session:
    event = session.data.read(timeout=2.0)
```

位置 PWM 舵机没有反馈。如果从未调用 `move_to()`，其命令角度应视为未知，而不是实际位置。

## 15. 实时命令流

实时命令流用于连续更新电机开环速度百分比、闭环 RPM、连续 PWM 舵机速度或位置 PWM 舵机角度。它采用“最新命令优先”：如果上一条尚未发出，新命令会替换待发送命令。

### 15.1 电机开环百分比

```python
import time

with lite.control():
    with lite.realtime.open(
        command_targets={"motor_speeds": (1, 2)},
    ) as session:
        for speed in range(0, 31):
            session.commands.motor_speeds.write(
                {1: speed, 2: speed},
                valid_for=0.3,
            )
            time.sleep(0.05)

        session.commands.motor_speeds.stop()
        print(session.commands.motor_speeds.stats())
```

`motor_speeds` 的值为开环 `-100～100%`。会话启动时只执行一次开环模式准备，后续 `write()` 不重复切换模式。

### 15.2 电机闭环 RPM

```python
import time

with lite.control():
    with lite.realtime.open(
        command_targets={"motor_rpms": (1, 2, 3, 4)},
    ) as session:
        commands = session.commands.motor_rpms
        for rpm in range(0, 121, 4):
            commands.write(
                {1: rpm, 2: rpm, 3: rpm, 4: rpm},
                valid_for=0.35,
            )
            time.sleep(0.05)
        commands.stop()
        print(commands.stats())
```

`motor_rpms` 的值必须是 `-360～360` 的整数 RPM。会话启动时只执行一次闭环模式准备；后续 USB 实时命令或 Wi-Fi UDP 命令只刷新 RPM。它适合连续速度轨迹、闭环循迹和导航控制。几秒才改变一次目标的程序应优先使用 `lite.motors.set_rpms()`。

### 15.3 连续旋转 PWM 舵机

```python
with lite.control():
    with lite.realtime.open(
        command_targets={"pwm_continuous_servos": (1,)},
    ) as session:
        session.commands.pwm_continuous_servos.write(
            {1: 30},
            valid_for=0.3,
        )
        session.commands.pwm_continuous_servos.stop()
```

### 15.4 位置 PWM 舵机

```python
with lite.control():
    with lite.realtime.open(
        command_targets={"pwm_position_servos": (2,)},
    ) as session:
        session.commands.pwm_position_servos.write(
            {2: 90},
            valid_for=0.3,
        )
        session.commands.pwm_position_servos.stop()
```

### 15.5 实时命令规则

- 电机端口 1～4；PWM 端口 1～6。
- `command_targets` 的键名固定为 `motor_speeds`、`motor_rpms`、`pwm_continuous_servos`、`pwm_position_servos`；值直接是端口列表或元组。键名已经决定控制语义，不再重复填写 `mode`。
- 同一个 PWM 端口不能同时声明为连续和位置模式。
- 同一个电机端口不能同时出现在 `motor_speeds` 和 `motor_rpms` 中；两个目标可以控制互不重叠的端口。
- 每次 `write()` 必须包含该目标配置中的全部端口，不能只写其中一部分。
- 开环速度范围 `-100～100%`；闭环目标范围为整数 `-360～360 RPM`；位置角度范围 `0～180°`。
- `valid_for` 必填，范围 0.05～2.0 秒。设备在有效期内收不到新命令时会自动使目标过期，避免通信中断后持续运动。
- 实时会话关闭时会停止本次使用过的命令目标。
- 一个 `Lite` 连接同时只能有一个实时会话，但一个会话可以同时包含数据源和命令目标。
- USB 与 Wi-Fi 使用同一套公开 API；SDK 会根据链路和固件能力自动选择实时传输方式，用户不需要直接选择 UDP 或 RPC。
- 实时命令运行期间不会因短暂丢失确认而静默改用较慢的 RPC；连续丢失确认时会明确报错并安全停止。

`RealtimeCommandStats` 只提供 `sent` 和 `replaced` 两个字段。`replaced` 大于 0 表示 Python 写入速度高于链路实际发送速度，不表示设备执行了所有被替换的中间值。

这里统计对象实际只有两个字段：`sent` 是已经交给传输层发送的命令数，`replaced` 是发送前被更新值替换的待发送命令数。它们不是电机实际执行步数，也不是网络数据包总数。

## 16. 开发诊断与用户 API 的边界

I²C 拓扑、OLED 原始布局、ADC 原始量、来源序号、底层错误码和实时任务健康信息不属于正式用户 API。应用程序应使用本手册中的传感器、OLED、电源和状态接口；硬件验证与问题定位见 [SDK 开发诊断手册](SDK_DEVELOPER_DIAGNOSTICS_MANUAL.md)。

## 17. 异常处理

所有 SDK 公共异常均继承 `pm.lite.LiteError`：

```python
import pymotion as pm

try:
    with pm.lite.connect(timeout=15.0) as lite:
        with lite.control():
            lite.motor(1).set_speed(20, duration=1.0)
except pm.lite.AuthenticationError as exc:
    print("Token 不正确：", exc)
except pm.lite.DeviceNotFoundError as exc:
    print("没有找到目标设备：", exc)
except pm.lite.ControlUnavailableError as exc:
    print("当前无法取得控制权：", exc)
except pm.lite.LiteError as exc:
    print("PyMotion Lite 错误：", exc)
```

常见异常：

| 异常 | 常见触发情况 |
| --- | --- |
| `AuthenticationError` | Token 缺失、格式不合法或不匹配 |
| `DeviceNotFoundError` | 没有发现目标设备，或显式填写的设备 ID 格式不正确 |
| `MultipleDevicesFoundError` | 自动选择时发现多台设备 |
| `ConnectionTimeoutError` | 连接总时限到期 |
| `ConnectionClosedError` | 连接关闭后继续使用旧对象 |
| `ControlUnavailableError` | 控制已被占用、重复进入或嵌套控制 |
| `LeaseDeniedError` | 设备拒绝控制租约 |
| `DeviceBusyError` | 设备正忙，当前操作不能执行 |
| `EstopActiveError` | 急停锁存期间尝试普通控制 |
| `DeviceFaultError` | 设备故障锁存 |
| `StaleStatusError` | 最新状态超过允许年龄 |
| `SensorUnavailableError` | 所需传感器数据不可用 |
| `CapabilityUnsupportedError` | 当前固件不支持所调用能力 |
| `ProtocolError` | 设备响应违反当前公开协议约定 |
| `ProtocolVersionError` | SDK 与设备协议或数据结构不兼容 |
| `RpcError` | RPC 调用返回通用错误 |
| `RpcTimeoutError` | 已连接后的 RPC 调用超时 |
| `CommandOutcomeUnknownError` | 命令已发出但最终结果无法确认 |

遇到 `CommandOutcomeUnknownError` 时，不要盲目重放运动命令。先调用停止接口并读取状态，再决定下一步。

## 18. 默认值速查

| 项目 | 默认值 |
| --- | --- |
| 连接链路 | USB |
| 连接超时 | 15.0 秒 |
| Wi-Fi 端口 | 8787 |
| 设备发现时间 | 6.25 秒 |
| 控制申请超时 | 5.0 秒 |
| 普通传感器 `max_age` | 0.5 秒 |
| 电源 `max_age` | 1.0 秒 |
| 电机状态 `max_age` | 0.5 秒 |
| 里程计状态 `max_age` | 0.5 秒 |
| OLED 临时文字时间 | 5.0 秒 |
| OLED 动态刷新 | 0.5 秒 |
| OLED 自动换页 | 3.0 秒 |
| 实时数据频率 `frequency` | `low` |
| 实时本地队列 | 32 条 |
| 当前里程计默认左右轮 | M3 / M4 |
| 当前默认轮径 / 轮距 | 67.5 mm / 160 mm |

### 18.1 时间参数怎么选

| 场景 | 建议值 | 选择依据 |
| --- | --- | --- |
| USB 连接 `timeout` | 15 秒 | 覆盖 USB 打开后可能发生的 ESP32-S3 启动、认证、握手和状态确认 |
| Wi-Fi 连接 `timeout` | 8～15 秒 | 包含发现、认证和状态确认；网络刚恢复时可放宽到 30 秒 |
| 设备发现 `list_devices(timeout=...)` | 6.25～10 秒 | Wi-Fi 发现需要覆盖广播周期；只查 USB 时可缩短 |
| 控制申请 `lite.control(timeout=...)` | 5 秒 | 日常控制使用默认值；设备忙或链路不稳定时应先查原因，不要只盲目增大 |
| 普通传感器 `max_age` | 0.5 秒 | 适合界面显示和一般判断；快速控制应使用实时流 |
| 电源 `max_age` | 1.0 秒 | 电流值带平均处理，无需按控制周期重复查询 |
| 雷达 `next_scan(timeout=...)` | 3 秒 | 足以等待完整一圈；同时用 `max_age=0.5` 排除积压旧扫描 |
| 电机位置 `move_to/move_by(timeout=...)` | 默认 8 秒 | 小角度、空载通常可保持默认；大角度或低速时按预计运动时间留出余量 |
| 实时数据 `read(timeout=...)` | 0.2～1.0 秒 | 控制循环用 0.2～0.5 秒；交互显示可用 1 秒；返回 `None` 时自行处理 |
| 实时命令发送间隔 | 0.05～0.10 秒 | 对应 10～20 Hz；不要无等待地持续写入 |
| 实时命令 `valid_for` | 发送间隔的 3～5 倍 | 允许范围 0.05～2.0 秒，常用 0.3～0.5 秒；必须大于发送间隔，并为 Wi-Fi 抖动留余量 |
| PWM 速度 `duration` | 0.5～3 秒 | 适合短动作；需要持续运行时传 `None`，并在结束时显式 `stop()` |
| OLED 临时显示 `duration_seconds` | 2～10 秒 | 接口允许 0.1～60 秒；提示语通常使用默认 5 秒 |
| OLED `refresh_interval_seconds` | 0.5～1.0 秒 | 数值可读且不会频繁刷新；快速传感器没必要逐样本刷屏 |
| OLED `page_interval_seconds` | 3～8 秒 | 给用户足够阅读时间 |
| TTL 位置 `duration` | 0.5～2 秒 | 参数允许 0.001～65.535 秒；按角度跨度、负载和供电调整，跨度大时适当延长 |

`timeout` 是“最多等多久”，不等于设备固定延迟；`max_age` 是“数据最多允许多旧”；
`duration` 的具体语义由接口决定：PWM 速度和电机是命令持续时间，TTL 位置是协议运动时间；PWM 位置没有 `duration` 参数；
`valid_for` 是实时命令失联保护窗口。四者不能互换。

### 18.2 按场景选择 API

| 使用场景 | 推荐接口 |
| --- | --- |
| 偶尔读取一次传感器、状态或电源 | `lite.imu()`、`lite.observe()`、`lite.status()`、`lite.power()` |
| 仪表盘、记录、多传感器联动 | `lite.realtime.open(data_sources=...)` |
| 电机保持一个固定值数秒 | `motor.set_speed()`、`motor.set_rpm()` 或批量普通接口 |
| 循迹、渐变轨迹、遥控和导航 | 实时命令 `motor_speeds` 或 `motor_rpms` |
| 连续旋转 PWM 舵机调速 | `pwm_servo(..., mode="speed").set_speed()`；连续变化时使用对应实时命令 |
| PWM 位置舵机移动到少量离散角度 | `pwm_servo(..., mode="position").move_to()` |
| PWM 位置舵机平滑轨迹 | `pwm_position_servos` 实时命令；注意它只有命令角度，没有位置反馈 |
| TTL 舵机首次安装 | 断电后只接一只舵机，使用 `ttl_servos.configure(new_id=...)` 标准化 ID、波特率和限位 |
| TTL 舵机精确位置与状态读取 | `ttl_servo(id)`；型号自动识别，位置模式为默认模式 |
| 断线保护要求较高的连续控制 | 实时命令并合理设置 `valid_for`，同时监控新鲜数据和异常 |

表中的闭环 RPM、位置控制和里程计场景均以当前已测试的标配电机为前提。更换其他型号
电机时，不能仅通过修改编码器 PPR/减速比直接套用这些闭环场景。

需要根据传感器立即改变运动时，建议在同一个实时会话中同时订阅数据和启用命令目标。
控制循环应按固定周期发送“最新目标”，不要让不规则的传感器到达时刻直接决定命令发送节奏。

## 19. 推荐程序骨架

```python
import pymotion as pm


def main():
    with pm.lite.connect(
        device_id=None,
        transport="usb",
        timeout=15.0,
    ) as lite:
        print("Device:", lite.connection.device_id)
        print("Transport:", lite.connection.transport)

        imu = lite.imu()
        if imu.valid:
            print("Orientation:", imu.orientation_deg)

        with lite.control():
            lite.motor(1).set_speed(20, duration=1.0)


if __name__ == "__main__":
    try:
        main()
    except pm.lite.LiteError as exc:
        print("PyMotion Lite error:", exc)
```

这套结构能够明确管理连接、控制权、停止清理和 SDK 异常，适合作为新项目起点。

## 20. 公开符号索引

下面列出 `pm.lite` 当前正式导出的符号。应用程序通常不需要自行构造返回数据类，只需读取 API 返回对象的字段。

### 20.1 入口与连接

- `__version__`
- `connect`
- `list_devices`
- `Lite`
- `LiteDeviceInfo`

### 20.2 电机、GPIO 与里程计

- `Motor`、`Motors`、`MotorState`、`MotionResult`
- `MotorEncoder`、`EncoderConfiguration`
- `DigitalOutput`、`DIGITAL_OUTPUT_GPIOS`
- `Odometry`、`OdometryConfiguration`、`OdometryState`

### 20.3 舵机

- `PwmServo`、`PwmServoMode`、`PwmServoState`、`PwmServos`
- `TtlServo`、`TtlServos`
- `TtlServoMode`、`TtlServoModel`（型号枚举仅表示自动识别结果）
- `TtlServoConfigurationResult`

### 20.4 传感器、电源与雷达

- `SensorObservation`
- `UltrasonicReading`
- `ImuReading`
- `LineTrackerReading`
- `AmbientLightReading`
- `ColorReading`
- `PowerReading`
- `LidarPoint`、`LidarFrame`、`LidarScan`、`LidarStream`

### 20.5 OLED

- `Oled`、`OledField`

### 20.6 实时流

- `REALTIME_SENSOR_SOURCES`、`REALTIME_ACTUATOR_SOURCES`
- `Realtime`、`RealtimeSession`
- `RealtimeData`、`RealtimeDataEvent`、`RealtimeDataStats`
- `RealtimeCommands`、`RealtimeCommandStats`
- `RealtimeMotorSpeedCommands`
- `RealtimeMotorRpmCommands`
- `RealtimePwmContinuousServoCommands`
- `RealtimePwmPositionServoCommands`

### 20.7 状态与安全

- `ProductStatus`、`SafetyActionReport`

### 20.8 异常

- `LiteError`
- `AuthenticationError`
- `CapabilityUnsupportedError`
- `CommandOutcomeUnknownError`
- `ConnectionClosedError`
- `ConnectionTimeoutError`
- `ControlUnavailableError`
- `DeviceBusyError`
- `DeviceFaultError`
- `DeviceNotFoundError`
- `EstopActiveError`
- `LeaseDeniedError`
- `MultipleDevicesFoundError`
- `ProtocolError`
- `ProtocolVersionError`
- `RpcError`
- `RpcTimeoutError`
- `SensorUnavailableError`
- `StaleStatusError`

## 21. 正式接口完整签名速查

本节按当前 `pm.lite` 正式门面列出全部用户操作接口。类型名中的 `Mapping[int, float]` 表示以产品端口号为键的字典；所有控制类方法都应放在 `with lite.control():` 内。

### 21.1 发现、连接与生命周期

| 接口 | 参数、默认值和返回值 |
| --- | --- |
| `pm.lite.list_devices(*, timeout=6.25)` | `timeout` 范围 `(0, 30]` 秒；返回 `tuple[LiteDeviceInfo, ...]` |
| `pm.lite.connect(device_id=None, *, timeout=15.0, auth_token=None, transport="usb", wifi_host="0.0.0.0", wifi_port=8787)` | 返回 `Lite`；完整参数见 1.5 |
| `lite.close()` | 关闭连接；可重复调用；返回 `None` |
| `lite.closed` | 只读 `bool` |
| `lite.connection` | 只读连接信息；用户字段为 `device_id`、`transport` |
| `lite.control(*, timeout=5.0)` | 返回控制上下文；`timeout` 必须大于 0；同一连接不可嵌套 |

### 21.2 Lite 顶层对象入口

| 接口 | 返回值/说明 |
| --- | --- |
| `lite.motor(port)` | `Motor`，`port` 为 1～4 |
| `lite.motors` | `Motors` 批量对象 |
| `lite.digital_output(gpio)` | `DigitalOutput`；GPIO 必须属于 `DIGITAL_OUTPUT_GPIOS` |
| `lite.pwm_servo(port, *, mode)` | `PwmServo`；`port` 为 1～6，`mode` 为 `speed` 或 `position` |
| `lite.pwm_servos` | `PwmServos` 统一批量对象，支持位置和速度两类 PWM 舵机 |
| `lite.ttl_servo(servo_id, *, mode="position")` | `TtlServo`；ID 1～253，型号自动识别，模式为 `position` 或 `speed` |
| `lite.ttl_servos` | `TtlServos` 配置和批量控制对象 |
| `lite.odometry`、`lite.oled`、`lite.lidar`、`lite.realtime` | 对应功能对象 |
| `lite.diagnostics` | 开发诊断入口；不属于普通用户控制 API，见开发诊断手册 |

### 21.3 电机与数字输出

| 接口 | 参数和返回值 | 控制权 |
| --- | --- | --- |
| `motor.set_speed(speed, *, duration=None)` | `speed` 为 `-100～100%`；`duration` 为 `None` 或大于 0 秒；返回 `None` | 需要 |
| `motor.set_rpm(rpm, *, duration=None)` | `rpm` 必须是整数 `-360～360`；返回 `None` | 需要 |
| `lite.motors.set_rpms(rpms, *, duration=None)` | 1～4 个端口到整数 RPM 的非空映射；一次批量 RPC；返回 `None` | 需要 |
| `motor.stop()` | 当前模式目标归零；返回 `None` | 需要 |
| `motor.status(*, max_age=0.5)` | `max_age` 为 0～10 秒；返回 `MotorState` | 不需要 |
| `motor.encoder` | 返回当前 M1～M4 对应的 `MotorEncoder` 视图 | 不需要 |
| `motor.encoder.configuration()` | 返回 `EncoderConfiguration` | 不需要 |
| `motor.encoder.configure(*, ppr, gear_ratio)` | 写入铭牌参数并回读；返回实际配置 | 需要 |
| `motor.encoder.configure_counts(*, counts_per_revolution)` | 直接写入输出轴每圈计数并回读；返回实际配置 | 需要 |
| `motor.zero_position()` | 静止且编码器有效时建立软件零点；返回 `None` | 需要 |
| `motor.move_to(angle, *, speed=20, tolerance=2, timeout=8)` | 返回 `MotionResult`；范围见 5.5 | 需要 |
| `motor.move_by(angle, *, speed=20, tolerance=2, timeout=8)` | 返回 `MotionResult`；范围见 5.5 | 需要 |
| `lite.motors.set_speeds(speeds, *, duration=None)` | 1～4 个端口的非空映射；返回 `None` | 需要 |
| `lite.motors.status(*, max_age=0.5)` | 返回只读 `Mapping[int, MotorState]` | 不需要 |
| `lite.motors.stop()` | 停止四路电机；返回 `None` | 需要 |
| `output.set_high()` / `output.set_low()` | 设置高/低电平；返回 `None` | 需要 |

### 21.4 PWM 与 TTL 舵机

| 接口 | 参数和返回值 | 控制权 |
| --- | --- | --- |
| `pwm.set_speed(speed, *, duration=None)` | 仅 `mode="speed"`；`-100～100%`；返回 `None` | 需要 |
| `pwm.move_to(angle)` | 仅 `mode="position"`；`0～180°`；返回 `None` | 需要 |
| `pwm.stop()` | 两种模式均可用，关闭本路 PWM；返回 `None` | 需要 |
| `pwm.status(*, max_age=0.5)` | 返回 `PwmServoState`；仅描述命令和输出状态，无物理位置反馈 | 不需要 |
| `lite.pwm_servos.set_speeds(speeds, *, duration=None)` | 端口到速度映射；返回 `None` | 需要 |
| `lite.pwm_servos.move_to(angles)` | 端口到角度映射；返回 `None` | 需要 |
| `lite.pwm_servos.stop()` | 关闭六路 PWM；返回 `None` | 需要 |
| `lite.pwm_servos.status(*, max_age=0.5)` | 返回只读 `Mapping[int, PwmServoState]` | 不需要 |
| `ttl.move_to(angle, *, duration=None)` | 位置模式；角度受型号上限约束；返回 `None` | 需要 |
| `ttl.set_speed(speed, *, duration=None)` | `mode="speed"`；`-100～100%`；返回 `None` | 需要 |
| `ttl.stop()` | 停止本 ID；返回 `None` | 需要 |
| `ttl.status()` | 返回 TTL 状态对象 | 不需要 |
| `ttl.read_mode()` | 返回 `TtlServoMode` | 不需要 |
| `ttl.configure_mode()` | 写入对象声明的模式；返回 `None` | 需要 |
| `lite.ttl_servos.configure(*, new_id)` | 总线上只接一只舵机时配置 ID，并统一波特率/限位；返回 `TtlServoConfigurationResult` | 需要 |
| `lite.ttl_servos.move_to(mapping, *, duration=None)` | 1～8 个 `TtlServo` 对象到角度的映射；返回 `None` | 需要 |
| `lite.ttl_servos.set_speeds(mapping, *, duration=None)` | 1～8 个 `TtlServo` 对象到速度的映射；返回 `None` | 需要 |
| `lite.ttl_servos.stop()` | 停止当前连接已登记的 TTL ID；返回 `None` | 需要 |
| `lite.ttl_servos.status()` | 返回已创建或配置 TTL 舵机的只读 `Mapping[int, BusServoStatus]` | 不需要 |

### 21.5 传感器、电源、雷达与里程计

| 接口 | 参数和返回值 |
| --- | --- |
| `lite.observe(*, max_age=0.5, refresh=True, timeout=None)` | 一次返回五种用户传感器的同代 `SensorObservation` |
| `lite.imu(*, max_age=0.5)` | 返回 `ImuReading` |
| `lite.ultrasonic(*, max_age=0.5)` | 返回 `UltrasonicReading` |
| `lite.line_tracker(*, max_age=0.5)` | 返回 `LineTrackerReading` |
| `lite.ambient_light(*, max_age=0.5)` | 返回 `AmbientLightReading` |
| `lite.color(*, max_age=0.5)` | 返回 `ColorReading` |
| `lite.power(*, max_age=1.0)` | 返回 `PowerReading` |
| `lite.lidar.frame(*, max_age=0.5)` | 返回 `LidarFrame` |
| `lite.lidar.scan(*, max_age=0.5)` | 返回 `LidarScan` |
| `lite.lidar.stream()` | 返回 `LidarStream` 上下文 |
| `stream.next_scan(*, timeout=3.0, max_age=0.5)` | 等待并返回下一圈 `LidarScan`；超时抛异常 |
| `stream.latest_scan(*, max_age=0.5)` | 返回最新 `LidarScan`，没有时返回 `None` |
| `stream.stats` | 返回 `LidarStreamStats` |
| `lite.odometry.status(*, max_age=0.5)` | 返回 `OdometryState` |
| `lite.odometry.configuration()` | 返回当前 `OdometryConfiguration` |
| `lite.odometry.configure(*, left_motor, right_motor, wheel_diameter_mm, track_width_mm)` | 参数均必填；需要控制权；返回实际生效配置 |

上述传感器和状态 `max_age` 均要求有限数值且范围为 0～10 秒。`max_age=0` 表示只接受设备当前可提供的最新状态，不代表等待时间无限。

### 21.6 OLED

| 接口 | 参数和返回值 |
| --- | --- |
| `lite.oled.show(lines, *, duration_seconds=5.0)` | `lines` 为一个字符串或 1～4 行字符串；持续 0.1～60 秒；返回 `None` |
| `lite.oled.show_pages(pages, *, refresh_interval_seconds=0.5, page_interval_seconds=3.0)` | 1～8 页；动态刷新 0.2～5 秒，换页 1～60 秒；返回 `None` |
| `lite.oled.show_page(page=None, *, page_index=None, page_name=None)` | 三种选择方式只能提供一种；返回 `None` |
| `lite.oled.show_slideshow(start_page=None, *, start_page_index=None, start_page_name=None)` | 从指定页恢复轮播；返回 `None` |
| `lite.oled.show_default()` | 恢复设备默认页；返回 `None` |

### 21.7 状态与安全

| 接口 | 参数和返回值 |
| --- | --- |
| `lite.status(*, max_age=1.0, timeout=None)` | 返回 `ProductStatus` |
| `lite.stop(*, timeout=None)` | 聚合普通停止；返回对象提供稳定布尔字段 `ok` |
| `lite.emergency_stop(*, timeout=None)` / `lite.estop(...)` | 锁存急停；返回 `SafetyActionReport` |
| `lite.reset_estop(*, timeout=None)` | 解除急停锁存；返回 `SafetyActionReport` |
| `lite.clear_fault(*, timeout=None)` | 清除已排除原因的故障锁存；返回 `SafetyActionReport` |

`SafetyActionReport` 的用户字段为 `operation`、`ok`、`already_latched`、`estop_latched`、`fault_latched` 和 `outputs_replay_allowed`。其余嵌套停止证据供 SDK 内部一致性校验和开发诊断使用。

### 21.8 实时流

```python
lite.realtime.open(
    *,
    data_sources=(),
    command_targets=None,
    frequency="low",
    data_queue_size=32,
    ttl_servos=(),
    pwm_servos=(),
)
```

- `data_sources` 可以为空（仅命令会话），有数据时不能重复，来源必须来自第 14.1 节。
- `command_targets` 可以为空（仅读会话），结构和范围见第 15 节。
- `frequency` 仅为 `low`（约 5 Hz，监视/记录）、`medium`（约 10 Hz，一般联动控制）或 `high`（约 20 Hz，快速反馈）；`status` 和雷达不随档位升频。
- `data_queue_size` 必须是 1～1024 的整数。
- 请求 `ttl_servos` 数据源时必须提供 1～8 个属于当前连接且 ID 不重复的 `TtlServo` 对象。
- `pwm_servos` 最多 6 个，端口不能重复，并且必须属于当前连接；声明仅描述实际硬件类型，不会让舵机动作。

实时数据方法：`session.data.read(timeout=None)`、`session.data.stats()`；命令通道均提供只读 `ports`、`write(mapping, *, valid_for)`、`stop()`、`stats()`。`read()` 超时返回 `None`，会话后台错误则在读取时抛出。

Wi‑Fi 实时命令、控制心跳和实时 `stop()` 均使用当前固件声明的认证 UDP 通道，不会降级为 HTTP/RPC；`stop()` 在确认丢失时最多重发三次幂等停止包。USB 没有该 UDP 通道，因此继续使用 RPC。连接、控制权申请/释放及普通配置查询仍属于 RPC 控制面，不应与实时命令数据面混为一谈。

声明 `command_targets={"motor_speeds": (1, 2)}` 时，SDK 会在实时工作线程启动前对目标端口幂等设置一次开环模式；声明 `command_targets={"motor_rpms": (3, 4)}` 时则一次性准备为闭环模式。固定键名已经表示模式，端口列表中不再填写重复的 `mode`。模式准备不发生在每次 `write()` 中，因此不会占用后续实时命令频率。实时会话运行期间不要再对同一端口混用 `set_speed()`、`set_rpm()` 或另一种实时电机命令目标。

### 21.9 开发诊断

`lite.diagnostics` 仅供硬件验证和故障定位；其接口统一记录在开发诊断手册中，不计入用户 API 速查。
