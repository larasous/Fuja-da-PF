import glfw
from OpenGL.GL import *
from src.constants.metrics import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from src.constants.colors import COLOR_PALETTE
from src.constants.shaders_path import VERTEX_BASIC, FRAGMENT_BASIC
from src.utils.colors import lerp_color
from src.engine.shader import Shader
import numpy as np
from ctypes import c_void_p


class Window:
    def __init__(self):
        if not glfw.init():
            raise Exception("GLFW could not be initialized")

        self.window = glfw.create_window(
            WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, None, None
        )
        if not self.window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        glfw.make_context_current(self.window)
        glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Carrega os shaders a partir dos arquivos
        with open(VERTEX_BASIC, "r") as f:
            vertex_source = f.read()
        with open(FRAGMENT_BASIC, "r") as f:
            fragment_source = f.read()

        self.shader = Shader(vertex_source, fragment_source)
        self.vao = self._create_triangle()

    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            t = glfw.get_time()
            speed = 2.0

            index = int(t // speed) % len(COLOR_PALETTE)
            next_index = (index + 1) % len(COLOR_PALETTE)
            blend = (t % speed) / speed

            c1 = COLOR_PALETTE[index]
            c2 = COLOR_PALETTE[next_index]
            current_color = lerp_color(c1, c2, blend)

            glClearColor(*current_color)
            glClear(GL_COLOR_BUFFER_BIT)

            self.shader.use()
            glBindVertexArray(self.vao)
            glDrawArrays(GL_TRIANGLES, 0, 3)

            glfw.swap_buffers(self.window)

        glfw.terminate()

    def _create_triangle(self):
        vertices = np.array(
            [-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.0, 0.5, 0.0], dtype=np.float32
        )

        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        return vao
