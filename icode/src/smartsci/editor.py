
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QThread

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
from .codesmart import Editor, EditorBase
from .minimap import MiniMapBox
from .editor_core import IFile
from functions import filefn, getfn
from . import iconsts, get_unicon
import settings
import mimetypes
from .media_viewer import ImageView

class BreadcrumbController(QObject):
    on_update_header = pyqtSignal(dict)
    
    def __init__(self, parent):
        super().__init__()
        self.editor = parent
    
    def run(self):
        self.make_headers(self.editor.editor_main)
        
        self.editor.editor_main.on_text_changed.connect(lambda: self.text_changed(self.editor.editor_main))
        self.editor.editor_main.on_saved.connect(lambda: self.editor_saved(self.editor.editor_main))
        self.editor.editor_main.idocument.on_changed.connect(lambda: self.make_headers(self.editor.editor_main))
        
        self.editor.editor_mirror.on_text_changed.connect(lambda: self.text_changed(self.editor.editor_mirror))
        self.editor.editor_mirror.on_saved.connect(lambda: self.editor_saved(self.editor.editor_mirror))
        self.editor.editor_mirror.idocument.on_changed.connect(lambda: self.make_headers(self.editor.editor_mirror))
        
        self.editor.file_watcher.on_file_deleted.connect(self.file_deleted)
        self.editor.file_watcher.on_file_modified.connect(self.file_modified)

    def make_headers(self, editor):
        if editor.file_path is None:
            self.on_update_header.emit({
                "text": " Unsaved",
                "widget": "first",
                "last":False
            })
        else:
            widgets = [
                "second", "third",
                "fourth", "last"
            ]
            path_levels = getfn.get_path_splited(editor.idocument.file)
            while len(path_levels) > len(widgets):
                path_levels.pop(0)

            i = 0
            for path in path_levels:
                if path.replace(" ", "") == "":
                    continue
                if i < len(widgets):
                    self.on_update_header.emit({
                        "text": f" {str(path)}",
                        "widget": widgets[i],
                        "last": False
                    })
                else:
                    break
                    self.on_update_header.emit({
                        "text":f" {str(editor.idocument.file_name)}",
                        "widget":widgets[i],
                        "last":True
                    })
                i += 1
        self.on_update_header.emit({
            "widget": "first",
            "icon": editor.idocument.icon,
            "last":False
        })

    def file_deleted(self, file):
        self.on_update_header.emit({
            "text": "D",
            "widget": "info-file",
            "type": "red",
            "last":True
        })

    def file_modified(self, file):
        if filefn.read_file(file) != editor.text():
            self.on_update_header.emit({
                "text": "M",
                "widget": "info-file",
                "type": "red",
                "last":True
            })

    def text_changed(self, editor):
        if editor.file_path is not None:
            self.on_update_header.emit({
                "text": "M",
                "widget": "info-file",
                "type": "orange",
                "last":True
            })
        else:
            self.on_update_header.emit({
                "text": "U",
                "widget": "info-file",
                "type": "orange",
                "last":True
            })

    def editor_saved(self, editor):
        self.on_update_header.emit({
            "text": "S",
            "widget": "info-file",
            "type": "green",
            "last":True
        })
    

class Breadcrumbs(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.file_menu = FileMenu(self)
        self.file_menu.save_file.triggered.connect(self.parent.save_file)
        self.file_menu.reload_file.triggered.connect(self.parent.load_file)
        
        self.setObjectName("up-map")
        
        self.hbox = QHBoxLayout(self)
        self.hbox.setSpacing(0)
        self.setLayout(self.hbox)
        
        self.spacing=QWidget(self)
        self.spacing.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.breadcrumb0 = QPushButton(self)
        self.breadcrumb0.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb0.setVisible(False)
        
        self.breadcrumb1 = QPushButton(self)
        self.breadcrumb1.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb1.setVisible(False)
        
        self.breadcrumb2 = QPushButton(self)
        self.breadcrumb2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb2.setVisible(False)
        
        self.breadcrumb3 = QPushButton(self)
        self.breadcrumb3.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb3.setVisible(False)
        
        self.breadcrumb4 = QPushButton(self)
        self.breadcrumb4.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb4.setVisible(False)
        
        self.breadcrumb00 = QPushButton(self)
        self.breadcrumb00.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb00.setVisible(False)
        
        self.breadcrumb01 = QPushButton(self)
        self.breadcrumb01.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb01.setVisible(False)
        
        self.breadcrumb02 = QPushButton(self)
        self.breadcrumb02.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb02.setVisible(False)
        
        self.breadcrumb03 = QPushButton(self)
        self.breadcrumb03.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.breadcrumb03.setVisible(False)
        
        self.file_info = QPushButton(self)
        self.file_info.setIcon(self.parent.icons.get_icon("file"))
        self.file_info.setMenu(self.file_menu)
        self.file_info.clicked.connect(lambda: self.file_info.showMenu())
        
        self.src_ctrl_info = QPushButton(self)
        self.src_ctrl_info.setIcon(self.parent.icons.get_icon("source_control"))
        
        self.warnings_info = QPushButton(self)
        self.warnings_info.setIcon(self.parent.icons.get_icon("warnings"))
        self.warnings_info.setStyleSheet("color:yelllow")
        
        self.errors_info = QPushButton(self)
        self.errors_info.setIcon(self.parent.icons.get_icon("errors"))
        self.errors_info.setStyleSheet("color:red")
        
        self.hbox.addWidget(self.breadcrumb0)
        self.hbox.addWidget(self.breadcrumb1)
        self.hbox.addWidget(self.breadcrumb2)
        self.hbox.addWidget(self.breadcrumb3)
        self.hbox.addWidget(self.breadcrumb4)
        self.hbox.addWidget(self.breadcrumb00)
        self.hbox.addWidget(self.breadcrumb01)
        self.hbox.addWidget(self.breadcrumb02)
        self.hbox.addWidget(self.breadcrumb03)
        self.hbox.addWidget(self.spacing)
        self.hbox.addWidget(self.file_info)
        self.hbox.addWidget(self.src_ctrl_info)
        self.hbox.addWidget(self.warnings_info)
        self.hbox.addWidget(self.errors_info)
        
        self.setFixedHeight(iconsts.BREADCRUMB_FIXED_HEIGHT)
        self.hbox.setContentsMargins(10, 2, 0, 0)
    
class FileMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.reload_file = QAction("Reload File", self)
        self.save_file = QAction("Save File", self)
        self.open_folder = QAction("Open Folder", self)
        
        self.addAction(self.reload_file)
        self.addAction(self.save_file)
        self.addAction(self.open_folder)

class SourceMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.add_file = QAction("Add This File", self)
        self.remove_file = QAction("Remove This File", self)
    
        self.addAction(self.add_file)
        self.addAction(self.remove_file)
        
class EditorView(QFrame):
    
    on_tab_content_changed = pyqtSignal(dict)

    def __init__(self, api:object, parent:object, notebook:object, file = None) -> None:
        super().__init__(parent)
        self.setObjectName("editor-frame")
        self.api = api
        self.parent=parent
        self.notebook = notebook
        self._title = None
        self.file = file
        self._editor = None
        self._editors = []
        self.icons = getfn.get_smartcode_icons("editor")
        self.file_watcher = IFile(self)
        
        self.view_thread = QThread(self)
        self.breadcrumb_controller = BreadcrumbController(self)
        self.breadcrumb_controller.on_update_header.connect(self.set_info)
        self.breadcrumb_controller.moveToThread(self.view_thread)
        self.view_thread.started.connect(self.breadcrumb_controller.run)
        
        if self.file is not None:
            self.file_watcher.start_monitoring(str(self.file))
            print(mimetypes.guess_type(file))
            
        self.init_ui()

    def init_ui(self) -> None:        
        self.layout=QVBoxLayout(self)
        self.layout.setSpacing(iconsts.EDITOR_LAYOUT_SPACING)
        self.setLayout(self.layout)                
        self.layout.setContentsMargins(0,0,0,0)

        self.div = QSplitter(self)
        self.div.setOrientation(Qt.Vertical)

        self.div_main=Div(self.div)
        
        self.editor_main=Editor(self, self.file)
        self.editor_main.connector.auto_save_file.connect(self.file_saved)
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
        self.div.setSizes(iconsts.EDITOR_DIV_SIZES)
        
        self.setMinimumWidth(iconsts.EDITOR_MIN_WIDTH)

        self.editor_main.update_document()
        self.editor_mirror.update_document()

        self._editor = self.editor_main
        self._editors.append(self.editor_main)
        self._editors.append(self.editor_mirror)
        self.join_in_group()
        
        self.breadcrumbs_widget = Breadcrumbs(self)
        
        self.drop_shadow = QGraphicsDropShadowEffect(self)
        self.drop_shadow.setBlurRadius(iconsts.BREADCRUMB_SHADOW_BLURRADIUS_STATE0)
        self.drop_shadow.setOffset(iconsts.BREADCRUMB_SHADOW_Y_OFFSET_STATE0, iconsts.BREADCRUMB_SHADOW_X_OFFSET_STATE0)
        self.drop_shadow.setColor(QColor(0,0,0))
        self.breadcrumbs_widget.setGraphicsEffect(self.drop_shadow)
        
        self.breadcrumbs = {
            "first":self.breadcrumbs_widget.breadcrumb0,
            "second":self.breadcrumbs_widget.breadcrumb1,
            "third":self.breadcrumbs_widget.breadcrumb2,
            "fourth":self.breadcrumbs_widget.breadcrumb3,
            "last":self.breadcrumbs_widget.breadcrumb4,
            "code-first":self.breadcrumbs_widget.breadcrumb00,
            "code-second":self.breadcrumbs_widget.breadcrumb01,
            "code-third":self.breadcrumbs_widget.breadcrumb02,
            "code-last":self.breadcrumbs_widget.breadcrumb03,
            "info-file":self.breadcrumbs_widget.file_info,
            "info-git":self.breadcrumbs_widget.src_ctrl_info,
            "info-warings":self.breadcrumbs_widget.warnings_info,
            "info-errors":self.breadcrumbs_widget.errors_info
        }
        
        self.layout.addWidget(self.breadcrumbs_widget)
        self.layout.addWidget(self.div)
        self.view_thread.start()
    
    def set_info(self, data:dict) -> None:
        text = False
        widget = False
        type = False
        icon = False
        last = False
        keys = data.keys()
        if "text" in keys:
            text = data["text"]
        if "widget" in keys:
            if data["widget"] in self.breadcrumbs.keys():
                widget = self.breadcrumbs[data["widget"]]
        if "type" in keys:
            type = data["type"]
        if "icon" in keys:
            icon = data["icon"]
        if "last" in keys:
            last = data["last"]
        
        if widget:
            if text:
                if not last:
                    text += f" {get_unicon('fae', 'bigger')}"
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
            self.drop_shadow.setBlurRadius(iconsts.BREADCRUMB_SHADOW_BLURRADIUS_STATE1)
            self.drop_shadow.setOffset(iconsts.BREADCRUMB_SHADOW_Y_OFFSET_STATE1, iconsts.BREADCRUMB_SHADOW_X_OFFSET_STATE1)
        else:
            w = self.editor.minimap.size().width()
            y_offset = self.size().width() - w - 200
            self.drop_shadow.setBlurRadius(iconsts.BREADCRUMB_SHADOW_BLURRADIUS_STATE0)
            self.drop_shadow.setOffset(y_offset, iconsts.BREADCRUMB_SHADOW_X_OFFSET_STATE0)

    @property
    def editor(self):
        return self._editor
    
    @property
    def editors(self):
        return self._editors
    
    def get_editors(self):
        return self.editor_main, self.editor_mirror

    @property
    def title(self):
        return self._title

    def set_title(self, title):
        self._title = title

    def update_title(self, new_title):
        self.set_title(new_title)

    def update_code(self, data):
        self.on_tab_content_changed.emit({"widget":self, "data":data})
    
    def save_file(self):
        if self.file is None:
            home_dir = settings.ipwd()
            file = QFileDialog.getSaveFileName(None, 'Open file', home_dir)
            if file[0]:
                self.file=file[0]
                settings.icwd(Path(self.file).parent)
                
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
    
    def file_saved(self):
        if self.file is None:
            self.save_file()
            
        else:
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