import numpy as np
from OpenGL.GL import *
from pyrr import Matrix44
from src.objects.model import Model


class Object:
    def __init__(self, model, position=[0, 0, 0], rotation=[0, 0, 0], scale=[1, 1, 1]):
        self.model = model
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)

    def get_model_matrix(self):
        translation = Matrix44.from_translation(self.position)
        rotation = Matrix44.identity()
        scaling = Matrix44.from_scale(self.scale)
        model_matrix = translation @ rotation @ scaling
        return model_matrix

    def render(self, shader):
        shader.set_mat4("model", self.get_model_matrix())
        self.model.draw()


class Obstacle(Object):
    def __init__(
        self,
        model: Model,
        x: float,
        z: float,
        scale: float = 0.5,
        color=(1.0, 0.0, 0.0),
    ):
        super().__init__(
            model=model,
            position=[x, 0.0, z],
            rotation=[0.0, 0.0, 0.0],
            scale=[scale, scale, scale],
        )
        self.color = np.array(color, dtype=np.float32)

    def update(self, speed: float):
        self.position[2] += speed

    def render(self, shader):
        shader.set_mat4("model", self.get_model_matrix())
        shader.set_vec3("color", self.color)
        self.model.draw()
