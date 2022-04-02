from extension_api import *
from smartpy_api import python_api
import jedi
from smartpy_ide_core import builtin_classes, builtin_functions, primitive_types
from PyQt5.Qsci import QsciStyledText, QsciStyle
from PyQt5.QtCore import QTimer
import json
import requests
import ast

JEDI_TEXT_WRAP_WIDTH = 50
JEDI_HELP_SHORTEN_WIDTH = 400
JEDI_SIGNATURES_WRAP_WIDTH = 90

FUNCTION_REGEX = re.compile(r"(def)\s([_a-zA-Z0-9-]*)")
CLASS_REGEX = re.compile(r"(class)\s([_a-zA-Z0-9-]*)")
BAD_IF_COMPARATION_BOOL_REGEX = re.compile(r"(if|elif)\s([_a-zA-Z0-9-.]*)\s(==|!=)\s(True|False|None)")


class Pyntellisense(QObject):
    on_update_header = pyqtSignal(dict)
    on_tooltip_request = pyqtSignal(dict)

    def __init__(self, parent, server_name):
        super().__init__()
        self.editor = parent
        self.server_name = server_name
        self._env = None
        self.colors = icode_api.get_lexers_frontend()
        self.last_row = 0

    @property
    def env(self):
        return self._env

    def set_env(self, env: object) -> None:
        self._env = env

    def run(self):
        self.make_inline_tree()
        self.editor.on_mouse_stoped.connect(self.build_tooltip)
        self.editor.cursorPositionChanged.connect(self.make_inline_tree)

    def make_inline_tree(self):
        color_main = color_main = self.colors['Default']['fg']
        color_child = color_main = self.colors['Default']['fg']
        name = "..."
        child_name = "..."
        icon1 = getfn.get_qicon(None)
        icon2 = getfn.get_qicon(None)

        if self.editor.lexer_name == "python":

            row, col = self.editor.getCursorPosition()
            if row != self.last_row:
                self.last_row = row
                tree = python_api.get_python_node_tree(self.editor.text(),
                                                       "number")
                if not isinstance(tree, bool):

                    for branch in tree:
                        if branch.line_number <= row + 1:
                            name = branch.name
                            child_branch = sorted(branch.children,
                                                  key=lambda x: x.line_number)

                            if child_branch:
                                for child in child_branch:
                                    if child.line_number <= row + 1:
                                        child_name = child.name

                                        if child.type == "class":
                                            icon2 = self.editor.icons.get_icon(
                                                "class")
                                            color_child = self.colors[
                                                'ClassName']['fg']

                                        elif child.type == "function":
                                            icon2 = self.editor.icons.get_icon(
                                                "function")
                                            color_child = self.colors[
                                                'FunctionMethodName']['fg']

                                        elif child.type == "global_variable":
                                            icon2 = self.editor.icons.get_icon(
                                                "statement")
                                            color_child = color_main = self.colors[
                                                'Default']['fg']

                                        elif child.type == "import":
                                            icon2 = self.editor.icons.get_icon(
                                                "module")
                                            color_child = color_main = self.colors[
                                                'Default']['fg']

                            if branch.type == "class":
                                icon1 = self.editor.icons.get_icon("class")
                                color_main = self.colors['ClassName']['fg']

                            elif branch.type == "function":
                                icon1 = self.editor.icons.get_icon("function")
                                color_main = self.colors['FunctionMethodName'][
                                    'fg']

                            elif branch.type == "global_variable":
                                icon1 = self.editor.icons.get_icon("statement")
                                color_main = color_main = self.colors[
                                    'Default']['fg']

                            elif branch.type == "import":
                                icon1 = self.editor.icons.get_icon("module")
                                color_main = color_main = self.colors[
                                    'Default']['fg']

                if name.startswith("_"):
                    color_main = "gray"

                if child_name.startswith("_"):
                    color_child = "gray"

                self.on_update_header.emit({
                    "text": " " + name,
                    "widget": "code-first",
                    "type": color_main,
                    "icon": icon1,
                    "last": False
                })
                self.on_update_header.emit({
                    "text": " " + child_name,
                    "widget": "code-second",
                    "type": color_child,
                    "icon": icon2,
                    "last": True
                })

    def build_help_string(self, jedi_help):
        if jedi_help.get_type_hint() is None:
            return ''
        ihelp_string = f"<h4 style = 'color:{self.colors['Keyword']['fg']}'>{jedi_help.get_type_hint()}</h4><ul>"
        if jedi_help.full_name is not None:
            ihelp_string += f"<li>Full name: <strong>{jedi_help.full_name}</strong></li>"

        if jedi_help.module_name is not None:
            ihelp_string += f"<li style = 'color:{self.colors['FunctionMethodName']['fg']}'>From: <strong>{jedi_help.module_name}</strong></li>"
        if jedi_help.line is not None:
            ihelp_string += f"<li style = 'color:{self.colors['Comment']['fg']}'>At line: <strong>{jedi_help.line}</strong></li>"
        if jedi_help.description != "":
            ihelp_string += f"<hr><span><h4>Description:</h4><p style = 'color:{self.colors['TripleSingleQuotedFString']['fg']}'>{jedi_help.description}</p></span>"

        if len(jedi_help.docstring()) > 2 and jedi_help.docstring() not in {
                "", " "
        }:

            wrapper = textwrap.TextWrapper(width=JEDI_TEXT_WRAP_WIDTH)
            dedented_text = textwrap.dedent(text=jedi_help.docstring())
            original = wrapper.fill(text=dedented_text)
            shortened = textwrap.shorten(text=original,
                                         width=JEDI_HELP_SHORTEN_WIDTH)
            shortened_wrapped = wrapper.fill(text=shortened)

            ihelp_string += f"<hr><span><h4>Doc:</h4><p style = 'color:{self.colors['TripleSingleQuotedFString']['fg']}'>{shortened_wrapped}</p></span>"

        ihelp_string += "</ul>"

        return ihelp_string

    def build_tooltip(self, pos, x, y) -> None:
        if self.editor.lexer_name == "python":
            try:
                script, hoverWord = self._get_jedi_help(pos, x, y)
                if not script:
                    return
                ihelp = ''
                for jedi_help in script:
                    if not jedi_help.docstring():
                        return
                    if hoverWord == jedi_help.name:
                        ihelp = self.build_help_string(jedi_help)
                        break
                if not ihelp.strip():
                    return
                pos = QPoint(x, y)
                data = {
                    "pos": pos,
                    "text": ihelp,
                }
                self.on_tooltip_request.emit(data)
            except Exception as e:
                return str(e)

    def _get_jedi_help(self, pos, x, y):
        import jedi
        try:
            row, col = self.editor.lineIndexFromPosition(pos)
            if row == -1 or col == -1:
                return None, None
            hover_word = self.editor.wordAtLineIndex(row, col)
            return jedi.Script(code=self.editor.text(),
                               path=self.editor.file_path,
                               environment=self._env).help(row + 1,
                                                           col + 1), hover_word
        except:
            return False, False


class PyntellisenseEdition(QObject):

    on_update_header = pyqtSignal(dict)
    on_annotation_request = pyqtSignal(int, object, int, str)
    on_add_indicator_range = pyqtSignal(int, int, int, int, int, bool)
    on_clear_indicator_range = pyqtSignal(int, int, int, int, int, bool)

    def __init__(self, parent, server_name):
        super().__init__()
        self.editor = parent
        self.server_name = server_name
        self.indicator_ranges = []
        self._env = None

    @property
    def env(self):
        return self._env

    def set_env(self, env: object) -> None:
        self._env = env

    def run(self):
        self.editor.on_text_changed.connect(self.text_changed)
        self.editor.on_modify_key.connect(self.modifiers_keys)
        self.editor.on_saved.connect(self.editor_saved)

    def text_changed(self):
        if self.editor.lexer_name == "python":
            self.do_live_tips()

    def modifiers_keys(self):
        if self.editor.lexer_name == "python":
            self.do_error_finder()
            self.do_warning_finder()

    def editor_saved(self):
        if self.editor.lexer_name == "python":
            self.do_error_finder()
            self.do_warning_finder()

    def do_warning_finder(self):
        code = self.editor.text()
        results = []

        try:
            root = ast.parse(code)
            names = sorted({
                node.id
                for node in ast.walk(root) if isinstance(node, ast.Name)
            })
            regex = "([_a-zA-Z0-9-]*\\(.\\)*)"
            for x in re.findall(regex, code):
                for i in re.findall("([_a-zA-Z0-9-]*)(\\(.*)", x):
                    if i[0] not in results:
                        results.append(i[0])

            for name in results:
                if name in names:
                    continue
                else:
                    pass
                #print(name)
            #print(results)
            #print(names)

        except Exception as e:
            print(e)

    def do_error_finder(self):
        try:
            for range in self.indicator_ranges:
                self.on_clear_indicator_range.emit(0, 0, -1, -1, 1, True)

            code = self.editor.text()
            errors = jedi.Script(code=code, path=None,
                                 environment=self._env).get_syntax_errors()
            if len(errors) > 0:
                self.on_update_header.emit({
                    "text": str(len(errors)),
                    "widget": "info-errors",
                    "type": "red",
                    "last":True
                })
            else:
                self.on_update_header.emit({
                    "text": "0",
                    "widget": "info-errors",
                    "type": "green",
                    "last":True
                })

            for error in errors:
                self.on_add_indicator_range.emit(error.line - 1, error.column,
                                                 error.until_line - 1,
                                                 error.until_column, 1, True)
            self.indicator_ranges = errors

        except Exception as e:
            print(e)
            pass

    def do_live_tips(self):
        row, col = self.editor.getCursorPosition()
        raw_text = self.editor.text(row)
        raw_material = raw_text
        material = raw_material.lstrip()

        if material.split(" ")[0] == "def":
            ans = self.analyze_function(raw_text)
            if ans:
                self.on_annotation_request.emit(row, ans, 1, "on_text_changed")

        if material.split(" ")[0] == "class":
            ans = self.analyze_class(raw_text)
            if ans:
                self.on_annotation_request.emit(row, ans, 1, "on_text_changed")

        if material.split(" ")[0] == "if" or material.split(" ")[0] == "elif":
            ans = self.analyze_conditions(raw_text)
            if ans:
                self.on_annotation_request.emit(row, ans, 1, "on_text_changed")

    def extract_name(self,
                     query: str,
                     compiled_regex: object,
                     group_number: int = 1) -> str:
        string = ""

        regexp = compiled_regex

        for match in regexp.finditer(query):
            if group_number < 0:
                return match.groups()
            string += match.group(group_number)
        return string

    def analyze_class(self, material):
        class_name = self.extract_name(material, CLASS_REGEX, 2)
        good_class_name = class_name.capitalize()

        if class_name != "":
            if class_name.lower() == class_name:

                return [
                    QsciStyledText(
                        "PEP-8 recommendation: Start each class name with a capital letter!\n",
                        1),
                    QsciStyledText("SUGGESTION: ", 7),
                    QsciStyledText(good_class_name, 8)
                ]

            elif "_" in class_name:
                return [
                    QsciStyledText(
                        "PEP-8 recommendation: Do not separate class name with underscores!\n",
                        1),
                    QsciStyledText("SUGGESTION: ", 200),
                    QsciStyledText(
                        f"{good_class_name.replace('_','')}||{good_class_name.title().replace('_','')}",
                        8),
                ]

            elif class_name in primitive_types or class_name in builtin_classes:
                return [
                    QsciStyledText(
                        f"WARNING: {class_name} it's an integrated class or primitive type!\n",
                        1),
                    QsciStyledText("This could cause future errors!\n", 1),
                    QsciStyledText("SUGGESTION: ", 7),
                    QsciStyledText(
                        f"{good_class_name.replace('_','')}||{good_class_name.title().replace('_','')}",
                        8),
                ]

        return False

    def analyze_function(self, material: str) -> str:

        function_name = self.extract_name(material, FUNCTION_REGEX, 2)
        if function_name != "":
            if function_name.lower() != function_name:
                return [
                    QsciStyledText(
                        "PEP-8 recommendation: Use a lowercase word or words!\n",
                        1),
                    QsciStyledText(
                        "Separate words by underscores to improve readability.\n",
                        1),
                    QsciStyledText("SUGGESTION: ", 7),
                    QsciStyledText(function_name.lower(), 9)
                ]

            elif function_name in builtin_functions:
                return [
                    QsciStyledText(
                        f"WARNING: {function_name} it's an integrated function!\n",
                        1),
                    QsciStyledText("This could cause future errors.\n", 1),
                    QsciStyledText("SUGGESTION: ", 7),
                    QsciStyledText(f"{function_name.lower()}_", 9)
                ]

        return False

    def analyze_conditions(self, material: str) -> str:
        material = material.lstrip()
        condition = self.extract_name(material, BAD_IF_COMPARATION_BOOL_REGEX,
                                      -1)
        if len(condition) > 3:
            if condition[3] == "True" or condition[3] == "False":
                return QsciStyledText(
                    f"> Anti-pattern: '{condition[2]}'\n When comparing a variable to boolean, you should use the form\n> '{condition[0]} {condition[1]} is {condition[3]}' or simply '{condition[0]} {condition[1]}'",
                    200)

            if condition[3] == "None":
                return QsciStyledText(
                    f"> Anti-pattern: '{condition[2]}'\n Comparisons to the singleton objects, like True, False, and None\nshould be done with identity, not equality. Use “is” or “is not”\n> SUGGESTION: '{condition[0]} {condition[1]} is {condition[3]}' or '{condition[0]} is not {condition[1]}'",
                    200)


class PyntellisenseCompletions(QObject):

    on_error = pyqtSignal(object, object, object)
    on_load_completions = pyqtSignal(object, list)
    on_remove_dead_completion = pyqtSignal(object, list)
    on_show_help = pyqtSignal(object, int, list)

    def __init__(self, parent, server_name):
        super().__init__()
        self._runing = False
        self._env = None
        self._lexer_api = None
        self.editor = parent
        self.completions = []
        self.last_row = None
        self.__status = False
        self.server_name = server_name
        self.urls = None
        self._statements = []
        self.get_urls()

    def get_urls(self):
        server = langserver.icenter.get_server_by_name(self.server_name)
        if server is not None:
            self.urls = dict()
            self.urls[
                "complete"] = f"http://{server.host}:{server.port}/complete"
            self.urls[
                "complete-search"] = f"http://{server.host}:{server.port}/complete_search"
            self.__status = True

    @property
    def env(self):
        return self._env

    def set_env(self, env: object) -> None:
        self._env = env

    def run(self):
        self.editor.on_complete.connect(self.update_api)

    def is_builtin(self, dict, key):
        if key in dict.keys():
            return True
        return False

    def get_ref(self, completion):
        if completion == "function":
            return "?1"
        elif completion == "keyword":
            return "?2"
        elif completion == "class":
            return "?3"
        elif completion == "module":
            return "?4"
        elif completion == "instance":
            return "?5"
        elif completion == "statement":
            return "?6"
        elif completion == "param":
            return "?7"
        elif completion == "path":
            return "?8"
        elif completion == "property":
            return "?9"
        else:
            return "?10"

    def update_api(self, data):
        if self.__status:
            lexer_name = data["lexer-name"]
            source_code = data["code"]
            file_code = data["file"]
            row, col = data["cursor-pos"]
            lexer_api = data["lexer-api"]
            event_text = data["event-text"]
            word = data["word"]
            env = None
            if self._env is not None:
                env = self._env.executable

            if lexer_name == "python" and not self._runing:
                completions = []
                suggestions = []
                dead_statement = []
                try:
                    if lexer_api != self._lexer_api and lexer_api is not None:
                        self._lexer_api = lexer_api
                        self._lexer_api.apiPreparationStarted.connect(
                            lambda: self.runing(True))
                        self._lexer_api.apiPreparationFinished.connect(
                            lambda: self.runing(False))

                    if not col:  #or row == self.last_row:
                        return

                    complete_request_data = {
                        'code': source_code,
                        "file": str(file_code),
                        "cursor-pos": data["cursor-pos"],
                        "event-text": event_text,
                        "env": env
                    }
                    complete_help_request_data = {
                        'code': source_code,
                        "file": str(file_code),
                        "env": env,
                        "word": word,
                        "all-scopes": True,
                        "fuzzy": False
                    }

                    complete_response = requests.get(
                        self.urls["complete"],
                        data=json.dumps(complete_request_data))
                    complete_help_response = requests.get(
                        self.urls["complete-search"],
                        data=json.dumps(complete_help_request_data))

                    if complete_response.status_code == 200:
                        completers = complete_response.json()
                        for completion in completers["response"]:

                            ref = self.get_ref(completion["type"])
                            value = (f'{completion["name_with_symbols"]}{ref}')

                            if self.is_builtin(builtin_functions,
                                               completion["name"]):
                                value = f'{completion["name"]}{ref}{builtin_functions[completion["name"]]}'

                            if value not in self.completions:
                                self.completions.append(value)
                                completions.append(value)

                            if completion["type"] == "statement":
                                self._statements.append(completion["name"])

                    if complete_help_response.status_code == 200:
                        complete_helpers = complete_help_response.json()
                        suggestions = self.get_help(
                            complete_helpers["response"])

                    if completions:
                        self.on_load_completions.emit(self._lexer_api,
                                                      completions)

                    if suggestions:
                        self.on_show_help.emit(self.editor, row, suggestions)

                    if row != self.last_row:
                        root = ast.parse(source_code)
                        statements = sorted({
                            node.id
                            for node in ast.walk(root)
                            if isinstance(node, ast.Name)
                        })
                        for var in self._statements:
                            if var not in statements:
                                self._statements.remove(var)
                                dead_statement.append(
                                    var + self.get_ref("statement"))

                    if dead_statement:
                        self.on_remove_dead_completion.emit(
                            self._lexer_api, dead_statement)

                    self.last_row = row
                except Exception as e:
                    print("Completions: Python: jedi: ", e)
                    self.on_error.emit(self, self.editor, e)
            else:
                if self.urls is None:
                    self.get_urls()

    def get_help(self, complete_helpers) -> list:
        help_names = []
        items = []
        for x, suggestion in enumerate(complete_helpers):
            if suggestion["name"] not in help_names:
                items.append(QsciStyledText(suggestion["name"] + "  ", 210))
                help_names.append(suggestion["name"])

            if x > 5:
                break

        return items

    def runing(self, status):
        self._runing = status

    def stop(self):
        self.__status = False

    def start(self):
        self.__status = True
