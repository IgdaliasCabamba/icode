from howdoi.howdoi import howdoi
from typing import Union

def ask(args) -> Union[str, None]:

    if not "query" in args:
        return None
    
    if not "pos" in args:
        args["pos"]=1
    
    if not "num_answers" in args:
        args["num_answers"]=1
    
    if not "all" in args:
        args["all"]=False
    
    if not "link" in args:
        args["link"]=True

    if not "color" in args:
        args["color"]=False

    if not "explain" in args:
        args["explain"]=False

    if not "json_output" in args:
        args["json_output"]=True

    if not "search_engine" in args:
        args["search_engine"]=None

    if not "save" in args:
        args["save"]=False
    
    if not "view" in args:
        args["view"]=False
    
    if not "remove" in args:
        args["remove"]=False
    
    if not "empty" in args:
        args["empty"]=False
    
    if not "sanity_check" in args:
        args["sanity_check"]=False

    results = howdoi(args)
    return results