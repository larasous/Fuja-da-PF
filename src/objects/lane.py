import numpy as np
from OpenGL.GL import *

class Lane:
    def __init__(self, width=2.0, depth=30.0, color=(1.0, 1.0, 1.0)):
        self.width = width
        self.depth = depth
        self.color = color
        self.model = np.identity(4, dtype=np.float32)

        vertices = np.array([
            -width/2, 0.0, -depth,
            width/2, 0.0, -depth,
            width/2, 0.0,  5.0,
            -width/2, 0.0,  5.0,
        ], dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, ctypes.c_void_p(0))

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def set_position(self, x):
        self.model = np.identity(4, dtype=np.float32)
        self.model[3,0] = x

    def render(self, shader, projection, view):
        shader.use()
        shader.set_matrices(projection, view, self.model)
        shader.set_vec3("laneColor", np.array(self.color, dtype=np.float32))
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)