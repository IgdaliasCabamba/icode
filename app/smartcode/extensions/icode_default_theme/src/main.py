import pathlib
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QColor
from system import BASE_PATH, SYS_SEP
from config import get_palette, get_icons_package, get_icons_theme
from functions import getfn
from data import ijson

SOURCE_PATH=f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}icode_default_theme{SYS_SEP}src{SYS_SEP}"

class Init(QObject):
    def __init__(self, data) -> None:
        super().__init__(data["app"])
        self.app=data["app"]
        self.qapp=data["qt_app"]

        self.ui=self.app.ui
        self.qpalette = get_palette()

        self.listen_slots()
        self.apply_style()

    def listen_notbook_slots(self, notebook):
        notebook.widget_added.connect(self.apply_style_in_editor)

    def listen_slots(self):
        self.ui.notebook.widget_added.connect(self.apply_style_in_editor)
        self.app.on_new_notebook.connect(self.listen_notbook_slots)

    def apply_style(self):
        style_sheet=pathlib.Path(f"{SOURCE_PATH}dark.qss")

        if self.qpalette in {"light","white",1,"day"}:
            style_sheet=pathlib.Path(f"{SOURCE_PATH}light.qss")

        app_style_sheet=style_sheet.read_text("utf-8")
        app_style_sheet=app_style_sheet.replace(
            "<get_resources_path>",
            f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}icode_default_theme{SYS_SEP}res{SYS_SEP}"
            )
        app_style_sheet=app_style_sheet.replace(
            "<get_app_icons_path>",
            f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}icons{SYS_SEP}{get_icons_package()}{SYS_SEP}{get_icons_theme()}{SYS_SEP}app{SYS_SEP}"
            )

        self.qapp.setStyleSheet(app_style_sheet)
        self.ui.setStyleSheet(app_style_sheet)
    
    def apply_style_in_editor(self, widget):
        if widget.objectName()=="editor-frame":            
            for editor in widget.editors:
                editor.on_style_changed.connect(self.beautify_editor)
                self.beautify_editor(editor)

    def beautify_editor(self, editor):
        margin_font=editor.font()
        margin_font.setPointSize(10)
        editor.setMarginsFont(margin_font)
        lexer = editor.lexer()
        if lexer is not None:
            self.apply_styles_in_lexer(lexer)

        if self.qpalette in {"light","white",1,"day"}:
            self.apply_light_theme_in_editor(editor)
        else:
            self.apply_dark_theme_in_editor(editor)
    
    def apply_light_theme_in_editor(self, editor):
        editor.setColor(QColor(255,255,255))
        editor.setPaper(QColor(30, 30, 30))
        editor.minimap.setColor(QColor(255,255,255))
        editor.minimap.setPaper(QColor(30, 30, 30))
        editor.setCaretForegroundColor(QColor(221, 221, 221))
        editor.setCaretLineBackgroundColor(QColor(180,180,180,70))
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
        editor.setMatchedBraceForegroundColor(QColor(255,255,255))
        editor.setWhitespaceBackgroundColor(QColor("#1e1e1e"))
        editor.setWhitespaceForegroundColor(QColor("#999999"))
        editor.setCallTipsBackgroundColor(QColor("#2a2a2a"))
        editor.setCallTipsForegroundColor(QColor("#c683f2"))
        editor.setCallTipsHighlightColor(QColor("#ffffff"))

    def apply_dark_theme_in_editor(self, editor):
        editor.setColor(QColor(255,255,255))
        editor.setPaper(QColor(30, 30, 30))
        editor.minimap.setColor(QColor(255,255,255))
        editor.minimap.setPaper(QColor(30, 30, 30))
        editor.setCaretForegroundColor(QColor(221, 221, 221))
        editor.setCaretLineBackgroundColor(QColor(180,180,180,70))
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
        editor.setMatchedBraceForegroundColor(QColor(255,255,255))
        editor.setWhitespaceBackgroundColor(QColor("#1e1e1e"))
        editor.setWhitespaceForegroundColor(QColor("#999999"))
        editor.setCallTipsBackgroundColor(QColor("#2a2a2a"))
        editor.setCallTipsForegroundColor(QColor("#eeeeee"))
        editor.setCallTipsHighlightColor(QColor("#c683f2"))


    def apply_styles_in_lexer(self, lexer):
        if lexer is not None:
            if self.qpalette in {"light","white",1,"day"}:
                lexer.set_style_api(
                    ijson.load(
                        f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}icode_default_theme{SYS_SEP}src{SYS_SEP}light.json"
                    )
                )
            else:
                lexer.set_style_api(
                    ijson.load(
                        f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}icode_default_theme{SYS_SEP}src{SYS_SEP}dark.json"
                    )
                )

            font=getfn.get_native_font()
            font.setPixelSize(1)
            font.setPointSizeF(10.5)
            font.setBold(False)
            lexer.setDefaultFont(font)
            
            end_styles = lexer.styles_num
            
            for i in range(0, end_styles):
                lexer.setFont(font, i)
            
            if lexer.language() == "python":
                lexer.setFoldComments(True)
                lexer.setFoldQuotes(True)