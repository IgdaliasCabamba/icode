from functions import getfn
import pathlib
from .char_utils import get_unicon

class IndexRender:
    def __init__(self):
        self.icons=getfn.get_smartcode_icons("index")
        self.logo=f'image: url("{self.icons["logo"]}")'
        self.__paths = []
    
    def set_paths(self, paths:list=[]):
        if not isinstance(paths, list):
            paths = []
        
        self.__paths = paths
    
    @property
    def paths(self):
        return self.__paths
    
    @property
    def hello_code(self) -> str:
        return f"""
        <div>
            <p>
                <a href='#show-commands' style='text-decoration:none;'>Show Command Palette</a>
                <span>
                    <strong>CTRL+Shift+P</strong>
                </span>
            </p>
            <p>
                <a href='#new' style='text-decoration:none;'>New File</a>
                <span>
                    <strong>CTRL+N</strong>
                </span>
            </p>
            <p>
                <a href='#open-folder' style='text-decoration:none;'>Open Folder</a>
                    <span>
                        <strong>CTRL+K</strong>
                </span>
            <p>
            </p>
                <a href='#open-file' style='text-decoration:none;'>Open File</a>
                <span>
                    <strong>CTRL+O</strong>
                </span>
            </p>
        </div>
        
    """  
    
    @property
    def recent_paths(self) -> str:
        
        paths = getfn.get_list_without_duplicates(self.paths)
        recent_paths_names = []
        recent_paths = []
        
        for i in range(6):
            paths.insert(0, "#")
        
        for i in range(1, 6):
            path = paths[i*-1]
            path_obj = pathlib.Path(path)
            parent = f"~{path_obj.parent}"
            name = path_obj.name
            if path == "#":
                path = ""
                parent = ""
                name = ""
                
            recent_paths.append(path)
            recent_paths_names.append(f"<small>{name}<span style='color:gray'>&nbsp;&nbsp;&nbsp;{parent}</span></small>")
            
        return f"""
        <p>
            <span>
                <h1>Intelligent code</h1>
                <img src="{self.icons["python"]}"/>
                <h2><nobr>Editing evolved with a new <span style="color:#11f2c8">p</span><span style="color:#48cdd0">e</span><span style="color:#74afd6">r</span><span style="color:#9897db">s</span><span style="color:#c876e2">p</span><span style="color:#f458e8">e</span><span style="color:#eb58eb">c</span><span style="color:#e158ed">t</span><span style="color:#db58ef">i</span><span style="color:#d458f1">v</span><span style="color:#c958f4">e</span>
                </nobr></h2>
            </span>
        </p>

        <br>

        <p>
            <h4>
                Start:
            </h4>
            <p>
                <a href='#new' style='text-decoration:none;'>New File</a>
            </p>
            <p>
                <a href='#open-file' style='text-decoration:none;'>Open File</a>
            </p>
            <p>
                <a href='#open-folder' style='text-decoration:none;'>Open Folder</a>
            </p>
        </p>

        <p>
            <h4>
                Recents:
            </h4>
            <p> 
                <a href='{recent_paths[0]}' style='text-decoration:none;'>{recent_paths_names[0]}</a>
            </p>
            <p>
                <a href='{recent_paths[1]}' style='text-decoration:none;'>{recent_paths_names[1]}</a>
            </p>
            <p>
                <a href='{recent_paths[2]}' style='text-decoration:none;'>{recent_paths_names[2]}</a>
            </p>
            <p>
                <a href='{recent_paths[3]}' style='text-decoration:none;'>{recent_paths_names[3]}</a>
            </p>
            <p>
                <a href='{recent_paths[4]}' style='text-decoration:none;'>{recent_paths_names[4]}</a>
            </p>
        </p>
        <br>
        <br>
        """
    
    @property
    def dev_utils(self) -> str:
       return f"""
        <h3><nobr>Useful links</nobr></h3>
        <p>
            <nobr><a href='#show-commands' style='text-decoration:none;'><span style="font-size:15pt">{ get_unicon("fa", "external_link")}</span> Read The Docs</a></nobr>
        </p>
        <p>
            <nobr><a href='#show-commands' style='text-decoration:none;'><span style="font-size:15pt">{get_unicon("fa", "external_link")}</span> Get Started</nobr></a></nobr>
        </p>
        <p>
            <nobr><a href='#show-commands' style='text-decoration:none;'><span style="font-size:15pt">{get_unicon("fa", "external_link")}</span> YouTube Chanel</a></nobr>
        </p>
        <p>
            <nobr><a href='#show-commands' style='text-decoration:none;'><span style="font-size:15pt">{get_unicon("fa", "external_link")}</span> Tips and Tricks</a></nobr>
        </p>
        <br>
        """

class AprilRender:
    def __init__(self):
        pass
    
    @property
    def error_log(self):
        return """
            <nobr>
                <h3 style="color:#f23f57">Sorry <span style="font-size:20pt">\uf6f7</span></h3>
            </nobr>
            <hr>
            <p style="font-size:12pt">
                I didn't find results!
            </p>
            
        """
    @property
    def readme(self):
        return """
            <nobr>
                <h3>
                    Hello, i'm <span style="color:#11f2c8">A</span><span style="color:#74afd6">p</span><span style="color:#c876e2">r</span><span style="color:#eb58eb">i</span><span style="color:#db58ef">l</span> <span style="font-size:20pt; color:#c958f4">\uf4a2</span>
                </h3>
            </nobr>
            <hr>
            <nobr style="font-size:11pt">
                I'm here to help with some things like:
                <p>&nbsp;&nbsp;Give code snippets <span style="font-size:15pt">\ue796</span></p>
                <p>&nbsp;&nbsp;Analyze your code <span style="font-size:15pt">\ufcca</span></p>
                <p>&nbsp;&nbsp;Adjust your code <span style="font-size:15pt">\uf75f</span></p>
                <p>&nbsp;&nbsp;Answer questions <span style="font-size:15pt">\uf477</span></p>
            </nobr>
        """
    
    @property
    def asks(self) -> list:
        return ["hello","hi"," "]
    
    @property
    def answers(self) -> list:
        return ["Hello!","Hi!","???"]