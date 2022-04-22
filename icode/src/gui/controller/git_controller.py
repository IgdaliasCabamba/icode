from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog
import pygit2 as pygit
import settings

class GitController(QObject):
    def __init__(self, application_core, view):
        super().__init__()
        self.application_core = application_core
        self.view = view
        self.repository = None

        self.view.repository_menu.init_repository.triggered.connect(self.init_repository)
        self.view.repository_menu.clone_repository.triggered.connect(self.clone_repository)
        self.view.repository_menu.add_all.triggered.connect(self.add_all)
        
        self.view.btn_reload.clicked.connect(self.reload)
        self.view.btn_clone_repository.clicked.connect(self.clone_repository)
        self.view.input_commit_log.textChanged.connect(self.find_commit)
        self.view.input_commit_log.returnPressed.connect(self.do_commit)

    def open_repository(self, repo_path=None):
        if repo_path is None:
            home_dir = settings.ipwd()
            path = QFileDialog.getExistingDirectory(
                None, "Open Folder", home_dir, QFileDialog.ShowDirsOnly
            )

            if path == "":
                return None
            repo_path = path

        try:
            repository = pygit.Repository(repo_path + "/.git")
            self.load_repository(repository)
            return repository
        except Exception as e:
            print(e)

    def clone_repository(self):
        self.view.set_page(0)
        self.application_core.editor_widgets.do_clone_repo()

    def init_repository(self):
        self.view.set_page(0)
        self.application_core.editor_widgets.do_init_repo()

    def reload(self):
        self.view.set_page(0)
        self.view.status_tree.build_tree(self.repository)

    def add_all(self):
        if isinstance(self.repository, pygit.Repository):
            index = self.repository.index
            index.add_all()
            index.write()
            self.reload()

    def find_commit(self, text):
        if len(text) > 0:
            self.view.set_page(1)
            self.view.commit_tree.search_commit(self.repository, text)
        else:
            self.view.set_page(0)
    
    def do_commit(self):
        print(self.view.input_commit_log.text())
    
    def load_repository(self, repository: object) -> None:
        self.view.set_page(0)
        try:
            self.repository = repository

            # t0=repository.revparse_single('HEAD')
            # t1=repository.revparse_single('HEAD^')

            # out=repository.diff(t0,t1)
            # print(dir(out))

            self.view.btn_clone_repository.setVisible(False)
            self.view.btn_open_repository.setVisible(False)
            self.view.input_commit_log.setVisible(True)
            if self.repository is not None:
                self.view.status_tree.build_tree(self.repository)
                self.view.status_tree.setVisible(True)
        except Exception as e:
            print(e)