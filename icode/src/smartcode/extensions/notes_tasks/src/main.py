from extension_api import *

from PyQt5.QtWidgets import QPushButton

from .controller import NotesController, TodosController
from .view import NotesUi, TodosUi


class Init(ModelApp):
    def __init__(self, data) -> None:
        super().__init__(data, "notes_tasks")
        self.build_ui()
        self.init_controllers()
        self.listen_slots()
    

    def listen_slots(self):
        self.app.on_current_editor_changed.connect(self.update_todos)
        self.do_on(
            lambda: self.app.open_research_space("notes_tasks"),
            "btn_open_notes_tasks",
            "clicked",
        )

    def init_controllers(self):
        self.notes_controller = NotesController(self.notes)
        self.todos_controller = TodosController(self.todos)

    def update_todos(self, widget):
        self.todos_controller.set_data(widget, widget.file)

    def build_ui(self):
        self.btn_open_notes_tasks = QPushButton("Open")
        self.btn_open_notes_tasks.setObjectName("btn-get-notes")

        self.btn_add_label = QPushButton("+")
        self.btn_show_hide_labels = QPushButton("Show")

        space = self.ui.side_right.new_space("notes_tasks")

        self.ui.side_left.labs.new_work_space("Notes and Tasks", "notes_tasks",
                                              "<p>Create notes and tasks</p>",
                                              self.btn_open_notes_tasks)

        self.notes = NotesUi(self)
        self.todos = TodosUi(self)

        self.table_notes = self.ui.side_right.new_table("Notes", self.notes)
        self.table_todos = self.ui.side_right.new_table("Labels", self.todos)

        self.table_todos.add_header_widget(self.btn_show_hide_labels)
        self.table_todos.add_header_widget(self.btn_add_label)

        self.table_notes.add_widget(self.notes)
        self.table_todos.add_widget(self.todos)
        
        space.add_table(self.table_notes, 0, 0)
        space.add_table(self.table_todos, 1, 0)
