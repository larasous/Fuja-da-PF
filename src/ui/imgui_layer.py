import imgui
from imgui.integrations.glfw import GlfwRenderer


class ImGuiLayer:
    def __init__(self, window):
        imgui.create_context()
        self.impl = GlfwRenderer(window)

        self._setup_style()

        io = imgui.get_io()
        io.font_global_scale = 1.8

    def _setup_style(self):
        style = imgui.get_style()
        style.window_rounding = 12
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.1, 1.0)

    def begin_frame(self):
        self.impl.process_inputs()
        imgui.new_frame()

    def end_frame(self):
        imgui.render()
        self.impl.render(imgui.get_draw_data())
