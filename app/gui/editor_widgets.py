from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize
from PyQt5.QtWidgets import (
    QFrame, QGridLayout,
    QHBoxLayout, QLineEdit, QListWidget,
    QPushButton, QSizePolicy,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QLabel, QMenu, QAction, QActionGroup
)

from .igui import EditorListWidgetItem, InputHistory
from PyQt5.QtGui import QColor

from functions import getfn
from smartlibs.jedit2 import edit
from .widgets import *

class FindOptions(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        group_mode = QActionGroup(self)
        
        self.normal_mode = QAction("Normal Mode", self)
        self.normal_mode.setCheckable(True)
        self.addAction(self.normal_mode)
        
        self.regex_mode = QAction("Regex Mode", self)
        self.regex_mode.setCheckable(True)
        self.addAction(self.regex_mode)
        
        group_mode.addAction(self.normal_mode)
        group_mode.addAction(self.regex_mode)
        
        self.case_sensitive = QAction("Case Sensitive", self)
        self.case_sensitive.setCheckable(True)
        self.addAction(self.case_sensitive)
        
        self.whole_word = QAction("Whole Word", self)
        self.whole_word.setCheckable(True)
        self.addAction(self.whole_word)
        
        self.wrap = QAction("Wrap", self)
        self.wrap.setCheckable(True)
        self.wrap.setChecked(True)
        self.addAction(self.wrap)
    
class FindPanel(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("finder")
        self.parent = parent
        self.options_menu = FindOptions(self)
        self.icons = getfn.get_application_icons("finder")
        self.init_ui()
    
    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.input_edit = InputHistory(self)
        self.input_edit.setMaximumHeight(32)
        self.input_edit.setPlaceholderText("Find...")

        self.btn_find_next = QPushButton(self)
        self.btn_find_next.setIcon(self.icons.get_icon("next"))
    
        self.btn_find_prev = QPushButton(self)
        self.btn_find_prev.setIcon(self.icons.get_icon("prev"))
        
        self.btn_options = QPushButton(self)
        self.btn_options.setIcon(self.icons.get_icon("menu"))
        self.btn_options.setMenu(self.options_menu)
        self.btn_options.clicked.connect(lambda: self.btn_options.showMenu())
        
        self.btn_close = QPushButton(self)
        self.btn_close.setIcon(self.icons.get_icon("close"))

        self.layout.addWidget(self.input_edit)
        self.layout.addWidget(self.btn_find_next)
        self.layout.addWidget(self.btn_find_prev)
        self.layout.addWidget(self.btn_options)
        self.layout.addWidget(self.btn_close)

class ReplacePanel(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("replacer")
        self.init_ui()
    
    def init_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        self.input_edit = InputHistory(self)
        self.input_edit.setMaximumHeight(30)
        self.input_edit.setPlaceholderText("Replace...")
        
        self.btn_replace = QPushButton("R", self)
        self.btn_replace_all = QPushButton("RA", self)
        
        self.layout.addWidget(self.input_edit)
        self.layout.addWidget(self.btn_replace)
        self.layout.addWidget(self.btn_replace_all)
        
        self.setVisible(False)


class FindReplace(QFrame):
    
    def __init__(self, view, parent):
        super().__init__(parent)
        self.setObjectName("finder_replacer")
        self.view = view
        self.parent = parent
        self.find_query = ""
        self.replace_query = ""
        self.icons = getfn.get_application_icons("finder_replacer")
        self.parent.on_resized.connect(self.update_ui)
        
        self.layout = QHBoxLayout(self)
        self.setLayout(self.layout)

        self.layout.setContentsMargins(2,2,2,2)

        sub_layout = QGridLayout()
        sub_layout.setContentsMargins(2,2,2,2)

        self.finder = FindPanel(self)
        self.replacer = ReplacePanel(self)

        self.btn_mode = QPushButton(self)
        self.btn_mode.setIcon(self.icons.get_icon("collapse"))
        self.btn_mode.setObjectName("btn-expand-collapse")
        self.btn_mode.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.btn_mode.clicked.connect(self.change_mode)
        
        self.options = self.finder.options_menu
        self.options.normal_mode.triggered.connect(self.normal_mode)
        self.options.regex_mode.triggered.connect(self.regex_mode)
        self.options.case_sensitive.triggered.connect(
            lambda: self.set_case_sensitive(
                self.options.case_sensitive.isChecked()
            )
        )
        self.options.wrap.triggered.connect(
            lambda: self.set_wrap(
                self.options.wrap.isChecked()
            )
        )
        self.options.whole_word.triggered.connect(
            lambda: self.set_whole_word(
                self.options.whole_word.isChecked()
            )
        )
        
        self.re = self.options.regex_mode.isChecked()
        self.whole_word = self.options.whole_word.isChecked()
        self.case_sensitive = self.options.case_sensitive.isChecked()
        self.wrap = self.options.wrap.isChecked()
        
        self.input_find = self.finder.input_edit
        self.input_find.returnPressed.connect(self.find)
        self.input_find.textChanged.connect(self.find)
        self.input_replace = self.replacer.input_edit
        self.input_replace.returnPressed.connect(self.replace)

        self.btn_close = self.finder.btn_close
        self.btn_close.clicked.connect(self.close_all)

        self.btn_find_prev = self.finder.btn_find_prev
        self.btn_find_next = self.finder.btn_find_next
        self.btn_find_next.clicked.connect(self.find_next)
        
        self.btn_replace = self.replacer.btn_replace
        self.btn_replace.clicked.connect(self.replace)
        self.btn_replace_all = self.replacer.btn_replace_all
        self.btn_replace_all.clicked.connect(self.replace_all)
        
        sub_layout.addWidget(self.finder, 1,1)
        sub_layout.addWidget(self.replacer, 2,1)

        self.layout.addWidget(self.btn_mode)
        self.layout.addLayout(sub_layout)

        self.gde = QGraphicsDropShadowEffect(self)
        self.gde.setBlurRadius(12)
        self.gde.setOffset(0, 0)
        self.gde.setColor(QColor(0,0,0))
        self.setGraphicsEffect(self.gde)

        self.setVisible(False)
    
    def _update_position(self):
        h = self.parent.tabBar().geometry().height() + 7
        w = self.parent.geometry().width()
        self.move(w-self.geometry().width()-180, h)
    
    def _update_size(self):
        if self.replacer.isVisible():
            self.setFixedHeight(70)
        else:
            self.setFixedHeight(36)
    
    @property
    def current_editor(self):
        return self.parent.currentWidget()

    def update_ui(self):
        self._update_position()
        self._update_size()
    
    def do_find(self):
        selected_text = self.current_editor.editor.selectedText()
        if selected_text.replace(" ","") != "":
            self.input_find.setText(selected_text)
            
        self.input_find.setFocus()
        self.setVisible(True)
        self.collapse()
    
    def do_replace(self):
        self.setVisible(True)
        self.expand()
    
    def find(self, query=None):
        self.find_query = query
        if self.find_query is None:
            self.find_query = self.input_find.text()
        self.current_editor.editor.findFirst(self.find_query, self.re, self.case_sensitive, self.whole_word, self.wrap)
    
    def find_next(self):
        self.current_editor.editor.findNext()
    
    def replace(self):
        self.replace_query = self.input_replace.text()
        self.find()
        self.current_editor.editor.replace(self.replace_query)
    
    def replace_all(self):
        self.find_query = self.input_find.text()
        self.replace_query = self.input_replace.text()
        editor = self.current_editor.editor
        row, col = editor.getCursorPosition()
        text = editor.text()
        replaced_text = text.replace(self.find_query, self.replace_query)
        editor.set_text(replaced_text)
        editor.setCursorPosition(row, col)
        
    
    def change_mode(self):
        self.replacer.setVisible( not self.replacer.isVisible())
        if self.replacer.isVisible():
            self.expand()
        else:
            self.collapse()
        self.update_ui()
    
    def expand(self):
        self.btn_mode.setIcon(self.icons.get_icon("expand"))
        self.replacer.setVisible(True)
        self.update_ui()
    
    def collapse(self):
        self.btn_mode.setIcon(self.icons.get_icon("collapse"))
        self.replacer.setVisible(False)
        self.update_ui()
    
    def hide_all(self):
        self.setVisible(False)
    
    def close_all(self):
        self.hide_all()        
    
    def regex_mode(self):
        self.options.case_sensitive.setChecked(False)
        self.options.whole_word.setChecked(False)
        self.options.wrap.setChecked(False)
        
        self.options.case_sensitive.setEnabled(False)
        self.options.whole_word.setEnabled(False)
        self.options.wrap.setEnabled(False)

        self.re = True

    def normal_mode(self):
        self.options.case_sensitive.setEnabled(True)
        self.options.whole_word.setEnabled(True)
        self.options.wrap.setEnabled(True)

        self.re = False
    
    def set_whole_word(self, state:bool):
        self.whole_word = state
    
    def set_case_sensitive(self, state:bool):
        self.case_sensitive = state
    
    def set_wrap(self, state:bool):
        self.wrap = state

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
        self.python_envs = PythonEnvs(self, self.view)
        self.command_palette = ApplicationCommandPalette(self, self.view)
        self.language_mode_selection = LexerMode(self, self.view)
        self.go_to = GotoLine(self, self.view)
        self.symbol_navigator = SymbolExplorer(self, self.view)
        self.clone_repo = CloneRepo(self, self.view)

        self.widget_list.append(self.python_envs)
        self.widget_list.append(self.command_palette)
        self.widget_list.append(self.language_mode_selection)
        self.widget_list.append(self.go_to)
        self.widget_list.append(self.symbol_navigator)
        self.widget_list.append(self.clone_repo)
        
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
        self.addWidget(widget(self.view, self._parent))
    
    def addWidget(self, widget:object) -> None:
        self.widget_list.append(widget)
        self.configure_widget(widget)
    
    def configure_widget(self, widget):
        self.update_gde()

        if hasattr(widget, "focus_out"):
            if widget.focus_out not in {None, True, False}:
                widget.focus_out.connect(self.hide_widget)
                return
        
        self.widgets_without_focus.append(widget)
    
    def hide_widget(self, widget, event):
        widget.setVisible(False)
    
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
            self.close_widget(self.go_to)
            self.close_widget(self.language_mode_selection)
            self.close_widget(self.symbol_navigator)
                    
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
    
    def do_pyenvs(self):
        self.python_envs.set_envs(self.get_all_envs())
        self.run_widget(self.python_envs)
    
    def do_languages(self):
        self.language_mode_selection.set_langs(self.get_all_languages())
        self.run_widget(self.language_mode_selection)
    
    def do_goto_line(self):
        if self.api is not None:
            if self.api.notebook_have_editor():
                self.run_widget(self.go_to)
    
    def do_goto_symbol(self):
        if self.api is not None:
            editor = self.api.notebook_have_editor_with_python()
            if editor:
                self.symbol_navigator.set_symbols(self.get_code_tree(editor))
                self.run_widget(self.symbol_navigator)
    
    def do_clone_repo(self):
        self.run_widget(self.clone_repo)
    
    def get_all_commands(self):
        if self.api is not None:
            return self.api.commands_list

    def get_all_envs(self):
        if self.api is not None:
            return self.api.envs_list
    
    def get_all_languages(self):
        if self.api is not None:
            if self.api.notebook_have_editor():
                return self.api.lexers_list
    
    def get_code_tree(self, editor):
        if self.api is not None:
            if self.api.notebook_have_editor():
                return getfn.get_python_node_tree(editor.text())
    
    def get_current_editor(self):
        return self._editor_widget.editor
    
    def set_current_env(self, env):
        if self.api is not None:
            self.api.set_current_env(env)
    
    def add_env(self, env):
        if self.api is not None:
            self.api.add_env(env)
        self.python_envs.set_envs(self.get_all_envs())
    
    def run_by_id(self, widget, text):
        if text.startswith(":"):
            self.do_goto_line()
            widget.hide()
        
        elif text.startswith(">"):
            self.do_commands()
            widget.hide()
        
        elif text.startswith("@"):
            self.do_goto_symbol()
            widget.hide()