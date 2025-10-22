import glfw
from OpenGL.GL import *
from src.constants.metrics import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from src.constants.colors import COLOR_PALETTE
from src.utils.colors import lerp_color


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

    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            # Tempo contínuo
            t = glfw.get_time()
            speed = 2.0  # segundos por transição

            # Índice fracionado
            index = int(t // speed) % len(COLOR_PALETTE)
            next_index = (index + 1) % len(COLOR_PALETTE)
            blend = (t % speed) / speed

            # Interpolação suave entre cores
            c1 = COLOR_PALETTE[index]
            c2 = COLOR_PALETTE[next_index]
            current_color = lerp_color(c1, c2, blend)

            glClearColor(*current_color)
            glClear(GL_COLOR_BUFFER_BIT)

            glfw.swap_buffers(self.window)

        glfw.terminate()
