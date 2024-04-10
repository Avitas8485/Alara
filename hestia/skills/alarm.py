import threading
import sounddevice as sd
import soundfile as sf
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import logging
import time
import pythoncom
from hestia.skills.base_skill import Skill




logger = logging.getLogger(__name__)

class VolumeMute:
    """Class to mute and unmute the volume of the system.
    Note:
        This class uses the pycaw library to interact with the Windows Core Audio API.
        It is only compatible with Windows. In the future, this class could be extended
        to support other operating systems.
    Attributes:
        volume: An instance of the IAudioEndpointVolume class."""
    
    def __init__(self):
        pythoncom.CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    def get_mute_status(self)-> bool:
        """Get the mute status of the system.
        Returns:
            bool: The mute status of the system."""
        return self.volume.GetMute() # type: ignore

    def set_mute_status(self, mute_status: bool)-> None:
        """Set the mute status of the system.
        Args:
            mute_status (bool): The mute status to set."""
        try:
            self.volume.SetMute(mute_status, None) # type: ignore 
        except Exception as e:
            logger.error(f"Error setting mute status: {e}")
            raise

    def mute(self):
        """Mute the system volume."""
        self.set_mute_status(True)

    def unmute(self):
        """Unmute the system volume."""
        self.set_mute_status(False)


class Alarm(Skill):
    """An alarm clock skill that plays a sound when triggered.
    By itself, it can only play alarm and dismiss the alarm.
    However, it can be extended to include more features such as setting the alarm time, snoozing the alarm, etc.
    At present, you'll need to have a scheduled task to trigger the alarm at the desired time.
    Attributes:
        sound_path: The path to the sound file to play when the alarm is triggered.
        alarm_active: A boolean to indicate if the alarm is active.
        alarm_thread: A thread to trigger the alarm.
        input_thread: A thread to handle user input.
        lock: A lock to prevent 
        volume_mute: An instance of the VolumeMute class.
        output_device: The index of the output device to play the alarm sound on."""
    def __init__(self, sound_path: str="hestia/tools/sounds/star-dust-alarm-clock-114194.wav"):
        self.sound_path = sound_path
        self.alarm_active = False
        self.alarm_thread = threading.Thread(target=self.trigger_alarm)
        self.input_thread = threading.Thread(target=self.handle_input)
        self.lock = threading.Lock()
        self.volume_mute = VolumeMute()
        self.output_device = self.get_main_speaker()
        

    def get_main_speaker(self) -> int|None:
        """Get the index of the main speaker device."""
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if "Speakers" in device["name"]: # type: ignore
                return i
        return None

    def trigger_alarm(self):
        """Trigger the alarm and play the sound.
        Note:
            This method will increase the volume of the system every 5 seconds until the alarm is dismissed."""
        try:
            data, samplerate = sf.read(self.sound_path)
        except FileNotFoundError:
            logger.error(f"Sound file not found: {self.sound_path}")
            return
        print(f"Time to wake up!")
        increase_volume = 0
        sd.play(data, samplerate, device=self.output_device)
        if self.volume_mute.get_mute_status():
            self.volume_mute.unmute()
        
        while self.alarm_active:
            new_volume_level = max(-20.0 + increase_volume, -20.0)
            if new_volume_level > 0.0:
                new_volume_level = 0.0
            try:
                self.volume_mute.volume.SetMasterVolumeLevel(new_volume_level, None) # type: ignore
            except Exception as e:
                logger.error(f"Error setting volume: {e}")
                pass
            increase_volume += 5
            time.sleep(5)
        sd.stop()
        self.reset_volume()

    def reset_volume(self):
        """Reset the volume of the system to the default level."""
        self.volume_mute.volume.SetMasterVolumeLevel(-20.0, None) # type: ignore

    def handle_input(self):
        """Handle user input to dismiss or snooze the alarm."""
        try:
            while True:
                user_input = input("Press 'q' to stop alarm: ").lower()
                if user_input == "q":
                    self.dismiss_alarm()
                    break
                elif self.dismiss_alarm():
                    break
                elif self.snooze_alarm():
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.alarm_thread.join()
            print("Alarm stopped. Good morning!")
            self.reset_volume()
            

    def dismiss_alarm(self):
        """Dismiss the alarm."""
        
        with self.lock:
            self.alarm_active = False
            sd.stop()
            

    def snooze_alarm(self, snooze_duration: int=5):
        """Snooze the alarm for a specified duration."""
        with self.lock:
            self.alarm_active = False

        def snooze():
            """Snooze the alarm for a specified duration."""
            time.sleep(snooze_duration * 60)
            with self.lock:
                self.alarm_active = True
            self.start()

        snooze_thread = threading.Thread(target=snooze)
        snooze_thread.start()

    def start(self):
        """Start the alarm."""
        
        try:
            with self.lock:
                self.alarm_active = True
            self.alarm_thread.start()
            self.input_thread.start()
        except Exception as e:
            logger.error(f"Error starting alarm: {e}")
            raise

    def is_active(self)-> bool:
        """Check if the alarm is active."""
        with self.lock:
            return self.alarm_active


if __name__ == "__main__":
    alarm = Alarm()
    alarm.start()