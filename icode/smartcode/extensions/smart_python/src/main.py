from extension_api import *

need_dirs = [os.path.join(BASE_PATH, '.cache', 'jedi'), os.path.join(BASE_PATH, 'smartcode', 'data', 'user', 'envs')]
make_dirs(need_dirs)

export(path="smart_python.src")
export(path="smart_python.src.vendor")
export(path="smart_python.src.resourcelibs")
export(path="smart_python.src.resourcelibs.jedi")

from smartpy_core import *
from smartpy_consoles import *
from smartcode_navigator import *
from smartpy_envs import *
from smartpy_api import *
from smartcode_tree import *
from smartcode_doctor import *
from smartcode_analyze import *
from smart_refactor import *
from smartcode_warning import *
from smartpy_debug import *

class Init(ModelApp):
    
    on_env_changed = pyqtSignal(object)
    
    def __init__(self, data) -> None:
        super().__init__(data, "smart_python")
        self.build_ui()
        self.listen_slots()
        self._current_env = None
        self.api_envs_list = envs_api.python_envs
        self.objects_mem = {
            "editors":[],
            "autocompleters":[],
            "live_tipers":[],
            "ide_utils":[]            
        }
        
    def build_ui(self):
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
        self.pylab_desc = """
            <h5>Icode Python Labs</h5>
        """
        self.ui.side_left.labs.new_work_space("Python", "smart_python", self.pylab_desc, self.btn_open_pylab)
        
        self.code_tree = CodeTree(None)
        self.btn_run_tree = QPushButton()
        self.btn_run_tree.setObjectName("Button")
        self.btn_run_tree.setProperty("style-bg","transparent")
        self.btn_run_tree.setIcon(corner_icons.get_icon("start"))
        table1 = self.ui.side_right.new_table("Code Tree", self.code_tree)
        table1.setMinimumSize(250,300)
        table1.add_header_widget(self.btn_run_tree)
        
        self.code_doctor = CodeDoctor(None)
        self.btn_run_doctor = QPushButton()
        self.btn_run_doctor.setObjectName("Button")
        self.btn_run_doctor.setProperty("style-bg","transparent")
        self.btn_run_doctor.setIcon(corner_icons.get_icon("start"))
        table2 = self.ui.side_right.new_table("Code Doctor", self.code_doctor)
        table2.add_header_widget(self.btn_run_doctor)
        table2.setMinimumSize(250,300)
        
        self.code_warnings = CodeWarnings(None)
        self.btn_run_warnings = QPushButton()
        self.btn_run_warnings.setObjectName("Button")
        self.btn_run_warnings.setProperty("style-bg", "transparent")
        self.btn_run_warnings.setIcon(corner_icons.get_icon("start"))
        table3 = self.ui.side_right.new_table("Code Warnings", self.code_warnings)
        table3.add_header_widget(self.btn_run_warnings)
        table3.setMinimumSize(250,300)
        
        self.refactor = Refactor(None)
        table4 = self.ui.side_right.new_table("Code Refactor", self.refactor)
        table4.setMinimumSize(250,300)
        
        self.deep_analyze = DeepAnalyze(None)
        self.btn_run_analyze = QPushButton()
        self.btn_run_analyze.setObjectName("Button")
        self.btn_run_analyze.setProperty("style-bg","transparent")
        self.btn_run_analyze.setIcon(corner_icons.get_icon("start"))
        table5 = self.ui.side_right.new_table("Deep Analyze", self.deep_analyze)
        table5.add_header_widget(self.btn_run_analyze)
        table5.setMinimumSize(200,200)
        
        self.debug = Debug(None)
        self.btn_clear_debug=QPushButton()
        self.btn_clear_debug.setObjectName("Button")
        self.btn_clear_debug.setProperty("style-bg","transparent")
        self.btn_clear_debug.setIcon(corner_icons.get_icon("clear"))
        self.btn_start_debug=QPushButton()
        self.btn_start_debug.setObjectName("Button")
        self.btn_start_debug.setProperty("style-bg","transparent")
        self.btn_start_debug.setIcon(corner_icons.get_icon("start"))
        self.btn_stop_debug=QPushButton()
        self.btn_stop_debug.setObjectName("Button")
        self.btn_stop_debug.setProperty("style-bg","transparent")
        self.btn_stop_debug.setIcon(corner_icons.get_icon("stop"))
        table6 = self.ui.side_right.new_table("Debug", self.debug)
        table6.add_header_widget(self.btn_start_debug)
        table6.add_header_widget(self.btn_stop_debug)
        table6.add_header_widget(self.btn_clear_debug)
        table6.setMinimumSize(200,300)
        
        space.add_table(table1, 0, 0)
        space.add_table(table2, 0, 1)
        space.add_table(table3, 1, 0)
        space.add_table(table4, 1, 1)
        space.add_table(table5, 2, 0, 2, 2)
        space.add_table(table6, 4, 0, 4, 2)
    
    def add_env(self, env:object) -> None:
        self.api_envs_list.append(env)
        self.python_envs.set_envs(self.api_envs_list)
        
    def set_current_env(self, env: object) -> None:
        self._current_env = env
        self.on_env_changed.emit(env)
        l = []
        l.extend(self.objects_mem["autocompleters"])
        l.extend(self.objects_mem["ide_utils"])
        l.extend(self.objects_mem["live_tipers"])
        for x in l:
            if hasattr(x, "set_env"):
                x.set_env(self._current_env)
    
    def show_envs(self):
        self.python_envs.set_envs(self.api_envs_list)
        self.ui.editor_widgets.run_widget(self.python_envs)
    
    def show_goto_symbol(self):
        editor = self.app.notebook_have_editor_with_python()
        if editor:
            self.symbol_navigator.set_symbols(self.get_code_tree(editor))
            self.ui.editor_widgets.run_widget(self.symbol_navigator)
    
    def get_code_tree(self, editor):
        return python_api.get_python_node_tree(editor.text())
        
    def update_statusbar_env(self, env):
        self.interpreter.setText(f"Python {env.version_info.major}.{env.version_info.minor}.{env.version_info.micro}")
        
    def listen_notebook_slots(self, notebook):
        notebook.widget_added.connect(self.take_editor)

    def listen_slots(self):
        self.add_event("ui.notebook.widget_added", self.take_editor)
        self.add_event("app.on_new_notebook", self.listen_notebook_slots)
        self.add_event("on_env_changed", self.update_statusbar_env)
        self.add_event("straighten_code.triggered", self.adjust_code)
        self.add_event("sort_imports.triggered", self.adjust_imports)
        self.add_event("interpreter.clicked", self.show_envs)
        self.add_event("python_env.triggered", self.show_envs)
        self.add_event("goto_symbol.triggered", self.show_goto_symbol)
        self.add_event("btn_open_pylab.clicked", lambda: self.app.open_research_space("smart_python"))        
        self.add_event("btn_run_tree.clicked", self.run_code_tree)
        self.add_event("btn_run_doctor.clicked", self.run_code_doctor)
        self.add_event("btn_run_warnings.clicked", self.run_code_warnings)
        self.add_event("code_doctor.btn_get_diagnosis.clicked", self.run_code_doctor)
        self.add_event("code_warnings.btn_get_warnings.clicked", self.run_code_warnings)
        self.add_event("code_warnings.on_fix_bugs_clicked", self.fix_bugs)
        self.add_event("python_envs.on_env_added", self.add_env)
        self.add_event("python_envs.on_current_env", self.set_current_env)
    
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
            
            elif editor.lexer_name.lower() != "python" and status:
                editor.smartpy = False
                
        else:
            if editor.lexer_name.lower() == "python":
                self.make_smart(editor)
                setattr(editor, "smartpy", True)
    
    def make_smart(self, editor) -> None:
        editor.setIndentationsUseTabs(False)
        editor.lexer().setFoldComments(True)
        editor.lexer().setFoldQuotes(True)
        
        autocomplete=PyntellisenseCompletions(editor)        
        ide_utils=Pyntellisense(editor)
        live_tips=PyntellisenseEdition(editor)
        
        live_tips.on_annotation_request.connect(editor.display_annotation)
        live_tips.on_add_indicator_range.connect(editor.add_indicator_range)
        live_tips.on_clear_indicator_range.connect(editor.clear_indicator_range)
        live_tips.on_update_header.connect(editor.update_header)
        ide_utils.on_update_header.connect(editor.update_header)
        ide_utils.on_tooltip_request.connect(editor.display_tooltip)
        
        editor.add_code_completer(autocomplete, autocomplete.run)
        editor.add_development_environment_component(ide_utils, ide_utils.run)
        editor.add_development_environment_component(live_tips, live_tips.run)
        
        if editor not in self.objects_mem["editors"]:
            self.objects_mem["editors"].append(editor)
        
        if autocomplete not in self.objects_mem["autocompleters"]:
            self.objects_mem["autocompleters"].append(autocomplete)
        
        if ide_utils not in self.objects_mem["ide_utils"]:
            self.objects_mem["ide_utils"].append(ide_utils)
        
        if live_tips not in self.objects_mem["live_tipers"]:
            self.objects_mem["live_tipers"].append(live_tips)
    
    def run_code_warnings(self):
        editor = self.app.notebook_have_editor_with_python()
        if editor:
            self.code_warnings.get_warnings(editor)

    def run_code_tree(self):
        editor = self.app.notebook_have_editor_with_python()
        if editor:
            self.code_tree.build_tree(editor)

    def run_code_doctor(self):
        editor = self.app.notebook_have_editor_with_python()
        if editor:
            self.code_doctor.do_analyze(editor.text(), editor)

    def adjust_code(self, editor=None) -> None:
        """Straighten the Python code """
        if editor is None or isinstance(editor, bool):
            editor = self.app.notebook_have_editor_with_python(self.ui.notebook)

        if editor is None or isinstance(editor, bool):
            return
            
        code_smell = editor.text()
        nice_code = python_api.get_straighten_code(code_smell)
        editor.set_text(nice_code)

    def adjust_imports(self):
        """Sort the imported Python libs in code by name"""
        editor = self.app.notebook_have_editor_with_python(self.ui.notebook)
        if editor is None or isinstance(editor, bool):
            return
        code_smell = editor.text()
        nice_code = python_api.get_sorted_imports(code_smell)
        editor.set_text(nice_code)

    def fix_bugs(self, editor):
        """Call method to fix some pep-8 issues and remake the analyze"""
        self.adjust_code(editor)
        self.run_code_warnings()