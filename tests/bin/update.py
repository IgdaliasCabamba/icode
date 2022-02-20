import requests
import json
import validus
import threading
import pathlib
import os

base_path = os.getcwd()

def download(url, path):
    path = pathlib.Path(path)
    data = requests.get(url, stream = True)
  
    with open(path, "wb") as save:
        for chunk in data.iter_content(chunk_size=1024):
             if chunk:
                 save.write(chunk)
    
def create_new_download_thread(link, filelocation):
    download_thread = threading.Thread(target=download, args=(link, filelocation))
    download_thread.start()

def make(kernel_version, bin_version, frameworks_version, app_version):
    print(kernel_version, bin_version, frameworks_version, app_version)
    pass
        
#update_thread = threading.Thread(target=run)
#update_thread.start()