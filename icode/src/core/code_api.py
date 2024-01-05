from .system import *
import settings
import smartlibs.mjson as ijson
import pathlib


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
                    pathlib.Path(ROOT_PATH)
                    .joinpath("smartcode")
                    .joinpath("extensions")
                    .joinpath(ext)
                    .joinpath("src")
                    .joinpath(f"{palette}.json")
                )
            except Exception as e:
                print(e)

        return None

    def get_editor_settings(self):
        return ijson.load(settings.EDITOR_FILE)

    def get_terminals(self):
        return ijson.load(settings.TERMINALS_FILE)

    def get_terminal_emulators(self):
        return ijson.load(settings.TERMINALS_FILE)["emulators"]

    def get_terminal_theme(self) -> str:
        ext = settings.get_theme()
        palette = settings.get_palette()
        if ext:
            return str((pathlib.Path(ROOT_PATH)
                    .joinpath("smartcode")
                    .joinpath("extensions")
                    .joinpath(ext)
                    .joinpath("src")
                    .joinpath(f"terminal.{palette}.theme.json")))
        
        return None

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
