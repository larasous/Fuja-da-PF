import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr import Matrix44
from src.constants import metrics, objects_path, textures_path, shaders_path
from src.utils.shaders import read_shader_file
from src.engine.shader import Shader
from src.scene.lore_scene import LoreScene
from src.objects.objects import Obstacle
from src.objects.model import Model
from src.ui.start_screen import StartScreen
from src.engine.input import InputManager
from src.engine.skybox import Skybox
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

        skybox_vertex = read_shader_file(shaders_path.VERTEX_SKYBOX)
        skybox_fragment = read_shader_file(shaders_path.FRAGMENT_SKYBOX)

        french_fries_vertex = read_shader_file(shaders_path.VERTEX_FRENCH_FRIES)
        french_fries_fragment = read_shader_file(shaders_path.FRAGMENT_FRENCH_FRIES)

        self.french_fries_shader = Shader(french_fries_vertex, french_fries_fragment)

        self.skybox_shader = Shader(skybox_vertex, skybox_fragment)

        self.skybox = Skybox(
            [
                textures_path.SKYBOX_TEXTURES["PX"],
                textures_path.SKYBOX_TEXTURES["NX"],
                textures_path.SKYBOX_TEXTURES["PY"],
                textures_path.SKYBOX_TEXTURES["NY"],
                textures_path.SKYBOX_TEXTURES["PZ"],
                textures_path.SKYBOX_TEXTURES["NZ"],
            ]
        )

        self.input = InputManager()
        self.input.register_callbacks(self.window)

        self.frenchFries = Model(objects_path.FRENCH_FRIES_PATH)

        self._update_metrics()

        self.start_screen = StartScreen(self.window, self.input)
        self.state = "start"

        self.lanes = [-2.0, 0.0, 2.0]
        self.player_lane = 1
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
                    self.show_lore(
                        "assets/lore/intro.json",
                        typing_speed=0.05,
                        pause_between_blocks=3.0,
                    )
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

                # MATRIZES
                projection_matrix = Matrix44.perspective_projection(
                    45.0, metrics.WINDOW_WIDTH / metrics.WINDOW_HEIGHT, 0.1, 100.0
                )

                view_matrix = Matrix44.look_at([0, 5, 5], [0, 0, -10], [0, 1, 0])

                view_matrix_skybox = view_matrix.copy()
                view_matrix_skybox[3, :3] = 0.0

                glDepthFunc(GL_LEQUAL)
                self.skybox_shader.use()
                glUniformMatrix4fv(
                    glGetUniformLocation(self.skybox_shader.program, "projection"),
                    1,
                    GL_FALSE,
                    projection_matrix.astype(np.float32),
                )
                glUniformMatrix4fv(
                    glGetUniformLocation(self.skybox_shader.program, "view"),
                    1,
                    GL_FALSE,
                    view_matrix_skybox.astype(np.float32),
                )
                glUniform1i(
                    glGetUniformLocation(self.skybox_shader.program, "skybox"), 0
                )
                self.skybox.draw(self.skybox_shader.program)
                glDepthFunc(GL_LESS)

                # --- Objetos ---
                self.french_fries_shader.use()
                glUniformMatrix4fv(
                    glGetUniformLocation(
                        self.french_fries_shader.program, "projection"
                    ),
                    1,
                    GL_FALSE,
                    projection_matrix.astype(np.float32),
                )
                glUniformMatrix4fv(
                    glGetUniformLocation(self.french_fries_shader.program, "view"),
                    1,
                    GL_FALSE,
                    view_matrix.astype(np.float32),
                )

                # desenhar obstáculos
                self._spawn_obstacles()
                self._update_obstacles()
                for obs in self.obstacles:
                    obs.render(self.french_fries_shader)

                # desenhar player (quando migrar para Object)
                # self.player.render(self.french_fries_shader)

                self._check_collisions()

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
            obs.update(0.01)
        self.obstacles = [obs for obs in self.obstacles if obs.position[2] < 0]

    def _check_collisions(self):
        for obs in self.obstacles:
            if (
                abs(obs.position[2]) < 1.0
                and obs.position[0] == self.lanes[self.player_lane]
            ):
                # print("💥 COLISÃO!")
                pass

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
