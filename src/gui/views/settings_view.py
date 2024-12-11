from src.gui.views.base_view import BaseView


class SettingsView(BaseView):
    def __init__(self):
        super().__init__("Ustawienia")
        main_layout = self.layout
        self.setLayout(main_layout)
