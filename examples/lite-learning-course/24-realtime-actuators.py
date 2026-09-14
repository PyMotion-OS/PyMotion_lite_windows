"""持续接收直流电机、PWM 舵机和 TTL 舵机的状态。

本例程只读取状态，不会申请设备控制权，也不会让执行器产生动作。按下 ``Ctrl+C``
即可停止采集并查看各类执行器的最新状态。

TTL 舵机只需用 ``ttl_servo()`` 写明实际 ID，SDK 会自动读取版本指纹并识别当前支持的
FT 型号。本例读取 ID1 与 ID2；如果接线不同，请修改对应 ID。
PWM 舵机没有位置反馈，显示的是命令与输出状态，不能据此判断舵盘的真实角度。
位置舵机显示角度（degrees），连续旋转舵机显示速度（%）。声明舵机类型不会产生
动作；如果本次启动后尚未向该端口发送过命令，角度或速度会显示为 unavailable。
没有声明类型的端口显示为 unknown。
"""

import pymotion as pm


DEVICE_ID = None
TRANSPORT = "usb"
MAX_SAMPLES_PER_SOURCE = 100
ACTUATOR_SOURCES = ["motors", "pwm_servos", "ttl_servos"]

# 根据板卡上实际连接的两种 PWM 舵机填写端口号。
# 在这里创建设备对象不会发送动作命令，也不会让舵机转动。
CONTINUOUS_PWM_SERVO_PORT = 1
POSITION_PWM_SERVO_PORT = 2


def show_latest(source, data):
    """显示一组最新执行器状态。"""
    if source == "motors":
        for motor in data:
            if motor.control_mode == "closed_loop":
                command = f"target={motor.target_rpm} RPM"
            else:
                command = f"commanded={motor.commanded_speed}%"
            print(f"  M{motor.port}: {command}, measured={motor.measured_rpm} RPM")
    elif source == "pwm_servos":
        for servo in data:
            if servo.mode == "position":
                command = (
                    "angle=unavailable"
                    if servo.commanded_angle_deg is None
                    else f"angle={servo.commanded_angle_deg} degrees"
                )
            elif servo.mode == "speed":
                command = (
                    "speed=unavailable"
                    if servo.commanded_speed is None
                    else f"speed={servo.commanded_speed}%"
                )
            else:
                command = "command=unavailable"
            print(
                f"  S{servo.port}: mode={servo.mode}, "
                f"{command}, enabled={servo.output_enabled}"
            )
    elif source == "ttl_servos":
        for servo in data:
            print(
                f"  ID{servo.id} ({servo.model}): "
                f"angle={servo.angle_deg:.2f} degrees, "
                f"online={servo.online}"
            )


def main():
    """持续采集状态，直到用户按下 Ctrl+C。"""
    actuator_data = {source: [] for source in ACTUATOR_SOURCES}

    with pm.lite.connect(DEVICE_ID, transport=TRANSPORT, timeout=15.0) as lite:
        # 同一入口通过 mode 区分连续旋转舵机和 0～180°位置舵机。
        continuous_servo = lite.pwm_servo(
            CONTINUOUS_PWM_SERVO_PORT, mode="speed"
        )
        position_servo = lite.pwm_servo(
            POSITION_PWM_SERVO_PORT, mode="position"
        )
        print(
            f"PWM servo types: S{continuous_servo.port}=continuous, "
            f"S{position_servo.port}=position"
        )

        # 首次创建对象时自动识别型号，后续状态换算复用本次连接内的缓存。
        ttl_1 = lite.ttl_servo(1, mode="position")
        ttl_2 = lite.ttl_servo(2, mode="position")

        with lite.realtime.open(
            data_sources=ACTUATOR_SOURCES,
            pwm_servos=[continuous_servo, position_servo],
            ttl_servos=[ttl_1, ttl_2],
            frequency="low",
            data_queue_size=32,
        ) as session:
            print("Collecting realtime actuator-state data...")
            print("Press Ctrl+C to stop.")

            try:
                while True:
                    event = session.data.read(timeout=0.1)
                    if event is None or event.source not in actuator_data:
                        continue

                    samples = actuator_data[event.source]
                    samples.append(event.data)
                    if len(samples) > MAX_SAMPLES_PER_SOURCE:
                        del samples[0]
            except KeyboardInterrupt:
                print("\nActuator collection stopped by the user.")

            print("\nCollected actuator-state data:")
            for source in ACTUATOR_SOURCES:
                samples = actuator_data[source]
                print(f"- {source}: {len(samples)} sample(s)")
                if samples:
                    show_latest(source, samples[-1])
                else:
                    print("  Latest data: unavailable")

            stats = session.data.stats()
            print("\nRealtime data statistics:")
            print(f"Received: {stats.received}")
            print(f"Dropped: {stats.dropped}")


try:
    main()
except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
