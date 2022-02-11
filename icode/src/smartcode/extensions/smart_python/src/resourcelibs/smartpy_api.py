from extension_api import *

import ast
import codecs
import itertools
import locale
import os
import os.path
import pathlib
import re
import sys

from PyQt5.QtCore import QSettings
import pathlib
import autopep8
import isort
from yapf.yapflib import yapf_api
import jedi
import smartpy_ide_core as ide
from radon.complexity import cc_rank, cc_visit
from radon.raw import analyze

class EnvApi(QSettings):
    def __init__(self, file_with_path:str, format=QSettings.IniFormat):
        super().__init__(file_with_path, format)
        self.file_path = file_with_path
        self.file_path_object = pathlib.Path(self.file_path)
        self._python_envs = [jedi.get_default_environment()]

        if 'PYTHONPATH' in os.environ:
            envs = os.environ['PYTHONPATH'].split(os.pathsep)
            if envs:
                for env in envs:
                    self._python_envs.append(jedi.create_environment(str(env)))

        if SYS_NAME == "linux":
            try:
                self._python_envs.append(jedi.create_environment("/usr/bin/python3"))
                self._python_envs.append(jedi.create_environment("/bin/python3"))
            except Exception as e:
                print(e)
                pass
    
    def add_env(self, env_path:str) -> list:
        env = self.create_env(env_path)
        if env:
            self._python_envs.append(env)
        self.save_envs()
    
    @property
    def python_envs(self) -> list:
        return self._python_envs
    
    def clear_envs(self) -> list:
        self._python_envs.clear()
        return self._python_envs
    
    def remove_env(self, name:str) -> list:
        for env in self._python_envs:
            if env.executable == name:
                self._python_envs.remove(env)
        return self._python_envs

    def create_env(self, env_path):
        try:
            return jedi.create_environment(env_path)
        except Exception as e:
            print(e)
        return False
    
    def restore_envs(self) -> None:
        return self.value("envs")
    
    def save_envs(self) -> None:
        key = "envs"
        base_list = self.value(key)
        if not isinstance(base_list, list):
            base_list = []
                
        for env in self._python_envs:
            base_list.append(env.executable)
                
        self.setValue(key, base_list)

class PythonApi:
    def __init__(self):
        pass
    
    def get_env(self, path: str):
        try:
            return jedi.create_environment(path)
        except:
            pass
        return None
    
    def get_code_warnings(self, editor) -> dict:
        return_functions_tuple = (ide.tabs_obsolete, ide.trailing_whitespace)
        yield_functions_tuple = (
            ide.extraneous_whitespace, ide.whitespace_around_keywords,
            ide.missing_whitespace_after_import_keyword,
            ide.missing_whitespace, ide.whitespace_around_operator,
            ide.whitespace_around_comma, ide.imports_on_separate_lines,
            ide.compound_statements, ide.comparison_negative,
            ide.python_3000_raise_comma, ide.python_3000_not_equal,
            ide.python_3000_backticks)
        data = {"warnings": [], "lines": []}
        for line in range(editor.lines()):
            line_text = editor.text(line)

            warning = ide.tabs_or_spaces(line_text, "\t")

            if warning != None:
                data["warnings"].append(warning[1])
                data["lines"].append(line)

            for function in return_functions_tuple:
                warning = function(line_text)
                if warning != None:
                    data["warnings"].append(warning[1])
                    data["lines"].append(line)

            for function in yield_functions_tuple:
                warnings = list(function(line_text))
                for warning in warnings:
                    if warning != None:
                        data["warnings"].append(warning[1])
                        data["lines"].append(line)

        return data
    
    def get_python_diagnosis(self, code) -> dict:

        errors = jedi.Script(code=code, path=None).get_syntax_errors()

        try:
            analyze_result = analyze(code)
            complexity_result = cc_visit(code)
        except Exception as e:
            print(e)
            analyze_result = False
            complexity_result = False

        results = {
            "analyze": analyze_result,
            "complexity": complexity_result,
            "syntax_errors": errors
        }
        return results

    def get_pycode_2to3(self, code):
        return autopep8.fix_2to3(code, True)

    def get_straighten_code(self, code):
        return yapf_api.FormatCode(code, style_config='pep8')[0]

    def get_sorted_imports(self, code):
        return isort.code(code)
    
    def get_python_node_tree(self, python_code, sort_way="name"):
        try:
            # Node object
            class PythonNode:
                def __init__(self, name, type, line_number, level):
                    self.name = name
                    self.type = type
                    self.line_number = line_number
                    self.level = level
                    self.children = []

            # Main parsing function
            def parse_node(ast_node, level, parent_node=None):
                nonlocal globals_list
                nonlocal python_node_tree
                new_node = None
                if isinstance(ast_node, ast.ClassDef):
                    new_node = PythonNode(ast_node.name, "class",
                                          ast_node.lineno, level)
                    for child_node in ast_node.body:
                        result = parse_node(child_node, level + 1, new_node)
                        if result != None:
                            if isinstance(result, list):
                                for n in result:
                                    new_node.children.append(n)
                            else:
                                new_node.children.append(result)
                    new_node.children = sorted(new_node.children,
                                               key=lambda x: x.name)
                elif isinstance(ast_node, ast.FunctionDef):
                    new_node = PythonNode(ast_node.name, "function",
                                          ast_node.lineno, level)
                    for child_node in ast_node.body:
                        result = parse_node(child_node, level + 1, new_node)
                        if result != None:
                            if isinstance(result, list):
                                for n in result:
                                    new_node.children.append(n)
                            else:
                                new_node.children.append(result)
                    new_node.children = sorted(new_node.children,
                                               key=lambda x: x.name)
                elif isinstance(ast_node, ast.Import):
                    new_node = PythonNode(ast_node.names[0].name, "import",
                                          ast_node.lineno, level)
                elif isinstance(ast_node,
                                ast.Assign) and (level == 0
                                                 or parent_node == None):
                    # Globals that do are not defined with the 'global' keyword,
                    # but are defined on the top level
                    new_nodes = []
                    for target in ast_node.targets:
                        if hasattr(target, "id") == True:
                            name = target.id
                            if not (name in globals_list):
                                new_nodes.append(
                                    PythonNode(name, "global_variable",
                                               ast_node.lineno, level))
                                globals_list.append(name)
                    return new_nodes
                elif isinstance(ast_node,
                                ast.AnnAssign) and (level == 0
                                                    or parent_node == None):
                    # Type annotated globals
                    new_nodes = []
                    target = ast_node.target
                    if hasattr(target, "id") == True:
                        name = target.id
                        if not (name in globals_list):
                            new_nodes.append(
                                PythonNode(name, "global_variable",
                                           ast_node.lineno, level))
                            globals_list.append(name)
                    return new_nodes
                elif isinstance(ast_node, ast.Global):
                    # Globals can be nested somewhere deep in the AST, so they
                    # are appended directly into the non-local python_node_tree list
                    for name in ast_node.names:
                        if not (name in globals_list):
                            python_node_tree.append(
                                PythonNode(name, "global_variable",
                                           ast_node.lineno, level))
                            globals_list.append(name)
                else:
                    if parent_node != None and hasattr(ast_node, "body"):
                        for child_node in ast_node.body:
                            result = parse_node(child_node, level + 1,
                                                parent_node)
                            if result != None:
                                if isinstance(result, list):
                                    for n in result:
                                        parent_node.children.append(n)
                                else:
                                    parent_node.children.append(result)
                        parent_node.children = sorted(parent_node.children,
                                                      key=lambda x: x.name)
                    else:
                        new_nodes = []
                        if hasattr(ast_node, "body"):
                            for child_node in ast_node.body:
                                result = parse_node(child_node, level + 1,
                                                    None)
                                if result != None:
                                    if isinstance(result, list):
                                        for n in result:
                                            new_nodes.append(n)
                                    else:
                                        new_nodes.append(result)
                        if hasattr(ast_node, "orelse"):
                            for child_node in ast_node.orelse:
                                result = parse_node(child_node, level + 1,
                                                    None)
                                if result != None:
                                    if isinstance(result, list):
                                        for n in result:
                                            new_nodes.append(n)
                                    else:
                                        new_nodes.append(result)
                        if hasattr(ast_node, "finalbody"):
                            for child_node in ast_node.finalbody:
                                result = parse_node(child_node, level + 1,
                                                    None)
                                if result != None:
                                    if isinstance(result, list):
                                        for n in result:
                                            new_nodes.append(n)
                                    else:
                                        new_nodes.append(result)
                        if hasattr(ast_node, "handlers"):
                            for child_node in ast_node.handlers:
                                result = parse_node(child_node, level + 1,
                                                    None)
                                if result != None:
                                    if isinstance(result, list):
                                        for n in result:
                                            new_nodes.append(n)
                                    else:
                                        new_nodes.append(result)
                        if new_nodes != []:
                            return new_nodes
                return new_node

            # Initialization
            parsed_string = ast.parse(python_code)
            python_node_tree = []
            # List of globals for testing for duplicates
            globals_list = []
            # Parse the nodes recursively
            for node in ast.iter_child_nodes(parsed_string):
                result = parse_node(node, 0)
                if result != None:
                    if isinstance(result, list):
                        for n in result:
                            python_node_tree.append(n)
                    else:
                        python_node_tree.append(result)

            # Sort the node list
            if sort_way == "name":
                python_node_tree = sorted(python_node_tree,
                                          key=lambda x: x.name)
            elif sort_way == "number":
                python_node_tree = sorted(python_node_tree,
                                          key=lambda x: x.line_number)

            return python_node_tree

        except SyntaxError:
            return False

python_api = PythonApi()
envs_api = EnvApi(f"{BASE_PATH}{SYS_SEP}.data{SYS_SEP}user{SYS_SEP}envs{SYS_SEP}envs.idt")