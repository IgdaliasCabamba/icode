from functions import getfn
import pathlib
from .char_utils import get_unicon

icons=getfn.get_smartcode_icons("index")

logo=f'image: url("{icons["logo"]}")'

def hello_msg():
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

def welcome_msg_left(files:list=[]):
    if not isinstance(files, list):
        files = []
    
    files = getfn.get_list_without_duplicates(files)
    recent_files_names = []
    recent_files = []
    
    for i in range(6):
        files.insert(0, "#")
    
    for i in range(1, 6):
        file = files[i*-1]
        path_obj = pathlib.Path(file)
        parent = f"~{path_obj.parent}"
        name = path_obj.name
        if file == "#":
            file = ""
            parent = ""
            name = ""
            
        recent_files.append(file)
        recent_files_names.append(f"<small>{name}<span style='color:gray'>&nbsp;&nbsp;&nbsp;{parent}</span></small>")
        
    return f"""
    <p>
        <span>
            <h1>Intelligent code</h1>
            <img src="{icons["python"]}"/>
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
            <a href='{recent_files[0]}' style='text-decoration:none;'>{recent_files_names[0]}</a>
        </p>
        <p>
            <a href='{recent_files[1]}' style='text-decoration:none;'>{recent_files_names[1]}</a>
        </p>
        <p>
            <a href='{recent_files[2]}' style='text-decoration:none;'>{recent_files_names[2]}</a>
        </p>
        <p>
            <a href='{recent_files[3]}' style='text-decoration:none;'>{recent_files_names[3]}</a>
        </p>
        <p>
            <a href='{recent_files[4]}' style='text-decoration:none;'>{recent_files_names[4]}</a>
        </p>
    </p>
    <br>
    <br>
    """

def welcome_msg_right():
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