"""读取四路直流电机的编码器反馈。

本例只读取状态，不会让电机动作。Has encoder 表示该端口支持编码器；Measured RPM
是当前实测转速；Encoder count 是设备本次启动以来保存的原始有符号净累计计数，
重新运行 Python 程序不会自动归零。正转和反转产生相反符号的计数并会互相抵消，
因此计数变化很小不代表电机没有转动；不同端口的原始正负号也可能因固定接线而不同。
"""

import pymotion as pm


# 单设备 USB 场景可保持 None；多设备时填写第 17 课发现到的目标 ID。
DEVICE_ID = None

# 可选值："usb" 或 "wifi"。使用 Wi-Fi 时需配置目标设备的 Token。
TRANSPORT = "usb"


def connect_target():
    """连接本例指定的设备。"""

    return pm.lite.connect(
        DEVICE_ID,
        transport=TRANSPORT,
        timeout=15.0,
    )


try:
    with connect_target() as lite:
        print(f"Connected device: {lite.connection.device_id}")
        print(f"Transport: {lite.connection.transport}")

        # 一次读取 M1～M4 的最新状态。
        motor_states = lite.motors.status(max_age=0.5)

        print("\nMotor encoder feedback")
        for port in sorted(motor_states):
            state = motor_states[port]
            print(f"\nM{state.port}")
            print(f"Has encoder: {state.has_encoder}")

            if not state.has_encoder:
                print("Measured RPM: not supported")
                print("Encoder count: not supported")
            else:
                if state.measured_rpm is None:
                    print("Measured RPM: unavailable")
                else:
                    print(f"Measured RPM: {state.measured_rpm}")

                # 这是带方向的净累计计数，不是忽略方向后累加的“总转动量”。
                if state.encoder_count is None:
                    print("Encoder count: unavailable")
                else:
                    print(f"Encoder count: {state.encoder_count}")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
