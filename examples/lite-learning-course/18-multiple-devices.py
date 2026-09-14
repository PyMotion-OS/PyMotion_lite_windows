"""发现当前可见的 Lite，并通过稳定的设备 ID 明确选择一台设备。

只有一台设备时会自动选择；存在多台设备时，请把目标 ID 填入 DEVICE_ID。
本课程只发现和选择设备，不建立控制连接，因此不需要任何设备的 Token。
真正连接所选设备时才需要它自己的 Token，连接生命周期将在下一课介绍。
"""

import pymotion as pm


# 只有一台 Lite 时保持为 None；有多台时填写需要连接的设备 ID。
DEVICE_ID = None


def select_device(devices):
    """选择唯一设备；无法明确选择时返回 None。"""

    if not devices:
        print("No Lite device found.")
        return None

    print(f"Found {len(devices)} Lite device(s):")
    for device in devices:
        print(f"- {device.device_id}, preferred link: {device.preferred_transport}")

    if DEVICE_ID is not None:
        for device in devices:
            if device.device_id == DEVICE_ID:
                return device
        print(f"Configured device was not found: {DEVICE_ID}")
        return None

    if len(devices) == 1:
        print("One Lite device found; selecting it automatically.")
        return devices[0]

    print("More than one Lite device was found.")
    print("Copy one listed ID into DEVICE_ID, then run this example again.")
    return None


try:
    devices = pm.lite.list_devices()
    selected = select_device(devices)

    if selected is not None:
        print("Device selected")
        print(f"Device ID: {selected.device_id}")
        print(f"Preferred link: {selected.preferred_transport}")
        print("No connection was opened, so no authentication Token was required.")

except pm.lite.LiteError as exc:
    print(f"PyMotion Lite error: {exc}")
