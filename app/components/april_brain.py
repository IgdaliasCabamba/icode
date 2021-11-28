from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import wikipedia

import re
import textwrap

from april_models import *
from april import ask

class Brain(QObject):
    
    on_answered=pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.api=parent
    
    def run(self):
        self.api.on_asked.connect(self.get_answer)
    
    def format_answer(self, value, code=False, line_width=80):
        if code:
            return f"```{value}```"

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
    
    def get_answer(self, text):
        if text.startswith("wiki:"):
            answer=self.get_wiki_answer(self.remove_commands(text, "wiki:"))
        elif text.startswith("april:"):
            answer=self.get_april_answer(self.remove_commands(text, "april:"))
        elif text.startswith("code:"):
            answer=self.get_code_snippets(self.remove_commands(text, "code:"))
        else:
            if text.lower() in ask_list:
                answer=self.get_april_answer(text)
            elif not " " in text and not "_" in text:
                answer=self.get_wiki_answer(text)
            else:
                answer=self.get_code_snippets(text)
        
        # TODO > Return multiples answers
        #answers=ask(args)
        #for answer in answers:
            #self.on_answered.emit(answer)

        self.on_answered.emit(answer)

    
    def get_april_answer(self, text):
        pos=ask_list.index(text.lower())
        return ans_list[pos]
    
    def get_wiki_answer(self, text, lang="en"):
        try:
            wikipedia.set_lang(lang)
            results = wikipedia.search(text.upper())
            if results:
                answer = wikipedia.summary(results[0])
                related_searches=results[1:-1]

                if related_searches:
                    items=""
                    for i in related_searches:
                        items+=f"- 👉 {i} \n"

                    answer+=f"\n ### Related Searches: \n *** \n {items}"
                
                return self.format_answer(answer, line_width=80)
        except Exception as e:
            return str(e)

    def get_code_snippets(self, text):
        query=text.split()
        args={"query":query}
        try:
            answer=ask(args)
            return self.format_answer(answer, code=True)
        except Exception as e:
            return error_msg + str(e)
