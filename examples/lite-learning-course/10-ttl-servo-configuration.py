"""逐只配置飞特 TTL 舵机的 ID 和统一运行参数。

新舵机投入使用前，应先完全断电，并确保 TTL 总线上只连接这一只待配置舵机。
程序会自动尝试受支持的出厂波特率、识别 SCS0002 或 SCS125，然后把目标 ID、
统一通信参数并完整读回确认。

禁止带电插拔。配置多只舵机时，每次只连接一只，依次修改 ``TARGET_ID`` 并运行；
全部配置完成且 ID 互不重复后，再断电将它们连接到同一总线。
"""

import pymotion as pm


TARGET_ID = 1
CONFIRMATION = f"CONFIGURE-TTL-{TARGET_ID}"


try:
    confirmation = input(
        "请确认设备已完全断电换线、总线上只接一只 TTL 舵机并已重新上电。\n"
        f"输入 {CONFIRMATION} 将它配置为 ID {TARGET_ID}："
    ).strip()
    if confirmation != CONFIRMATION:
        print("确认文本不匹配，未修改舵机配置。")
    else:
        with pm.lite.connect() as lite:
            with lite.control():
                result = lite.ttl_servos.configure(new_id=TARGET_ID)

        print(f"TTL servo ID: {result.old_id} -> {result.id}")
        print(f"Model: {result.model}")
        print(f"Maximum angle: {result.max_angle:.0f} degrees")
        print(f"Baudrate: {result.baudrate}")
        print(f"Position limits: {result.min_position}..{result.max_position}")
        print("Configuration verified. Power off and label this servo before continuing.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
