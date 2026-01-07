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
        scaling = Matrix44.from_scale(self.scale)
        rotation = Matrix44.identity()
        if self.rotation[0] != 0:
            rotation = Matrix44.from_x_rotation(self.rotation[0]) @ rotation
        if self.rotation[1] != 0:
            rotation = Matrix44.from_y_rotation(self.rotation[1]) @ rotation
        if self.rotation[2] != 0:
            rotation = Matrix44.from_z_rotation(self.rotation[2]) @ rotation
        translation = Matrix44.from_translation(self.position)

        model_matrix = scaling @ rotation @ translation
        return model_matrix

    def set_transform(self, translation=None, scale=None, rotation=None):
        if translation is not None:
            self.position = np.array(translation, dtype=np.float32)
        if scale is not None:
            self.scale = np.array(scale, dtype=np.float32)
        if rotation is not None:
            self.rotation = np.array(rotation, dtype=np.float32)

    def render(self, shader):
        shader.set_mat4("model", self.get_model_matrix())
        self.model.render()


class Obstacle(Object):
    def __init__(self, model, scale=[1.0, 1.0, 1.0], color=[1.0, 1.0, 1.0]):
        # sempre nasce na origem
        super().__init__(model, scale=scale)
        self.speed = 3.0
        self.color = np.array(color, dtype=np.float32)

    def set_lane_and_depth(self, lane, depth):
        """
        Aplica a transformação para deslocar o obstáculo
        até a pista (lane) e profundidade (depth).
        """
        self.set_transform(translation=[lane, 0.0, depth], scale=self.scale)

    def update(self, delta_time):
        # movimento no eixo Z (vem em direção ao player)
        self.position[2] += self.speed * delta_time

    def render(self, shader):
        shader.set_mat4("model", self.get_model_matrix())
        shader.set_vec3("color", self.color)
        self.model.render()
