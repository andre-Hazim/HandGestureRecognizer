from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# Get system audio device
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

def set_volume(level):
    """Set system volume (0.0 = mute, 1.0 = max)."""
    level = max(0.0, min(1.0, level))  # Ensure within bounds
    volume.SetMasterVolumeLevelScalar(level, None)
    print(f"Volume set to {level * 100:.0f}%")