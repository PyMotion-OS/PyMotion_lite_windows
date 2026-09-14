"""通过 Wi-Fi 连接一台 PyMotion Lite。

Token 规则：长度为 1～16 个 UTF-8 字节，建议使用英文字母和数字。设备配网页面与
电脑端的 Token 必须完全一致。Token 不需要每次运行都更换。

第一次使用 Wi-Fi：
1. 记下电脑在目标局域网中的 IPv4 地址。
2. 连接 PyMotion-Lite-XXXX 热点，密码为 pymotionlite。如果没有看到热点，运行中
   单次按下并释放板上的 CFG 按键，等待设备重启。
3. 打开 http://192.168.4.1:8787/wifi/setup，填写 Wi-Fi、SDK 服务地址
   ``http://电脑局域网IPv4:8787`` 和 Token。页面首次不会预填某台电脑的地址。
4. 如需修改设备热点密码，在页面中连续输入两遍相同的新密码；不修改则保持为空。
5. 在当前终端设置相同的 Token。Windows PowerShell：
       $env:PYMOTION_AUTH_TOKEN = "your-token"
   Ubuntu Bash：
       export PYMOTION_AUTH_TOKEN='your-token'
6. 运行本例程。通过认证的设备会报告自身 ID，不需要先用 USB 建立缓存。

以后使用 Wi-Fi：
- 同一个终端可直接再次运行本例程，不需要重新配网或重新设置 Token。
- 新开终端后，需要重新执行对应系统的环境变量命令。
- 如果希望以后新终端自动获得 Token，可执行一次：
      [Environment]::SetEnvironmentVariable(
          "PYMOTION_AUTH_TOKEN", "your-token", "User"
      )

更换 Token：
1. 先停止执行器并关闭正在运行的 Python 连接。
2. 单次按下并释放 CFG，重新进入上述配网页面并保存新 Token。
3. 将电脑端 PYMOTION_AUTH_TOKEN 更新成完全相同的新值，然后重新运行本例程。

电脑和 Lite 必须能在同一局域网内互相访问。不要把 8787 端口直接暴露到互联网。
SDK 使用当前终端中的 Token 认证设备，不需要把 Token 或设备 ID 写进连接代码。
多台设备同时在线时，应为它们配置不同 Token；运行前设置目标设备对应的 Token。
"""

import pymotion as pm


# 只有需要演示“关闭 Wi-Fi 后再改连 USB”时才改为 True。
SWITCH_TO_USB = False


def reconnect_by_usb() -> None:
    """在前一个 Wi-Fi 会话关闭后，使用默认 USB 链路重新连接。"""

    with pm.lite.connect(timeout=15.0) as lite:
        connection = lite.connection
        print("Reconnected by USB.")
        print(f"Device ID: {connection.device_id}")
        print(f"Transport: {connection.transport}")


try:
    # 读取 SDK 版本不需要先连接设备。
    print(f"PyMotion Lite SDK: {pm.lite.__version__}")

    # 运行前应已按上面的首次使用流程完成配网和 Token 设置。
    with pm.lite.connect(
        transport="wifi",
        timeout=60.0,
    ) as lite:
        connection = lite.connection
        status = lite.status(max_age=2.0)

        print(f"Device ID: {connection.device_id}")
        print(f"Transport: {connection.transport}")
        print(f"State: {status.state}")

    # Wi-Fi 的 with 已经退出后，才允许按需建立新的 USB 会话。
    if SWITCH_TO_USB:
        reconnect_by_usb()

except pm.lite.LiteError as exc:
    # 连接、身份认证和状态读取错误统一显示为 LiteError。
    print(f"PyMotion Lite error: {exc}")
