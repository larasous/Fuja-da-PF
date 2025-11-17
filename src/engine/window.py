import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from src.constants import metrics
from src.scene.lore_scene import LoreScene
from src.objects.objects import Obstacle
import numpy as np
import random
import time
import json


class Window:
    def __init__(self):
        if not glfw.init():
            raise Exception("GLFW could not be initialized")

        if metrics.WINDOW_MAXIMIZED:
            glfw.window_hint(glfw.MAXIMIZED, glfw.TRUE)

        self.window = glfw.create_window(
            metrics.WINDOW_WIDTH,
            metrics.WINDOW_HEIGHT,
            metrics.WINDOW_TITLE,
            None,
            None,
        )
        if not self.window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        glfw.make_context_current(self.window)
        glfw.set_window_size_callback(self.window, self._on_resize)
        glfw.set_key_callback(self.window, self._on_key)

        self._update_metrics()

        self.lanes = [-2.0, 0.0, 2.0]
        self.player_lane = 1
        self.obstacles = []
        self.spawn_timer = 0.0

        self.state = "lore"
        self.lore_screen = None

        glEnable(GL_DEPTH_TEST)

    def show_lore(self, path, typing_speed=0.05, pause_between_blocks=2.5):
        with open(path, "r", encoding="utf-8") as file:
            blocks = json.load(file)
            self.lore_screen = LoreScene(
                self.window, blocks, typing_speed, pause_between_blocks
            )

    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            if self.state == "lore":
                self.lore_screen.update()
                self.lore_screen.draw()
                if self.lore_screen.finished:
                    self.state = "playing"
            elif self.state == "playing":
                glClearColor(0.1, 0.1, 0.1, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(
                    45, metrics.WINDOW_WIDTH / metrics.WINDOW_HEIGHT, 0.1, 100.0
                )

                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                gluLookAt(0, 5, 5, 0, 0, -10, 0, 1, 0)

                self._spawn_obstacles()
                self._update_obstacles()
                self._draw_obstacles()
                self._draw_player()
                self._check_collisions()

            glfw.swap_buffers(self.window)

        glfw.terminate()

    def _spawn_obstacles(self):
        self.spawn_timer += 0.01
        if self.spawn_timer > 1.5:
            lane = random.choice(self.lanes)
            self.obstacles.append(Obstacle(lane, -20.0))
            self.spawn_timer = 0.0

    def _update_obstacles(self):
        for obs in self.obstacles:
            obs.update(0.1)

    def _draw_obstacles(self):
        for obs in self.obstacles:
            obs.draw()

    def _draw_player(self):
        glPushMatrix()
        glTranslatef(self.lanes[self.player_lane], 0.0, 0.0)
        glScalef(0.5, 0.5, 0.5)
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_QUADS)
        for dx, dz in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            glVertex3f(dx, 0.0, dz)
        glEnd()
        glPopMatrix()

    def _check_collisions(self):
        for obs in self.obstacles:
            if abs(obs.z) < 1.0 and obs.x == self.lanes[self.player_lane]:
                print("💥 COLISÃO!")

    def _on_key(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if self.state == "playing":
                if key == glfw.KEY_LEFT and self.player_lane > 0:
                    self.player_lane -= 1
                elif key == glfw.KEY_RIGHT and self.player_lane < 2:
                    self.player_lane += 1

    def _update_metrics(self):
        width, height = glfw.get_framebuffer_size(self.window)
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)

    def _on_resize(self, window, width, height):
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)
