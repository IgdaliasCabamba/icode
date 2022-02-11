from extension_api import *
from smartpy_api import python_api
import json
from klein import Klein
import jedi

class SmartPyLanguageServer(object):
    
    app = Klein()

    def __init__(self):
        cache_directory = os.path.join(BASE_PATH, '.cache', 'jedi')
        
        if pathlib.Path(cache_directory).is_dir():
            jedi.settings.cache_directory = cache_directory

        jedi.settings.add_bracket_after_function = False
        jedi.settings.fast_parser = True
        jedi.settings.call_signatures_validity = 3.0
        jedi.settings.dynamic_params_for_other_modules = True
        jedi.settings.dynamic_params = True
        jedi.settings.dynamic_array_additions = True
        jedi.settings.case_insensitive_completion = True
    
    def notfound(self, request, failure):
        request.setResponseCode(404)
        response = json.dumps({"response":404}, indent=4)
    
    def get_data(self, request):
        request.setHeader('Content-Type', 'application/json')
        return json.loads(request.content.read())
        
    @app.route('/complete', methods=['GET'])
    def complete(self, request):
        try:
            import jedi
            
            completions = []
            
            data = self.get_data(request)
            
            source_code = data["code"]
            file_code = data["file"]
            row, col = data["cursor-pos"]
            event_text = data["event-text"]
            env = None
            if isinstance(data["env"], str):
                env = jedi.create_environment(data["env"])
                
            script = jedi.Script(code=source_code, path=file_code, environment=env)
            completers=script.complete(row+1, col)
            
            for completion in completers:
                completion_object = {
                    "name_with_symbols":str(completion.name_with_symbols),
                    "name":str(completion.name),
                    "type":str(completion.type),
                    "docstring":str(completion.docstring()),
                    "prefix_length":str(completion.get_completion_prefix_length())
                }
                completions.append(completion_object)
            
            return json.dumps(dict(response=completions), indent=4)
            
        except Exception as e:
            print(e)
            self.notfound(request, e)
        
    @app.route('/complete_search', methods=['GET'])
    def complete_search(self, request):
        try:
            import jedi
            
            completions = []
            
            data = self.get_data(request)
            
            source_code = data["code"]
            file_code = data["file"]
            fuzzy = data["fuzzy"]
            all_scopes = data["all-scopes"]
            word = data["word"]
            env = None
            if isinstance(data["env"], str):
                env = jedi.create_environment(data["env"])
            
            script = jedi.Script(code=source_code, path=file_code, environment=env)
            complete_helpers = script.complete_search(string=word, all_scopes=all_scopes, fuzzy = fuzzy)
            
            for x, completion in enumerate(complete_helpers):
                completion_object = {
                    "name_with_symbols":str(completion.name_with_symbols),
                    "name":str(completion.name),
                    "type":str(completion.type),
                    "docstring":str(completion.docstring()),
                    "prefix_length":str(completion.get_completion_prefix_length())
                }
                    
                completions.append(completion_object)
                
            return json.dumps(dict(response=completions), indent=4)
            
        except Exception as e:
            print(e)
            self.notfound(request, e)

def run_lang_server():
    smartpy_lang_server = SmartPyLanguageServer()
    smartpy_lang_server.app.run('localhost', 9990)