import pathlib
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import QObject
from system import BASE_PATH, SYS_SEP
import json

class Init(QObject):
    def __init__(self, data) -> None:
        super().__init__(data["app"])
        self._db = None
        self.app=data["app"]
        self.ui = self.app.ui

        self.file=pathlib.Path(f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}icode_sky_view{SYS_SEP}data{SYS_SEP}data.json")
        
        self.menu = QMenu("Sky View")
        
        self.auto_connection = QAction("Auto")
        self.auto_connection.setCheckable(True)
        self.auto_connection.setChecked(True)
        self.auto_connection.triggered.connect(self.switch_status)
        
        self.user_connection = QAction("Show/Hide")
        self.user_connection.setCheckable(True)
        self.user_connection.setChecked(False)
        self.user_connection.triggered.connect(self.change_status)

        self.menu.addAction(self.auto_connection)
        self.menu.addAction(self.user_connection)
        
        self.ui.menu_bar.tools.addMenu(self.menu)

        if self.file.exists():
            if len(self.file.read_text()) <= 1:
                self.create_data(self.file)
            self.load_data(self.file)
        else:
            file = open(self.file, "w")
            file.close()
            self.create_data(self.file)
            self.switch_status()

    def change_status(self):
        if self.user_connection.isChecked():
            for notebook in self.ui.notebooks:
                notebook.tabBar().hide()
        else:
            for notebook in self.ui.notebooks:
                notebook.tabBar().show()
        
        self.save_status()
    
    def switch_status(self):
        if self.auto_connection.isChecked():
            self.enable()
        else:
            self.disable()
        
        self.save_status()
    
    def enable(self):
        for notebook in self.ui.notebooks:
            notebook.setTabBarAutoHide(True)
    
    def disable(self):
        for notebook in self.ui.notebooks:
            notebook.setTabBarAutoHide(False)
    
    def load_data(self, filename):
        with open(filename, "r") as file:
            db = json.load(file)
        self._db = db
        
        if "auto" in self._db.keys():
            if type(self._db["auto"]) == bool:
                self.auto_connection.setChecked(self._db["auto"])
                self.switch_status()
        
        if "user" in self._db.keys():
            if type(self._db["user"]) == bool:
                self.user_connection.setChecked(self._db["user"])
                self.change_status()
    
    def create_data(self, filename):
        with open(filename, "w") as file:
            json.dump({"auto":True, "user":False}, file)
        
        with open(filename, "r") as file:
            db = json.load(file)
        self._db = db
        self.load_data(self.file)
    
    def save_status(self):
        if self.app.ui.notebook.count() > 0:
            self._db["auto"] = self.auto_connection.isChecked()
            self._db["user"] = self.user_connection.isChecked()
            with open(self.file, "w") as file:
                json.dump(self._db, file)