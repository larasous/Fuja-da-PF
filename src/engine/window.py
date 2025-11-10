import glfw
from OpenGL.GL import *
from src.constants import metrics, colors, shaders_path
from src.utils.colors import lerp_color
from src.engine.shader import Shader
import numpy as np
from ctypes import c_void_p


class Window:
    def __init__(self):

        if not glfw.init():
            raise Exception("❌ GLFW could not be initialized")

        if metrics.WINDOW_MAXIMIZED:
            glfw.window_hint(glfw.MAXIMIZED, glfw.TRUE)

        self.window = glfw.create_window(
            metrics.WINDOW_WIDTH,
            metrics.WINDOW_HEIGHT,
            metrics.WINDOW_TITLE,
            None,
            None,
        )
        if not self.window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        glfw.make_context_current(self.window)

        glfw.set_window_size_callback(self.window, self._on_resize)

        self._update_metrics()

        with open(shaders_path.VERTEX_BASIC, "r") as file:
            vertex_source = file.read()
        with open(shaders_path.FRAGMENT_BASIC, "r") as file:
            fragment_source = file.read()

        self.shader = Shader(vertex_source, fragment_source)
        self.vao = self._create_triangle()

    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            # Efeito de transição de cor
            time = glfw.get_time()
            speed = 2.0
            index = int(time // speed) % len(colors.COLOR_PALETTE)
            next_index = (index + 1) % len(colors.COLOR_PALETTE)
            blend = (time % speed) / speed

            color_one = colors.COLOR_PALETTE[index]
            color_two = colors.COLOR_PALETTE[next_index]
            current_color = lerp_color(color_one, color_two, blend)

            glClearColor(*current_color)
            glClear(GL_COLOR_BUFFER_BIT)

            self.shader.use()
            glBindVertexArray(self.vao)
            glDrawArrays(GL_TRIANGLES, 0, 3)

            glfw.swap_buffers(self.window)

        glfw.terminate()

    def _create_triangle(self):
        """Cria um triângulo simples para renderização."""
        vertices = np.array(
            [-0.5, -0.5, 0.0, 0.5, -0.5, 0.0, 0.0, 0.5, 0.0],
            dtype=np.float32,
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

    def _update_metrics(self):
        """Atualiza as métricas com base no framebuffer atual."""
        width, height = glfw.get_framebuffer_size(self.window)
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)

    def _on_resize(self, window, width, height):
        """Callback de redimensionamento da janela."""
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)
