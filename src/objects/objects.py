import numpy as np
from OpenGL.GL import *


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


class Obstacle(Object):
    def __init__(self, model, lane_x, z_pos):
        super().__init__(model, position=[lane_x, 0, z_pos])
        self.size = 0.5

    def update(self, speed):
        self.z += speed

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0.0, self.z)
        glScalef(self.size, self.size, self.size)
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        for dx, dz in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            glVertex3f(dx, 0.0, dz)
        glEnd()
        glPopMatrix()
