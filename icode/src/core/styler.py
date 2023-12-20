from .font_loader import get_fonts_from_resources, add_application_font
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, QObject

import settings
from functions import getfn

windows_style = settings.get_window_style()


class Styler(QObject):

    def __init__(self, application_core, ui, qt_app):
        self.application_core = application_core
        self.ui = ui
        self.qt_app = qt_app
        self.fonts = []
        self._configure_qt()
        self.application_core.on_style_changed.connect(self.beautify)

    def _configure_qt(self):
        self.qt_app.setWindowIcon(getfn.get_app_icon())
        self.qt_app.setEffectEnabled(Qt.UI_AnimateMenu, True)
        self.qt_app.setEffectEnabled(Qt.UI_FadeMenu, True)
        self.qt_app.setEffectEnabled(Qt.UI_AnimateCombo, True)
        self.qt_app.setEffectEnabled(Qt.UI_AnimateTooltip, True)
        self.qt_app.setEffectEnabled(Qt.UI_FadeTooltip, True)
        self.qt_app.setEffectEnabled(Qt.UI_AnimateToolBox, True)

    def beautify(self):
        palette = settings.get_palette()
        if palette in {"dark", "black", 0, "night"}:
            self.dark()

        elif palette in {"light", "white", 1, "day"}:
            self.light()

        self.apply_base_theme()

        self.fonts = get_fonts_from_resources()
        for font in self.fonts:
            add_application_font(font)

    def apply_base_theme(self):
        self.qt_app.setStyle(settings.get_qt_theme())

    def dark(self):

        dark_palette = QPalette()

        # base
        dark_palette.setColor(QPalette.WindowText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.Light, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.Midlight, QColor(90, 90, 90))
        dark_palette.setColor(QPalette.Dark, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.Text, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.BrightText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.Base, QColor(42, 42, 42))
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.Link, QColor(0, 162, 232))
        dark_palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
        dark_palette.setColor(QPalette.LinkVisited, QColor(80, 80, 80))

        # disabled
        dark_palette.setColor(QPalette.Disabled, QPalette.WindowText,
                              QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.Text,
                              QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                              QColor(127, 127, 127))
        dark_palette.setColor(QPalette.Disabled, QPalette.Highlight,
                              QColor(80, 80, 80))
        dark_palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                              QColor(127, 127, 127))

        self.qt_app.setPalette(dark_palette)

    def light(self):

        light_palette = QPalette()

        # base
        light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.Light, QColor(180, 180, 180))
        light_palette.setColor(QPalette.Midlight, QColor(200, 200, 200))
        light_palette.setColor(QPalette.Dark, QColor(225, 225, 225))
        light_palette.setColor(QPalette.Text, QColor(0, 0, 0))
        light_palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Base, QColor(237, 237, 237))
        light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
        light_palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        light_palette.setColor(QPalette.Highlight, QColor(76, 163, 224))
        light_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Link, QColor(0, 162, 232))
        light_palette.setColor(QPalette.AlternateBase, QColor(225, 225, 225))
        light_palette.setColor(QPalette.ToolTipBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.LinkVisited, QColor(222, 222, 222))

        # disabled
        light_palette.setColor(QPalette.Disabled, QPalette.WindowText,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.Text,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.ButtonText,
                               QColor(115, 115, 115))
        light_palette.setColor(QPalette.Disabled, QPalette.Highlight,
                               QColor(190, 190, 190))
        light_palette.setColor(QPalette.Disabled, QPalette.HighlightedText,
                               QColor(115, 115, 115))

        self.qt_app.setPalette(light_palette)
