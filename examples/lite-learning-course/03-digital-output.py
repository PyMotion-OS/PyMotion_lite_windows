"""数字输出。

可用端口为 GPIO9、10、14、38、39、40，只支持输出高、低电平。
板卡输出为 3.3 V 逻辑电平，只适合连接 LED、逻辑输入等小负载；连接 LED 时
必须串联限流电阻，不要直接驱动电机、舵机或其他大电流负载。

数字输出必须在 ``lite.control()`` 中设置。设备启动、退出控制、连接超时、急停
或故障时，所有数字输出都会恢复为低电平。
"""

import time

import pymotion as pm


GPIO = 14  # 可改为 9、10、14、38、39 或 40


try:
    with pm.lite.connect() as lite:
        output = lite.digital_output(GPIO)

        with lite.control():
            print(f"GPIO{output.gpio} is HIGH for 2 seconds...")
            try:
                output.set_high()
                time.sleep(2.0)
            finally:
                output.set_low()

        print(f"GPIO{output.gpio} is LOW.")
except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
