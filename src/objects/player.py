import numpy as np
from OpenGL.GL import *
from src.objects.objects import Object
from src.constants import metrics


class Player(Object):
    def __init__(self, model, scale=[1, 1, 1], color=[0.0, 1.0, 0.0]):
        # sempre nasce na origem
        super().__init__(
            model, position=[0.0, 0.0, 0.0], rotation=[0, 0, 0], scale=scale
        )
        self.current_lane = 1
        self.target_x = 0.0
        self.speed = metrics.SPEED_LANE_CHANGE
        self.color = np.array(color, dtype=np.float32)
        self.is_jumping = False
        self.jump_velocity = 0.0
        self.gravity = -6.0
        self.jump_strength = 5.0
        self.ground_y = self.position[1]

    def move_left(self, lanes):
        if self.current_lane > 0:
            self.current_lane -= 1
            self.target_x = lanes[self.current_lane]

    def move_right(self, lanes):
        if self.current_lane < len(lanes) - 1:
            self.current_lane += 1
            self.target_x = lanes[self.current_lane]
            
    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = self.jump_strength

    def update(self, delta_time):
        # movimento suave no eixo X
        dx = self.target_x - self.position[0]
        if abs(dx) > 0.01:  # tolerância
            step = self.speed * delta_time
            if abs(dx) < step:
                self.position[0] = self.target_x
            else:
                self.position[0] += step if dx > 0 else -step
        else:
            self.position[0] = self.target_x

        if self.is_jumping:
            self.position[1] += self.jump_velocity * delta_time
            self.jump_velocity += self.gravity * delta_time

            if self.position[1] <= self.ground_y:
                self.position[1] = self.ground_y
                self.is_jumping = False
                self.jump_velocity = 0.0

    def render(self, shader):
        shader.set_mat4("model", self.get_model_matrix())
        shader.set_vec3("color", self.color)
        self.model.render(shader)
