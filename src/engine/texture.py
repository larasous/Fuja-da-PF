from OpenGL.GL import *
from PIL import Image


class Texture:
    def __init__(self, target=GL_TEXTURE_2D):
        self.target = target
        self.texture_id = glGenTextures(1)

    def bind(self, unit=0):
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(self.target, self.texture_id)

    def unbind(self):
        glBindTexture(self.target, 0)

    def delete(self):
        glDeleteTextures([self.texture_id])

    def load_texture(self, width, height, data=None):
        self.bind()
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(
            self.target,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            data,
        )
        self.unbind()

    def load_cubemap(self, faces, size=(1024, 1024)):
        self.bind()
        targets = [
            GL_TEXTURE_CUBE_MAP_POSITIVE_X,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
            GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
            GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
        ]

        for i, face in enumerate(faces):
            img = Image.open(face).convert("RGB").resize(size)
            img_data = img.tobytes()
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

        glTexParameteri(self.target, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(self.target, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(self.target, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        self.unbind()
