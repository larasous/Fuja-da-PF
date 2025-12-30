import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from src.constants import metrics, objects_path
from src.scene.lore_scene import LoreScene
from src.objects.objects import Obstacle
from src.objects.model import Model
import numpy as np
import random
import time
import json
from src.ui.start_screen import StartScreen
from src.engine.input import InputManager
from src.objects.player import Player
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
        self.input = InputManager()
        glfw.set_key_callback(self.window, self._on_key)

        self.frenchFries = Model(objects_path.FRENCH_FRIES_PATH)

        self._update_metrics()

        self.game_over = False
        self.start_screen = StartScreen(self.window, self.input)
        self.state = "start"

        self.lanes = [-2.0, 0.0, 2.0]
        self.player = Player(self.lanes)
        self.obstacles = []
        self.spawn_timer = 0.0

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
            # Processa eventos do GLFW
            glfw.poll_events()
            self.state = "playing"

            # --- Tela inicial ---
            if self.state == "start":
                print("Estado: start")
                self.start_screen.update()
                self.start_screen.draw()
                if self.start_screen.finished:
                    # Quando ENTER for detectado
                    self.show_lore("assets/lore/intro.json", typing_speed=0.05, pause_between_blocks=3.0)
                    self.state = "lore"

            # --- Tela de lore ---
            elif self.state == "lore":
                self.lore_screen.update()
                self.lore_screen.draw()
                if self.lore_screen.finished:
                    self.state = "playing"

            # --- Jogo rodando ---
            elif self.state == "playing":
                glClearColor(0.1, 0.1, 0.1, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(
                    45, metrics.WINDOW_WIDTH / metrics.WINDOW_HEIGHT, 1.0, 100.0
                )

                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
                gluLookAt(0, 5, 5, 0, 0, -10, 0, 1, 0)

                if not self.game_over:
                    self._spawn_obstacles()
                    self._update_obstacles()

                
                self._draw_obstacles()
                self.player.draw()
                self._check_collisions()

            # ✅ Atualiza o InputManager só no final do frame
            self.input.update()
            glfw.swap_buffers(self.window)

        glfw.terminate()
    
    def _spawn_obstacles(self):
        self.spawn_timer += 0.01
        if self.spawn_timer > 1.5:
            lane = random.choice(self.lanes)
            self.obstacles.append(Obstacle(self.frenchFries, lane, -20.0, scale=3.5))
            self.spawn_timer = 0.05

    def _update_obstacles(self):
        for obs in self.obstacles:
            obs.update(0.02)
        self.obstacles = [obs for obs in self.obstacles if obs.z < 0]

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
            player_x = self.lanes[self.player.current_lane]
            for obs in self.obstacles:
                if abs(obs.z + 3.0) < 0.01 and abs(obs.x - player_x) < 0.01:
                    self.game_over = True
                    print("💥 COLISÃO!")

    def _on_key(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            if self.state == "playing":
                if key == glfw.KEY_LEFT:
                    self.player.move_left()
                elif key == glfw.KEY_RIGHT:
                    self.player.move_right()

    def _update_metrics(self):
        width, height = glfw.get_framebuffer_size(self.window)
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)

    def _on_resize(self, window, width, height):
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)
