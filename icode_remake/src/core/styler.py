from .font_loader import get_fonts_from_resources, add_application_font
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QObject
import typing

import settings
from functions import getfn

windows_style = settings.get_window_style()


def apply_base_theme(settings, qapp):
    qapp.setStyle(settings.get_qt_theme())


def dark(app):

    darkPalette = QPalette()

    # base
    darkPalette.setColor(QPalette.WindowText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.Light, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Midlight, QColor(90, 90, 90))
    darkPalette.setColor(QPalette.Dark, QColor(35, 35, 35))
    darkPalette.setColor(QPalette.Text, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.BrightText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.Link, QColor(0, 162, 232))
    darkPalette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
    darkPalette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))

    # disabled
    darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(
        QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127)
    )

    app.setPalette(darkPalette)


def light(app):

    lightPalette = QPalette()

    # base
    lightPalette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.Button, QColor(240, 240, 240))
    lightPalette.setColor(QPalette.Light, QColor(180, 180, 180))
    lightPalette.setColor(QPalette.Midlight, QColor(200, 200, 200))
    lightPalette.setColor(QPalette.Dark, QColor(225, 225, 225))
    lightPalette.setColor(QPalette.Text, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.BrightText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.Base, QColor(237, 237, 237))
    lightPalette.setColor(QPalette.Window, QColor(240, 240, 240))
    lightPalette.setColor(QPalette.Shadow, QColor(20, 20, 20))
    lightPalette.setColor(QPalette.Highlight, QColor(76, 163, 224))
    lightPalette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.Link, QColor(0, 162, 232))
    lightPalette.setColor(QPalette.AlternateBase, QColor(225, 225, 225))
    lightPalette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
    lightPalette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    lightPalette.setColor(QPalette.LinkVisited, QColor(222, 222, 222))

    # disabled
    lightPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(115, 115, 115))
    lightPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(115, 115, 115))
    lightPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(115, 115, 115))
    lightPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(190, 190, 190))
    lightPalette.setColor(
        QPalette.Disabled, QPalette.HighlightedText, QColor(115, 115, 115)
    )

    app.setPalette(lightPalette)


def beautify(qapp, app=None):
    qapp.setWindowIcon(getfn.get_app_icon())
    qapp.setEffectEnabled(Qt.UI_AnimateMenu, True)
    qapp.setEffectEnabled(Qt.UI_FadeMenu, True)
    qapp.setEffectEnabled(Qt.UI_AnimateCombo, True)
    qapp.setEffectEnabled(Qt.UI_AnimateTooltip, True)
    qapp.setEffectEnabled(Qt.UI_FadeTooltip, True)
    qapp.setEffectEnabled(Qt.UI_AnimateToolBox, True)

    if settings.get_palette() in {"dark", "black", 0, "night"}:
        dark(qapp)

    elif settings.get_palette() in {"light", "white", 1, "day"}:
        light(qapp)

    else:
        pass

    apply_base_theme(settings, qapp)

    fonts = get_fonts_from_resources()
    for font in fonts:
        add_application_font(font)


class Styler(QObject):
    def __init__(
        self, qapp: object, app: object, parent: typing.Optional["QObject"] = ...
    ) -> None:
        super().__init__(parent)
        self.qapp = qapp
        self.app = app
