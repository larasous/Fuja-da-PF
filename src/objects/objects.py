import numpy as np
from OpenGL.GL import *
from src.objects.model import Model


class Object:
    def __init__(self, model, position=[0, 0, 0], rotation=[0, 0, 0], scale=[1, 1, 1]):
        self.model = model
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)

    def get_model_matrix(self):
        # retorna a matriz de transformação TRS
        pass

    def update(self):
        """Sobrescrito por Player ou Obstacles"""
        pass

    def render(self, shader):
        shader.set_mat4("model", self.get_model_matrix())
        self.model.draw()


class Obstacle:
    def __init__(
        self,
        model: Model,
        x: float,
        z: float,
        scale: float = 0.5,
        color=(1.0, 0.0, 0.0),
    ):
        self.model = model
        self.x = x
        self.z = z
        self.scale = scale
        self.color = color

        # bounding box aproximada
        self.width = 2.0 * self.scale
        self.depth = 2.0 * self.scale

    def update(self, speed: float):
        # move em direção ao player (z mais próximo de -3)
        self.z += speed

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0.0, self.z)
        glScalef(self.scale, self.scale, self.scale)
        glColor3f(*self.color)
        self.model.draw()
        glPopMatrix()