from PyQt5.QtGui import QFont
import base.consts as iconsts
from base.system import *


def get_font():
    font = QFont("Courier New", iconsts.APP_BASE_FONT_SIZE)
    if SYS_NAME.startswith("linux"):
        font = QFont("DejaVu Sans Mono", iconsts.APP_BASE_FONT_SIZE)
    elif SYS_NAME.startswith("darwin"):
        font = QFont("Menlo", iconsts.APP_BASE_FONT_SIZE)
    elif SYS_NAME.startswith("win"):
        font = QFont("Consolas", iconsts.APP_BASE_FONT_SIZE)
    return font


def made_font(data: dict):
    font = get_font()

    keys = [
        "name",
        "pixel-size",
        "fixed-pitch",
        "point-size",
        "bold",
        "stretch",
        "underline",
        "weight",
        "word-spacing",
        "strike-out",
        "kerning",
        "italic",
        "capitalization",
        "hinting-preference",
    ]

    for key in keys:
        if key in data.keys():
            value = data[key]

            if key == "name":
                if isinstance(value, list):
                    l_names = []

                    for family in value:
                        l_names.append(str(family))

                    font.setFamilies(l_names)

                elif isinstance(value, str):
                    font.setFamily(value)

            if key == "pixel-size":
                if isinstance(value, int):
                    font.setPixelSize(value)

            if key == "fixed-pitch":
                value = data["fixed-pitch"]
                if isinstance(value, bool):
                    font.setFixedPitch(value)

            if key == "point-size":
                value = data["point-size"]
                if isinstance(value, int):
                    font.setPointSize(value)

                elif isinstance(value, float):
                    font.setPointSizeF(value)

            if key == "bold":
                if isinstance(value, bool):
                    font.setBold(value)

            if key == "stretch":
                if isinstance(value, int):
                    font.setStretch(value)

            if key == "underline":
                if isinstance(value, bool):
                    font.setUnderline(value)

            if key == "weight":
                if isinstance(value, int):
                    font.setWeight(value)

            if key == "word-spacing":
                if isinstance(value, float):
                    font.setWordSpacing(value)

            if key == "strike-out":
                if isinstance(value, bool):
                    font.setStrikeOut(value)

            if key == "kerning":
                if isinstance(value, bool):
                    font.setKerning(value)

            if key == "italic":
                if isinstance(value, bool):
                    font.setItalic(value)

            if key == "capitalization":
                if isinstance(value, int):
                    font.setCapitalization(value)

            if key == "hinting-preference":
                if isinstance(value, int):
                    font.setHintingPreference(value)

    return font
