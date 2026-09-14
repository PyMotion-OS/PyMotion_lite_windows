"""使用编码器反馈控制 M1 的角度位置。

本例可以独立运行，不依赖其他课程。程序先把 M1 当前静止位置设为临时 0°，再演示
``move_to()`` 和 ``move_by()``。设置零点本身不会驱动电机；如果运动方向异常、编码器
没有变化或未在限定时间内到位，电机会停止并报告错误。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 先确认 M1 端口支持编码器；feedback_valid=False 只表示本次启动后
        # 还没有观察到有效运动，不影响在静止状态下设置零点。
        motor = lite.motor(1)
        status = motor.status(max_age=0.5)

        if status.has_encoder:
            with lite.control():
                try:
                    # 等待电机静止，并把当前位置定义为本次程序使用的 0°。
                    motor.zero_position()

                    # 移动到以新零点为参考的绝对 45° 位置。
                    print("Moving M1 to 45 degrees...")
                    result = motor.move_to(
                        45,
                        speed=20,
                        tolerance=2,
                        timeout=8,
                    )
                    print(
                        f"move_to: completed={result.completed}, "
                        f"verified={result.verified}"
                    )

                    # 从当前角度相对移动 -45°，回到零点附近。
                    print("Moving M1 back by 45 degrees...")
                    result = motor.move_by(
                        -45,
                        speed=20,
                        tolerance=2,
                        timeout=8,
                    )
                    print(
                        f"move_by: completed={result.completed}, "
                        f"verified={result.verified}"
                    )
                finally:
                    # 零点在本次设备运行期间保留；再次调用 zero_position() 可以
                    # 将另一个静止位置重新定义为零点。
                    motor.stop()
                    print("M1 stopped; the current zero position remains active.")

        else:
            # 当前端口没有编码器时，不能使用角度位置控制。
            print("Position control skipped: M1 has no encoder capability.")

except pm.lite.LiteError as exc:
    # 位置、反馈和设备错误统一显示为 LiteError。
    print(f"PyMotion Lite error: {exc}")
