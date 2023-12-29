import threading
import pygame

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
#from hestia.lib.hestia_logger import logger

class VolumeMute:
    
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        
    def get_mute_status(self):
        return self.volume.GetMute()
    
    def set_mute_status(self, mute_status):
        self.volume.SetMute(mute_status, None)
        
    def mute(self):
        self.set_mute_status(True)
        
    def unmute(self):
        self.set_mute_status(False)
        

# get default audio device using PyCAW
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))




   

class Alarm:
    def __init__(self, sound_path: str="hestia/tools/system_and_utility/rain_alarm.mp3"):
        self.sound_path = sound_path
        self.alarm_active = False
        self.alarm_thread = threading.Thread(target=self.trigger_alarm)
        self.input_thread = threading.Thread(target=self.handle_input)
        self.lock = threading.Lock()
        self.volume_mute = VolumeMute()

    def trigger_alarm(self):
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(self.sound_path)
        except pygame.error:
#            logger.error(f"Sound file not found: {self.sound_path}")
            return

        print(f"Time to wake up!")
        increase_volume = 0
        pygame.mixer.music.play()
        if self.volume_mute.get_mute_status():
            self.volume_mute.unmute()
            
        while self.alarm_active:  
            # increase volume by 5% every 5 seconds
            new_volume_level = max(-20.0 + increase_volume, -20.0)
            volume.SetMasterVolumeLevel(new_volume_level, None) #type: ignore
            increase_volume += 5
            time.sleep(5)
        pygame.mixer.music.stop()
        self.reset_volume()
        
            
            
    def handle_input(self):
        try:
            while True:
                user_input = input("Press 'q' to stop alarm: ").lower()
                if user_input == "q":
                    with self.lock:
                        self.alarm_active = False
                        pygame.mixer.music.stop()
                        break
        except KeyboardInterrupt:
            pass
        finally:
            self.alarm_thread.join()
            print("Alarm stopped. Good morning!")
            self.reset_volume()
            
    def reset_volume(self):
        # set volume to 20%
        volume.SetMasterVolumeLevel(-20.0, None) #type: ignore
            
    def start(self):
        with self.lock:
            self.alarm_active = True
        self.alarm_thread.start()
        self.input_thread.start()
        
    def is_active(self):
        with self.lock:
            return self.alarm_active
        
    

        
    
    
if __name__ == "__main__":
    alarm = Alarm()
    alarm.start()
    import time
    while alarm.is_active():
        time.sleep(1)
    print("Alarm stopped. Good morning!")
    
    
