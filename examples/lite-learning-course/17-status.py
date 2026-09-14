"""读取并查看一次设备状态。

max_age 表示允许状态数据最多有多旧，单位是秒；它不是连接超时时间。
status.age 是 SDK 中这份状态的年龄，不是 USB/Wi-Fi 通信延迟。
本例只读取状态，不申请控制权限，也不会让执行器动作。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 状态读取是只读快照；超过 max_age 时 SDK 会报过期，而不是返回旧值。
        status = lite.status(max_age=1.0)

        print("Device status")
        print(f"Device ID: {status.device_id}")
        print(f"State: {status.state}")
        print(f"Status age: {status.age:.3f} s")

        print("\nControl")
        print(f"Active: {status.lease_active}")

        print("\nSafety")
        print(f"Emergency stop: {status.estop_latched}")
        print(f"Fault: {status.fault_latched}")

        if status.estop_latched:
            print(f"Emergency stop reason: {status.estop_reason}")

        if status.fault_latched:
            print(f"Fault reason: {status.fault_reason}")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
