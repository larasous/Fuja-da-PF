from src.objects.objects import Object
from OpenGL.GL import *


class Collectible(Object):
    def __init__(
        self,
        model,
        scale=[1.0, 1.0, 1.0],
        color=[1.0, 0.84, 0.0],
        speed=2.0,
        rotation_speed=2.0,
    ):
        super().__init__(model, scale=scale)
        self.color = color
        self.collected = False
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]

    def update(self, delta_time):
        self.position[2] += self.speed * delta_time
        self.rotation[1] = (self.rotation[1] + self.rotation_speed * delta_time) % 360
        self.set_transform(
            translation=self.position, rotation=self.rotation, scale=self.scale
        )

    def collect(self):
        self.collected = True
        # talvez esconder ou remover do mundo
        self.scale = [0.0, 0.0, 0.0]

    def render(self, shader_program, camera=None, light_pos=None):
        glUseProgram(shader_program.program)

        if camera is None:
            camera = self.default_camera
        if light_pos is None:
            light_pos = [0.0, 4.0, 2.0]

        # cor dourada
        glUniform3f(
            glGetUniformLocation(shader_program.program, "objectColor"),
            self.color[0],
            self.color[1],
            self.color[2],
        )

        # luz branca
        glUniform3f(
            glGetUniformLocation(shader_program.program, "lightColor"), 1.0, 1.0, 1.0
        )

        # posição da luz
        glUniform3f(
            glGetUniformLocation(shader_program.program, "lightPos"),
            light_pos[0],
            light_pos[1],
            light_pos[2],
        )

        # posição da câmera
        glUniform3f(
            glGetUniformLocation(shader_program.program, "viewPos"),
            camera.position[0],
            camera.position[1],
            camera.position[2],
        )

        # matrizes
        glUniformMatrix4fv(
            glGetUniformLocation(shader_program.program, "model"),
            1,
            GL_FALSE,
            self.get_model_matrix(),
        )
        glUniformMatrix4fv(
            glGetUniformLocation(shader_program.program, "view"),
            1,
            GL_FALSE,
            camera.get_view_matrix(),
        )
        glUniformMatrix4fv(
            glGetUniformLocation(shader_program.program, "projection"),
            1,
            GL_FALSE,
            camera.projection_matrix,
        )

        # chama render do modelo
        self.model.render(shader_program)
