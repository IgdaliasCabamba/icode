from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSize, QThread
from PyQt5.QtWidgets import (
    QFrame, QGridLayout, QFileDialog,
    QHBoxLayout, QListWidget,
    QPushButton, QSizePolicy,
    QVBoxLayout, QGraphicsDropShadowEffect,
    QLabel
)
from ..igui import InputHistory
from PyQt5.QtGui import QColor

import pathlib
from functions import getfn
import pygit2 as pygit
import re
import os
from typing import Union
import settings

REGEX = re.compile(r"((https|http)(://[_a-zA-Z0-9-]*.[_a-zA-Z0-9-]*/[_a-zA-Z0-9-]*)/([-_a-zA-Z0-9-]*.git))")
group_number = 4

def get_folder_name_from_clone_url(url:str) -> Union[str, tuple, None]:
    string = str()
    
    for match in REGEX.finditer(url):
        if group_number < 0:
            return match.groups()
        string += match.group(group_number)
    
    if len(string) >= 0:
            
        name = re.split("\.", string)
        if name:
            return name[0]
            
    return None

class Cloner(QObject):
    
    finished = pyqtSignal(object, str)
    error = pyqtSignal(str)
    
    def __init__(self, main:object):
        super().__init__()
        self.main = main
    
    def run(self):
        self.main.on_clone_request.connect(self.clone)
    
    def clone(self, url, path):
        try:
            name = get_folder_name_from_clone_url(url)
            path+=os.sep+name
            repo = pygit.clone_repository(url, path)
            if isinstance(repo, pygit.Repository):
                self.finished.emit(repo, name)
        
        except ValueError as e:
            self.error.emit(str(e))
            # TODO
            
        except Exception as e:
            print(e)

class CloneRepo(QFrame):
    
    on_clone_request = pyqtSignal(str, str)
    focus_out = pyqtSignal(object, object)
    
    def __init__(self, api, parent):
        super().__init__(parent)
        self.api = api
        self._parent = parent
        
        self.clone_thread = QThread(self)
        self.cloner = Cloner(self)
        self.cloner.finished.connect(self.cloned)
        self.cloner.error.connect(self.dont_cloned)
        self.cloner.moveToThread(self.clone_thread)
        self.clone_thread.started.connect(self.cloner.run)
        self.clone_thread.start()
        
        self.setParent(parent)
        self.setObjectName("editor-widget")
        self.init_ui()
    
    def init_ui(self):

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self.layout)

        self.input_url = InputHistory(self)
        self.input_url.returnPressed.connect(lambda: self.clone_repo(self.input_url.text()))
        self.size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.input_url.setSizePolicy(self.size_policy)
        self.input_url.setPlaceholderText("Url to repository")
        self.input_url.setObjectName("child")
        
        self.layout.addWidget(self.input_url)
    
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self.focusWidget() not in self.findChildren(object, "child"):
            self.focus_out.emit(self, event)
    
    def clone_repo(self, url:str):
        home_dir = settings.ipwd()
        folder = QFileDialog.getExistingDirectory(None, 'Select Location', home_dir)
        if folder is not None:
            self.on_clone_request.emit(url, folder)
        
    def cloned(self, repo:object, name:str):
        repo_path = getattr(repo, "workdir", None)
        btn_open_folder = QPushButton("Open Folder")
        btn_open_repo = QPushButton("Open Repository")
        btn_open_folder.clicked.connect(lambda: self.api.api.side_left.explorer.open_folder(repo_path))
        btn_open_repo.clicked.connect(lambda: self.api.api.side_left.git.load_repository(repo))
        self.api.api.ui.notificator.new_notification("Repo Cloned", f"The repository{name} was cloned to {repo_path}", [btn_open_repo, btn_open_folder])
    
    def dont_cloned(self, error:str):
        print(error)
        
    def run(self):
        self.input_url.setFocus()
        self.setFixedHeight(35)

class ComitCode(QFrame):pass