import json
import os
from backend.config import Config
from backend.logger import Logger


class Translator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.lang = Config().language
            self.logger = Logger()
            self.translations = self.load_translations()

    def load_translations(self):
        filepath = os.path.join('translations', f'{self.lang}.json')
        if not os.path.exists(filepath):
            self.logger.log("Translator", f"No translation file found for language: {self.lang}")
            raise FileNotFoundError(f"No translation file found for language: {self.lang}")

        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)

    def translate(self, key):
        return self.translations.get(key, key)

    @classmethod
    def get_available_languages(cls):
        languages = []
        translations_dir = 'translations'

        if not os.path.exists(translations_dir):
            return languages

        for filename in os.listdir(translations_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(translations_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                        language_code = filename[:-5]
                        language_name = data.get('language_name', language_code)
                        languages.append({
                            'code': language_code,
                            'name': language_name
                        })
                except (json.JSONDecodeError, IOError):
                    continue

        Logger().log("Translator", f"Available languages: {languages}")
        return languages
