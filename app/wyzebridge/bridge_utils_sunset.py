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

        # Calculate dynamic window boundaries
        dawn_to_sunrise = (s["sunrise"] - s["dawn"]).total_seconds()
        sunset_to_dusk = (s["dusk"] - s["sunset"]).total_seconds()

        sunrise_start = s["dawn"] - timedelta(hours=1)
        sunrise_end = s["sunrise"] + timedelta(seconds=dawn_to_sunrise) + timedelta(hours=1)
        sunset_start = s["sunset"] - timedelta(seconds=sunset_to_dusk) - timedelta(hours=1)
        sunset_end = s["dusk"] + timedelta(hours=1)

        # Determine if current time is within the windows
        now = datetime.now(get_localzone())
        in_sunrise_window = sunrise_start <= now <= sunrise_end
        in_sunset_window = sunset_start <= now <= sunset_end

        # Interval selection
        interval = 30 if in_sunrise_window or in_sunset_window else SNAPSHOT_INT
    except Exception as e:
        # Log error with traceback
        print("Error calculating sunrise/sunset times:")
        print(traceback.format_exc())
        interval = SNAPSHOT_INT

    # Return whether a snapshot should be taken
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
