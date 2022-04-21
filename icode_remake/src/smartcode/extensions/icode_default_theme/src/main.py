from extension_api import *


class Init(ModelUi):

    dark_vars = {
        "mid": "#222222",
        "base": "#1e1e1e",
        "border": "#007acc",
        "base2": "#252526",
        "contrast": "#3c3c3c",
        "contrast2": "#333333",
    }
    light_vars = {
        "mid": "#f3f3f3",
        "base": "#ffffff",
        "border": "#007acc",
        "base2": "#f3f3f3",
        "contrast": "#dddddd",
        "contrast2": "#eeeeee",
    }

    def __init__(self, data) -> None:
        super().__init__(data, "icode_default_theme")
        self.listen_slots()
        self.apply_style()

    def listen_notebook_slots(self, notebook):
        notebook.widget_added.connect(self.apply_style_in_editor)

    def listen_slots(self):
        self.do_on(self.apply_style_in_editor, "ui", "notebook", "widget_added")
        self.do_on(self.listen_notebook_slots, "app", "on_new_notebook")

    def apply_style(self):
        style_sheet = self.get_styles(
            dark={"styles": "dark.qss", "vars": self.dark_vars},
            light={"styles": "light.qss", "vars": self.light_vars},
        )
        style_sheet.format_style(
            ["<get_resources_path>", "<get_app_icons_path>"],
            [self.path_to("res"), self.icons_path_to("app")],
        )
        style_sheet.apply()

    def apply_style_in_editor(self, editor):
        self.paint_editor(widget=editor, painter=self.beautify_editor)

    def beautify_editor(self, editor):
        font = getfn.get_native_font()
        font.setPixelSize(1)
        font.setBold(False)
        font.setFixedPitch(True)
        font.setPointSize(10)
        editor.setMarginsFont(font)
        editor.setFont(font)

        self.set_code_style(
            editor=editor,
            editor_dark=self.editor_dark,
            editor_light=self.editor_light,
            lexer_styler=self.lexer_styler,
        )

    def editor_light(self, editor):
        editor.setColor(QColor(255, 255, 255))
        editor.setPaper(QColor(255, 255, 255))
        editor.minimap.setColor(QColor(255, 255, 255))
        editor.minimap.setPaper(QColor(255, 255, 255))
        editor.setCaretForegroundColor(QColor(21, 21, 21))
        editor.setCaretLineBackgroundColor(QColor(180, 180, 180, 70))
        editor.setIndentationGuidesBackgroundColor(QColor(0, 162, 232))
        editor.setIndentationGuidesForegroundColor(QColor(0, 162, 232))
        editor.setMarginsBackgroundColor(QColor(255, 255, 255))
        editor.setMarginsForegroundColor(QColor(170, 170, 170))
        editor.setFoldMarginColors(QColor("#ffffff"), QColor("#ffffff"))
        editor.setMarkerBackgroundColor(QColor(255, 255, 255), -1)
        editor.setMarkerForegroundColor(QColor(200, 200, 200), -1)
        editor.setSelectionBackgroundColor(QColor(0, 162, 232, 70))
        editor.setSelectionForegroundColor(QColor("#000000"))
        editor.setMatchedBraceBackgroundColor(QColor(0, 162, 232))
        editor.setMatchedBraceForegroundColor(QColor(255, 255, 255))
        editor.setWhitespaceBackgroundColor(QColor("#ffffff"))
        editor.setWhitespaceForegroundColor(QColor("#999999"))
        editor.setCallTipsBackgroundColor(QColor("#eaeaea"))
        editor.setCallTipsForegroundColor(QColor("#111111"))
        editor.setCallTipsHighlightColor(QColor("#c683f2"))

    def editor_dark(self, editor):
        editor.setColor(QColor(255, 255, 255))
        editor.setPaper(QColor(30, 30, 30))
        editor.minimap.setColor(QColor(255, 255, 255))
        editor.minimap.setPaper(QColor(30, 30, 30))
        editor.setCaretForegroundColor(QColor(221, 221, 221))
        editor.setCaretLineBackgroundColor(QColor(180, 180, 180, 70))
        editor.setIndentationGuidesBackgroundColor(QColor(0, 162, 232))
        editor.setIndentationGuidesForegroundColor(QColor(0, 162, 232))
        editor.setMarginsBackgroundColor(QColor(30, 30, 30))
        editor.setMarginsForegroundColor(QColor(170, 170, 170))
        editor.setFoldMarginColors(QColor("#1e1e1e"), QColor("#1e1e1e"))
        editor.setMarkerBackgroundColor(QColor(30, 30, 30), -1)
        editor.setMarkerForegroundColor(QColor(200, 200, 200), -1)
        editor.setSelectionBackgroundColor(QColor(0, 162, 232, 70))
        editor.setSelectionForegroundColor(QColor("#ffffff"))
        editor.setMatchedBraceBackgroundColor(QColor(0, 162, 232))
        editor.setMatchedBraceForegroundColor(QColor(255, 255, 255))
        editor.setWhitespaceBackgroundColor(QColor("#1e1e1e"))
        editor.setWhitespaceForegroundColor(QColor("#999999"))
        editor.setCallTipsBackgroundColor(QColor("#2a2a2a"))
        editor.setCallTipsForegroundColor(QColor("#eeeeee"))
        editor.setCallTipsHighlightColor(QColor("#c683f2"))

    def lexer_styler(self, lexer):
        if lexer is not None:
            self.set_lexer_style(
                lexer=lexer, key="lexer-styles", dark="dark.json", light="light.json"
            )
