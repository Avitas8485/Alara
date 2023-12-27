from pydub import AudioSegment
from pydub.playback import play
import threading

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

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
        

    def trigger_alarm(self):
        try:
            sound = AudioSegment.from_mp3(self.sound_path)
        except FileNotFoundError:
            print(f"File not found: {self.sound_path}")
            return

        print(f"Time to wake up!")
        increase_volume = 0
        while self.alarm_active:
            play(sound)
            # increase volume
            with self.lock:
                current_volume = volume.GetMasterVolumeLevel() #type: ignore
                volume.SetMasterVolumeLevel(min(current_volume + increase_volume, volume.GetVolumeRange()[1]), None) #type: ignore
                increase_volume += 1
                if increase_volume > 10:
                    increase_volume = 0
            
    def handle_input(self):
        try:
            while True:
                user_input = input("Press 'q' to stop alarm: ").lower()
                if user_input == "q":
                    with self.lock:
                        self.alarm_active = False
                        break
        except KeyboardInterrupt:
            pass
        finally:
            self.alarm_thread.join()
            print("Alarm stopped. Good morning!")
            self.reset_volume()
            
    def reset_volume(self):
        # set volume to 20%
        volume.SetMasterVolumeLevel(volume.GetVolumeRange()[1] * 0.2, None) #type: ignore
            
    def start(self):
        with self.lock:
            self.alarm_active = True
        self.alarm_thread.start()
        self.input_thread.start()
        
    
if __name__ == "__main__":
    alarm = Alarm()
    alarm.start()
    
    
    
