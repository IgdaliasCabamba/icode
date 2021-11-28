from PyQt5.QtCore import QObject, Qt, pyqtSignal

from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout,
    QPushButton, QVBoxLayout,
    QSplitter, QFileDialog,
    QGraphicsDropShadowEffect, QSizePolicy,
    QWidget, QMenu, QAction
)

from PyQt5.Qsci import *
from PyQt5.QtGui import QColor
from pathlib import Path
from .codesmart import Editor
from .minimap import MiniMapBox
from .editor_core import IFile
from functions import filefn, getfn

class FileMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.reload_file = QAction("Reload File", self)
        self.save_file = QAction("Save File", self)
        self.open_folder = QAction("Open Folder", self)
        
        self.addAction(self.reload_file)
        self.addAction(self.save_file)
        self.addAction(self.open_folder)
        

class EditorView(QFrame):
    
    on_tab_content_changed = pyqtSignal(dict)

    def __init__(self, api:object, parent:object, notebook:object, file = None) -> None:
        super().__init__(parent)
        self.setObjectName("editor-frame")
        self.api = api
        self.parent=parent
        self.notebook = notebook
        self._title = None
        self.file=file
        self._editor = None
        self._editors = []
        self.icons = getfn.get_application_icons("editor")
        self.file_watcher = IFile(self)
        self.file_menu = FileMenu(self)
        self.file_menu.save_file.triggered.connect(self.save_file)
        self.file_menu.reload_file.triggered.connect(self.load_file)
        
        if self.file is not None:
            self.file_watcher.start_monitoring(str(self.file))
            
        self.init_ui()
        self.run()
    
    def run(self) -> None:
        self.api.on_env_changed.connect(self.update_env)
        self.update_env(self.api.current_env)
    
    def init_ui(self) -> None:        
        self.layout=QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)                
        self.layout.setContentsMargins(0,0,0,0)

        self.div = QSplitter(self)
        self.div.setOrientation(Qt.Vertical)

        self.div_main=Div(self.div)
        
        self.editor_main=Editor(self, self.file)
        self.editor_main.connector.auto_save_file.connect(self.save_file)
        self.editor_main.verticalScrollBar().valueChanged.connect(self.update_shadow)
        self.editor_main.cursorPositionChanged.connect(lambda: self.update_shadow(self.editor_main.verticalScrollBar().value()))
        self.editor_main.on_focused.connect(self.focused)
        self.editor_main.on_saved.connect(self.update_title)
        self.editor_main.idocument.on_changed.connect(self.update_code)
        self.minimap_main=MiniMapBox(self.editor_main, self)
        self.editor_main.set_minimap(self.minimap_main)

        self.idocument = self.editor_main.idocument
        
        self.div_main.addWidget(self.editor_main)
        self.div_main.addWidget(self.minimap_main)

        self.div.addWidget(self.div_main)
        #-------------------------------------------------------------------------

        self.div_mirror = Div(self.div)

        self.editor_mirror=Editor(self, self.file)
        self.editor_mirror.setDocument(self.editor_main.document())
        self.editor_mirror.verticalScrollBar().valueChanged.connect(self.update_shadow)
        self.editor_mirror.cursorPositionChanged.connect(lambda: self.update_shadow(self.editor_mirror.verticalScrollBar().value()))
        self.editor_mirror.on_focused.connect(self.focused)
        self.editor_mirror.on_saved.connect(self.update_title)
        self.editor_mirror.idocument.on_changed.connect(self.update_code)
        self.minimap_mirror=MiniMapBox(self.editor_mirror, self)
        self.editor_mirror.set_minimap(self.minimap_mirror)

        self.idocument_mirror = self.editor_mirror.idocument
        
        self.div_mirror.addWidget(self.editor_mirror)
        self.div_mirror.addWidget(self.minimap_mirror)

        self.div.addWidget(self.div_mirror)
        self.div.setSizes([100,100])
        
        self.setMinimumWidth(200)

        self.editor_main.update_document()
        self.editor_mirror.update_document()

        self._editor = self.editor_main
        self._editors.append(self.editor_main)
        self._editors.append(self.editor_mirror)

        self.join_in_group()
        
        self.hbox = QHBoxLayout()
        
        self.up_map = QFrame(self)
        self.up_map.setObjectName("up-map")
        self.up_map.setLayout(self.hbox)
        
        self.spacing=QWidget(self)
        self.spacing.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.up_info0 = QPushButton(self.up_map)
        self.up_info0.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info0.setVisible(False)
        
        self.up_info1 = QPushButton(self.up_map)
        self.up_info1.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info1.setVisible(False)
        
        self.up_info2 = QPushButton(self.up_map)
        self.up_info2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info2.setVisible(False)
        
        self.up_info3 = QPushButton(self.up_map)
        self.up_info3.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info3.setVisible(False)
        
        self.up_info4 = QPushButton(self.up_map)
        self.up_info4.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info4.setVisible(False)
        
        self.up_info5 = QPushButton(self.up_map)
        self.up_info5.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info5.setVisible(False)
        
        self.up_info6 = QPushButton(self.up_map)
        self.up_info6.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info6.setVisible(False)
        
        self.up_info7 = QPushButton(self.up_map)
        self.up_info7.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info7.setVisible(False)
        
        self.up_info00 = QPushButton(self.up_map)
        self.up_info00.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info00.setVisible(False)
        
        self.up_info01 = QPushButton(self.up_map)
        self.up_info01.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info01.setVisible(False)
        
        self.up_info02 = QPushButton(self.up_map)
        self.up_info02.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info02.setVisible(False)
        
        self.up_info03 = QPushButton(self.up_map)
        self.up_info03.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.up_info03.setVisible(False)
        
        
        self.file_info = QPushButton(self.up_map)
        self.file_info.setIcon(self.icons.get_icon("file"))
        self.file_info.setMenu(self.file_menu)
        self.file_info.clicked.connect(lambda: self.file_info.showMenu())
        
        self.src_ctrl_info = QPushButton(self.up_map)
        self.src_ctrl_info.setIcon(self.icons.get_icon("source_control"))
        
        self.warnings_info = QPushButton(self.up_map)
        self.warnings_info.setIcon(self.icons.get_icon("warnings"))
        self.warnings_info.setStyleSheet("color:yelllow")
        
        self.errors_info = QPushButton(self.up_map)
        self.errors_info.setIcon(self.icons.get_icon("errors"))
        self.errors_info.setStyleSheet("color:red")
        
        self.hbox.addWidget(self.up_info0)
        self.hbox.addWidget(self.up_info1)
        self.hbox.addWidget(self.up_info2)
        self.hbox.addWidget(self.up_info3)
        self.hbox.addWidget(self.up_info4)
        self.hbox.addWidget(self.up_info5)
        self.hbox.addWidget(self.up_info6)
        self.hbox.addWidget(self.up_info7)
        self.hbox.addWidget(self.up_info00)
        self.hbox.addWidget(self.up_info01)
        self.hbox.addWidget(self.up_info02)
        self.hbox.addWidget(self.up_info03)
        self.hbox.addWidget(self.spacing)
        self.hbox.addWidget(self.file_info)
        self.hbox.addWidget(self.src_ctrl_info)
        self.hbox.addWidget(self.warnings_info)
        self.hbox.addWidget(self.errors_info)
        
        self.up_map.setFixedHeight(24)
        
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(2)
        self.drop_shadow.setOffset(0, 0)
        self.drop_shadow.setColor(QColor(0,0,0))
        self.up_map.setGraphicsEffect(self.drop_shadow)
    
        self.hbox.setContentsMargins(10, 2, 0, 0)
        
        self.layout.addWidget(self.up_map)
        self.layout.addWidget(self.div)
    
    def set_info(self, data:dict) -> None:
        text = False
        widget = False
        type = False
        icon = False
        keys = data.keys()
        if "text" in keys:
            text = data["text"]
        if "widget" in keys:
            widget = data["widget"]
        if "type" in keys:
            type = data["type"]
        if "icon" in keys:
            icon = data["icon"]
        
        if widget:
            if text:
                widget.setText(text)
            if icon:
                widget.setIcon(icon)
                
            if type:
                widget.setStyleSheet(f"color:{type}")
                
            widget.setVisible(True)
            
            if not text and not icon:
                widget.setVisible(False)
                
        
            
    def split_horizontally(self):
        self.div.setOrientation(Qt.Vertical)
        self.div_mirror.show()
    
    def split_vertically(self):
        self.div.setOrientation(Qt.Horizontal)
        self.div_mirror.show()
    
    def join_in_group(self):
        self.div_mirror.hide()
    
    def focused(self, event, widget):
        self._editor = widget
        self.api.tab_focused(self, event)
        self.update_shadow(self._editor.verticalScrollBar().value())
    
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_shadow(self._editor.verticalScrollBar().value())
    
    def update_shadow(self, value):
        if value > 2:
            self.drop_shadow.setBlurRadius(10)
            self.drop_shadow.setOffset(0, 3)
        else:
            w = self.editor.minimap.size().width()
            x_offset = self.size().width() - w - 200
            self.drop_shadow.setBlurRadius(2)
            self.drop_shadow.setOffset(x_offset, 0)

    @property
    def editor(self):
        return self._editor
    
    @property
    def editors(self):
        return self._editors

    @property
    def title(self):
        return self._title

    def set_title(self, title):
        self._title = title

    def update_title(self, new_title):
        self.set_title(new_title)

    def update_code(self, data):
        self.on_tab_content_changed.emit({"widget":self, "data":data})
    
    def update_env(self, env):
        for editor in self._editors:
            editor.set_env(env)
    
    def save_file(self):
        if self.file is None:
            home_dir = str(Path.home())
            file = QFileDialog.getSaveFileName(None, 'Open file', home_dir)
            if file[0]:
                self.file=file[0]
                
                filefn.write_to_file(self.editor_main.text(), file[0])
                self.editor_main.save_file(self.file)
                self.editor_mirror.save_file(self.file)
                
                self.editor_main.define_lexer()
                self.editor_mirror.define_lexer()
                self.file_watcher.start_monitoring(str(self.file))
        else:
            filefn.write_to_file(self.editor_main.text(), self.file)
            self.editor_main.save_file(self.file)
            self.editor_mirror.save_file(self.file)
    
    def load_file(self):
        if self.file is not None:
            row1, col1 = self.editor_main.getCursorPosition()
            row2, col2 = self.editor_mirror.getCursorPosition()
            self.editor_main.set_text(filefn.read_file(self.file))
            self.editor_main.setCursorPosition(row1, col1)
            self.editor_mirror.setCursorPosition(row2, row2)
            self.save_file()
    
    def make_deep_copy(self, editor):
        self.file = editor.file
        self.editor_main.file_path = self.file
        self.editor_mirror.file_path = self.file
        self.editor_main.copy_this_editor(editor.editor_main)
        self.editor_mirror.copy_this_editor(editor.editor_mirror)
    

class Div(QSplitter):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("editor-splitter")
        self.parent=parent
        self.setStyleSheet("QSplitter::handle:horizontal {width: 0px;}QSplitter::handle:vertical {height: 0px;}")