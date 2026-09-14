"""让 M1 直流电机分别向两个方向短暂转动。

本例的无参数 ``connect()`` 只适用于电脑当前只连接一台 USB Lite 的入门场景。
多设备环境必须先按第 17 课确认设备 ID，再明确传入 ``device_id``、``transport``
和该设备的 ``auth_token``。Token 只用于认证，不负责选机；多台使用相同 Token
也不会收到同一条广播动作命令。
"""

import pymotion as pm


try:
    # 未指定 transport 时使用默认 USB 连接。
    with pm.lite.connect() as lite:
        # motor(1) 选择连接在 M1 端口的直流电机。
        motor = lite.motor(1)
        print(f"Motor port: M{motor.port}")

        # 电机动作必须在有效的控制会话中执行。
        with lite.control():
            # 速度范围是 -100～100。正负号表示方向，绝对值表示指令百分比；
            # 这里的 30 表示 30% 指令，不表示 30 RPM。
            print("Running M1 in one direction...")
            motor.set_speed(30, duration=2.0)

            # 负值让同一个电机向相反方向转动。
            print("Running M1 in the opposite direction...")
            motor.set_speed(-30, duration=2.0)

            # 示例结束前明确停止 M1。
            motor.stop()

        print("M1 finished and stopped.")

except pm.lite.LiteError as exc:
    # 以简洁信息显示连接、控制或电机命令错误。
    print(f"PyMotion Lite error: {exc}")
