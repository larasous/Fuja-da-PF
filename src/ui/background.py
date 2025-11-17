import OpenGL.GL as gl
import glfw
from src.ui.ui_texture import load_ui_texture


class LoreBackground:
    def __init__(self, path):
        self.texture_id, self.width, self.height = load_ui_texture(path)

    def draw(self, window):
        window_width, window_height = glfw.get_window_size(window)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, window_width, 0, window_height, -1, 1)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)

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
