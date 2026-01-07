from src.objects.model import Model
from src.objects.objects import Object

from src.objects.objects import Obstacle

class Collectible(Obstacle):
    def __init__(self, model, scale=[1.0, 1.0, 1.0], color=[1.0, 0.84, 0.0]):
        super().__init__(model, scale=scale, color=color)
        self.collected = False

    def update(self, delta_time):
        self.position[2] += self.speed * delta_time
        self.set_transform(translation=self.position, scale=self.scale)
