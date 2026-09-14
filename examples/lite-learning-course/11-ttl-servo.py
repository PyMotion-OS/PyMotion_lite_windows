"""分别演示 TTL 舵机的位置模式和速度模式。

运行前通过 ``DEMO_MODE`` 选择 ``"position"`` 或 ``"speed"``。一次运行只演示
一种模式，避免同一只舵机在连续旋转后立刻切回有限角度位置模式而发生大范围寻位。

位置模式预期现象：ID1 和 ID2 先到各自角度范围的中心；ID1 移动约 40°；随后
ID1 返回中心且 ID2 移动约 40°；最后两只舵机都回到中心并检查位置反馈。

速度模式预期现象：ID1 先以 20% 速度连续旋转 3 秒并停止；随后 ID1、ID2 以
相反方向和 20% 速度同时旋转 3 秒并停止。结束后两只舵机仍保持速度模式。

``configure_mode()`` 是低频配置操作，实际切换时可能写入舵机 EPROM，不能放进
高频循环。切换模式前应拆除连杆、清空舵臂范围并接好稳定的外部电源。
"""

import time

import pymotion as pm


DEMO_MODE = "position"
MOVE_DURATION_SECONDS = 2.0
MOVE_WAIT_SECONDS = 2.4
SPEED_PERCENT = 20.0
SPEED_DURATION_SECONDS = 3.0
MOVE_OFFSET_DEG = 40.0
RETURN_TOLERANCE_DEG = 5.0


def ensure_declared_mode(*servos) -> None:
    """仅在舵机实际模式与对象声明不同时执行一次持久化配置。"""

    for servo in servos:
        if servo.read_mode() != servo.mode:
            servo.configure_mode()


def run_position_demo(lite: pm.lite.Lite) -> None:
    servo_1 = lite.ttl_servo(1, mode="position")
    servo_2 = lite.ttl_servo(2, mode="position")
    center_1 = servo_1.max_angle / 2.0
    center_2 = servo_2.max_angle / 2.0
    target_1 = center_1 + MOVE_OFFSET_DEG
    target_2 = center_2 + MOVE_OFFSET_DEG

    ensure_declared_mode(servo_1, servo_2)

    print("Centering TTL servos ID1 and ID2...")
    lite.ttl_servos.move_to(
        {servo_1: center_1, servo_2: center_2},
        duration=MOVE_DURATION_SECONDS,
    )
    time.sleep(MOVE_WAIT_SECONDS)

    print(f"Moving TTL servo 1: {center_1:.1f} -> {target_1:.1f} degrees...")
    servo_1.move_to(target_1, duration=MOVE_DURATION_SECONDS)
    time.sleep(MOVE_WAIT_SECONDS)

    print("Returning ID1 to center while ID2 moves about 40 degrees...")
    lite.ttl_servos.move_to(
        {servo_1: center_1, servo_2: target_2},
        duration=MOVE_DURATION_SECONDS,
    )
    time.sleep(MOVE_WAIT_SECONDS)

    print("Returning both TTL servos to their center positions...")
    lite.ttl_servos.move_to(
        {servo_1: center_1, servo_2: center_2},
        duration=MOVE_DURATION_SECONDS,
    )
    time.sleep(MOVE_WAIT_SECONDS)

    final_1 = servo_1.status().angle_deg
    final_2 = servo_2.status().angle_deg
    error_1 = abs(final_1 - center_1)
    error_2 = abs(final_2 - center_2)
    print(
        "Final position feedback: "
        f"ID1={final_1:.2f}° (error {error_1:.2f}°), "
        f"ID2={final_2:.2f}° (error {error_2:.2f}°)"
    )
    if error_1 > RETURN_TOLERANCE_DEG or error_2 > RETURN_TOLERANCE_DEG:
        raise RuntimeError("TTL servo did not return to its center position")

    lite.ttl_servos.stop()


def run_speed_demo(lite: pm.lite.Lite) -> None:
    servo_1 = lite.ttl_servo(1, mode="speed")
    servo_2 = lite.ttl_servo(2, mode="speed")

    ensure_declared_mode(servo_1, servo_2)

    print("TTL servo 1 runs at 20% speed for 3 seconds...")
    servo_1.set_speed(SPEED_PERCENT, duration=SPEED_DURATION_SECONDS)

    print("TTL servos ID1 and ID2 run in opposite directions for 3 seconds...")
    lite.ttl_servos.set_speeds(
        {servo_1: SPEED_PERCENT, servo_2: -SPEED_PERCENT},
        duration=SPEED_DURATION_SECONDS,
    )
    lite.ttl_servos.stop()
    print("Speed outputs stopped; both servos remain configured in speed mode.")


try:
    with pm.lite.connect() as lite:
        with lite.control():
            if DEMO_MODE == "position":
                run_position_demo(lite)
            elif DEMO_MODE == "speed":
                run_speed_demo(lite)
            else:
                raise ValueError("DEMO_MODE must be 'position' or 'speed'")

        print("TTL servo demonstration completed.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
except (RuntimeError, ValueError) as exc:
    print(f"TTL servo demonstration failed: {exc}")
