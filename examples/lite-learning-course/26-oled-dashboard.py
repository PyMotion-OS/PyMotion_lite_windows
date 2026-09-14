"""学习创建、选择和自动轮播 OLED 动态仪表盘。

OLED_PAGES 中每个名称代表一个页面。最多可设置 8 页，每页最多 4 行，
每行最多 21 个 ASCII 字符。带单位的字段名说明了显示单位，例如 rpm、V 和 A。
页面设置完成后，设备会自动刷新本地数据；Python 无需循环读取传感器再更新屏幕。
input() 只用于暂停程序以便观察；按 Enter 后继续执行下一条 OLED 命令。
"""

import pymotion as pm


OLED_PAGES = {
    "device": [
        "PyMotion Dashboard",
        "{status.state}",
        "{wifi.ip}",
        "{system.uptime_s}",
    ],
    "motors_1_2": [
        "Motor Speed 1-2",
        "{motors.1.measured_rpm}",
        "{motors.2.measured_rpm}",
    ],
    "motors_3_4": [
        "Motor Speed 3-4",
        "{motors.3.measured_rpm}",
        "{motors.4.measured_rpm}",
    ],
    "power_voltage": [
        "Power Voltage",
        "{power.battery_voltage_v}",
        "{power.pwm_servo_current_a}",
    ],
    "power_motors": [
        "Motor Current",
        "{power.m1_m2_current_a}",
        "{power.m3_m4_current_a}",
    ],
    "sensors": [
        "Sensors",
        "{ultrasonic.distance_cm}",
        "{line_tracker.levels}",
        "{ambient_light.lux}",
    ],
    "imu": [
        "Orientation",
        "{imu.roll_pitch_deg}",
    ],
    "color": [
        "Color Sensor",
        "{color.rgb_raw}",
        "{color.clear_raw}",
    ],
}


try:
    with pm.lite.connect() as lite:
        # 设置页面、数据刷新间隔和自动换页间隔。
        lite.oled.show_pages(
            OLED_PAGES,
            refresh_interval_seconds=0.5,
            page_interval_seconds=3.0,
        )

        print(f"OLED dashboard started with {len(OLED_PAGES)} pages.")
        input("Observe automatic page rotation, then press Enter...")

        # 暂停自动轮播，并按名称固定显示 sensors 页面。
        lite.oled.show_page("sensors")
        # 也可以按页码选择第六页：lite.oled.show_page(5)
        input("The sensors page is selected. Press Enter to resume rotation...")

        # 从 device 页面恢复自动轮播。
        lite.oled.show_slideshow("device")
        input("Observe page rotation, then press Enter to restore the welcome page...")

        lite.oled.show_default()
        print("Default welcome page restored.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
