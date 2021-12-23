from extension_api import *
export(path="smart_python.src")
from smartpycore import *
from pyterms import *
from symbol_navigator import *
from pyenvs import *
from pyapi import *
from code_tree import *
from code_doctor import *
from code_analyze import *
from refactor import *
from code_warning import *

python_api = PythonApi(
    f"{BASE_PATH}{SYS_SEP}.data{SYS_SEP}user{SYS_SEP}envs{SYS_SEP}envs.idt")

python_envs = []

def build_envs():
    env = jedi.get_default_environment()
    python_envs.append(env)

    if 'PYTHONPATH' in os.environ:
        envs = os.environ['PYTHONPATH'].split(os.pathsep)
        if envs:
            for env in envs:
                python_envs.append(jedi.create_environment(str(env)))

    if SYS_NAME == "linux":
        try:
            python_envs.append(jedi.create_environment("/usr/bin/python3"))
            python_envs.append(jedi.create_environment("/bin/python3"))
        except Exception as e:
            print(e)
            pass

build_envs()

class Init(ModelApp):
    on_env_changed = pyqtSignal(object)
    def __init__(self, data) -> None:
        super().__init__(data, "smart_python")
        self.create_components()
        self.listen_slots()
        self._current_env = None
        self.api_envs_list = python_api.get_default_envs()
        
    def create_components(self):
        # Menu
        self.menu = QMenu("Smart Python")
        
        self.straighten_code = QAction("Straighten Code")
        self.sort_imports = QAction("Sort Imports")
        
        self.menu.addAction(self.straighten_code)
        self.menu.addAction(self.sort_imports)
        self.ui.menu_bar.tools.addMenu(self.menu)
        
        self.python_env = QAction("Python Interpreter\tCtrl+Alt+E")
        self.python_env.setShortcut("Ctrl+Alt+E")
        
        self.goto_symbol = QAction("Goto Symbol in Editor\tCtrl+Shift+O")
        self.goto_symbol.setShortcut("Ctrl+Shift+O")
        
        self.ui.menu_bar.view.addSeparator()
        self.ui.menu_bar.view.addAction(self.python_env)
        self.ui.menu_bar.go.addAction(self.goto_symbol)
        
        # StatusBar
        self.interpreter = QPushButton()
        self.interpreter.setText(f"(smartenv) {getfn.get_python_version()}")
        
        self.ui.status_bar.add_status_widget(self.interpreter)
        
        # Side Bottom
        corner_icons=getfn.get_application_icons("tab-corner")
        
        self.py_console = PyConsole(self.ui.side_bottom)
        self.btn_add_pycell = QPushButton()
        self.btn_add_pycell.setIcon(corner_icons.get_icon("add"))
        self.btn_add_pycell.clicked.connect(lambda: self.py_console.add_cell())
        
        self.ui.side_bottom.insert_widget(1, self.py_console, "PYCONSOLE", [self.btn_add_pycell])
        
        # Editor Widgets
        self.python_envs = self.ui.editor_widgets.addWidgetObject(PythonEnvs)
        self.symbol_navigator = self.ui.editor_widgets.addWidgetObject(SymbolExplorer)
        
        # Lab Widgets
        space = self.ui.side_right.new_space("smart_python")
        
        self.btn_open_pylab=QPushButton("Open")
        self.btn_open_pylab.setObjectName("btn-open-pylab")
        self.btn_open_pylab.clicked.connect(lambda: self.app.open_research_space("smart_python"))
        self.ui.side_left.labs.new_work_space("Python", "smart_python", self.btn_open_pylab)
        
        self.code_tree = CodeTree(None)
        table1 = self.ui.side_right.new_table("Code Tree", self.code_tree)
        
        self.code_doctor = CodeDoctor(None)
        table2 = self.ui.side_right.new_table("Code Doctor", self.code_doctor)
        
        self.code_warnings = CodeWarnings(None)
        table3 = self.ui.side_right.new_table("Code Warnings", self.code_warnings)
        
        self.refactor = Refactor(None)
        table4 = self.ui.side_right.new_table("Code Refactor", self.refactor)
        
        self.deep_analyze = DeepAnalyze(None)
        table5 = self.ui.side_right.new_table("Deep Analyze", self.deep_analyze)
        
        space.add_table(table1, 0, 0)
        space.add_table(table2, 0, 1)
        space.add_table(table3, 1, 0)
        space.add_table(table4, 1, 1)
        space.add_table(table5, 2, 0, 2, 2)
        
        
    def set_current_env(self, env: object) -> None:
        self._current_env = env
        self.on_env_changed.emit(env)
    
    def show_envs(self):
        self.python_envs.set_envs([])
        self.ui.editor_widgets.run_widget(self.python_envs)
    
    def show_goto_symbol(self):
        editor = self.app.notebook_have_editor_with_python()
        if editor:
            self.symbol_navigator.set_symbols(self.get_code_tree(editor))
            self.ui.editor_widgets.run_widget(self.symbol_navigator)
    
    def get_code_tree(self, editor):
        return getfn.get_python_node_tree(editor.text())
        
    def update_statusbar_env(self, env):
        self.status_bar.interpreter.setText(
            f"Python {env.version_info.major}.{env.version_info.minor}.{env.version_info.micro}"
        )
        
    def listen_notebook_slots(self, notebook):
        notebook.widget_added.connect(self.take_editor)

    def listen_slots(self):
        self.add_event("ui.notebook.widget_added", self.take_editor)
        self.add_event("app.on_new_notebook", self.listen_notebook_slots)
        self.on_env_changed.connect(self.update_statusbar_env)
        self.straighten_code.triggered.connect(self.adjust_code)
        self.sort_imports.triggered.connect(self.adjust_imports)
        self.interpreter.clicked.connect(self.show_envs)
        self.python_env.triggered.connect(self.show_envs)
        self.goto_symbol.triggered.connect(self.show_goto_symbol)
    
    def take_editor(self, widget):
        if self.object_is(widget, "editor-frame"):
            editor1, editor2 = widget.get_editors()
            
            if editor1.lexer_name.lower() == "python":
                self.build_editor(editor1)
                
            if editor2.lexer_name.lower() == "python":
                self.build_editor(editor2)
                
            editor1.on_lexer_changed.connect(self.build_editor)
            editor2.on_lexer_changed.connect(self.build_editor)
    
    def build_editor(self, editor):
        status = getattr(editor, "smartpy", None)
        if status is not None:
            
            if editor.lexer_name.lower() == "python" and not status:
                self.make_smart(editor)
                editor.smartpy = True
        else:
            if editor.lexer_name.lower() == "python":
                self.make_smart(editor)
                setattr(editor, "smartpy", True)
    
    def make_smart(self, editor) -> None:
        editor.setIndentationsUseTabs(False)
        
        autocomplete=PyntellisenseCompletions(editor)        
        ide_tools=Pyntellisense(editor)
        live_tips=PyntellisenseEdition(editor)
        live_tips.on_annotation_request.connect(editor.display_annotation)
        live_tips.on_add_indicator_range.connect(editor.add_indicator_range)
        live_tips.on_clear_indicator_range.connect(editor.clear_indicator_range)
        live_tips.on_update_header.connect(editor.update_header)
        ide_tools.on_update_header.connect(editor.update_header)
        ide_tools.on_tooltip_request.connect(editor.display_tooltip)
        
        editor.add_code_completer(autocomplete, autocomplete.run)
        editor.add_development_environment_component(ide_tools, ide_tools.run)
        editor.add_development_environment_component(live_tips, live_tips.run)
    
    def run_code_warnings(self):
        editor = self.app.notebook_have_editor_with_python()
        if editor:
            self.ui.side_right.code_warnings.get_warnings(editor)

    def run_code_tree(self):
        editor = self.app.notebook_have_editor_with_python()
        if editor:
            self.ui.side_right.code_tree.build_tree(editor)

    def run_code_doctor(self):
        editor = self.app.notebook_have_editor_with_python()
        if editor:
            self.ui.side_right.code_doctor.do_analyze(editor.text(), editor)

    def adjust_code(self, editor=None) -> None:
        """Straighten the Python code """
        if editor is None or isinstance(editor, bool):
            editor = self.app.notebook_have_editor_with_python(self.ui.notebook)

        if editor is None or isinstance(editor, bool):
            return
            
        code_smell = editor.text()
        nice_code = getfn.get_straighten_code(code_smell)
        editor.set_text(nice_code)

    def adjust_imports(self):
        """Sort the imported Python libs in code by name"""
        editor = self.app.notebook_have_editor_with_python(self.ui.notebook)
        if editor is None or isinstance(editor, bool):
            return
        code_smell = editor.text()
        nice_code = getfn.get_sorted_imports(code_smell)
        editor.set_text(nice_code)

    def fix_bugs(self, editor):
        """Call method to fix some pep-8 issues and remake the analyze"""
        self.adjust_code(editor)
        self.run_code_warnings()