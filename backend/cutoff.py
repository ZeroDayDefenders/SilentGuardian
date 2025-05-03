import threading
import time

from backend.audio_core import SoundManager
from backend.config import Config
from backend.logger import Logger


class CutOff:
    def __init__(self, sound_manager, debug):
        self.config = Config()
        self.sound_manager = sound_manager
        self.debug = debug
        self.normal_level = self.config.normal_sound_level / 100
        self.reduced_level = self.config.reduced_sound_level / 100
        self.duration = self.config.fade_duration
        self.is_muted = False
        self.is_faded = False
        self.is_running = False
        self.selected_mode_index = None
        self.logger = Logger()
        self.previous_process = self.sound_manager.process_name
        self.should_cutoff_run = False

        self.fade_thread = None
        self.is_fading = False
        self.fade_direction = None
        self.current_volume = None

    def set(self, index):
        self.selected_mode_index = index

    def apply(self, index):
        self.set(index)
        self.config.selectedCutoff = index
        self.config.save()

        message = ""

        if self.selected_mode_index == 0:
            message = "Changed to hard"
        elif self.selected_mode_index == 1:
            message = "Changed to fade"
        elif self.selected_mode_index == 2:
            message = "Changed to mute / unmute"
        elif self.selected_mode_index == 3:
            message = "Changed to hard down / fade up"
        elif self.selected_mode_index == 4:
            message = "Changed to fade down / hard up"
        elif self.selected_mode_index == 5:
            message = "Changed to mute / fade up"
        elif self.selected_mode_index == 6:
            message = "Changed to mute / hard up"
        else:
            message = "Selected incorrect index"
            raise Exception('Incorrect index')

        if self.debug:
            print(message)
        self.logger.log("Cutoff", message)

    def run(self):
        if self.selected_mode_index is None:
            if self.debug:
                print("No mode selected")
            self.logger.log("Cutoff", "No mode selected")
            raise Exception('Cutoff index not selected')

        self.duration = self.config.fade_duration
        self.normal_level = self.config.normal_sound_level / 100
        self.reduced_level = self.config.reduced_sound_level / 100

        if self.selected_mode_index == 0:
            self.hard()
        elif self.selected_mode_index == 1:
            self.fade()
        elif self.selected_mode_index == 2:
            self.mute_unmute()
        elif self.selected_mode_index == 3:
            self.hard_cut_fade_up()
        elif self.selected_mode_index == 4:
            self.fade_down_hard_up()
        elif self.selected_mode_index == 5:
            self.mute_fade_up()
        elif self.selected_mode_index == 6:
            self.mute_hard_up()
        else:
            if self.debug:
                print("Tried to run incorrect cutoff")
            self.logger.log("Cutoff", "Tried to run incorrect cutoff")
            raise Exception('Incorrect index')

    def set_threshold_reached(self, threshold):
        self.sound_manager.set_threshold_reached(threshold)

    def hard(self):
        if self.is_faded:
            self.sound_manager.set_volume(self.normal_level)
        else:
            self.sound_manager.set_volume(self.reduced_level)
        self.is_faded = not self.is_faded

    def fade(self):
        if self.is_faded:
            self.fade_audio(self.normal_level)
        else:
            self.fade_audio(self.reduced_level)
        self.is_faded = not self.is_faded

    def mute_unmute(self):
        if self.is_muted:
            self.sound_manager.unmute()
        else:
            self.sound_manager.mute()
        self.is_muted = not self.is_muted

    def hard_cut_fade_up(self):
        if self.is_faded:
            self.fade_audio(self.normal_level)
        else:
            self.sound_manager.set_volume(self.reduced_level)
        self.is_faded = not self.is_faded

    def fade_down_hard_up(self):
        if self.is_faded:
            self.sound_manager.set_volume(self.normal_level)
        else:
            self.fade_audio(self.reduced_level)
        self.is_faded = not self.is_faded

    def mute_fade_up(self):
        if not self.is_muted:
            self.sound_manager.set_volume(0)
            self.sound_manager.mute()
        else:
            self.sound_manager.unmute()
            self.fade_audio(self.normal_level)
        self.is_muted = not self.is_muted

    def mute_hard_up(self):
        if not self.is_muted:
            self.sound_manager.set_volume(0)
            self.sound_manager.mute()
        else:
            self.sound_manager.unmute()
            self.sound_manager.set_volume(self.normal_level)
        self.is_muted = not self.is_muted

    def fade_audio(self, target_level):
        current_level = self.sound_manager.process_volume()
        if current_level is None:
            return

        self.current_volume = current_level

        self.fade_direction = 'up' if target_level > current_level else 'down'

        if self.is_fading:
            if self.fade_thread is not None:
                self.fade_thread.stop()
                self.fade_thread = None

        self.is_fading = True
        self.fade_thread = FadeThread(
            self.debug,
            self.sound_manager,
            target_level,
            self.duration,
            self
        )
        self.fade_thread.start()

    def interrupt_fade_if_needed(self):
        if self.is_fading and self.fade_direction == 'up':
            if self.fade_thread is not None:
                self.current_volume = self.sound_manager.process_volume()
                self.fade_thread.stop()
                self.fade_thread = None
                if self.current_volume is not None:
                    self.start_fade_down()
            self.is_fading = False
            self.is_faded = True
            return True
        return False

    def start_fade_down(self):
        self.fade_audio(self.reduced_level)


class FadeThread(threading.Thread):
    def __init__(self, debug, sound_manager, target_level, duration, cutoff_instance):
        super().__init__()
        self.debug = debug
        self.sound_manager = sound_manager
        self.target_level = target_level
        self.duration = duration
        self.cutoff_instance = cutoff_instance
        self._stop_event = threading.Event()
        self.daemon = True

    def stop(self):
        self._stop_event.set()

    def run(self):
        current_level = self.sound_manager.process_volume()
        if current_level is None:
            self.cutoff_instance.is_fading = False
            return

        start_time = time.time()

        while not self._stop_event.is_set():
            elapsed = time.time() - start_time
            if elapsed > self.duration:
                break

            try:
                new_level = current_level + (self.target_level - current_level) * (elapsed / self.duration)
                self.sound_manager.set_volume(new_level)
            except Exception as e:
                Logger().log("FadeThread", f"Error during fade: {e}")
                if self.debug:
                    print(f"Error during fade: {e}")
                break

            time.sleep(0.01)

        if not self._stop_event.is_set():
            try:
                self.sound_manager.set_volume(self.target_level)
            except Exception as e:
                Logger().log("FadeThread", f"Error while setting the final level: {e}")
                if self.debug:
                    print(f"Error while setting the final level: {e}")

        self.cutoff_instance.is_fading = False
        self.cutoff_instance.fade_thread = None
