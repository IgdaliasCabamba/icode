import os
import pathlib
from system import BASE_PATH
from PyQt5.Qsci import *
from PyQt5.QtCore import QObject, pyqtSignal, QPoint, QTimer
from data import builtin_functions, builtin_classes, primitive_types
from functions import getfn, filefn
import textwrap
import re
import jedi
from . import iconsts

FUNCTION_REGEX = re.compile(r"(def)\s([_a-zA-Z0-9-]*)")
CLASS_REGEX = re.compile(r"(class)\s([_a-zA-Z0-9-]*)")
BAD_IF_COMPARATION_BOOL_REGEX = re.compile(r"(if|elif)\s([_a-zA-Z0-9-.]*)\s(==|!=)\s(True|False|None)")

class IdeTools(QObject):
    on_update_header = pyqtSignal(dict)
    on_tooltip_request=pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__()
        self.editor=parent
        self._env = None
        self.colors = getfn.get_lexer_colors()
        self.last_row = 0
    
    @property
    def env(self):
        return self._env
    
    def set_env(self, env:object) -> None:
        self._env = env
    
    def run(self):
        self.configure_headers()
        self.configure_inline_tree()
        self.editor.on_mouse_stoped.connect(self.build_tooltip)
        self.editor.idocument.on_changed.connect(self.configure_headers)
        self.editor.cursorPositionChanged.connect(self.configure_inline_tree)
    
    def configure_headers(self):
        if self.editor.file_path is None:
            self.on_update_header.emit({"text":" Unsaved >", "widget":self.editor.parent.up_info0})
        else:
            widgets = [
                self.editor.parent.up_info0,
                self.editor.parent.up_info1,
                self.editor.parent.up_info2,
                self.editor.parent.up_info3,
                self.editor.parent.up_info4,
                self.editor.parent.up_info5,
                self.editor.parent.up_info6,
                self.editor.parent.up_info7
                ]
            path_levels = getfn.get_path_splited(self.editor.idocument.file)
            i = 0
            for path in path_levels:
                if path.replace(" ", "") == "":
                    continue
                if i < len(widgets):
                    self.on_update_header.emit({"text":" "+str(path)+" >", "widget":widgets[i]})
                else:
                    break
                    self.on_update_header.emit({"text":" "+str(self.editor.idocument.file_name)+" >", "widget":widgets[i]})
                i+=1
            #self.on_update_header.emit({"text":" "+str(self.editor.idocument.file_name)+" >", "widget":self.editor.parent.up_info7})
        self.on_update_header.emit({"widget":self.editor.parent.up_info0, "icon":self.editor.idocument.icon})
    
    def configure_inline_tree(self):
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
                tree = getfn.get_python_node_tree(self.editor.text(), "number")
                if not isinstance(tree, bool):
                    
                    for branch in tree:
                        if branch.line_number <= row+1:
                            name = branch.name
                            child_branch = sorted(branch.children, key=lambda x: x.line_number)
                            
                            if child_branch:
                                name += " >"
                                for child in child_branch:
                                    if child.line_number <= row+1:
                                        child_name = child.name
                                        
                                        if child.type == "class":
                                            icon2 = self.editor.icons.get_icon("class")
                                            color_child = self.colors['ClassName']['fg']
                                            
                                        elif child.type == "function":
                                            icon2 = self.editor.icons.get_icon("function")
                                            color_child = self.colors['FunctionMethodName']['fg']
                                        
                                        elif child.type == "global_variable":
                                            icon2 = self.editor.icons.get_icon("statement")
                                            color_child = color_main = self.colors['Default']['fg']
                                        
                                        elif child.type == "import":
                                            icon2 = self.editor.icons.get_icon("module")
                                            color_child = color_main = self.colors['Default']['fg']
                            
                            if branch.type == "class":
                                icon1 = self.editor.icons.get_icon("class")
                                color_main = self.colors['ClassName']['fg']
                            
                            elif branch.type == "function":
                                icon1 = self.editor.icons.get_icon("function")
                                color_main = self.colors['FunctionMethodName']['fg']
                            
                            elif branch.type == "global_variable":
                                icon1 = self.editor.icons.get_icon("statement")
                                color_main = color_main = self.colors['Default']['fg']
                            
                            elif branch.type == "import":
                                icon1 = self.editor.icons.get_icon("module")
                                color_main = color_main = self.colors['Default']['fg']
                
                if name.startswith("_"):
                    color_main = "gray"
                
                if child_name.startswith("_"):
                    color_child = "gray"
                
                self.on_update_header.emit({"text":" "+name, "widget":self.editor.parent.up_info01, "type":color_main, "icon":icon1})
                self.on_update_header.emit({"text":" "+child_name, "widget":self.editor.parent.up_info02, "type":color_child, "icon":icon2})
                    

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
        
        if len(jedi_help.docstring()) > 2 and jedi_help.docstring() not in {""," "}:
            
            wrapper = textwrap.TextWrapper(width=iconsts.JEDI_TEXT_WRAP_WIDTH)  
            dedented_text = textwrap.dedent(text=jedi_help.docstring())
            original = wrapper.fill(text=dedented_text)
            shortened = textwrap.shorten(text=original, width=iconsts.JEDI_HELP_SHORTEN_WIDTH)
            shortened_wrapped = wrapper.fill(text=shortened)

            ihelp_string += f"<hr><span><h4>Doc:</h4><p style = 'color:{self.colors['TripleSingleQuotedFString']['fg']}'>{shortened_wrapped}</p></span>"

        ihelp_string +="</ul>"

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
                pos=QPoint(x, y)
                data={
                    "pos":pos,
                    "text":ihelp,
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
            return jedi.Script(
                code=self.editor.text(),
                path=self.editor.file_path,
                environment=self._env
                ).help(
                    row+1,
                    col+1
                    ), hover_word
        except:
            return False, False

class LiveEdition(QObject):
    
    on_update_header = pyqtSignal(dict)
    on_annotation_request = pyqtSignal(int, str, int, str)
    on_add_indicator_range = pyqtSignal(int, int, int, int, int, bool)
    on_clear_indicator_range = pyqtSignal(int, int, int, int, int, bool)

    def __init__(self, parent):
        super().__init__()
        self.editor=parent
        self.indicator_ranges = []
        self._env = None
    
    @property
    def env(self):
        return self._env
    
    def set_env(self, env:object) -> None:
        self._env = env
    
    def run(self):
        self.editor.on_text_changed.connect(self.text_changed)
        self.editor.on_modify_key.connect(self.modifiers_keys)
        self.editor.on_saved.connect(self.editor_saved)
        self.editor.file_watcher.on_file_deleted.connect(self.file_deleted)
        self.editor.file_watcher.on_file_modified.connect(self.file_modified)
    
    def file_deleted(self, file):
        self.on_update_header.emit({"text":"D", "widget":self.editor.parent.file_info, "type":"red"})
    
    def file_modified(self, file):
        if filefn.read_file(file) != self.editor.text():
            self.on_update_header.emit({"text":"M", "widget":self.editor.parent.file_info, "type":"red"})
    
    def text_changed(self):
        if self.editor.lexer_name=="python":
            self.do_live_tips()
        
        if self.editor.file_path is not None:
            self.on_update_header.emit({"text":"M", "widget":self.editor.parent.file_info, "type":"orange"})
        else:
            self.on_update_header.emit({"text":"U", "widget":self.editor.parent.file_info, "type":"orange"})
    
    def modifiers_keys(self):
        if self.editor.lexer_name=="python":
            self.do_error_finder()
    
    def editor_saved(self):
        if self.editor.lexer_name=="python":
            self.do_error_finder()
        
        self.on_update_header.emit({"text":"S", "widget":self.editor.parent.file_info, "type":"green"})
        
    def do_error_finder(self):
            try:
                for range in self.indicator_ranges:
                    self.on_clear_indicator_range.emit(0, 0, -1, -1, 1, True)

                code=self.editor.text()
                errors=jedi.Script(code=code, path=None, environment=self._env).get_syntax_errors()
                if len(errors) > 0:
                    self.on_update_header.emit({"text":str(len(errors)), "widget":self.editor.parent.errors_info, "type":"red"})
                else:
                    self.on_update_header.emit({"text":"0", "widget":self.editor.parent.errors_info, "type":"green"})
                
                for error in errors:
                    self.on_add_indicator_range.emit(error.line-1, error.column, error.until_line-1, error.until_column, 1, True)
                self.indicator_ranges = errors
            
            except Exception as e:
                print(e)
                pass

    def do_live_tips(self):
        row, col = self.editor.getCursorPosition()
        raw_text = self.editor.text(row)
        raw_material = raw_text
        material = raw_material.lstrip()
        
        if material.split(" ")[0]=="def":
            ans = self.analyze_function(raw_text)
            if ans:
                self.on_annotation_request.emit(row, ans, 1, "on_text_changed")

        if material.split(" ")[0]=="class":
            ans = self.analyze_class(raw_text)
            if ans:
                self.on_annotation_request.emit(row, ans, 1, "on_text_changed")
        
        if material.split(" ")[0]=="if" or material.split(" ")[0]=="elif":
            ans = self.analyze_conditions(raw_text)
            if ans:
                self.on_annotation_request.emit(row, ans, 1, "on_text_changed")
    
    def extract_name(self, query:str, compiled_regex:object, group_number:int = 1) -> str:
        string = ""
        
        regexp = compiled_regex
        
        for match in regexp.finditer(query):
            if group_number < 0:
                return match.groups()
            string += match.group(group_number)
        return string

    def analyze_class(self, material):
        class_name=self.extract_name(material, CLASS_REGEX, 2)
        good_class_name = class_name.capitalize()

        if class_name != "":
            if class_name.lower() == class_name:
                return f"> PEP-8 recommendation: Start each class name with a capital letter.\n> SUGGESTION: {good_class_name}"
            elif "_" in class_name:
                return f"> PEP-8 recommendation: Do not separate class name with underscores.\n> SUGGESTION: {good_class_name.replace('_','')}||{good_class_name.title().replace('_','')}"
            elif class_name in primitive_types or class_name in builtin_classes:
                return f"> WARNING: {class_name} it's an integrated class or primitive type\nThis could cause future errors.\n> SUGGESTION: {good_class_name.replace('_','')}||{good_class_name.title().replace('_','')}"
        return False

    def analyze_function(self, material:str) -> str:
        
        function_name=self.extract_name(material, FUNCTION_REGEX, 2)
        if function_name != "":
            if function_name.lower() != function_name:
                return f"> PEP-8 recommendation: Use a lowercase word or words.\nSeparate words by underscores to improve readability.\n> SUGGESTION: {function_name.lower()}"
            elif function_name in builtin_functions:
                return f"> WARNING: {function_name} it's an integrated function\nThis could cause future errors.\n> SUGGESTION: {function_name.lower()}_"
        return False
    
    def analyze_conditions(self, material:str) -> str:
        material = material.lstrip()
        condition=self.extract_name(material, BAD_IF_COMPARATION_BOOL_REGEX, -1)
        if len(condition) > 3:
            if condition[3] == "True" or condition[3] == "False":
                return f"> Anti-pattern: '{condition[2]}'\n When comparing a variable to boolean, you should use the form\n> '{condition[0]} {condition[1]} is {condition[3]}' or simply '{condition[0]} {condition[1]}'"
            
            if condition[3] == "None":
                return f"> Anti-pattern: '{condition[2]}'\n Comparisons to the singleton objects, like True, False, and None\nshould be done with identity, not equality. Use “is” or “is not”\n> SUGGESTION: '{condition[0]} {condition[1]} is {condition[3]}' or '{condition[0]} is not {condition[1]}'"
    
    def close_char(self, char):
        row, col = self.editor.getCursorPosition()
        char_to_close = self.editor.closable_key_map[char]
        can_close = getfn.get_char_is_closable(col, self.editor.text(row))
        if not can_close:
            self.editor.insertAt(char_to_close, row, col)

class Autocompletions(QObject):
    
    on_error = pyqtSignal(str)
    
    def __init__(self, parent):
        super().__init__()
        self._runing = False
        self._env = None
        self.editor=parent
        self.configure_jedi()
    
    @property
    def env(self):
        return self._env

    def set_env(self, env:object) -> None:
        self._env = env

    def configure_jedi(self):
        import jedi 

        self.names_list=[]
        
        cache_directory = os.path.join(BASE_PATH, '.cache', 'jedi')
        
        if pathlib.Path(cache_directory).is_dir():
            jedi.settings.cache_directory = cache_directory

        jedi.settings.add_bracket_after_function = False
        jedi.settings.fast_parser = False
        jedi.settings.call_signatures_validity = 3.0
        jedi.settings.dynamic_params_for_other_modules = True
        jedi.settings.dynamic_params = True
        
    def run(self):
        self.update_api()
        self.editor.on_update_completions.connect(self.update_api)
    
    def is_builtin(self, dict, key):      
        if key in dict.keys():
            return True
        return False
    
    def get_ref(self, completion):
        if completion=="function":
            return "?1"
        elif completion=="keyword":
            return "?2"
        elif completion=="class":
            return "?3"
        elif completion=="module":
            return "?4"
        elif completion=="instance":
            return "?5"
        elif completion=="statement":
            return "?6"
        elif completion=="param":
            return "?7"
        elif completion=="path":
            return "?8"
        elif completion=="property":
            return "?9"
        else:
            print(completion)
            return "?10"

    def update_api(self):
        if self.editor.lexer_name=="python" and not self._runing:
            try:
                self.__api=self.editor.lexer_api
                if self.__api is not None:
                    self.__api.apiPreparationStarted.connect(lambda: self.runing(True))
                    self.__api.apiPreparationFinished.connect(lambda: self.runing(False))
                    self.__api.clear()
                    import jedi
                            
                    source_code=self.editor.text()
                    file_code=self.editor.file_path

                    row, col = self.editor.getCursorPosition()

                    if not col:
                        return
                    
                    script = jedi.Script(code=source_code, path=file_code, environment=self._env)
                    completions=script.complete(row+1, col)
                    signatures = script.get_signatures(row+1, col)
                    
                    for completion in completions:
                        
                        ref = self.get_ref(completion.type)

                        if self.is_builtin(builtin_functions, completion.name):
                            self.__api.add(f"{completion.name}{ref}{builtin_functions[completion.name]}")
                            if not completion.name in self.names_list or not completion.name_with_symbols in self.names_list:
                                self.names_list.append(completion.name)
                            continue
                        
                        if completion.type == "class" or completion.type == "function":

                            if signatures:
                                params_str = "("
                                call_tip = signatures[-1]

                                for param in call_tip.params:
                                    params_str+=param.to_string()
                                    params_str+=", "
                                params_str+=")"
                                
                                wrapper = textwrap.TextWrapper(width=iconsts.JEDI_SIGNATURES_WRAP_WIDTH)
                                dedented_text = textwrap.dedent(text=params_str)
                                params_wrapped = wrapper.fill(text=dedented_text)

                                self.__api.add(f"{completion.name}{ref}{params_wrapped}")
                                if not completion.name in self.names_list or not completion.name_with_symbols in self.names_list:
                                    self.names_list.append(completion.name)
                            
                            else:
                                self.__api.add(f"{completion.name}{ref}")
                                if not completion.name in self.names_list or not completion.name_with_symbols in self.names_list:
                                    self.names_list.append(completion.name)

                            continue

                        self.__api.add(f"{completion.name_with_symbols}{ref}")
                        if not completion.name in self.names_list or not completion.name_with_symbols in self.names_list:
                            self.names_list.append(completion.name_with_symbols)

                self.__api.prepare()
            except Exception as e:
                print(e)
                self.on_error.emit(str(e))
                return
        else:
            return
    
    def get_help(self, source: str, row: int, col: int, filename: str = None):
        try:
            help = jedi.Script(code=source, path=filename).help(row+1, col)
            if help:
                return help
        except Exception as e:
            print(e)
            return False
    
    def runing(self, status):
        self._runing = status
