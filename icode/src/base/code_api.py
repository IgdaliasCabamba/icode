from .system import *
import settings
import frameworks.jedit2 as ijson

class Code:
    def __init__(self):
        pass
        
    @staticmethod
    def get_theme_in_json():
        ext = settings.get_theme()
        palette = settings.get_palette()
        if ext:
            try:
                return ijson.load(
                    f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}{ext}{SYS_SEP}src{SYS_SEP}{palette}.json"
                )
            except Exception as e:
                print(e)

        return None
    
    def get_terminals(self):
        path = settings.get_terminals()
        if path:
            try:
                return ijson.load(
                    f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}{ext}{SYS_SEP}src{SYS_SEP}{palette}.json"
                )
            except Exception as e:
                print(e)

        return None

    def get_terminal_color_map(self):
        data = self.get_theme_in_json()
        if data:
            return data["terminal-styles"]

    def get_drop_shadow_color(self):
        data = self.get_theme_in_json()
        if data:
            return data["global-styles"]["drop-shadow-color"]

    def get_lexers_frontend(self):
        data = self.get_theme_in_json()
        if data:
            return data["lexer-styles"]

    def get_generic_lexer_styles(self):
        data = self.get_theme_in_json()
        if data:
            return data["generic-lexer-styles"]

    def get_editor_styles(self):
        data = self.get_theme_in_json()
        if data:
            return data["editor-styles"]
    

icode_api = Code()