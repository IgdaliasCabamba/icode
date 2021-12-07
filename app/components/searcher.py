from functions import filefn
from PyQt5.QtCore import QObject, pyqtSignal

class SearchEngine(QObject):
    
    on_results=pyqtSignal(list, str)

    def __init__(self, parent):
        super().__init__()
        self.parent=parent
        self._fifo_stack = []
    
    def run(self):
        self.parent.on_searched.connect(self.search)
    
    def search(self, query1, query2, folder, event, args):
        try:
            if query2 == "" or event == 0:
                results=filefn.find_files_with_text(
                search_text=query1,
                search_dir=folder,
                case_sensitive=args["cs"],
                search_subdirs=args["ss"],
                break_on_find=args["bf"]
            )
            
            elif event == 1:
                results=filefn.replace_text_in_files(
                search_text=query1, 
                replace_text=query2,
                search_dir=folder,
                case_sensitive=args["cs"],
                search_subdirs=args["ss"]
            )
            else:
                results=filefn.find_files_by_name(
                search_filename=query1,
                search_dir=folder,
                case_sensitive=args["cs"],
                search_subdirs=args["ss"]
            )
            
            self.on_results.emit(results, query1)
        
        except Exception as e:
            return e
