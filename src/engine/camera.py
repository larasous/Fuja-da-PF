from pyrr import Matrix44
import numpy as np

class CameraManager:
    def __init__(self):
        self.mode = "third_person"

        self.current_pos = np.array([0.0, 5.0, 7.0], dtype=np.float32)
        self.current_target = np.array([0.0, 0.0, -10.0], dtype=np.float32)

        self.target_pos = self.current_pos.copy()
        self.target_target = self.current_target.copy()

        self.transition_speed = 0.01

    def set_mode(self, mode: str):
        if mode in ("first_person", "third_person", "top_down"):
            self.mode = mode

    def update(self, player_x, player_y, player_z):
        # define alvo conforme o modo
        if self.mode == "first_person":
            self.target_pos = np.array([player_x, player_y + 0.5, player_z], dtype=np.float32)
            self.target_target = np.array([player_x, player_y + 0.5, player_z - 5.0], dtype=np.float32)

        elif self.mode == "third_person":
            self.target_pos = np.array([0.0, 5.0, 7.0], dtype=np.float32)
            self.target_target = np.array([0.0, 0.0, -10.0], dtype=np.float32)

        elif self.mode == "top_down":
            self.target_pos = np.array([player_x, 20.0, 0.0], dtype=np.float32)
            self.target_target = np.array([player_x, 0.0, player_z - 5.0], dtype=np.float32)

        # interpolação suave
        self.current_pos += (self.target_pos - self.current_pos) * self.transition_speed
        self.current_target += (self.target_target - self.current_target) * self.transition_speed

    def get_view_matrix(self):
        # retorna a matriz de visão moderna
        return Matrix44.look_at(
            eye=self.current_pos,
            target=self.current_target,
            up=[0.0, 1.0, 0.0]
        )
