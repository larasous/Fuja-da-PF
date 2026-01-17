from src.objects.objects import Object
from src.constants import metrics
from OpenGL.GL import *
import numpy as np


class Collectible(Object):
    def __init__(
        self,
        model,
        scale=[1.0, 1.0, 1.0],
        color=[1.0, 0.84, 0.0],
        speed=metrics.SPEED_OBJECTS,
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
        self.scale = [0.0, 0.0, 0.0]

    def render(self, shader, projection, view, camera=None, light_pos=None):
        shader.use()
        shader.set_matrices(projection, view, self.get_model_matrix())
        shader.set_vec3("objectColor", self.color)
        shader.set_vec3("lightColor", [1.0, 1.0, 1.0])
        shader.set_vec3("lightPos", light_pos or [0.0, 4.0, 2.0])
        shader.set_vec3("viewPos", camera.position)
        self.model.render(shader)
