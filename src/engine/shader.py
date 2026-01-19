import numpy as np
from OpenGL.GL import *


class Shader:
    def __init__(
        self,
        vertex_path=None,
        fragment_path=None,
        vertex_source=None,
        fragment_source=None,
    ):
        self.program = glCreateProgram()

        if vertex_path and fragment_path:
            vertex_source = self._read_shader_file(vertex_path)
            fragment_source = self._read_shader_file(fragment_path)

        vertex_shader = self._compile_shader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = self._compile_shader(fragment_source, GL_FRAGMENT_SHADER)

        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)
        glLinkProgram(self.program)

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.program).decode()
            raise Exception(f"Program link failed: {error}")

    def _read_shader_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            raise Exception(f"Shader compilation failed: {error}")

        return shader

    def use(self):
        glUseProgram(self.program)

    # --- Uniform helpers ---
    def set_matrices(self, projection, view, model=None):
        self.use()
        self.set_mat4("projection", projection)
        self.set_mat4("view", view)
        if model is not None:
            self.set_mat4("model", model)

    def set_texture(self, texture, uniform_name="texture1", unit=0):
        self.use()
        glActiveTexture(GL_TEXTURE0 + unit)
        glBindTexture(GL_TEXTURE_2D, texture)
        glUniform1i(glGetUniformLocation(self.program, uniform_name), unit)

    def set_mat4(self, name, mat):
        loc = glGetUniformLocation(self.program, name)
        glUniformMatrix4fv(loc, 1, GL_FALSE, mat.astype(np.float32))

    def set_vec3(self, name, vec):
        loc = glGetUniformLocation(self.program, name)
        glUniform3fv(loc, 1, np.array(vec, dtype=np.float32))
    
    def set_float(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniform1f(loc, float(value))

    def set_int(self, name, value):
        loc = glGetUniformLocation(self.program, name)
        glUniform1i(loc, int(value))
