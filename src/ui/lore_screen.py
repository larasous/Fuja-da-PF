import imgui
from imgui.integrations.glfw import GlfwRenderer
import time
import glfw
from PIL import Image
import OpenGL.GL as gl



class LoreScreen:
    def __init__(self, window, text_blocks, typing_speed=0.05, pause_between_blocks=2.5):
        self.bg_texture, self.bg_width, self.bg_height = self._load_texture("assets/backgrounds/capeta_lore.png")
        imgui.create_context()
        self.impl = GlfwRenderer(window)
        self.text_blocks = text_blocks
        self.typing_speed = typing_speed
        self.pause_between_blocks = pause_between_blocks
        self.start_time = time.time()
        self.finished = False

        io = imgui.get_io()
        io.font_global_scale = 1.8

        style = imgui.get_style()
        style.window_rounding = 12
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.1, 1.0)

        # Pré-calcula os tempos de início de cada bloco
        self.block_timings = []
        total = 0.0
        for block in self.text_blocks:
            duration = len(block) * self.typing_speed + self.pause_between_blocks
            self.block_timings.append((total, total + duration))
            total += duration

    def update(self):
        if time.time() - self.start_time > self.block_timings[-1][1]:
            self.finished = True

    def draw(self):
        self.impl.process_inputs()

        window_width, window_height = glfw.get_window_size(self.impl.window)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, window_width, 0, window_height, -1, 1)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.bg_texture)

        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0, 0); gl.glVertex2f(0, 0)
        gl.glTexCoord2f(1, 0); gl.glVertex2f(window_width, 0)
        gl.glTexCoord2f(1, 1); gl.glVertex2f(window_width, window_height)
        gl.glTexCoord2f(0, 1); gl.glVertex2f(0, window_height)
        gl.glEnd()

        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glEnable(gl.GL_DEPTH_TEST)
        imgui.new_frame()


        lore_width, lore_height = 900, 200
        center_x = (window_width - lore_width) // 2
        center_y = int(window_height * 0.75)

        imgui.set_next_window_position(center_x, center_y)
        imgui.set_next_window_size(lore_width, lore_height)

        imgui.begin("Lore", False,
                    imgui.WINDOW_NO_TITLE_BAR |
                    imgui.WINDOW_NO_RESIZE |
                    imgui.WINDOW_NO_MOVE |
                    imgui.WINDOW_NO_SCROLLBAR)

        now = time.time() - self.start_time

        for i, (start, end) in enumerate(self.block_timings):
            if start <= now < end:
                block = self.text_blocks[i]
                typing_duration = len(block) * self.typing_speed
                time_into_block = now - start

                if time_into_block < typing_duration:
                    visible_chars = int(time_into_block / self.typing_speed)
                    visible_text = block[:max(0, visible_chars)]
                else:
                    visible_text = block

                imgui.text_wrapped(visible_text)
                break

        imgui.end()
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def _load_texture(self, image_path):
        image = Image.open(image_path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
        img_data = image.tobytes()
        width, height = image.size

        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0,
                        gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        return texture_id, width, height