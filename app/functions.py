import codecs
import itertools
import locale
import os
import os.path
import pathlib
import re
import sys

from PyQt5.QtGui import QColor, QFont, QIcon, QImage, QPixmap
from shamanld import Shaman
from system import BASE_PATH, SYS_NAME, SYS_SEP
from typing_extensions import ParamSpec

import components.consts as iconsts
import config
import data
import smartlibs.jedit2 as ijson
from components.extension_manager import Ext
from smartsci.lexers import *


class IO:
    """
    IO functions to control tasks related to data input and output in the operating system
    """
    def __init__(self) -> None:
        pass

    def adjust_path(self, path: str) -> str:
        return os.path.normpath(path)

    def correct_path(self, path: str) -> str:
        tmp = os.path.realpath(path)
        return os.path.normpath(tmp)

    def correct_path_join(self, *paths) -> str:
        return self.correct_path(os.path.join(*paths))

    def create_directory(self, path: str) -> bool:
        if not os.path.isdir(path):
            os.mkdir(directory)
            return True
        return Flase

    def create_file(self, file_name: str):
        if not os.path.isfile(file_name):
            file = open(file_name, "w")
            file.close()

    def remove_file(self, file_with_path):
        return False

    def read_file(self, file):
        return file

    def write_in_file(self, file):
        return file


class File(IO):
    """
    File functions to control tasks related to writing and reading files in the operating system
    """
    def __init__(self):
        pass

    def find_files_with_text(self,
                             search_text,
                             search_dir,
                             case_sensitive=False,
                             search_subdirs=True,
                             break_on_find=False):

        path = pathlib.Path(search_dir)
        if not path.is_dir():
            return False

        text_file_list = []

        if search_subdirs == True:
            walk_tree = os.walk(search_dir)
        else:
            walk_tree = [next(os.walk(search_dir))]
        for root, subFolders, files in walk_tree:

            for file in files:

                full_with_path = os.path.join(root, file)
                if self.test_text_file(full_with_path) != None:

                    full_with_path = full_with_path.replace("\\", "/")
                    text_file_list.append(full_with_path)

        return_file_list = []
        for file in text_file_list:
            try:
                file_text = self.read_file_to_string(file)

                if case_sensitive == False:
                    compare_file_text = file_text.lower()
                    compare_search_text = search_text.lower()
                else:
                    compare_file_text = file_text
                    compare_search_text = search_text

                if compare_search_text in compare_file_text:
                    return_file_list.append(file)

                    if break_on_find == True:
                        break
            except Exception as e:
                continue

        return return_file_list

    def replace_text_in_files(self,
                              search_text,
                              replace_text,
                              search_dir,
                              case_sensitive=False,
                              search_subdirs=True):

        found_files = self.find_files_with_text(search_text, search_dir,
                                                case_sensitive, search_subdirs)
        if found_files == None:
            return []

        for file in found_files:

            file_text = self.read_file_to_string(file)

            if case_sensitive == True:
                compiled_search_re = re.compile(search_text)
            else:
                compiled_search_re = re.compile(search_text, re.IGNORECASE)

            replaced_text = re.sub(compiled_search_re, replace_text, file_text)

            self.write_to_file(replaced_text, file)

        return found_files

    def find_files_by_name(self,
                           search_filename,
                           search_dir,
                           case_sensitive=False,
                           search_subdirs=True):
        path = pathlib.Path(search_dir)

        if not path.is_dir():
            return False

        found_file_list = []

        if search_subdirs == True:
            walk_tree = os.walk(search_dir)
        else:

            walk_tree = [next(os.walk(search_dir))]
        for root, subFolders, files in walk_tree:
            for file in files:

                full_with_path = os.path.join(root, file)

                if case_sensitive == False:
                    compare_actual_filename = file.lower()
                    compare_search_filename = search_filename.lower()
                else:
                    compare_actual_filename = file
                    compare_search_filename = search_filename

                if compare_search_filename in compare_actual_filename:

                    full_with_path = full_with_path.replace("\\", "/")
                    found_file_list.append(full_with_path)

        return found_file_list

    def replace_tabs_with_space(self, file_with_path):
        file = pathlib.Path(file_with_path)
        if file.is_file():
            text = file.read_text()
            text = text.replace('\t', ' ' * 4)
            file.write_text(text)

    def test_text_file(self, file_with_path):
        try:
            file = open(file_with_path,
                        "r",
                        encoding=locale.getpreferredencoding(),
                        errors="strict")
            for line in itertools.islice(file, 10):
                line = line
            file.readlines()
            file.close()

            return locale.getpreferredencoding()
        except:
            test_encodings = [
                "utf-8", "ascii", "utf-16", "utf-32", "iso-8859-1", "latin-1"
            ]
            for current_encoding in test_encodings:
                try:
                    file = open(file_with_path,
                                "r",
                                encoding=current_encoding,
                                errors="strict")

                    for line in itertools.islice(file, 10):
                        line = line

                    file.close()

                    return current_encoding
                except:
                    continue
        return None

    def test_binary_file(self, file_with_path):
        file = open(file_with_path, "rb")

        binary_text = None
        for line in itertools.islice(file, 20):
            if b"\x00" in line:

                file.seek(0)

                binary_text = file.read()
                break
        file.close()
        return binary_text

    def read_file_to_list(self, file_with_path):
        text = self.read_file_to_string(file_with_path)
        if text != None:
            return text.split("\n")
        else:
            return None

    def read_file_to_string(self, file_with_path):
        """Read contents of a text file to a single string"""
        binary_text = self.test_binary_file(file_with_path)
        if binary_text != None:
            cleaned_binary_text = binary_text.replace(b"\x00", b"")
            return cleaned_binary_text.decode(encoding="utf-8",
                                              errors="replace")
        else:
            test_encodings = [
                "utf-8", "cp1250", "ascii", "utf-16", "utf-32", "iso-8859-1",
                "latin-1"
            ]
            for current_encoding in test_encodings:
                try:

                    with open(file_with_path,
                              "r",
                              encoding=current_encoding,
                              errors="strict") as file:

                        text = file.read()

                        file.close()

                    return text
                except:

                    continue

        return None

    def read_binary_file_as_generator(self, file_object, chunk_size=1024):
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def read_file_to_list(self, file_with_path):
        text = self.read_file_to_string(file_with_path)
        if text != None:
            return text.split("\n")
        else:
            return None

    def read_file(self, file):
        return self.read_file_to_string(file)

    def write_to_file(self, text, file_with_path, encoding="utf-8"):
        try:
            if encoding != "utf-8":
                byte_string = bytearray(text,
                                        encoding=encoding,
                                        errors="replace")
                text = codecs.decode(byte_string, encoding, "replace")

            with open(file_with_path, "w", newline="",
                      encoding=encoding) as file:
                file.write(text)
                file.close()

            return True
        except Exception as ex:
            return ex


class Get:
    """
    Application functions set, all core functions of icode
    """
    def __init__(self):
        self.update_apis()
        self.io = IO()

    def update_apis(self):
        self.theme = f"{config.get_icons_package()}{SYS_SEP}{config.get_icons_theme()}"
        self.icon_path = f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}icons{SYS_SEP}{self.theme}{SYS_SEP}"

    def get_adjusted_path(self, path):
        try:
            return self.io.adjust_path(path)
        except:
            return False

    def get_correct_path(self, path):
        try:
            return self.io.correct_path(path)
        except:
            return False

    def get_correct_path_join(self, *path):
        try:
            return self.io.correct_path_join(*path)
        except:
            return False

    def get_path_splited(self, path):
        path = os.path.normpath(path)
        return path.split(os.sep)

    def get_native_font(self):
        font = QFont('Courier New', iconsts.APP_BASE_FONT_SIZE)
        if SYS_NAME.startswith("linux"):
            font = QFont("DejaVu Sans Mono", iconsts.APP_BASE_FONT_SIZE)
        elif SYS_NAME.startswith("darwin"):
            font = QFont("Menlo", iconsts.APP_BASE_FONT_SIZE)
        elif SYS_NAME.startswith("win"):
            font = QFont('Consolas', iconsts.APP_BASE_FONT_SIZE)
        return font

    def get_python_version(self):
        return f"Python{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def get_line_indentation(self, line):
        indentation = 0
        for char in line:
            if char == " ":
                indentation += 1
            else:
                break
        return indentation

    def get_char_is_closable(self, col: int, text: str) -> bool:
        return len(text) > col + 1

    def get_text_without(text: str, old_char: str, new_char: str) -> str:
        return text.replace(old_char, new_char)

    def get_expanded_tab_text(txt: str,
                              tabWidth: int = iconsts.EXPANDED_TAB_WIDTH
                              ) -> str:
        out = []
        for line in txt.split('\n'):
            try:
                while True:
                    i = line.index('\t')
                    if (tabWidth > 0):
                        pad = " " * (tabWidth - (i % tabWidth))
                    else:
                        pad = ""
                    line = line.replace("\t", pad, 1)
            except:
                out.append(line)
        return "\n".join(out)

    def get_code_with_identation(code: str, old_char: str,
                                 new_char: str) -> str:
        return re.sub(old_char, new_char, code)

    def get_file_with_identation(file: str, old_char: str,
                                 new_char: str) -> str:
        pass

    def get_root_path(self):
        return BASE_PATH

    def get_full_path(self, relative_path):
        full_path = self.get_root_path() + relative_path
        return self.get_correct_path(full_path)

    def get_selection_from_item_data(self, editor, name, line):
        line -= 1
        line_from = line
        line_to = line

        editor_text = editor.text(line)

        try:
            x = re.search(name, editor_text)
            index_from = x.start()
            index_to = x.end()

            return line_from, index_from, line_to, index_to
        except:
            return False

    def get_lexer_from_code(self, code: str) -> object:
        langs = Shaman.default().detect(code)
        if langs:
            lang = langs[0][0].lower()
            return self.get_lexer_from_name(lang)

    def get_lexer_from_name(self, lang_name: str) -> object:
        if lang_name == "python":
            return PythonLexer
        elif lang_name == "c":
            return CLexer
        elif lang_name == "javascript":
            return JavaScriptLexer
        elif lang_name == "html":
            return HTMLLexer
        elif lang_name == "css":
            return CSSLexer
        else:
            return NoneLexer

    def get_lexer_from_extension(self, file) -> object:
        file_extension = pathlib.Path(file).suffix
        file_extension = file_extension.lower()

        if file_extension in data.ext_c:
            return CLexer
        elif file_extension in data.ext_cpp:
            return CPPLexer
        elif file_extension in data.ext_css:
            return CSSLexer
        elif file_extension in data.ext_html:
            return HTMLLexer
        elif file_extension in data.ext_json:
            return JSONLexer
        elif file_extension in data.ext_javascript:
            return JavaScriptLexer
        elif file_extension in data.ext_python:
            return PythonLexer
        else:
            return NoneLexer
    
    def get_lexer_from_instance(self, lexer_instance):
        lexers = [CLexer, CPPLexer, CSSLexer, HTMLLexer, JSONLexer, JavaScriptLexer, PythonLexer, NoneLexer]
        if lexer_instance is None:
            return NoneLexer
            
        for lexer in lexers:
            if isinstance(lexer_instance, lexer):
                return lexer
        

    def get_all_lexers_objects_api(self) -> dict:
        return [{
            "name": "python",
            "lexer": PythonLexer,
            "icon": self.get_lexer_icon_by_name("python")
        }, {
            "name": "c",
            "lexer": CLexer,
            "icon": self.get_lexer_icon_by_name("c")
        }, {
            "name": "c++",
            "lexer": CPPLexer,
            "icon": self.get_lexer_icon_by_name("c++")
        }, {
            "name": "css",
            "lexer": CSSLexer,
            "icon": self.get_lexer_icon_by_name("css")
        }, {
            "name": "html",
            "lexer": HTMLLexer,
            "icon": self.get_lexer_icon_by_name("html")
        }, {
            "name": "javaScript",
            "lexer": JavaScriptLexer,
            "icon": self.get_lexer_icon_by_name("javascript")
        }, {
            "name": "json",
            "lexer": JSONLexer,
            "icon": self.get_lexer_icon_by_name("json")
        }, {
            "name": "text",
            "lexer": NoneLexer,
            "icon": self.get_lexer_icon_by_name("text")
        }]

    def get_qcolor(self, color):
        return QColor(color)

    def get_qimage(self, path) -> object:
        return QImage(path)

    def get_pixmap(self, icon_path) -> object:
        return QPixmap(icon_path)

    def get_qicon(self, icon_path) -> object:
        return QIcon(icon_path)

    def get_lexer_icon_by_name(self, name):
        api = self.get_icon_api()
        if api is None:
            return None
        try:
            raw_key = api["lexer-" + name]
            processed_key = self.get_adjusted_path(raw_key)
            icon = self.icon_path + processed_key

        except Exception as e:
            print(e)
            return None
        return self.get_qicon(icon)

    def get_icon_from_lexer(self, lexer_name):
        return self.get_lexer_icon_by_name(lexer_name.lower())

    def get_icon_from_ext(self, file, ext=False) -> str:
        theme = f"{config.get_icons_package()}{SYS_SEP}{config.get_icons_theme()}"
        icon_path = f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}icons{SYS_SEP}{theme}{SYS_SEP}languages{SYS_SEP}"

        if file == ".?icode" or file is None:
            return f"{icon_path}multiline-text.png"

        if ext:
            ext = ext
        else:
            ext = pathlib.Path(file).suffix

        if ext in data.ext_text:
            return f"{icon_path}multiline-text.png"
        elif ext in data.ext_python:
            return f"{icon_path}python.png"
        elif ext in data.ext_json:
            return f"{icon_path}json.png"
        elif ext in data.ext_javascript:
            return f"{icon_path}javascript.png"
        else:
            return f"{icon_path}multiline-text.png"

    def get_icon_api(self):
        api_file = pathlib.Path(
            f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}icons{SYS_SEP}{config.get_icons_package()}{SYS_SEP}main.json"
        )
        if api_file.is_file() and api_file.exists():
            return ijson.load(api_file)
        return None

    def get_app_icon(self) -> object:
        return self.get_qicon(
            f"smartcode{SYS_SEP}icons{SYS_SEP}icons{SYS_SEP}logo-min.svg")

    # TODO
    def get_application_icons(self, area: str = "-") -> dict:
        class IconMaker:
            def __init__(self, icon_path: str, api: dict, area: str):
                self.icon_path = icon_path
                self.api = api
                self.area = area
                self.area += "-"

            def _get(self, key):
                try:
                    raw_key = self.api[self.area + key]
                    processed_key = getfn.get_adjusted_path(raw_key)

                    return f"{self.icon_path}{processed_key}"
                except Exception as e:
                    print(e)
                    return None

            def get_path(self, key):
                return self._get(key)

            def get_pixmap(self, key):
                return getfn.get_pixmap(self._get(key))

            def get_image(self, key):
                return getfn.get_qimage(self._get(key))

            def get_icon(self, key):
                return getfn.get_qicon(self._get(key))

        api = self.get_icon_api()
        if api is None:
            return None

        if area == "index":
            return {
                "logo":
                f"smartcode{SYS_SEP}icons{SYS_SEP}icons{SYS_SEP}logo.svg",
                "python":
                f"smartcode{SYS_SEP}icons{SYS_SEP}icons{SYS_SEP}python.svg"
            }

        return IconMaker(self.icon_path, api, area)

    def get_theme_in_json(self):
        ext = config.get_theme()
        palette = config.get_palette()
        if ext:
            try:
                return ijson.load(
                    f"{BASE_PATH}{SYS_SEP}smartcode{SYS_SEP}extensions{SYS_SEP}{ext}{SYS_SEP}src{SYS_SEP}{palette}.json"
                )
            except Exception as e:
                print(e)

        return None

    def get_terminal_color_map(self):
        data = self.get_theme_in_json()
        if data:
            return data["terminal-styles"]

    def get_drop_shadow_color(self):
        data = self.get_theme_in_json()
        if data:
            return data["global-styles"]["drop-shadow-color"]

    def get_lexer_colors(self):
        data = self.get_theme_in_json()
        if data:
            return data["lexer-styles"]

    def get_generic_lexer_styles(self):
        data = self.get_theme_in_json()
        if data:
            return data["generic-lexer-styles"]

    def get_editor_styles(self):
        data = self.get_theme_in_json()
        if data:
            return data["editor-styles"]

    def get_bool_from_str(self, chars):
        text = str(chars).lower()

        if text == "true":
            return True
        elif text == "false":
            return False

        return None


filefn = File()
getfn = Get()
iofn = IO()