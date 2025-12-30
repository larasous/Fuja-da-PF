# src/objects/player.py
from OpenGL.GL import *
from OpenGL.GLU import *

class Player:
    def __init__(self, lanes, start_lane=1):
        self.lanes = lanes
        self.current_lane = start_lane

        # atributos visuais
        self.color = (0.0, 1.0, 0.0)  # verde
        self.radius = 0.1             # tamanho da esfera
        self.z = -3.0  # posição fixa em z

    def move_left(self):
        if self.current_lane > 0:
            self.current_lane -= 1

    def move_right(self):
        if self.current_lane < len(self.lanes) - 1:
            self.current_lane += 1

    def draw(self):
        glPushMatrix()
        glTranslatef(self.lanes[self.current_lane], 0.0, -3.0)  # z ajustado
        glColor3f(*self.color)

        quadric = gluNewQuadric()
        gluSphere(quadric, self.radius, 32, 32)
        gluDeleteQuadric(quadric)

        glPopMatrix()
