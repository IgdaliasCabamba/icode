data = requests.get(url, stream = True)
  
with open(path, "wb") as save:
    for chunk in data.iter_content(chunk_size=1024):
         if chunk:
             save.write(chunk)