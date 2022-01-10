from functions import getfn
import pathlib

icons=getfn.get_application_icons("index")

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

def welcome_msg_left(files:list):
    enough_files_count = 4
    recent_files = ["#", "#", "#"]
    tmp_recent_files = []
    recent_files_names = ["./", "./", "./"]
    
    if files is not None: 
        if len(files) > 3:
            for i in range(1, 4):
                tmp_recent_files.append(files[i*-1])
            
            recent_files = tmp_recent_files
        else:
            for i in range((len(files)-enough_files_count)*-1):
                files.append("#")
        
            recent_files = files
            
        recent_files_names = []
        for file in recent_files:
            if file == "#":
                recent_files_names.append("...")
            else:
                recent_files_names.append(pathlib.Path(file).name)
        
    return f"""
    <p>
        <span>
            <h1>Intelligent code</h1>
            <img src="{icons["python"]}"/>
            <h2><nobr>Editing evolved with a new perspective</nobr></h2>
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
    </p>
    <br>
    <br>
    """

def welcome_msg_right():
   return """
    <h3>Useful links</h3>
    <p>
        <a href='#show-commands' style='text-decoration:none;'>Read The Docs</a>
    </p>
    <p>
        <a href='#show-commands' style='text-decoration:none;'>Get Started</a>
    </p>
    <p>
        <a href='#show-commands' style='text-decoration:none;'>YouTube Chanel</a>
    </p>
    <p>
        <a href='#show-commands' style='text-decoration:none;'>Tips and Tricks</a>
    </p>
    <br>
    """