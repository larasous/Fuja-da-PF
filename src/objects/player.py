# src/objects/player.py
from OpenGL.GL import *
from OpenGL.GLU import *

class Player:
    def __init__(self, lanes):
        self.lanes = lanes
        self.current_lane = 1

        self.target_lane = 1
        self.x = lanes[self.current_lane]
        self.z = -3.0 
        self.speed = 0.05

        self.color = (0.0, 1.0, 0.0)  
        self.radius = 0.1             
        

    def move_left(self):
        if self.target_lane > 0:
            self.target_lane -= 1

    def move_right(self):
        if self.target_lane < len(self.lanes) - 1:
            self.target_lane += 1

    def update(self):
        target_x = self.lanes[self.target_lane]

        if abs(self.x - target_x) > 0.01:
            direction = 1 if target_x > self.x else -1
            self.x += direction * self.speed
        else:
            self.x = target_x
            self.current_lane = self.target_lane


    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0.0, self.z)  
        glColor3f(*self.color)

        quadric = gluNewQuadric()
        gluSphere(quadric, self.radius, 32, 32)
        gluDeleteQuadric(quadric)

        glPopMatrix()
