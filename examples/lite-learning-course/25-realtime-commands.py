"""使用实时命令连续更新 M1、M2 的速度。

两个电机先从 0% 加速到 30%，再减速至停止。``valid_for`` 表示每条命令的
最长有效时间；如果下一条命令未按时到达，设备会自动停止对应电机。正常发送
结束后也应调用 ``stop()`` 主动停止电机。

运行前请架空车轮并清理运动范围。若某个电机的安装方向相反，请将对应的
``M1_DIRECTION`` 或 ``M2_DIRECTION`` 改为 -1。确认安全后再把
``RUN_MOTORS`` 改为 True。
"""

import time

import pymotion as pm


DEVICE_ID = None
TRANSPORT = "wifi"
RUN_MOTORS = True

M1_DIRECTION = 1
M2_DIRECTION = 1
PEAK_SPEED = 30
RAMP_DURATION = 5.0

RAMP_STEPS = PEAK_SPEED
# 每 1°/1% 更新一次目标；本例为约 6 Hz，valid_for=0.5 秒可覆盖短暂 Wi-Fi 抖动。
COMMAND_INTERVAL = RAMP_DURATION / RAMP_STEPS


def get_motor_speeds(step):
    """计算当前步骤中 M1、M2 应使用的速度。"""
    if step <= RAMP_STEPS:
        speed = step
    else:
        speed = 2 * RAMP_STEPS - step

    return {
        1: M1_DIRECTION * speed,
        2: M2_DIRECTION * speed,
    }


def main():
    """发送一次加速、减速实时命令序列。"""

    if not RUN_MOTORS:
        print("Realtime motor commands are disabled.")
        print("Raise the wheels, clear the surroundings, then set RUN_MOTORS = True.")
        return

    with pm.lite.connect(DEVICE_ID, transport=TRANSPORT, timeout=15.0) as lite:
        with lite.control(timeout=5.0):
            with lite.realtime.open(
                command_targets={"motor_speeds": [1, 2]},
                frequency="medium",
            ) as session:
                motor_commands = session.commands.motor_speeds

                print("Starting two-motor speed profile.")
                try:
                    for step in range(2 * RAMP_STEPS + 1):
                        speeds = get_motor_speeds(step)

                        # 命令采用“最新值优先”；链路来不及发送时旧的待发值会被替换。
                        # 0.5 秒内没有后续命令时，设备使目标失效并停止对应电机。
                        motor_commands.write(speeds, valid_for=0.5)
                        print(f"M1={speeds[1]}%, M2={speeds[2]}%")

                        if step < 2 * RAMP_STEPS:
                            time.sleep(COMMAND_INTERVAL)
                finally:
                    motor_commands.stop()
                    print("Motors stopped.")

                stats = motor_commands.stats()
                print(f"Commands sent: {stats.sent}")
                print(f"Commands replaced: {stats.replaced}")


try:
    main()
except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
