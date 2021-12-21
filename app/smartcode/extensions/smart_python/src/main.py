from extension_api import *
export(path="smart_python.src")
from smartpycore import *

class Init(ModelApp):
    def __init__(self, data) -> None:
        super().__init__(data, "smart_python")
        self.listen_slots()
        
    def listen_notebook_slots(self, notebook):
        notebook.widget_added.connect(self.take_editor)

    def listen_slots(self):
        self.add_event("ui.notebook.widget_added", self.take_editor)
        self.add_event("app.on_new_notebook", self.listen_notebook_slots)
    
    def take_editor(self, widget):
        if self.object_is(widget, "editor-frame"):
            editor1, editor2 = widget.get_editors()
            
            if editor1.lexer_name.lower() == "python":
                self.build_editor(editor1)
                
            if editor2.lexer_name.lower() == "python":
                self.build_editor(editor2)
                
            editor1.on_lexer_changed.connect(self.build_editor)
            editor2.on_lexer_changed.connect(self.build_editor)
    
    def build_editor(self, editor):
        status = getattr(editor, "smartpy", None)
        if status is not None:
            
            if editor.lexer_name.lower() == "python" and not status:
                self.make_smart(editor)
                editor.smartpy = True
        else:
            if editor.lexer_name.lower() == "python":
                self.make_smart(editor)
                setattr(editor, "smartpy", True)
    
    def make_smart(self, editor) -> None:
        editor.setIndentationsUseTabs(False)
        
        autocomplete=PyntellisenseCompletions(editor)        
        ide_tools=Pyntellisense(editor)
        live_tips=PyntellisenseEdition(editor)
        live_tips.on_annotation_request.connect(editor.display_annotation)
        live_tips.on_add_indicator_range.connect(editor.add_indicator_range)
        live_tips.on_clear_indicator_range.connect(editor.clear_indicator_range)
        live_tips.on_update_header.connect(editor.update_header)
        ide_tools.on_update_header.connect(editor.update_header)
        ide_tools.on_tooltip_request.connect(editor.display_tooltip)
        
        editor.add_code_completer(autocomplete, autocomplete.run)
        editor.add_development_environment_component(ide_tools, ide_tools.run)
        editor.add_development_environment_component(live_tips, live_tips.run)
        
        editor.on_env_changed.connect(live_tips.set_env)
        editor.on_env_changed.connect(ide_tools.set_env)
        editor.on_env_changed.connect(autocomplete.set_env)