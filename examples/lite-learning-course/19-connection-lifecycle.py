"""学习连接的关闭和重新连接。

本例不控制电机或舵机。它演示三件事：
1. ``close()`` 可以安全地重复调用；
2. 连接关闭后，由该连接创建的电机对象不能继续使用；
3. 使用同一个设备 ID 可创建一条全新的连接。

只有一台 USB Lite 时，可以保持 ``DEVICE_ID = None``。Wi-Fi 下保持 None 会使用
SDK 最近一次记住的设备 ID，并不是重新扫描后随意选择；只有确认记录正确时才这样用。
多设备或正式程序应填写第 17 课列出的目标 ID，并把 ``TRANSPORT`` 设为实际链路。
连接前在当前终端设置该设备自己的 ``PYMOTION_AUTH_TOKEN``；设备 ID 用于选机，
Token 用于认证，不会广播控制命令。
"""

import pymotion as pm


# 单设备 USB 入门场景保持 None；多设备时填入第 17 课发现到的设备 ID。
DEVICE_ID = None

# 可选值："usb" 或 "wifi"。
TRANSPORT = "usb"


def connect_target(device_id=None):
    """按本例配置连接目标设备。"""

    return pm.lite.connect(
        DEVICE_ID if device_id is None else device_id,
        transport=TRANSPORT,
        timeout=15.0,
    )


def close_and_check_old_child():
    """关闭连接，并确认旧对象已经失效。"""

    lite = None
    try:
        lite = connect_target()
        device_id = lite.connection.device_id
        old_motor = lite.motor(1)

        print("Initial connection")
        print(f"Device ID: {device_id}")
        print(f"Transport: {lite.connection.transport}")
        print(f"Closed: {lite.closed}")

        lite.close()

        print("\nAfter close")
        print(f"Closed: {lite.closed}")

        # 重复关闭是安全的，不会重新打开连接。
        lite.close()
        print("Calling close() a second time completed safely.")

        print("\nOld motor object")
        try:
            old_motor.status(max_age=0.5)
        except pm.lite.ConnectionClosedError:
            print("The old motor object is no longer usable.")
        else:
            print("Unexpected: the old motor object remained usable.")

        return device_id
    finally:
        if lite is not None and not lite.closed:
            lite.close()


try:
    original_device_id = close_and_check_old_child()

    print("\nReconnect")
    with connect_target(original_device_id) as new_lite:
        new_motor = new_lite.motor(1)
        print(f"Requested device: {original_device_id}")
        print(f"Connected device: {new_lite.connection.device_id}")
        print(f"Fresh motor object: M{new_motor.port}")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
