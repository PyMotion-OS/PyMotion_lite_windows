"""连接一台 PyMotion Lite，并显示基本状态。

全新设备需要先完成一次初始化：

1. 给 Lite 上电，电脑连接 ``PyMotion-Lite-XXXX`` 热点，密码为 ``pymotionlite``。
   如果没有看到热点，运行中单次按下并释放板上的 CFG 按键，等待设备重启。
2. 浏览器打开 ``http://192.168.4.1:8787/wifi/setup``。
3. 填写 2.4 GHz Wi-Fi、运行 SDK 的电脑在该局域网中的服务地址（例如
   ``http://192.168.1.100:8787``），并设置一个 1～16 字节的设备 Token。页面首次
   不会预填某台电脑的地址；需要修改设备热点密码时，必须输入两遍相同的新密码。
   保存后页面会完成网络和 Token 初始化。
4. 在当前终端设置完全相同的 Token，再运行本例程。
   Windows PowerShell：

    $env:PYMOTION_AUTH_TOKEN = "设备的 Token"

   Ubuntu Bash：

    export PYMOTION_AUTH_TOKEN='设备的 Token'

USB 和 Wi-Fi 都使用该 Token 进行身份认证，但使用 USB 不要求 Wi-Fi 链路在线。
该环境变量只在当前终端中有效；关闭或重新打开终端后需要再次设置。
也可以通过 ``pm.lite.connect(auth_token="...")`` 传入，但不要把真实 Token 提交到
公开代码中。只有一台设备时可以省略设备 ID；连接多台设备时应明确传入目标 ID。
"""

import pymotion as pm


try:
    # 显示当前 Python 实际导入的 PyMotion Lite SDK 版本。
    print(f"PyMotion Lite SDK: {pm.lite.__version__}")

    # 连接一台 Lite。离开 with 代码块时，连接会自动关闭。
    with pm.lite.connect() as lite:
        # max_age=1.0 表示不接受超过 1 秒的旧状态。
        status = lite.status(max_age=1.0)

        # 输出设备标识和当前状态摘要，便于确认连接是否正确。
        print(f"Device ID: {lite.connection.device_id}")
        print(f"Transport: {lite.connection.transport}")
        print(f"State: {status.state}")
        # age 表示这份状态数据已经存在多久，不是 USB/Wi-Fi 通信耗时。
        print(f"Status age: {status.age:.3f} s")

except pm.lite.LiteError as exc:
    # SDK 连接或状态读取失败时，显示便于排查的错误信息。
    print(f"PyMotion Lite error: {exc}")
