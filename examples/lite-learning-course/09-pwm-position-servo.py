"""控制两路已经由用户确认的 0～180°位置 PWM 舵机。

警告：运行前必须确认 `SERVO_1_PORT`、`SERVO_2_PORT` 对应端口均已换成位置舵机，
并清空连杆附近空间。对 360°连续旋转舵机发送角度脉宽会被解释成持续转动，
而不是移动到指定角度。

位置 PWM 舵机没有角度反馈，程序只能发送目标角度，不能读取舵机是否已经到位。
本例先演示单路控制，再让两路执行“归中位→分开移动→回中位”，因此重复运行时
两路都能看到明确动作。``stop()`` 会关闭 PWM 输出，舵机随后不再主动保持角度。
"""

import time

import pymotion as pm


SERVO_1_PORT = 4
SERVO_2_PORT = 5
MOVE_WAIT_SECONDS = 1.0


def main() -> None:
    try:
        with pm.lite.connect() as lite:
            # 同一入口通过 mode 明确物理舵机类型；错误模式不会发送动作命令。
            servo = lite.pwm_servo(SERVO_1_PORT, mode="position")

            with lite.control():
                try:
                    print(f"Moving position servo S{servo.port} to 45 degrees...")
                    servo.move_to(45)
                    time.sleep(MOVE_WAIT_SECONDS)

                    # 先把两路都归到 90°，建立每次运行都一致的动作起点。
                    print(
                        f"Centering servos S{SERVO_1_PORT} and S{SERVO_2_PORT}..."
                    )
                    lite.pwm_servos.move_to(
                        {
                            SERVO_1_PORT: 90,
                            SERVO_2_PORT: 90,
                        }
                    )
                    time.sleep(MOVE_WAIT_SECONDS)

                    # 两路向相反方向移动，确保第二路在每次运行中都有可见行程。
                    print(
                        f"Moving S{SERVO_1_PORT} to 45 degrees and "
                        f"S{SERVO_2_PORT} to 135 degrees..."
                    )
                    lite.pwm_servos.move_to(
                        {
                            SERVO_1_PORT: 45,
                            SERVO_2_PORT: 135,
                        }
                    )
                    time.sleep(MOVE_WAIT_SECONDS)

                    print("Returning both position servos to 90 degrees...")
                    lite.pwm_servos.move_to(
                        {
                            SERVO_1_PORT: 90,
                            SERVO_2_PORT: 90,
                        }
                    )
                    time.sleep(MOVE_WAIT_SECONDS)
                finally:
                    # 正常结束、异常或 Ctrl+C 都关闭全部 PWM 输出。
                    lite.pwm_servos.stop()

            print("PWM position servo commands completed and outputs disabled.")

    except pm.lite.LiteError as exc:
        print(f"PyMotion Lite error: {exc}")


if __name__ == "__main__":
    main()
