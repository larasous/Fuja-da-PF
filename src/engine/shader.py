import numpy as np
from OpenGL.GL import *


class Shader:
    def __init__(self, vertex_source, fragment_source):
        self.program = glCreateProgram()
        vertex_shader = self._compile_shader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = self._compile_shader(fragment_source, GL_FRAGMENT_SHADER)

        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)
        glLinkProgram(self.program)

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    def _compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            raise Exception(f"Shader compilation failed: {error}")

        return shader

    def set_mat4(self, name, mat):
        loc = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, mat.astype(np.float32))

    def set_vec3(self, name, vec):
        loc = glGetUniformLocation(self.program, name)
        glUniform3fv(loc, 1, np.array(vec, dtype=np.float32))

    def use(self):
        glUseProgram(self.program)
