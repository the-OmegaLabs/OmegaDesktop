import platform
import subprocess
import threading
import psutil
import cpuinfo
import socket
import playsound

class SoundSystem:
    def getSpeakerVolume() -> int:
        if platform.system() == 'Windows':
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from comtypes import CLSCTX_ALL

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = interface.QueryInterface(IAudioEndpointVolume)
            volume_scalar = volume.GetMasterVolumeLevelScalar()

            return round(volume_scalar * 100)

        
        elif platform.system() == 'Linux':
            try:
                output = subprocess.check_output(["amixer", "get", "Master"])
                lines = output.decode().splitlines()

                for line in lines:
                    if "%" in line and "Mono:" in line or "Front Left:" in line or "Right:" in line:
                        parts = line.strip().split()
                        for part in parts:
                            if part.endswith("%") and part.startswith("["):
                                return int(part[1:-2]) if part.endswith("]%") else int(part[1:-1])
            except Exception as e:
                return None
            
    def playSound(path: str):
        threading.Thread(target=playsound.playsound, args=[path], daemon=True).start()
        

