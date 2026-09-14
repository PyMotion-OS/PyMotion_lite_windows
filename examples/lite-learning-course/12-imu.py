"""读取一次 MPU6050 IMU 数据。

本例只读取传感器，不会让任何执行器动作。
加速度单位为 mm/s²，角速度单位为 rad/s，姿态角单位为度。
``max_age=0.5`` 表示只接受采集时间距当前不超过 0.5 秒的数据。

X、Y、Z 是设备上 IMU 的三个固定坐标轴。roll 表示绕 X 轴旋转，pitch 表示绕
Y 轴旋转，正方向遵循右手定则。MPU6050 没有磁力计，因此本例不提供 yaw。

"""

import pymotion as pm


try:
    with pm.lite.connect() as lite:
        imu = lite.imu(max_age=0.5)

        # 数据无效或过旧时，数值字段为 None，不会用 0 冒充真实测量值。
        acceleration = imu.acceleration_mm_s2
        if acceleration is not None:
            print("Acceleration (mm/s^2):")
            print(f"  x: {acceleration.x:.2f}")
            print(f"  y: {acceleration.y:.2f}")
            print(f"  z: {acceleration.z:.2f}")
        else:
            print("Acceleration: unavailable")

        angular_velocity = imu.angular_velocity_rad_s
        if angular_velocity is not None:
            print("Angular velocity (rad/s):")
            print(f"  x: {angular_velocity.x:.4f}")
            print(f"  y: {angular_velocity.y:.4f}")
            print(f"  z: {angular_velocity.z:.4f}")
        else:
            print("Angular velocity: unavailable")

        # orientation_deg 提供 roll 和 pitch，单位都是度。
        orientation = imu.orientation_deg
        if orientation is not None:
            print("Orientation (degrees):")
            print(f"  roll: {orientation.roll:.2f}")
            print(f"  pitch: {orientation.pitch:.2f}")
        else:
            print("Orientation: unavailable")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
