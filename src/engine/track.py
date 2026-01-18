import numpy as np
import pygame
from OpenGL.GL import *

from src.constants import metrics

class Track:
    def __init__(self, shader, texture_path):
        self.shader = shader
        self.texture_path = texture_path
        self.tracks = []
        self.texture = None
        self._init_geometry()
        self._load_texture()

    def _init_geometry(self):
        x_offset = 0.0
        vertices = np.array([
            # x, y, z, u, v
            x_offset - 3.0, -2.0,   100.0, 0.0, 0.0, 
            x_offset + 3.0, -2.0,   100.0, 1.0, 0.0, 
            x_offset + 3.0, -2.0,  -100.0, 1.0, 10.0,
            x_offset - 3.0, -2.0,  -100.0, 0.0, 10.0,
        ], dtype=np.float32)


        indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        ebo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)

        self.tracks.append({
            "vao": vao,
            "vbo": vbo,
            "ebo": ebo,
            "scroll": 0.0
        })

    def _load_texture(self):
        surface = pygame.image.load(self.texture_path)
        image = pygame.image.tostring(surface, "RGBA", True)
        w, h = surface.get_size()

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

    def update_scroll(self, delta_time, speed=metrics.SPEED_LANE_CHANGE):
        for track in self.tracks:
            track["scroll"] += delta_time * speed


    def render(self, projection_matrix, view_matrix):
        self.shader.use()
        glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "projection"), 1,
                           GL_FALSE, projection_matrix.astype(np.float32))
        glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "view"), 1,
                           GL_FALSE, view_matrix.astype(np.float32))
        glUniformMatrix4fv(glGetUniformLocation(self.shader.program, "model"), 1,
                           GL_FALSE, np.identity(4, dtype=np.float32))

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glUniform1i(glGetUniformLocation(self.shader.program, "trackTex"), 0)

        for track in self.tracks:
            glUniform1f(glGetUniformLocation(self.shader.program, "scroll"), track["scroll"])
            glBindVertexArray(track["vao"])
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)