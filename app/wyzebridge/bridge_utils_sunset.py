from typing import Any
from datetime import datetime, timedelta
import time
import traceback
from astral import LocationInfo
from astral.sun import sun
from tzlocal import get_localzone
from wyzebridge.config import LATITUDE, LONGITUDE, SNAPSHOT_CAMERAS, SNAPSHOT_INT

def should_take_snapshot(snapshot_type: str, last_snap: float) -> bool:
    """
    Determine if a snapshot should be taken based on snapshot type, interval, and time of day.

    Args:
        snapshot_type (str): The type of snapshot (e.g., "rtsp").
        last_snap (float): The timestamp of the last snapshot.

    Returns:
        bool: True if a snapshot should be taken, False otherwise.
    """
    try:
        city = LocationInfo("CustomLocation", "CustomRegion", get_localzone().key, LATITUDE, LONGITUDE)
        s = sun(city.observer, date=datetime.now(get_localzone()))

        sunrise_start = s["sunrise"] - timedelta(minutes=90)
        sunrise_end = s["sunrise"] + timedelta(minutes=90)
        sunset_start = s["sunset"] - timedelta(minutes=90)
        sunset_end = s["sunset"] + timedelta(minutes=90)

        now = datetime.now(get_localzone())
        in_sunrise_window = sunrise_start <= now <= sunrise_end
        in_sunset_window = sunset_start <= now <= sunset_end

        interval = 30 if in_sunrise_window or in_sunset_window else SNAPSHOT_INT
    except Exception as e:
        print("Error calculating sunrise/sunset times:")
        print(traceback.format_exc())
        interval = SNAPSHOT_INT

    return snapshot_type == "rtsp" and (time.time() - last_snap >= interval)

def should_skip_snapshot(cam_name: str) -> bool:
    """
    Return if camera in list of permitted snapshot cameras

    Args:
        cam_name (str): Camera name to check

    Returns:
        bool: If camera is in filtered cameras, or no var set
    """
    if not SNAPSHOT_CAMERAS:
        return False
    if cam_name in SNAPSHOT_CAMERAS:
        return False
    return True
