"""短暂运行连续旋转 PWM 舵机。

运行前请确认 S1、S2 接的是连续旋转舵机，并清空连杆附近空间。
速度范围为 -100~100，表示开环百分比而不是真实 RPM；正负号表示相反方向。
``set_speeds()`` 可以用一个字典同时设置多路舵机，duration 到时后自动关闭输出。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # pwm_servo(1, mode="speed") 对应板卡丝印 S1 的连续旋转舵机。
        servo = lite.pwm_servo(1, mode="speed")

        with lite.control():
            try:
                # S1 以 25% 速度运行 2 秒，到时自动关闭 S1 输出。
                print("Running servo S1 for 2 seconds...")
                servo.set_speed(25, duration=2.0)

                # 字典同时设置 S1、S2；负速度表示相反方向。
                print("Running servos S1 and S2 in opposite directions...")
                lite.pwm_servos.set_speeds(
                    {
                        1: 25,
                        2: -25,
                    },
                    duration=2.0,
                )
            finally:
                # 正常结束、通信异常或 Ctrl+C 时都明确关闭全部六路 PWM 输出。
                lite.pwm_servos.stop()

        print("Continuous rotation servos stopped.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
