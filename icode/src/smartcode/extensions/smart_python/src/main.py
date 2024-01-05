from extension_api import *

make_dirs([os.path.join(ROOT_PATH, ".cache", "jedi")])

export(path="smart_python.src")
export(path="smart_python.src.vendor")
export(path="smart_python.src.resourcelibs")
export(path="smart_python.src.resourcelibs.jedi")

# extension loc

from .resourcelibs.smartpy_analyze import *
from .resourcelibs.smartpy_api import *
from .resourcelibs.smartpy_consoles import *
from .resourcelibs.smartpy_core import *
from .resourcelibs.smartpy_debug import *
from .resourcelibs.smartpy_doctor import *
from .resourcelibs.smartpy_envs import *
from .resourcelibs.smartpy_navigator import *
from .resourcelibs.smartpy_refactor import *
from .resourcelibs.smartpy_server import *
from .resourcelibs.smartpy_tree import *
from .resourcelibs.smartpy_utils import *
from .resourcelibs.smartpy_warning import *
from .resourcelibs.smartpy_jupyter import *

pylang_server_data = get_pylang_server()

py_server = langserver.icenter.run_new_server(
    pylang_server_data["run"],
    {
        "name": SERVER_NAME,
        "mode": "TCP4",
        "service": pylang_server_data["service"],
        "host": pylang_server_data["host"],
        "port": pylang_server_data["port"],
    },
)


class Init(ModelApp):

    on_env_changed = pyqtSignal(object)

    def __init__(self, data) -> None:
        super().__init__(data, "smart_python")
        self.build_ui()
        self.listen_slots()
        self.api_envs_list = envs_api.python_envs
        self._current_env = self.api_envs_list[0]
        self.objects_mem = {
            "editors": [],
            "autocompleters": [],
            "live_tipers": [],
            "ide_utils": [],
        }
        self.smartpy_intellisense = intellisense.IIntellisense(self)

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
        corner_icons = getfn.get_smartcode_icons("tab-corner")

        self.py_console = PyConsole(self.ui.side_bottom)
        self.btn_add_pycell = QPushButton()
        self.btn_add_pycell.setIcon(corner_icons.get_icon("add"))
        self.btn_add_pycell.clicked.connect(lambda: self.py_console.add_cell())

        self.ui.side_bottom.insert_widget(1, self.py_console, "PYCONSOLE",
                                          [self.btn_add_pycell])

        self.jupyter_console = JupyterConsole(self.ui.side_bottom)
        self.btn_add_jupyter_cell = QPushButton()
        self.btn_add_jupyter_cell.setIcon(corner_icons.get_icon("add"))
        self.btn_add_jupyter_cell.clicked.connect(
            lambda: self.jupyter_console.add_cell())

        self.ui.side_bottom.insert_widget(2, self.jupyter_console, "JUPYTER",
                                          [self.btn_add_jupyter_cell])

        # Editor Widgets
        self.python_envs = self.ui.editor_widgets.addWidgetObject(PythonEnvs)
        self.symbol_navigator = self.ui.editor_widgets.addWidgetObject(
            SymbolExplorer)

        # Lab Widgets
        space = self.ui.side_right.new_space("smart_python")

        self.btn_open_pylab = QPushButton("Open")
        self.btn_open_pylab.setObjectName("btn-open-pylab")
        self.pylab_desc = DESCRIPTION
        self.ui.side_left.labs.new_work_space("Python", "smart_python",
                                              self.pylab_desc,
                                              self.btn_open_pylab)

        self.code_tree = CodeTree(None)
        self.btn_run_tree = QPushButton()
        self.btn_run_tree.setObjectName("Button")
        self.btn_run_tree.setProperty("style-bg", "transparent")
        self.btn_run_tree.setIcon(corner_icons.get_icon("start"))
        table1 = self.ui.side_right.new_table("Code Tree", self.code_tree)
        table1.setMinimumSize(300, 360)
        table1.add_header_widget(self.btn_run_tree)

        self.code_doctor = CodeDoctor(None)
        self.btn_run_doctor = QPushButton()
        self.btn_run_doctor.setObjectName("Button")
        self.btn_run_doctor.setProperty("style-bg", "transparent")
        self.btn_run_doctor.setIcon(corner_icons.get_icon("start"))
        table2 = self.ui.side_right.new_table("Code Doctor", self.code_doctor)
        table2.add_header_widget(self.btn_run_doctor)
        table2.setMinimumSize(300, 360)

        self.code_warnings = CodeWarnings(None)
        self.btn_run_warnings = QPushButton()
        self.btn_run_warnings.setObjectName("Button")
        self.btn_run_warnings.setProperty("style-bg", "transparent")
        self.btn_run_warnings.setIcon(corner_icons.get_icon("start"))
        table3 = self.ui.side_right.new_table("Code Warnings",
                                              self.code_warnings)
        table3.add_header_widget(self.btn_run_warnings)
        table3.setMinimumSize(300, 360)

        self.refactor = Refactor(None)
        self.btn_run_refactor = QPushButton()
        self.btn_run_refactor.setObjectName("Button")
        self.btn_run_refactor.setProperty("style-bg", "transparent")
        self.btn_run_refactor.setIcon(corner_icons.get_icon("start"))
        table4 = self.ui.side_right.new_table("Code Refactor", self.refactor)
        table4.add_header_widget(self.btn_run_refactor)
        table4.setMinimumSize(300, 360)

        self.deep_analyze = DeepAnalyze(None)
        self.btn_run_analyze = QPushButton()
        self.btn_run_analyze.setObjectName("Button")
        self.btn_run_analyze.setProperty("style-bg", "transparent")
        self.btn_run_analyze.setIcon(corner_icons.get_icon("start"))
        table5 = self.ui.side_right.new_table("Deep Analyze",
                                              self.deep_analyze)
        table5.add_header_widget(self.btn_run_analyze)
        table5.setMinimumSize(200, 300)

        self.debug = Debug(None)
        self.btn_clear_debug = QPushButton()
        self.btn_clear_debug.setObjectName("Button")
        self.btn_clear_debug.setProperty("style-bg", "transparent")
        self.btn_clear_debug.setIcon(corner_icons.get_icon("clear"))
        self.btn_start_debug = QPushButton()
        self.btn_start_debug.setObjectName("Button")
        self.btn_start_debug.setProperty("style-bg", "transparent")
        self.btn_start_debug.setIcon(corner_icons.get_icon("start"))
        self.btn_stop_debug = QPushButton()
        self.btn_stop_debug.setObjectName("Button")
        self.btn_stop_debug.setProperty("style-bg", "transparent")
        self.btn_stop_debug.setIcon(corner_icons.get_icon("stop"))
        table6 = self.ui.side_right.new_table("Debug", self.debug)
        table6.add_header_widget(self.btn_start_debug)
        table6.add_header_widget(self.btn_stop_debug)
        table6.add_header_widget(self.btn_clear_debug)
        table6.setMinimumSize(300, 700)

        space.add_table(table1, 0, 0)
        space.add_table(table2, 0, 1)
        space.add_table(table3, 1, 0)
        space.add_table(table4, 1, 1)
        space.add_table(table5, 2, 0, 2, 2)
        space.add_table(table6, 4, 0, 4, 2)

    def listen_slots(self) -> None:
        self.do_on(self.set_current_editor, "app", "on_current_editor_changed")
        self.do_on(self.take_editor, "ui", "notebook", "widget_added")
        self.do_on(self.listen_notebook_slots, "app", "on_new_notebook")
        self.do_on(self.update_statusbar_env, "on_env_changed")
        self.do_on(self.adjust_code, "straighten_code", "triggered")
        self.do_on(self.adjust_imports, "sort_imports", "triggered")
        self.do_on(self.show_envs, "interpreter", "clicked")
        self.do_on(self.show_envs, "python_env", "triggered")
        self.do_on(self.show_goto_symbol, "goto_symbol", "triggered")
        self.do_on(
            lambda: self.app.open_research_space("smart_python"),
            "btn_open_pylab",
            "clicked",
        )
        self.do_on(self.run_code_tree, "btn_run_tree", "clicked")
        self.do_on(self.run_code_doctor, "btn_run_doctor", "clicked")
        self.do_on(self.run_code_warnings, "btn_run_warnings", "clicked")
        self.do_on(self.run_code_analyze, "btn_run_analyze", "clicked")
        self.do_on(self.run_code_doctor, "code_doctor", "btn_get_diagnosis",
                   "clicked")
        self.do_on(self.run_code_warnings, "code_warnings", "btn_get_warnings",
                   "clicked")
        self.do_on(self.fix_bugs, "code_warnings", "on_fix_bugs_clicked")
        self.do_on(self.run_code_analyze, "deep_analyze", "btn_get_diagnosis",
                   "clicked")
        self.do_on(self.add_env, "python_envs", "on_env_added")
        self.do_on(self.set_current_env, "python_envs", "on_current_env")
        self.do_on(self.start_debugging, "btn_start_debug", "clicked")
        self.do_on(self.start_debugging, "debug", "btn_start_debug", "clicked")
        self.do_on(self.stop_debugging, "btn_stop_debug", "clicked")
        self.do_on(self.clear_debug_output, "btn_clear_debug", "clicked")

    def add_env(self, env: object) -> None:
        envs_api.add_env(env.executable)
        self.python_envs.set_envs(self.api_envs_list)
        self.api_envs_list = envs_api.python_envs

    def set_current_env(self, env: object) -> None:
        self._current_env = env
        self.on_env_changed.emit(env)
        l = []
        l.extend(self.objects_mem["autocompleters"])
        l.extend(self.objects_mem["ide_utils"])
        l.extend(self.objects_mem["live_tipers"])
        for x in l:
            if hasattr(x, "set_env"):
                x.set_env(env)

    def show_envs(self) -> None:
        self.python_envs.set_envs(self.api_envs_list)
        self.ui.editor_widgets.run_widget(self.python_envs)

    def show_goto_symbol(self):
        editor = self.app.current_notebook_editor(None, "lexer_name", "python")
        if editor:
            self.symbol_navigator.set_symbols(self.get_code_tree(editor))
            self.ui.editor_widgets.run_widget(self.symbol_navigator)

    def get_code_tree(self, editor) -> object:
        return python_api.get_python_node_tree(editor.text())

    def update_statusbar_env(self, env) -> None:
        self.interpreter.setText(
            f"Python {env.version_info.major}.{env.version_info.minor}.{env.version_info.micro}"
        )

    def listen_notebook_slots(self, notebook) -> None:
        notebook.widget_added.connect(self.take_editor)

    def take_editor(self, widget) -> None:
        if isfn.is_widget_code_editor(widget):
            editor1, editor2 = widget.get_editors()

            if editor1.lexer_name.lower() == "python":
                self.build_editor(editor1)

            if editor2.lexer_name.lower() == "python":
                self.build_editor(editor2)

            editor1.on_lexer_changed.connect(self.build_editor)
            editor2.on_lexer_changed.connect(self.build_editor)

    def build_editor(self, editor) -> None:
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

        autocomplete = PyntellisenseCompletions(editor, SERVER_NAME)
        ide_utils = Pyntellisense(editor, SERVER_NAME)
        live_tips = PyntellisenseEdition(editor, SERVER_NAME)

        autocomplete.on_error.connect(self.repair)
        autocomplete.on_load_completions.connect(self.add_completions)
        autocomplete.on_show_help.connect(self.show_help)
        autocomplete.on_remove_dead_completion.connect(
            self.remove_completion_entry)
        live_tips.on_annotation_request.connect(editor.display_annotation)
        live_tips.on_add_indicator_range.connect(editor.add_indicator_range)
        live_tips.on_clear_indicator_range.connect(
            editor.clear_indicator_range)
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

        editor.set_ide_mode(True)
        autocomplete.set_env(self._current_env)
        live_tips.set_env(self._current_env)
        ide_utils.set_env(self._current_env)

    def repair(self, broke, editor, error) -> None:
        if isinstance(broke, PyntellisenseCompletions):

            autocomplete = PyntellisenseCompletions(editor, SERVER_NAME)
            autocomplete.on_error.connect(self.repair)
            autocomplete.on_load_completions.connect(self.add_completions)
            autocomplete.on_show_help.connect(self.show_help)
            editor.add_code_completer(autocomplete, autocomplete.run)

            broke.stop()

    def show_help(self, editor, row, suggestion) -> None:
        # editor.display_annotation(row, suggestion, 210, "on_lines_changed", 1)
        pass

    def add_completions(self, lexer_api, completions) -> None:
        self.smartpy_intellisense.add(lexer_api, completions)

    def remove_completion_entry(self, lexer_api, completions) -> None:
        self.smartpy_intellisense.remove(lexer_api, completions)

    def set_current_editor(self, editor):
        pass

    def run_code_warnings(self) -> None:
        editor = self.app.current_notebook_editor(None, "lexer_name", "python")
        if editor:
            self.code_warnings.get_warnings(editor)

    def run_code_tree(self) -> None:
        editor = self.app.current_notebook_editor(None, "lexer_name", "python")
        if editor:
            self.code_tree.build_tree(editor)

    def run_code_doctor(self) -> None:
        editor = self.app.current_notebook_editor(None, "lexer_name", "python")
        if editor:
            self.code_doctor.do_analyze(editor.text(), editor)

    def run_code_analyze(self) -> None:
        editor = self.app.current_notebook_editor(None, "lexer_name", "python")
        if editor:
            self.deep_analyze.do_analyze(editor.text(), editor)

    def adjust_code(self, editor=None) -> None:
        """Straighten the Python code"""
        if editor is None or isinstance(editor, bool):
            editor = self.app.current_notebook_editor(self.ui.notebook,
                                                      "lexer_name", "python")

        if editor is None or isinstance(editor, bool):
            return

        code_smell = editor.text()
        nice_code = python_api.get_straighten_code(code_smell)
        if nice_code is not None:
            editor.set_text(nice_code)

    def adjust_imports(self) -> None:
        """Sort the imported Python libs in code by name"""
        editor = self.app.current_notebook_editor(self.ui.notebook,
                                                  "lexer_name", "python")
        if editor is None or isinstance(editor, bool):
            return
        code_smell = editor.text()
        nice_code = python_api.get_sorted_imports(code_smell)
        if nice_code is not None:
            editor.set_text(nice_code)

    def fix_bugs(self, editor) -> None:
        """Call method to fix some pep-8 issues and remake the analyze"""
        self.adjust_code(editor)
        self.run_code_warnings()

    def start_debugging(self):
        editor = self.app.current_notebook_editor(None, "lexer_name", "python")
        if editor:
            self.debug.start(editor, editor.text(), editor.file_path,
                             self._current_env)

    def stop_debugging(self):
        self.debug.stop()

    def clear_debug_output(self):
        self.debug.clear()
