from OpenGL.GL import *
import numpy as np
from src.utils.skybox import create_cube_vertices
from src.engine.texture import Texture


class Skybox:
    def __init__(self, faces):
        self.vertices = create_cube_vertices()

        # VAO e VBO
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(
            GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW
        )

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.texture = Texture(GL_TEXTURE_CUBE_MAP)
        self.texture.load_cubemap(faces)

    def draw(self, shader_program):
        glDepthFunc(GL_LEQUAL)
        glUseProgram(shader_program)
        glBindVertexArray(self.vao)
        self.texture.bind(0)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 3)
        glBindVertexArray(0)
        glDepthFunc(GL_LESS)
