import glfw
import imgui
import OpenGL.GL as gl
from PIL import Image
import imgui
from imgui.integrations.glfw import GlfwRenderer


class StartScreen:
    def __init__(self, window, input_manager, image_path="assets/backgrounds/capeta_inicial.png"):
        self.window = window
        self.input = input_manager
        self.texture_id, self.width, self.height = self._load_texture(image_path)
        self.finished = False

        imgui.create_context()
        self.impl = GlfwRenderer(window, attach_callbacks=False)



    def _load_texture(self, path):
        image = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
        img_data = image.tobytes()
        width, height = image.size

        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
                        gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        return texture_id, width, height

    def update(self):
        # ✅ Apenas ENTER inicia
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
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)

        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0, 0); gl.glVertex2f(0, 0)
        gl.glTexCoord2f(1, 0); gl.glVertex2f(window_width, 0)
        gl.glTexCoord2f(1, 1); gl.glVertex2f(window_width, window_height)
        gl.glTexCoord2f(0, 1); gl.glVertex2f(0, window_height)
        gl.glEnd()

        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # --- Ciclo do ImGui ---
        self.impl.process_inputs()
        imgui.new_frame()

        # Caixa de texto centralizada
        imgui.set_next_window_position((window_width - 600) // 2, int(window_height * 0.75))
        imgui.set_next_window_size(600, 100)

        imgui.begin("StartPrompt", False,
                    imgui.WINDOW_NO_TITLE_BAR |
                    imgui.WINDOW_NO_RESIZE |
                    imgui.WINDOW_NO_MOVE |
                    imgui.WINDOW_NO_BACKGROUND)

        text = "APERTE ENTER PARA INICIAR"
        text_width = imgui.calc_text_size(text)[0]
        imgui.set_cursor_pos_x((600 - text_width) / 2)

        imgui.text_colored(text, 1.0, 0.0, 0.0, 1.0)

        imgui.end()
        imgui.render()
        self.impl.render(imgui.get_draw_data())