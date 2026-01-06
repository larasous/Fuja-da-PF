import glfw
from src.ui.imgui_layer import ImGuiLayer
from src.ui.lore_background import LoreBackground
from src.ui.typing_box import TypingBox


class LoreScene:
    def __init__(self, window, text_blocks, typing_speed=0.05, pause=2.5):
        self.window = window

        # UI Components
        self.imgui_layer = ImGuiLayer(window)
        self.background = LoreBackground("assets/backgrounds/capeta_lore.png")
        self.typing_box = TypingBox(text_blocks, typing_speed, pause)

        self.finished = False

    def update(self):
        self.typing_box.update()
        if self.typing_box.finished:
            self.finished = True

    def draw(self):
        self.imgui_layer.begin_frame()

        self.background.draw(self.window)

        width, height = glfw.get_window_size(self.window)
        self.typing_box.draw(width, height)

        self.imgui_layer.end_frame()
