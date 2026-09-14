"""短时间运行 M1 电机，并读取电机状态。

运行前请先完成 02-connection.py，并在当前终端中设置设备 Token。
"""

import time

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 选择板卡丝印为 M1 的电机端口，并先读取状态。
        motor = lite.motor(1)
        status = motor.status(max_age=1.0)

        # 确认端口、控制模式以及是否具有有效编码器反馈。
        print(f"Motor port: M{motor.port}")
        print(f"Control mode: {status.control_mode}")
        print(f"Has encoder: {status.has_encoder}")
        print(f"Feedback valid: {status.feedback_valid}")

        # 所有电机写操作都放在 control 代码块中。
        with lite.control():
            print("Running M1 at 30% for 2 seconds...")

            # 30 是 -100..100 范围内的归一化速度，不是 30 RPM。
            # duration=2.0 会在约 2 秒后自动撤销该路驱动命令。
            # 先进行一段短时开环运动，让用户观察速度和转动方向。
            drive_started = time.monotonic()
            motor.set_speed(30, duration=2.0)
            drive_elapsed = time.monotonic() - drive_started
            print(f"M1 drive command stopped after {drive_elapsed:.2f} seconds.")

            # max_age=0.0 要求刷新状态，再判断位置反馈是否可用。
            status = motor.status(max_age=0.0)

            # 只有反馈完整、角度有效且没有故障时才做位置操作。
            if (
                status.has_encoder
                and status.feedback_valid
                and status.actual_angle is not None
                and status.fault is None
            ):
                print("Running the optional position example...")

                # 等待机械轴真正静止，再把当前位置定义为后续命令的 0°。
                print("Waiting for M1 to become stationary, then setting zero...")
                settle_started = time.monotonic()
                motor.zero_position()
                settle_elapsed = time.monotonic() - settle_started
                print(f"M1 zero position set after {settle_elapsed:.2f} seconds.")

                # 使用 Quick Start 的位置演示参数，先移动到相对零点的绝对 45°。
                result = motor.move_to(
                    45,
                    speed=20,
                    tolerance=2,
                    timeout=8,
                )
                print(
                    "move_to:",
                    result.completed,
                    result.verified,
                )

                # 从当前位置再相对移动 -45°，回到零点附近。
                result = motor.move_by(
                    -45,
                    speed=20,
                    tolerance=2,
                    timeout=8,
                )
                print(
                    "move_by:",
                    result.completed,
                    result.verified,
                )
            else:
                # 没有有效位置反馈时直接跳过，不用定时转动模拟角度。
                print("Position example skipped: feedback unavailable.")

except pm.lite.LiteError as exc:
    # SDK 拒绝命令、设备故障或连接失败时显示真实错误。
    print(f"PyMotion Lite error: {exc}")
