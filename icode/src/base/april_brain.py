from PyQt5.QtCore import pyqtSignal, QObject
import wikipedia
import json
import re
from .templates import AprilRender
from .april import ask

def get_query_clean(query:str):
    text = re.sub(r"-[hjn]","",query, 1)
    return text

class Brain(QObject):
    
    on_answered=pyqtSignal(object, int)

    def __init__(self, parent):
        super().__init__()
        self.api=parent
        self.templates = AprilRender()
    
    def run(self):
        self.api.on_asked.connect(self.get_answer)
    
    def format_answer(self, value, code=False, line_width=80):
        if code:
            return json.loads(value)

        return value

        # TODO > Format answers with textwrap and return it
    
    def remove_commands(self, text, command):
        pos = re.search(":", text)
        text_splited=re.split(":", text)
        if len(text_splited)>2:
            query_list=text_splited[1:-1]
            text= ' '.join(map(str, query_list))
            print(text)
        else:
            text=text_splited[1]
            print(text)
        print(text_splited)

        return text
    
    def get_answer(self, text, settings):
        if text.startswith("wiki:"):
            answer=self.get_wiki_answer(self.remove_commands(text, "wiki:"))
            type = 0
        elif text.startswith("april:"):
            answer=self.get_april_answer(self.remove_commands(text, "april:"))
            type = 1
        elif text.startswith("code:"):
            try:
                answer=self.get_code_snippets(self.remove_commands(text, "code:"), settings)
                type = 2
            except Exception as e:
                answer = self.templates.error_log + str(e)
                type = -1
        else:
            if not " " in text and not "_" in text:
                answer=self.get_wiki_answer(text)
                type = 0
            
            elif text.lower() in self.templates.asks:
                answer=self.get_april_answer(text)
                type = 1
            
            else:
                try:
                    answer=self.get_code_snippets(text, settings)
                    type = 2
                    
                except Exception as e:
                    answer = self.templates.error_log + str(e)
                    type = -1
        print(answer)
        self.on_answered.emit(answer, type)

    
    def get_april_answer(self, text:str):
        pos=self.templates.asks.index(text.lower())
        return self.templates.answers[pos]
    
    def get_wiki_answer(self, text:str, lang="en"):
        try:
            wikipedia.set_lang(lang)
            results = wikipedia.search(text.upper())
            if results:
                answer = wikipedia.summary(results[0])
                related_searches=results[1:-1]

                if related_searches:
                    items=""
                    for i in related_searches:
                        items+=f"- \uf7c6 {i} \n"

                    answer+=f"\n ### Related Searches: \n *** \n {items}"
                
                return self.format_answer(answer, line_width=80)
        except Exception as e:
            return str(e)

    def get_code_snippets(self, text:str, settings):
        query=text
        args={
            "query":get_query_clean(query),
            "json_output":True,
            "num_answers":settings["answer_count"],
            "all":settings["all_response"]
        }
        answer=ask(args)
        return self.format_answer(answer, code=True)