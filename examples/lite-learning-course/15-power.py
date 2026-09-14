"""读取一次设备支持的电源测量值。

M1/M2 与 M3/M4 分别显示两组直流电机的共用供电电流，PWM servo 显示
六路 PWM 舵机的共用供电电流；电流单位为 A，电池电压单位为 V。
三路电流是最近约 1 秒的平均值，可避免 PWM 驱动时读数偶尔显示为 0。
本例只读取数据，不会让电机或舵机动作。暂时无法获得某项数据时显示
unavailable。
"""

import pymotion as pm


def print_measurement(name, value, decimal_places):
    """按测量值的实际精度显示，缺少数据时显示 unavailable。"""

    if value is None:
        print(f"{name}: unavailable")
    else:
        print(f"{name}: {value:.{decimal_places}f}")


try:
    with pm.lite.connect() as lite:
        # 电源采样带平均处理，因此允许 1 秒年龄比高频重复查询更合适。
        power = lite.power(max_age=1.0)

        print("\nPower measurements")
        # 电流显示到 0.001 A，电压显示到 0.01 V，避免暗示不存在的测量精度。
        measurements = [
            ("M1/M2 supply current (A)", power.motor_1_2_current, 3),
            ("M3/M4 supply current (A)", power.motor_3_4_current, 3),
            ("PWM servo supply current (A)", power.pwm_servo_current, 3),
            ("Battery voltage (V)", power.battery_voltage, 2),
        ]
        for name, value, decimal_places in measurements:
            print_measurement(name, value, decimal_places)

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
