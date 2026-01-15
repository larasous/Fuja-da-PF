from src.ui.start_screen import StartScreen


class StartScene:
    def __init__(self, window, input_manager, imgui_renderer):

        self.screen = StartScreen(window, input_manager, imgui_renderer)
        self.finished = False

    def update(self):
        print("StartScene.update rodando")
        self.screen.update()
        if self.screen.finished:
            self.finished = True

    def render(self):
        self.screen.render()
