import pygit2 as pygit
import re
import os
from typing import Union

REGEX = re.compile(r"((https|http)(://[_a-zA-Z0-9-]*.[_a-zA-Z0-9-]*/[_a-zA-Z0-9-]*)/([-_a-zA-Z0-9-]*.git))")
group_number = 4

def get_folder_name_from_clone_url(url:str) -> Union[str, tuple, None]:
    string = str()
    
    for match in REGEX.finditer(url):
        if group_number < 0:
            return match.groups()
        string += match.group(group_number)
    
    if len(string) >= 0:
            
        name = re.split("\.", string)
        if name:
            return name[0]
            
    return None

url = "https://github.com/IgdaliasCabamba/iterm.git"
path="/home/igdalias/tests"
name = get_folder_name_from_clone_url(url)

path+=os.sep+name
repo = pygit.clone_repository(url, path)
print(repo)