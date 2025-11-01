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

    def use(self):
        glUseProgram(self.program)
