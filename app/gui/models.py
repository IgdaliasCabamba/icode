from functions import getfn

icons=getfn.get_application_icons("index")

logo=f'image: url("{icons["logo"]}")'
hello_msg=f"""
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

welcome_msg_left = f"""
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
        Example
    </p>
    <p>
        Example
    </p>
    <p>
        Example
    </p>
</p>
<br>
<br>
"""

welcome_msg_right = """
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