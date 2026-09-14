"""连续收集各类传感器和设备状态数据。

程序会持续接收数据，按下 ``Ctrl+C`` 后停止并显示汇总。它不申请设备控制权，
也不会让执行器动作。每类来源分别保留最近 100 条数据；如果接收队列已满，SDK
会丢弃最旧事件，并在结尾显示丢弃数量。

进入 ``realtime.open()`` 时，SDK 会启动一次数据流，之后由设备持续推送传感器
数据，不需要 Python 反复调用单次读取 API。状态沿用设备普通状态推送，所以更新
次数较少；电源的三路分组电流和电池电压与普通传感器一样由实时流主动推送。
``frequency="low"`` 适合一般程序；需要更快更新时可改为 ``frequency="medium"``；
循迹、姿态或避障需要约 50 ms 更新时可使用 ``frequency="high"``。频率越高，USB
或 Wi-Fi 链路负载越大。

事件的 sequence 是对应来源在设备本次启动后的累计采样序号，不是本次 Python
程序收到的条数。设备在程序运行前已经持续采样，因此 sequence 通常大于接收数。
API 保留完整数值精度供程序计算，本例显示时会按单位限制小数位。
"""

import pymotion as pm


DEVICE_ID = None
TRANSPORT = "usb"
MAX_SAMPLES_PER_SOURCE = 100

# 每个名称对应一种可以独立接收的数据来源。
SENSOR_SOURCES = [
    "status",
    "imu",
    "ultrasonic",
    "line_tracker",
    "ambient_light",
    "color",
    "lidar",
    "power",
]


def show_latest(source, data):
    """按适合终端阅读的格式显示一条最新数据。"""
    if source == "status":
        print(f"  State: {data.state}")
    elif source == "imu":
        acceleration = data.acceleration_mm_s2
        orientation = data.orientation_deg
        if acceleration is None or orientation is None:
            print("  IMU data: unavailable")
        else:
            print(
                "  Acceleration: "
                f"x={acceleration.x:.1f}, y={acceleration.y:.1f}, "
                f"z={acceleration.z:.1f} mm/s^2"
            )
            print(
                f"  Orientation: roll={orientation.roll:.2f}, "
                f"pitch={orientation.pitch:.2f} degrees"
            )
    elif source == "ultrasonic":
        if data.distance_mm is None:
            print("  Distance: unavailable")
        else:
            print(f"  Distance: {data.distance_mm:.1f} mm")
    elif source == "line_tracker":
        if data.levels is None:
            print("  Levels: unavailable")
        else:
            levels = ", ".join(str(level) for level in data.levels)
            print(f"  Levels: {levels}")
    elif source == "ambient_light":
        if data.illuminance_lux is None:
            print("  Illuminance: unavailable")
        else:
            print(f"  Illuminance: {data.illuminance_lux:.1f} lux")
    elif source == "color":
        if data.red is None:
            print("  Color values: unavailable")
        else:
            print(f"  RGB: {data.red}, {data.green}, {data.blue}")
    elif source == "lidar":
        print(f"  Point count: {len(data.points)}")
    elif source == "power":
        values = (
            ("M1/M2 supply current", data.motor_1_2_current, "A"),
            ("M3/M4 supply current", data.motor_3_4_current, "A"),
            ("S1-S6 PWM servo supply current", data.pwm_servo_current, "A"),
            ("Battery voltage", data.battery_voltage, "V"),
        )
        for name, value, unit in values:
            if value is None:
                print(f"  {name}: unavailable")
            else:
                print(f"  {name}: {value:.3f} {unit}")


def main():
    """持续收集数据，直到用户按下 Ctrl+C。"""

    # 为每种数据来源准备一个列表，列表中保存已经收到的数据对象。
    sensor_data = {source: [] for source in SENSOR_SOURCES}

    # DEVICE_ID=None 表示仅发现一台设备时自动选择；多设备时应填写目标设备 ID。
    with pm.lite.connect(
        DEVICE_ID,
        transport=TRANSPORT,
        timeout=15.0,
    ) as lite:
        # 进入上下文时启动数据流，退出时 SDK 会自动停止数据流并释放资源。
        with lite.realtime.open(
            data_sources=SENSOR_SOURCES,
            frequency="low",
            data_queue_size=32,
        ) as session:
            print("Collecting realtime sensor data...")
            print("Press Ctrl+C to stop.")

            try:
                while True:
                    # event.source 是来源名称，event.data 是对应的类型化数据对象。
                    # 0.1 秒内没有新数据时返回 None，程序可以继续等待。
                    event = session.data.read(timeout=0.1)
                    if event is None:
                        continue

                    # 只汇总本课程明确订阅的来源，避免把未知数据误当成课程结果。
                    if event.source not in sensor_data:
                        continue

                    samples = sensor_data[event.source]
                    samples.append(event.data)

                    # 只保留最近 100 条，避免程序长时间运行后列表无限增长。
                    if len(samples) > MAX_SAMPLES_PER_SOURCE:
                        del samples[0]

            except KeyboardInterrupt:
                print("\nSensor collection stopped by the user.")

            print("\nCollected sensor data:")
            for source in SENSOR_SOURCES:
                samples = sensor_data[source]
                print(f"- {source}: {len(samples)} sample(s)")
                if samples:
                    show_latest(source, samples[-1])
                else:
                    print("  Latest data: unavailable")

            # received 是 SDK 放入队列的事件总数；dropped 是队列满时丢弃的数量。
            stats = session.data.stats()
            print("\nRealtime data statistics:")
            print(f"Received: {stats.received}")
            print(f"Dropped: {stats.dropped}")


try:
    main()
except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
