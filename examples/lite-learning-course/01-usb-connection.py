"""通过默认 USB 链路连接一台 PyMotion Lite。

全新设备需要先完成一次初始化：连接 ``PyMotion-Lite-XXXX`` 热点（密码为
``pymotionlite``），打开 ``http://192.168.4.1:8787/wifi/setup``，填写 2.4 GHz
Wi-Fi、运行 SDK 的电脑在该局域网中的服务地址（例如
``http://192.168.1.100:8787``），并设置 1～16 字节的设备 Token。页面首次不会预填
某台电脑的地址。如果没有看到热点，运行中单次按下并释放板上的 CFG 按键，等待设备重启。

保存后，在当前终端设置完全相同的 Token。Windows PowerShell：

    $env:PYMOTION_AUTH_TOKEN = "设备的 Token"

Ubuntu Bash：

    export PYMOTION_AUTH_TOKEN='设备的 Token'

USB 和 Wi-Fi 都使用该 Token 认证；USB 连接不要求 Wi-Fi 链路在线。关闭或重新
打开新终端后需要再次设置。也可以通过 ``auth_token`` 参数传入，但不要把
真实 Token 提交到公开代码中。多设备的发现和明确选机方法见第 17 课。
"""

import pymotion as pm


try:
    # 打开设备前也可以读取当前安装的 SDK 版本。
    print(f"PyMotion Lite SDK: {pm.lite.__version__}")

    # 省略 transport 时使用默认 USB 连接。
    # Ubuntu 虚拟机在 USB 设备重新打开时可能需要更长的枚举时间。
    with pm.lite.connect(timeout=15.0) as lite:
        connection = lite.connection
        status = lite.status(max_age=1.0)

        print(f"Device ID: {connection.device_id}")
        print(f"Transport: {connection.transport}")
        print(f"State: {status.state}")

except pm.lite.LiteError as exc:
    # 连接或读取失败时统一显示 SDK 错误。
    print(f"PyMotion Lite error: {exc}")
