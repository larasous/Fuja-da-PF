from OpenGL.GL import *
import numpy as np


class Skybox:
    def __init__(self, faces):
        self.vertices = np.array(
            [
                -1,
                1,
                -1,
                -1,
                -1,
                -1,
                1,
                -1,
                -1,
                1,
                -1,
                -1,
                1,
                1,
                -1,
                -1,
                1,
                -1,
                -1,
                -1,
                1,
                -1,
                -1,
                -1,
                -1,
                1,
                -1,
                -1,
                1,
                -1,
                -1,
                1,
                1,
                -1,
                -1,
                1,
                1,
                -1,
                -1,
                1,
                -1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                -1,
                1,
                -1,
                -1,
                -1,
                -1,
                1,
                -1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                1,
                -1,
                1,
                -1,
                -1,
                1,
                -1,
                1,
                -1,
                1,
                1,
                -1,
                1,
                1,
                1,
                1,
                1,
                1,
                -1,
                1,
                1,
                -1,
                1,
                -1,
                -1,
                -1,
                -1,
                -1,
                -1,
                1,
                1,
                -1,
                -1,
                1,
                -1,
                -1,
                -1,
                -1,
                1,
                1,
                -1,
                1,
            ],
            dtype=np.float32,
        )

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

        self.texture_id = self._load_cubemap(faces)

    def _load_cubemap(self, faces):
        from PIL import Image

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture_id)

        targets = [
            GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        ]

        for i, face in enumerate(faces):
            img = Image.open(face).convert("RGB")
            img_data = np.array(img, dtype=np.uint8)
            glTexImage2D(
                targets[i],
                0,
                GL_RGB,
                img.width,
                img.height,
                0,
                GL_RGB,
                GL_UNSIGNED_BYTE,
                img_data,
            )

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        return texture_id

    def draw(self, shader_program):
        glDepthFunc(GL_LEQUAL)
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_id)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glBindVertexArray(0)
        glDepthFunc(GL_LESS)
