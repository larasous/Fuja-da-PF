import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from pyrr import Matrix44
from src.objects.collectible import Collectible
from src.constants import metrics, objects_path, textures_path, shaders_path
from src.utils.shaders import read_shader_file
from src.engine.shader import Shader
from src.scene.lore_scene import LoreScene
from src.objects.objects import Obstacle
from src.objects.model import Model
from src.ui.start_screen import StartScreen
from src.engine.input import InputManager
from src.engine.skybox import Skybox
from src.utils.camera import create_projection_matrix
import numpy as np
import random
import time
import json
from src.objects.player import Player
from src.engine.camera import CameraManager
from src.ui.hud import HUD


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
        self.camera = CameraManager()
        glfw.make_context_current(self.window)
        glfw.set_window_size_callback(self.window, self._on_resize)

        skybox_vertex = read_shader_file(shaders_path.VERTEX_SKYBOX)
        skybox_fragment = read_shader_file(shaders_path.FRAGMENT_SKYBOX)

        french_fries_vertex = read_shader_file(shaders_path.VERTEX_FRENCH_FRIES)
        french_fries_fragment = read_shader_file(shaders_path.FRAGMENT_FRENCH_FRIES)

        player_vertex = read_shader_file(shaders_path.VERTEX_PLAYER)
        player_fragment = read_shader_file(shaders_path.FRAGMENT_PLAYER)

        text_vert = read_shader_file(shaders_path.VERTEX_HUD)
        text_frag = read_shader_file(shaders_path.FRAGMENT_HUD)

        coin_vert = read_shader_file(shaders_path.VERTEX_COIN)
        coin_frag = read_shader_file(shaders_path.FRAGMENT_COIN)

        self.coin_shader = Shader(coin_vert, coin_frag)

        self.hud_text_shader = Shader(text_vert, text_frag).program

        self.hud = HUD(self.hud_text_shader)

        self.french_fries_shader = Shader(french_fries_vertex, french_fries_fragment)

        self.player_shader = Shader(player_vertex, player_fragment)

        self.skybox_shader = Shader(skybox_vertex, skybox_fragment)

        self.skybox = Skybox(
            [
                textures_path.SKYBOX_TEXTURES["NZ"],
                textures_path.SKYBOX_TEXTURES["PZ"],
                textures_path.SKYBOX_TEXTURES["PY"],
                textures_path.SKYBOX_TEXTURES["NY"],
                textures_path.SKYBOX_TEXTURES["NX"],
                textures_path.SKYBOX_TEXTURES["PX"],
            ]
        )

        self.last_time = time.time()
        self.player_speed = 3.0

        self.camera = CameraManager()
        self.player_model = Model(objects_path.CAKE_PATH)
        self.player = Player(self.player_model, scale=[2.0, 2.0, 2.0])

        self.input = InputManager()
        self.input.register_callbacks(self.window)
        glfw.set_key_callback(self.window, self._on_key)

        self.frenchFries = Model(objects_path.FRENCH_FRIES_PATH)

        self._update_metrics()

        self.start_screen = StartScreen(self.window, self.input)
        self.state = "start"

        self.lanes = [-2.0, 0.0, 2.0]
        self.player_lane = 1
        self.obstacles = []
        self.spawn_timer = 0.0

        self.lore_screen = None

        self.collectibles = []
        self.collectible_timer = 0.0
        self.collectible_frequency = 1.0
        self.collectible_batch = 1

        self.coinModel = Model(objects_path.COIN_PATH)

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

                now = time.time()
                delta_time = now - self.last_time
                self.last_time = now
                self.hud.start_timer()

                glClearColor(0.1, 0.1, 0.1, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                # --- Atualiza câmera ---
                self.camera.update(
                    self.player.position[0],
                    self.player.position[1],
                    self.player.position[2],
                )
                view_matrix = self.camera.get_view_matrix()

                # MATRIZES
                projection_matrix = create_projection_matrix()

                view_matrix_skybox = view_matrix.copy()
                view_matrix_skybox[3, :3] = 0.0

                glDepthFunc(GL_LEQUAL)
                glDepthMask(GL_FALSE)
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
                glDepthMask(GL_TRUE)

                # --- Player ---
                self.player_shader.use()

                # Matrizes
                glUniformMatrix4fv(
                    glGetUniformLocation(self.player_shader.program, "projection"),
                    1,
                    GL_FALSE,
                    projection_matrix.astype(np.float32),
                )
                glUniformMatrix4fv(
                    glGetUniformLocation(self.player_shader.program, "view"),
                    1,
                    GL_FALSE,
                    view_matrix.astype(np.float32),
                )
                glUniformMatrix4fv(
                    glGetUniformLocation(self.player_shader.program, "model"),
                    1,
                    GL_FALSE,
                    self.player.get_model_matrix().astype(np.float32),
                )

                # Textura
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(
                    GL_TEXTURE_2D,
                    self.player.model.textures[self.player.model.current_material],
                )
                glUniform1i(
                    glGetUniformLocation(self.player_shader.program, "texture1"), 0
                )

                # Desenhar player
                self.player.update(0.01)
                self.player.render(self.player_shader)
                # print("Player position:", self.player.position)

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

                # collectibles
                self.coin_shader.use()
                glUniformMatrix4fv(
                    glGetUniformLocation(self.coin_shader.program, "projection"),
                    1,
                    GL_FALSE,
                    projection_matrix.astype(np.float32),
                )

                glUniformMatrix4fv(
                    glGetUniformLocation(self.coin_shader.program, "view"),
                    1,
                    GL_FALSE,
                    view_matrix.astype(np.float32),
                )

                self._spawn_collectibles()
                self._update_collectibles()
                for coin in self.collectibles:
                    coin.render(self.coin_shader, self.camera, None)

                self.hud.update_time(delta_time)
                self.hud.update_distance(self.player_speed * delta_time)
                self.hud.draw(metrics.WINDOW_WIDTH, metrics.WINDOW_HEIGHT)

                for obs in self.obstacles:
                    if self.check_collision(self.player, obs, threshold=0.8):
                        print("Colisão com obstáculo!")
                        # self.game_over()   # quando tiver pronto
                        break

                for coin in self.collectibles:
                    if self.check_collision(self.player, coin, threshold=0.5):
                        coin.collected = True
                        self.hud.update_coins(1)
                        print("Moeda coletada! Total:", self.hud.coin_count)

                self.collectibles = [c for c in self.collectibles if not c.collected]

            self.input.update()
            glfw.swap_buffers(self.window)

        glfw.terminate()

    def _spawn_obstacles(self):
        self.spawn_timer += 0.01
        if self.spawn_timer > 1.5:
            lane = random.choice(self.lanes)
            # nasce na origem
            obs = Obstacle(self.frenchFries, scale=[2.5, 2.5, 2.5])
            print("Obstacle created at:", obs.position)  # ← log inicial

            # aplica transformação depois
            obs.set_transform(translation=[lane, 0.0, -20.0], scale=[2.5, 2.5, 2.5])
            print("Obstacle after transform:", obs.position)  # ← log após deslocamento

            self.obstacles.append(obs)
            self.spawn_timer = 0.05

    def _update_obstacles(self):
        for obs in self.obstacles:
            obs.update(0.01)
        # mantém apenas os obstáculos que ainda não passaram do player
        self.obstacles = [obs for obs in self.obstacles if obs.position[2] < 2.0]

    def _spawn_collectibles(self):
        self.collectible_timer += 0.01
        if self.collectible_timer > self.collectible_frequency:
            lane = random.choice(self.lanes)

            if self.obstacles and self.obstacles[-1].position[0] == lane:
                lanes_available = [l for l in self.lanes if l != lane]
                lane = random.choice(lanes_available)

            for i in range(self.collectible_batch):
                z_offset = -20.0 - i * 2.0
                coin_y = 0.0
                coin = Collectible(
                    self.coinModel,
                    scale=[1.0, 1.0, 1.0],
                    color=[1.0, 0.84, 0.0],
                )
                coin.set_transform(
                    translation=[lane, coin_y, z_offset], scale=[1.0, 1.0, 1.0]
                )
                self.collectibles.append(coin)

            self.collectible_timer = 0.0

    def _update_collectibles(self):
        for coin in self.collectibles:
            coin.update(0.01)
        self.collectibles = [
            coin
            for coin in self.collectibles
            if coin.position[2] < 2.0 and not coin.collected
        ]

    def check_collision(self, obj1, obj2, *, threshold=0.5):
        dist = np.linalg.norm(obj1.position - obj2.position)
        return dist < threshold

    def _on_key(self, window, key, scancode, action, mods):
        if action == glfw.PRESS and self.state == "playing":
            # movimento lateral
            if key == glfw.KEY_LEFT:
                self.player.move_left(self.lanes)
            elif key == glfw.KEY_RIGHT:
                self.player.move_right(self.lanes)

            # troca de câmera
            elif key == glfw.KEY_1:
                self.camera.set_mode("first_person")
            elif key == glfw.KEY_2:
                self.camera.set_mode("third_person")
            elif key == glfw.KEY_3:
                self.camera.set_mode("top_down")

    def _update_metrics(self):
        width, height = glfw.get_framebuffer_size(self.window)
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)

    def _on_resize(self, window, width, height):
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)
