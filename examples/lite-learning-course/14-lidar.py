"""读取一帧 LD14P 雷达数据，再获取一圈完整扫描。

本例只读取雷达，不会让执行器动作。``frame()`` 返回最新一帧的 12 个测量点，
``scan()`` 返回一圈完整扫描。两种读取方式都支持 USB 和已配置 Token 的 Wi-Fi；
课程默认使用 USB。
"""

import pymotion as pm


try:
    with pm.lite.connect(transport="usb") as lite:
        # frame 适合低延迟观察局部数据；每帧固定包含一小段角度范围。
        frame = lite.lidar.frame(max_age=0.5)

        print("\nLidar frame")
        print(f"Sequence: {frame.sequence}")
        print(f"Point count: {len(frame.points)}")

        if frame.points:
            point = frame.points[0]
            print("First frame point:")
            print(f"  angle: {point.angle_deg:.2f} degrees")
            print(f"  distance: {point.distance_mm} mm")
            print(f"  confidence: {point.confidence}")

        # scan 会把连续帧拼成一圈，适合绘图、避障地图和点云处理。
        scan = lite.lidar.scan(max_age=0.5)

        print("\nLidar scan")
        print(f"Sequence: {scan.sequence}")
        print(f"Point count: {len(scan.points)}")
        print(f"Frame count: {scan.frame_count}")
        print(f"Complete: {scan.complete}")

        if scan.points:
            print("First five scan points:")
            for point in scan.points[:5]:
                print(
                    f"  angle={point.angle_deg:.2f} degrees, "
                    f"distance={point.distance_mm} mm, "
                    f"confidence={point.confidence}"
                )

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
