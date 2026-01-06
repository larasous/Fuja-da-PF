from OpenGL.GL import *
import numpy as np
from src.objects.objects import Object


class Player(Object):
    def __init__(self, model, position=[0,0,0], rotation=[0,0,0], scale=[1,1,1]):
        super().__init__(model, position, rotation, scale)
        self.current_lane = 1
        self.target_x = position[0]   # posição alvo no eixo X
        self.speed = 3.5              # velocidade de transição
        self.color = np.array([0.0, 1.0, 0.0], dtype=np.float32)


    def move_left(self, lanes):
        if self.current_lane > 0:
            self.current_lane -= 1
            self.target_x = lanes[self.current_lane]

    def move_right(self, lanes):
        if self.current_lane < len(lanes) - 1:
            self.current_lane += 1
            self.target_x = lanes[self.current_lane]


    def update(self, delta_time):
        # movimento suave no eixo X
        dx = self.target_x - self.position[0]
        if abs(dx) > 0.01:  # tolerância
            step = self.speed * delta_time
            if abs(dx) < step:
                self.position[0] = self.target_x
            else:
                self.position[0] += step if dx > 0 else -step

    def render(self, shader):
        shader.set_mat4("model", self.get_model_matrix())
        shader.set_vec3("color", self.color)
        self.model.draw()
