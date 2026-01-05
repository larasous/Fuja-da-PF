from OpenGL.GL import *
from OpenGL.GLU import *

class CameraManager:
    def __init__(self):
        self.mode = "third_person"

        self.current_pos = [0.0, 5.0, 7.0]
        self.current_target = [0.0, 0.0, -10.0]

        self.target_pos = self.current_pos[:]
        self.target_target = self.current_target[:]

        self.transition_speed = 0.01

    def set_mode(self, mode: str):
        if mode in ("first_person", "third_person", "top_down"):
            self.mode = mode

    def apply(self, player_x, player_y, player_z):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if self.mode == "first_person":
            self.target_pos = [player_x, player_y + 0.5, player_z]
            self.target_target = [player_x, player_y + 0.5, player_z - 5.0]

        elif self.mode == "third_person":
            self.target_pos = [0.0, 5.0, 7.0]
            self.target_target = [0.0, 0.0, -10.0]

        elif self.mode == "top_down":
            self.target_pos = [player_x, 20.0, 0.0]
            self.target_target = [player_x, 0.0, player_z - 5.0]
        
        # --- interpolação suave ---
        for i in range(3):
            self.current_pos[i] += (self.target_pos[i] - self.current_pos[i]) * self.transition_speed
            self.current_target[i] += (self.target_target[i] - self.current_target[i]) * self.transition_speed

        gluLookAt(
            *self.current_pos,
            *self.current_target,
            0.0, 1.0, 0.0
        )

