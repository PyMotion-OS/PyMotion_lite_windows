"""读取超声波、五路循迹、环境光和颜色传感器。

本例只读取传感器，不会让任何执行器动作。
距离单位为 mm，环境光单位为 lux；循迹输出五路电平和对应的黑线检测结果，
颜色传感器输出红、绿、蓝和清光四路原始计数。
"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        # 分别读取四类传感器的最新数据。
        ultrasonic = lite.ultrasonic(max_age=0.5)
        line_tracker = lite.line_tracker(max_age=0.5)
        ambient_light = lite.ambient_light(max_age=0.5)
        color = lite.color(max_age=0.5)

        print("\nUltrasonic")
        # 无回波通常表示目标超出量程；None 表示“没有可靠距离”，不能当作 0 mm。
        if ultrasonic.distance_mm is not None:
            print(f"Distance: {ultrasonic.distance_mm:g} mm")
        else:
            print("Distance: unavailable")

        print("\nLine tracker")
        # 五个元素依次对应板上的五路循迹输入，顺序不可自行重排。
        if line_tracker.levels is not None:
            print(f"Levels: {line_tracker.levels}")
        else:
            print("Levels: unavailable")

        if line_tracker.detected is not None:
            print(f"Black line detected: {line_tracker.detected}")
        else:
            print("Black line detected: unavailable")

        print("\nAmbient light")
        if ambient_light.illuminance_lux is not None:
            print(f"Illuminance: {ambient_light.illuminance_lux:g} lux")
        else:
            print("Illuminance: unavailable")

        print("\nColor")
        if (
            color.red is not None
            and color.green is not None
            and color.blue is not None
            and color.clear is not None
        ):
            print(f"Red: {color.red}")
            print(f"Green: {color.green}")
            print(f"Blue: {color.blue}")
            print(f"Clear: {color.clear}")
        else:
            print("Color values: unavailable")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
