import os
from dataclasses import dataclass, asdict
import json


@dataclass
class Config:
    key_actions: dict
    # UI
    selectedScale: int
    selectedTheme: int
    language: str
    auto_launch: bool
    minimize_to_tray: bool
    scaleTitlebar: bool
    scaleMessageBox: bool
    # INPUT
    selectedInput1: int
    selectedInput2: int
    selectedCutoff: int
    threshold1: int
    threshold_not_reached1: int
    threshold2: int
    threshold_not_reached2: int
    # APP
    selectedApp: str
    normal_sound_level: int
    reduced_sound_level: int
    fade_duration: int

    scale = {
        0: {
            'scale': 1.0,
            'font-size-bigger': '15px',
            'font-size-smaller': '14px',
            'font-size-smallest': '13px',
            'font-size-footer': '12px',
            'font-size-dialog-bigger': '18px',
            'font-size-dialog-smaller': '16px',
        },
        1: {
            'scale': 1.25,
            'font-size-bigger': '18px',
            'font-size-smaller': '17px',
            'font-size-smallest': '16px',
            'font-size-footer': '15px',
            'font-size-dialog-bigger': '22px',
            'font-size-dialog-smaller': '20px',
        },
        2: {
            'scale': 1.5,
            'font-size-bigger': '22px',
            'font-size-smaller': '21px',
            'font-size-smallest': '19px',
            'font-size-footer': '18px',
            'font-size-dialog-bigger': '27px',
            'font-size-dialog-smaller': '24px',
        },
        3: {
            'scale': 1.75,
            'font-size-bigger': '26px',
            'font-size-smaller': '25px',
            'font-size-smallest': '24px',
            'font-size-footer': '21px',
            'font-size-dialog-bigger': '31px',
            'font-size-dialog-smaller': '28px',
        },
        4: {
            'scale': 2.0,
            'font-size-bigger': '30px',
            'font-size-smaller': '29px',
            'font-size-smallest': '28px',
            'font-size-footer': '24px',
            'font-size-dialog-bigger': '36px',
            'font-size-dialog-smaller': '32px',
        }
    }

    colorMode = {
        0: {  # LIGHT
            'windowBackground': '#ffffff',
            'text-color': '#000000',
            'widgetBackground': '#F2F2F2',
            'primaryColor': '#3498DB',
            'secondaryColor': '#F0932B',
            'activeWidget': '#D9D9D9',
            'hoverWidget': '#C1C1C1',
            'pressedWidget': '#9A9A9A',
            'tipMouseWidget': '#E8E8E8',
            'tipBackground': '#F2F2F2',
            'lineColor': '#CCCCCC',
            'sliderBackground': '#D9D9D9',
            'footerColor': '#CCCCCC',
            'scrollBackground': '#f0f0f0',
            'scrollHandle': '#c0c0c0',
        },
        1: {  # DARK
            'windowBackground': '#18191A',
            'text-color': '#CCCCCC',
            'widgetBackground': '#242526',
            'primaryColor': '#3498DB',
            'secondaryColor': '#F0932B',
            'activeWidget': '#2D2E2F',
            'hoverWidget': '#393A3B',
            'pressedWidget': '#606162',
            'tipMouseWidget': '#242526',
            'tipBackground': '#202122',
            'lineColor': '#3A3B3C',
            'sliderBackground': '#242526',
            'footerColor': '#3A3B3C',
            'scrollBackground': '#242526',
            'scrollHandle': '#2D2E2F',
        }
    }

    # Default English translation
    default_translation = {
        "language_name": "ENGLISH",
        "select_input_to_listen": "Select input to listen",
        "select_app_to_control": "Select app to control",
        "cutoff_mode": "Cutoff mode",
        "binds": "Binds",
        "settings": "Settings",
        "threshold": "Threshold",
        "threshold_not_reached": "Threshold not reached",
        "inputs": "Inputs",
        "select_first_input": "Select First Input",
        "select_second_input": "Select Second Input",
        "swap_inputs": "Swap Inputs",
        "deselect_second_input": "Deselect Second Input",
        "input": "Input",
        "threshold_of_second_input": "Threshold of second input",
        "threshold_not_reached_second": "Threshold not reached second",
        "create": "Create",
        "accept": "Accept",
        "cancel": "Cancel",
        "add": "Add",
        "remove": "Remove",
        "clear": "Clear",
        "normal_sound_level": "Normal sound level",
        "turned_down_to_level": "Turned down to level",
        "apps": "Apps",
        "add_bind": "Add bind",
        "key_bind": "Key bind",
        "actions": "Actions",
        "this_combination_exists": "This combination exists!",
        "are_you_sure": "Are you sure?",
        "you_want_to_delete_this_bind": "You want to delete this bind?",
        "you_want_to_clear_all_binds": "You want to clear all binds?",
        "no_binds_create_one": "No binds, create one!",
        "cutoff_modes": "Cutoff modes",
        "fade_duration": "Fade duration",
        "hard": "HARD",
        "fade": "FADE",
        "show": "Show",
        "quit": "Quit",
        "auto_launch_on_windows_startup": "Auto launch on windows startup",
        "minimize_to_app_tray_when_closing": "Minimize to app tray when closing",
        "scale_titlebar": "Scale titlebar",
        "scale_message_box": "Scale message box",
        "scale": "Scale",
        "theme": "Theme",
        "light": "LIGHT",
        "dark": "DARK",
        "language": "Language",
        "restart_required_for_changes": "Restart required for changes",
        "mute_controlled_app": "MUTE CONTROLLED APP",
        "start_stop_app": "START / STOP APP",
        "disable_input_1": "DISABLE INPUT 1",
        "disable_input_2": "DISABLE INPUT 2",
        "cutoff_mode_hard": "CUTOFF MODE HARD",
        "cutoff_mode_fade": "CUTOFF MODE FADE",
        "mute_unmute": "MUTE / UNMUTE",
        "hard_cut_fade_up": "HARD CUT + FADE UP",
        "fade_down_hard_up": "FADE DOWN + HARD UP",
        "mute_fade_up": "MUTE + FADE UP",
        "mute_hard_up": "MUTE + HARD UP",
        "version": "VERSION"
    }

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            if not os.path.exists('config.json'):
                default_config = {
                    'key_actions': {},
                    'selectedScale': 0,
                    'selectedTheme': 0,
                    'language': 'en',
                    'auto_launch': False,
                    'minimize_to_tray': True,
                    'scaleTitlebar': True,
                    'scaleMessageBox': True,
                    'selectedInput1': 1,
                    'selectedInput2': None,
                    'selectedCutoff': 1,
                    'threshold1': 10,
                    'threshold_not_reached1': 2,
                    'threshold2': 10,
                    'threshold_not_reached2': 2,
                    'selectedApp': None,
                    'normal_sound_level': 100,
                    'reduced_sound_level': 50,
                    'fade_duration': 1
                }
                with open('config.json', 'w') as f:
                    json.dump(default_config, f, indent=4)

            # Check and create translations folder and en.json if they don't exist
            self.ensure_translations_exist()

            self.load()

            self._initialized = True

    def ensure_translations_exist(self):
        """Ensure the translations directory and default language file exist"""
        # Create translations directory if it doesn't exist
        if not os.path.exists('translations'):
            os.makedirs('translations')

        # Create default English translation file if it doesn't exist
        en_path = os.path.join('translations', 'en.json')
        if not os.path.exists(en_path):
            with open(en_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_translation, f, indent=4, ensure_ascii=False)

    def load(self):
        with open('config.json') as f:
            config = json.load(f)
        for key, value in config.items():
            setattr(self, key, value)

        # Check translations again when loading config
        self.ensure_translations_exist()

    def save(self):
        for key, value in asdict(self).items():
            setattr(self, key, value)

        data_to_save = asdict(self)
        # Remove instance variables that shouldn't be saved
        for key in list(data_to_save.keys()):
            if key.startswith('_') or key in ['scale', 'colorMode', 'default_translation']:
                data_to_save.pop(key, None)

        with open('config.json', 'w') as f:
            json.dump(data_to_save, f, indent=4)
