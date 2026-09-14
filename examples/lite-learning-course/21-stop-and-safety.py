"""学习普通停止与锁存安全操作。

``lite.stop()`` 是非锁存普通停止：不需要控制权，可停止 DC 电机、PWM 舵机和已跟踪
的 TTL 舵机。程序报告完成后仍需观察机构是否已经物理静止。默认
``SAFETY_EXAMPLE = None``，本例只执行这项普通停止。

将 ``SAFETY_EXAMPLE`` 改成 ``"emergency_stop"`` 后，程序只有在用户输入指定确认词
时才触发锁存急停，并在再次人工确认后复位；旧运动命令不会恢复。改成
``"clear_fault"`` 时，仅在设备已有故障锁存且用户确认物理原因已解决后清除故障。
程序退出时绝不会自动清除急停或故障。

Emergency stop 和 Fault 是两个独立状态：主动急停后 Emergency stop 变为 True；
设备检测并锁存故障后 Fault 才会变为 True。复位急停不会顺带清除故障。

只有一台 USB Lite 时，可以保持 ``DEVICE_ID = None``。Wi-Fi 下保持 None 会使用
SDK 最近一次记住的设备 ID；多设备或正式程序应明确填写设备 ID。连接前应在
在当前终端设置目标设备自己的 ``PYMOTION_AUTH_TOKEN``。
"""

import pymotion as pm


# 单设备 USB 入门场景可保持 None；多设备时填写第 17 课发现到的目标 ID。
DEVICE_ID = None

# 可选值："usb" 或 "wifi"。
TRANSPORT = "usb"

# 可选值：None、"emergency_stop" 或 "clear_fault"。
# 急停和故障是两个独立状态：急停对应 Emergency stop，设备检测并锁存故障后
# Fault 才会变为 True。
SAFETY_EXAMPLE = "clear_fault"


def connect_target():
    """按本例配置连接目标设备。"""

    return pm.lite.connect(
        DEVICE_ID,
        transport=TRANSPORT,
        timeout=15.0,
    )


def show_safety_status(lite, heading):
    """显示设备状态，以及相互独立的急停和故障状态。"""

    status = lite.status(max_age=1.0)
    print(f"\n{heading}")
    print(f"State: {status.state}")
    print(f"Emergency stop: {status.estop_latched}")
    print(f"Fault: {status.fault_latched}")
    if status.estop_latched:
        print(f"Emergency stop reason: {status.estop_reason}")
    if status.fault_latched:
        print(f"Fault reason: {status.fault_reason}")
    return status


latched_safety_may_be_active = False


try:
    if SAFETY_EXAMPLE not in {None, "emergency_stop", "clear_fault"}:
        print(f"Unknown SAFETY_EXAMPLE value: {SAFETY_EXAMPLE!r}")
    else:
        with connect_target() as lite:
            print(f"Connected device: {lite.connection.device_id}")
            print(f"Transport: {lite.connection.transport}")
            status = show_safety_status(lite, "Status before stop")

            stop = lite.stop(timeout=2.0)
            if not stop.ok:
                raise pm.lite.DeviceFaultError(
                    "ordinary stop was not fully acknowledged"
                )
            print("\nOrdinary stop completed.")

            status = show_safety_status(lite, "Status after ordinary stop")

            if SAFETY_EXAMPLE == "emergency_stop":
                confirmation = input(
                    "After clearing the area, type TRIGGER ESTOP to continue: "
                )
                if confirmation == "TRIGGER ESTOP":
                    latched_safety_may_be_active = True
                    report = lite.emergency_stop(timeout=3.0)
                    print("Emergency stop activated.")
                    show_safety_status(lite, "Status after emergency stop")

                    confirmation = input(
                        "After a physical safety check, type RESET ESTOP: "
                    )
                    if confirmation == "RESET ESTOP":
                        report = lite.reset_estop(timeout=3.0)
                        latched_safety_may_be_active = report.estop_latched
                        print("Emergency stop reset.")
                        show_safety_status(
                            lite, "Status after emergency stop reset"
                        )
                        print("Previous motion was not resumed.")
                    else:
                        print("Emergency stop remains active.")
                else:
                    print("Emergency stop example skipped.")

            elif SAFETY_EXAMPLE == "clear_fault":
                if not status.fault_latched:
                    print("No fault is currently latched; nothing was cleared.")
                else:
                    print(f"Fault reason: {status.fault_reason}")
                    confirmation = input(
                        "After resolving the physical cause, type CLEAR FAULT: "
                    )
                    if confirmation == "CLEAR FAULT":
                        report = lite.clear_fault(timeout=3.0)
                        print("Fault cleared:", not report.fault_latched)
                        print("Previous motion was not resumed.")
                    else:
                        print("Fault remains active.")

            else:
                print("\nOrdinary stop example completed.")

except pm.lite.CommandOutcomeUnknownError as exc:
    latched_safety_may_be_active = True
    print("The safety operation result could not be confirmed.")
    print("Reconnect and inspect the device; do not repeat it automatically.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")

finally:
    if latched_safety_may_be_active:
        print("A safety latch may still be active; inspect the device before recovery.")
