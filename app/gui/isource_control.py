from PyQt5.QtWidgets import (QFrame, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTreeView, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal
from functions import getfn

import pygit2 as pygit
import pathlib
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from .igui import HeaderPushButton, IStandardItem, HeaderLabel

class GitMenu(QMenu):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.open_repository = QAction("Open Repository", self)
        self.addAction(self.open_repository)
        self.clone_repository = QAction("Clone Repository", self)
        self.addAction(self.clone_repository)
        self.addSeparator()
        self.add_all = QAction("Add All", self)
        self.addAction(self.add_all)
        self.commit = QAction("Commit", self)
        self.addAction(self.commit)
        

class StatusTree(QTreeView):
    
    on_count_changed = pyqtSignal(int, int, int)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.icons = getfn.get_application_icons("source_control")
        self.init_ui()
    
    def init_ui(self):
        self.header().hide()
        self.model = QStandardItemModel(self)
        self.setModel(self.model)
        self.setUniformRowHeights(True)
    
    def build_tree(self, repository):        
        total_count = 0
        unmodified_count = 0
        modified_count = 0
        
        repo_path = getattr(repository, "workdir", None)
        repo_name = ""
        if repo_path is not None:
            repo_name = pathlib.Path(repo_path).name
            
        status_data = repository.status()
        
        repo_branch = "No commits yet"
        try:
            repo_branch = "/"+repository.head.shorthand
        except:
            pass
        
        self.model.clear()

        self.repo_header = IStandardItem(self.icons.get_icon("repository"), repo_name, None, None, 0)
        self.repo_header.setCheckable(False)
        self.model.appendRow(self.repo_header)
        
        self.unmodified = IStandardItem(self.icons.get_icon("unmodified"), '•UNMODIFIED', None, None, 0)
        self.unmodified.setCheckable(False)
        self.unmodified.setForeground(QColor(63, 242, 105, 180))
        self.model.appendRow(self.unmodified)
        
        self.modified = IStandardItem(self.icons.get_icon("modified"), '•MODIFIED', None, None, 0)
        self.modified.setCheckable(False)
        self.modified.setForeground(QColor(212, 242, 63, 180))
        self.model.appendRow(self.modified)
        
        self.added = IStandardItem(self.icons.get_icon("added"), '•ADDED', None, None, 0)
        self.added.setCheckable(False)
        self.model.appendRow(self.added)
        
        self.deleted = IStandardItem(self.icons.get_icon("deleted"), '•DELETED', None, None, 0)
        self.deleted.setCheckable(False)
        self.model.appendRow(self.deleted)
        
        self.renamed = IStandardItem(self.icons.get_icon("renamed"), '•RENAMED', None, None, 0)
        self.renamed.setCheckable(False)
        self.model.appendRow(self.renamed)
        
        self.copied = IStandardItem(self.icons.get_icon("copied"), '•COPIED', None, None, 0)
        self.copied.setCheckable(False)
        self.model.appendRow(self.copied)
        
        self.updated_but_unmerged = IStandardItem(self.icons.get_icon("updated_unmerged"), '•UPDATED BUT UNMERGED', None, None, 0)
        self.updated_but_unmerged.setCheckable(False)
        self.model.appendRow(self.updated_but_unmerged)
        
        self.untracked = IStandardItem(self.icons.get_icon("untracked"), '•UNTRACKED', None, None, 0)
        self.untracked.setCheckable(False)
        self.model.appendRow(self.untracked)
        
        self.ignored = IStandardItem(self.icons.get_icon("ignored"), '•IGNORED FILES', None, None, 0)
        self.ignored.setCheckable(False)
        self.model.appendRow(self.ignored)
        
        for key, value in status_data.items():
            row = IStandardItem(self.icons.get_icon("file"), key, None, None, 0)
            if value in {1, 2}:
                self.unmodified.appendRow(row)
                row.setForeground(QColor(63, 242, 105))
                unmodified_count += 1
                total_count += 1
            
            elif value == 128:
                self.untracked.appendRow(row)
                total_count += 1
            
            elif value in {256,257,258}:
                self.modified.appendRow(row)
                row.setForeground(QColor(212, 242, 63))
                modified_count += 1
                total_count += 1
            
            elif value == 513:
                self.deleted.appendRow(row)
                total_count += 1
            
            elif value == 16384:
                self.ignored.appendRow(row)
                total_count += 1

            if value not in {1,2,128,257,256,258,513,16384}:
                print(key, value)
            else:
                pass
        
        repo_data = f"""
        <p>Name: {repo_name}</p>
        <p>Path: {repository.workdir}</p> 
        <p>Branch: {repo_branch}</p>
        <p>Total Files: {total_count}</p>
        """
        self.repo_header.setToolTip(repo_data)
        
        self.on_count_changed.emit(total_count, unmodified_count, modified_count)

class IGit(QFrame):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent=parent
        self.icons=getfn.get_application_icons("source_control")
        self.repository_menu = GitMenu(self)
        self.repository = None
        self.init_ui()
    
    def init_ui(self):
        self.layout=QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)

        self.top_info=QLabel("<small>SOURCE CONTROL</small>")
        self.top_info.setWordWrap(True)
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.top_info)
        
        self.btn_repository = HeaderPushButton(self)
        self.btn_repository.setMenu(self.repository_menu)
        self.btn_repository.setObjectName("source_control-header-button")
        self.btn_repository.setIcon(self.icons.get_icon("repository"))
        self.btn_repository.clicked.connect(lambda: self.btn_repository.showMenu())
        
        self.lbl_total = HeaderLabel(self)
        
        self.header_layout.addWidget(self.lbl_total)
        self.header_layout.addWidget(self.btn_repository)
        
        self.btn_reload = HeaderPushButton(self)
        self.btn_reload.setObjectName("source_control-header-button")
        self.btn_reload.setIcon(self.icons.get_icon("reload"))
        self.btn_reload.clicked.connect(self.reload)
        self.header_layout.addWidget(self.btn_reload)
    
        self.layout.addLayout(self.header_layout)
    
        self.btn_open_repository = QPushButton("Open Repository")
        self.btn_clone_repository = QPushButton("Clone Repository")
        
        self.status_tree = StatusTree(self)
        self.status_tree.on_count_changed.connect(self.update_headers)
        self.status_tree.setVisible(False)
        
        self.layout.addWidget(self.btn_open_repository)
        self.layout.addWidget(self.btn_clone_repository)
        self.layout.addWidget(self.status_tree)
    
    def open_repository(self, repo_path = None):
        if repo_path is None:
            path = QFileDialog.getExistingDirectory(None, 'Open Folder', "", QFileDialog.ShowDirsOnly)
            
            if path == "":
                return None
            
            repo_path = path
        
        try:
            self.repository = pygit.Repository(repo_path+'/.git')
            self.btn_clone_repository.setVisible(False)
            self.btn_open_repository.setVisible(False)
            if self.repository is not None:
                self.status_tree.build_tree(self.repository)
                self.status_tree.setVisible(True)
            return self.repository
        except Exception as e:
            print(e)

    def clone_repository(self):
        self.parent.parent.editor_widgets.do_clone_repo()
    
    def reload(self):
        self.status_tree.build_tree(self.repository)
    
    def update_headers(self, total, _, __):
        self.lbl_total.setText(f"<p><img src='{self.icons.get_path('file')}' width='16' height='16'>{str(total)}</p>")
        