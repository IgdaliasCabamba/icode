from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import QColor

from functions import getfn
from .widgets import *

class EditorWidgets(QObject):
    
    on_editor_changed = pyqtSignal(object)
    on_editor_widget_changed = pyqtSignal(object)

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.view = parent
        self._parent = parent
        self.widget_list = []
        self._editor = None
        self._editor_widget = None
        self._current_editors = []
        self.widgets_without_focus = []
        self.api = None
        self.view.resized.connect(self.update_ui)
        self.view.on_focused_buffer.connect(self.update_focus)
        self.view.on_editor_changed.connect(self.set_current_editor)
        self.build()
    
    def build(self):
        self.command_palette = ApplicationCommandPalette(self, self.view)
        self.language_mode_selection = LexerMode(self, self.view)
        self.go_to = GotoLine(self, self.view)
        self.clone_repo = CloneRepo(self, self.view)
        self.space_mode = SpaceMode(self, self.view)
        self.eol_mode = EOLMode(self, self.view)
        self.tab_browser = TabBrowser(self, self.view)

        self.widget_list.append(self.command_palette)
        self.widget_list.append(self.language_mode_selection)
        self.widget_list.append(self.go_to)
        self.widget_list.append(self.clone_repo)
        self.widget_list.append(self.space_mode)
        self.widget_list.append(self.eol_mode)
        self.widget_list.append(self.tab_browser)
        
        for widget in self.widget_list:
            self.configure_widget(widget)

        self.update_ui()
        self.update_gde()
        self.update_all_sizes()
    
    def set_api(self, api):
        self.api = api
    
    @property
    def current_editors(self):
        return self._current_editors

    @property
    def current_editor(self) -> object:
        return self._editor

    @property
    def current_editor_widget(self) -> object:
        return self._editor_widget

    def addWidgetObject(self, widget:object) -> None:
        called_widget = widget(self, self.view)
        self.addWidget(called_widget)
        return called_widget
    
    def addWidget(self, widget:object) -> None:
        self.widget_list.append(widget)
        self.configure_widget(widget)
    
    def configure_widget(self, widget):
        self.update_gde()
        self.update_all_sizes()
        self.update_ui()

        if hasattr(widget, "focus_out"):
            if widget.focus_out not in {None, True, False}:
                widget.focus_out.connect(self.hide_widget)
                return
        
        self.widgets_without_focus.append(widget)
    
    def hide_widget(self, widget, event):
        widget.setVisible(False)
    
    def is_runing(self, widget) -> bool:
        if widget.isVisible() and widget in self.widget_list:
            return True
        return False
    
    def set_current_editor(self, editor_widget:object) -> None:
        self._editor_widget = editor_widget
        self._editor = editor_widget.editor
        self._current_editors = editor_widget.editors
        self.on_editor_changed.emit(self._editor)
        self.on_editor_widget_changed.emit(self._editor_widget)
    
    def update_all_sizes(self):
        for widget in self.widget_list:
            widget.setMinimumWidth(460)
            widget.show()
            widget.hide()
    
    def update_gde(self):
        for widget in self.widget_list:
            tmp_gde = QGraphicsDropShadowEffect(widget)
            tmp_gde.setBlurRadius(12)
            tmp_gde.setOffset(0, 0)
            tmp_gde.setColor(QColor(0,0,0))
            widget.setGraphicsEffect(tmp_gde)
    
    def update_position(self):
        y = 4
        w = (self.view.geometry().width()/2)
        
        for widget in self.widget_list:    
            x = int(w-widget.geometry().width()/2)
            if x < 10:
                x = 10
            widget.move(x, y)

    def update_ui(self):
        self.update_position()

    def update_focus(self, widget):
        if widget not in self.widget_list:
            for i in  self.widget_list:
                if widget == i.children():
                    return
            
            self.close_widget(self.command_palette)
            self.close_widget(self.language_mode_selection)
            self.close_widget(self.go_to)
            self.close_widget(self.clone_repo)
            self.close_widget(self.space_mode)
            self.close_widget(self.eol_mode)
                    
    def run_widget(self, widget:object):
        if widget in self.widgets_without_focus:
            if widget.isVisible():
                widget.setVisible(False)
                return
            
            else:    
                for x in self.widget_list:
                    x.setVisible(False)
            
        else:
            if not widget.hasFocus() and widget.isVisible():
                widget.setVisible(False)
                return

        for x in self.widget_list:
            x.setVisible(False)

        widget.setVisible(True)
        widget.setFocus()
        
        if hasattr(widget, "run"):
            widget.run()
        
    def close_all(self):
        for widget in self.widget_list:
            widget.setVisible(False)
    
    def close_widget(self, widget):
        widget.setVisible(False)
    
    def do_commands(self):
        self.command_palette.set_commands(self.get_all_commands())
        self.run_widget(self.command_palette)
    
    def do_languages(self):
        self.language_mode_selection.set_langs(self.get_all_languages())
        self.run_widget(self.language_mode_selection)
    
    def do_space_mode(self):
        if self.api is not None:
            self.space_mode.set_spaces(self.get_all_indentations())
            self.run_widget(self.space_mode)
    
    def do_eol_mode(self):
        if self.api is not None:
            self.eol_mode.set_eols(self.get_all_eols())
            self.run_widget(self.eol_mode)
    
    def do_goto_line(self):
        if self.api is not None:
            if self.api.has_notebook_editor():
                self.run_widget(self.go_to)
    
    def do_goto_tab(self):
        if self.api is not None:
            if self.is_runing(self.tab_browser):
                self.tab_browser.next_item()
            else:
                self.tab_browser.set_navigation(self.api.tabs_navigation)
                self.run_widget(self.tab_browser)
    
    def do_clone_repo(self):
        self.run_widget(self.clone_repo)
    
    def get_all_commands(self):
        if self.api is not None:
            return self.api.commands
    
    def get_all_languages(self):
        if self.api is not None:
            if self.api.has_notebook_editor():
                return self.api.lexers
    
    def get_current_editor(self):
        return self._editor_widget.editor
    
    def get_all_eols(self):
        if self.api is not None:
            if self.api.has_notebook_editor():
                return self.api.eols
    
    def get_all_indentations(self):
        if self.api is not None:
            if self.api.has_notebook_editor():
                return self.api.indentations
    
    def run_by_id(self, widget, text):
        if text.startswith(":"):
            self.do_goto_line()
            widget.hide()
        
        elif text.startswith(">"):
            self.do_commands()
            widget.hide()
        
        elif text.startswith("!"):
            self.do_eol_mode()
            widget.hide()