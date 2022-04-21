import os
import os.path
import functions
import data
from PyQt5.QtGui import QFontDatabase


def get_fonts_from_resources() -> list:
    directory = functions.getfn.get_correct_path_join(
        f"{data.smartcode_directory}fonts{data.SYS_SEP}"
    )
    font_file_list = []
    if directory:
        for root, dirs, files in os.walk(directory):
            for file in files:
                item = functions.getfn.get_correct_path_join(root, file)
                if item.lower().endswith(".ttf") or item.lower().endswith(".otf"):
                    font_file_list.append(
                        functions.getfn.get_correct_path_join(directory, item)
                    )
    return font_file_list


def add_application_font(font_with_path) -> None:
    QFontDatabase.addApplicationFont(font_with_path)
