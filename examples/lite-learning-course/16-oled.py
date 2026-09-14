"""学习 OLED 临时文字、动态页面和页面切换。

每页最多 4 行，每行最多 21 个 ASCII 字符，最多 8 页。show() 用于临时显示，
show_pages() 用于自动轮播，show_page() 用于固定页面。page_index 从 0 开始，
所有时间参数的单位都是秒。本例结束时恢复默认欢迎页。
"""

import time

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        lite.oled.show("Connected", duration_seconds=2.0)
        time.sleep(2.0)

        # 花括号内容必须使用手册列出的动态字段名，设备会周期性替换为最新值。
        lite.oled.show_pages(
            [
                ["Sensor dashboard", "{ultrasonic.distance_cm}",
                 "{line_tracker.levels}"],
                ["Device", "{wifi.ip}", "{system.uptime_s}"],
            ],
            refresh_interval_seconds=0.5,
            page_interval_seconds=3.0,
        )
        time.sleep(7.0)

        # 手动选页会暂停自动轮播，索引 1 表示第二页。
        lite.oled.show_page(page_index=1)
        time.sleep(2.0)
        lite.oled.show_default()

        print("OLED page example completed and default page restored.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
