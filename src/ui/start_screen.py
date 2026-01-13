import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
from PIL import Image

from src.engine.texture import Texture


class StartScreen:
    def __init__(
        self,
        window,
        input_manager,
        imgui_renderer,
        image_path="assets/backgrounds/capeta_inicial.png",
    ):
        self.window = window
        self.input = input_manager
        self.finished = False

        self.texture = Texture(gl.GL_TEXTURE_2D)
        self._load_texture(image_path)

        self.impl = imgui_renderer

    def _load_texture(self, path):
        image = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
        img_data = image.tobytes()
        width, height = image.size

        self.texture.load_texture(width, height, img_data)

        self.width = width
        self.height = height

    def update(self):
        if self.input.enter_pressed():
            print("ENTER detectado!")
            self.finished = True

    def draw(self):
        window_width, window_height = glfw.get_window_size(self.window)

        # --- Desenha imagem de fundo ---
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, window_width, 0, window_height, -1, 1)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_TEXTURE_2D)

        self.texture.bind(0)

        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0, 0)
        gl.glVertex2f(0, 0)
        gl.glTexCoord2f(1, 0)
        gl.glVertex2f(window_width, 0)
        gl.glTexCoord2f(1, 1)
        gl.glVertex2f(window_width, window_height)
        gl.glTexCoord2f(0, 1)
        gl.glVertex2f(0, window_height)
        gl.glEnd()

        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.impl.process_inputs()
        imgui.new_frame()

        imgui.set_next_window_position(
            (window_width - 600) // 2, int(window_height * 0.75)
        )
        imgui.set_next_window_size(600, 100)

        imgui.begin(
            "StartPrompt",
            False,
            imgui.WINDOW_NO_TITLE_BAR
            | imgui.WINDOW_NO_RESIZE
            | imgui.WINDOW_NO_MOVE
            | imgui.WINDOW_NO_BACKGROUND,
        )

        text = "APERTE ENTER PARA INICIAR"
        text_width = imgui.calc_text_size(text)[0]
        imgui.set_cursor_pos_x((600 - text_width) / 2)

        imgui.text_colored(text, 1.0, 0.0, 0.0, 1.0)

        imgui.end()
        imgui.render()
        self.impl.render(imgui.get_draw_data())
