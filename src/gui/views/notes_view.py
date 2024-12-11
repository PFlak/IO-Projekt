from src.gui.views.base_view import BaseView


class NotesView(BaseView):
    def __init__(self):
        super().__init__("Notatki")
        main_layout = self.layout
        self.setLayout(main_layout)
