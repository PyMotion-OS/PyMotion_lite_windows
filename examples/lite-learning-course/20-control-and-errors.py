"""学习如何取得控制权，以及如何处理常见错误。

执行器命令必须放在 ``with lite.control():`` 内：进入时 SDK 申请控制权，退出时
SDK 自动停止该控制会话的输出并释放控制权。``RUN_MOTOR_EXAMPLE`` 控制是否运行
M1；启用前应让 M1 的输出轴和负载可以安全转动，并清空周围空间。

只有一台 USB Lite 时，可以保持 ``DEVICE_ID = None``。Wi-Fi 下保持 None 会使用
SDK 最近一次记住的设备 ID，并不是重新扫描后随意选择；只有确认记录正确时才这样用。
多设备或正式程序应填写第 17 课发现到的目标 ID，并把 ``TRANSPORT`` 设为实际链路。
连接前在当前终端设置该设备自己的 ``PYMOTION_AUTH_TOKEN``；设备 ID 用于选机，
Token 用于认证，二者不能互相替代。
"""

import pymotion as pm


# 单设备 USB 入门场景保持 None；多设备时填入目标设备 ID。
DEVICE_ID = None

# 可选值："usb" 或 "wifi"。
TRANSPORT = "usb"

# 为 True 时 M1 会低速运行 1 秒；运行前确认输出轴和负载可以安全转动。
RUN_MOTOR_EXAMPLE = True


def connect_target():
    """按本例配置连接目标设备。"""

    return pm.lite.connect(
        DEVICE_ID,
        transport=TRANSPORT,
        timeout=15.0,
    )


try:
    with connect_target() as lite:
        print(f"Connected device: {lite.connection.device_id}")
        print(f"Transport: {lite.connection.transport}")
        print("Requesting device control...")

        # 此控制块内的所有写命令共用同一份控制权。
        with lite.control(timeout=5.0):
            print("Device control acquired.")

            # 同一连接不能嵌套申请控制权；捕获这个错误后，外层控制块仍可继续使用。
            try:
                with lite.control(timeout=5.0):
                    pass
            except pm.lite.ControlUnavailableError:
                print("Nested control was rejected safely.")

            if RUN_MOTOR_EXAMPLE:
                print("Running M1 at low speed for one second.")
                lite.motor(1).set_speed(20, duration=1.0)
            else:
                print("Motor example disabled; no motion command was sent.")

        print("Device control released automatically.")

    print("Connection closed.")
    print("Control and error-handling example completed.")

except pm.lite.MultipleDevicesFoundError:
    print("More than one Lite device was found.")
    print("Set DEVICE_ID at the top of this file, then run it again.")

except (
    pm.lite.DeviceNotFoundError,
    pm.lite.AuthenticationError,
    pm.lite.ConnectionTimeoutError,
) as exc:
    print(f"Connection error ({type(exc).__name__}): {exc}")

except (pm.lite.LeaseDeniedError, pm.lite.DeviceBusyError) as exc:
    print(f"Device control is unavailable: {exc}")

except pm.lite.CommandOutcomeUnknownError as exc:
    print(f"Command outcome is unknown during {exc.operation} ({exc.stage}).")
    print("Do not automatically repeat a motion command; inspect the device first.")

except pm.lite.EstopActiveError as exc:
    print(f"Emergency stop is active: {exc}")
    print("Inspect the device before recovery.")

except pm.lite.DeviceFaultError as exc:
    print(f"Device fault: {exc}")
    print("Resolve the physical cause before clearing the fault.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
