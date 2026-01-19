import glfw
import random
import time
import numpy as np
from OpenGL.GL import *
from src.engine import window
from src.constants import metrics
from src.objects.player import Player
from src.objects.objects import Obstacle
from src.objects.collectible import Collectible
from src.engine.audio import AudioManager
from src.objects.lane import Lane
from src.constants.colors import COLOR_PALETTE


class GameScene:
    def __init__(self, window, input_manager, camera, hud, shaders, models, skybox):
        self.window = window
        self.input = input_manager
        self.camera = camera
        self.hud = hud
        self.shaders = shaders
        self.models = models
        self.skybox = skybox
        # Player
        self.player = Player(self.models["player"], scale=[2.0, 2.0, 2.0])
        self.state = "playing"
        self.death_timer = 0.0

        self.music = AudioManager()
        self.music.play_music("assets/sounds/background_sound.mp3")


        # Estado
        self.game_over = False
        self.lanes = [-2.0, 0.0, 2.0]
        self.player_lane = 1
        self.obstacles = []
        self.obstacle_scales = {
            "burger": [1, 1, 1],
            "sushi": [0.5, 0.5, 0.5],
            "french_fries": [2.5, 2.5, 2.5],
        }

        self.collectibles = []

        # Timers
        self.collectible_timer = 0.0
        self.collectible_frequency = 1.0
        self.collectible_batch = 1
        self.spawn_timer = 0.0

        # Velocidade
        self.player_speed = metrics.SPEED_PLAYER

        # Tempo
        self.last_time = time.time()
        
        self.lanes = [-2.0, 0.0, 2.0]
        self.lane_objects = [
            Lane(width=2.0, depth=30.0, color=(0.8,0.2,0.2)),
            Lane(width=2.0, depth=30.0, color=(0.2,0.8,0.2)),
            Lane(width=2.0, depth=30.0, color=(0.2,0.2,0.8)),
        ]

        for lane_obj, lane_x in zip(self.lane_objects, self.lanes):
            lane_obj.set_position(lane_x)


    def update(self):
        now = time.time()
        delta_time = now - self.last_time
        self.last_time = now

        self.hud.start_timer()

        # Input
        if self.input.was_pressed(glfw.KEY_LEFT):
            self.player.move_left(self.lanes)
        elif self.input.was_pressed(glfw.KEY_RIGHT):
            self.player.move_right(self.lanes)

        if self.input.was_pressed(glfw.KEY_SPACE):
            print("Espaço pressionado")
            self.player.jump()

        if self.input.was_pressed(glfw.KEY_1):
            self.camera.set_mode("first_person")
        elif self.input.was_pressed(glfw.KEY_2):
            self.camera.set_mode("third_person")
        elif self.input.was_pressed(glfw.KEY_3):
            self.camera.set_mode("top_down")

        # Render
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Atualiza câmera
        self.camera.update(*self.player.position)
        view_matrix = self.camera.get_view_matrix()
        projection_matrix = self.camera.projection_matrix
        
        if self.camera.mode == "top_down":
            light_direction = np.array([0.0, -1.0, 0.0], dtype=np.float32)
        else:
            light_direction = np.array([0.0, 0.0, -1.0], dtype=np.float32)

        light_color = np.array(COLOR_PALETTE["WHITE"][:3], dtype=np.float32)

        for shader_name in ["player", "obstacle", "coin"]:
            shader = self.shaders.get(shader_name)
            if shader:
                shader.use()
                shader.set_vec3("lightDir", light_direction)
                shader.set_vec3("lightColor", light_color)
                shader.set_vec3("viewPos", self.camera.position)

        # Skybox
        view_matrix_skybox = view_matrix.copy()
        view_matrix_skybox[3, :3] = 0.0
        glDepthFunc(GL_LEQUAL)
        glDepthMask(GL_FALSE)
        self.shaders["skybox"].set_matrices(projection_matrix, view_matrix_skybox)
        self.shaders["skybox"].set_texture(0, "skybox")
        self.skybox.draw(self.shaders["skybox"].program)
        glDepthFunc(GL_LESS)
        glDepthMask(GL_TRUE)
        
        shader_lane = self.shaders.get("lane")
        if shader_lane:
            for lane_obj in self.lane_objects:
                lane_obj.render(shader_lane, projection_matrix, view_matrix)

        # Player
        self.shaders["player"].set_matrices(
            projection_matrix, view_matrix, self.player.get_model_matrix()
        )

        if self.state == "dying":
            self.death_timer += delta_time

            if self.death_timer < 0.05:
                self.player.position[1] += 8.0 * delta_time
            else:
                self.player.position[1] -= 12.0 * delta_time 
            
            if self.death_timer > 1.0:
                self.state = "game_over"
                self.music.stop_music()

        self.player.update(metrics.TICK)
        self.player.render(self.shaders["player"])

        # Obstáculos
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        for obs in self.obstacles:
            shader = self.shaders.get("obstacle")
            if shader:
                obs.render(shader, projection_matrix, view_matrix)
        glDisable(GL_CULL_FACE)

        # Coletáveis
        for coin in self.collectibles:
            shader = self.shaders.get("coin")
            if shader:
                coin.render(shader, projection_matrix, view_matrix, self.camera)

        # HUD
        self.hud.update_time(delta_time)
        self.hud.update_distance(self.player_speed * delta_time)
        self.hud.draw(metrics.WINDOW_WIDTH, metrics.WINDOW_HEIGHT)

        self._spawn_obstacles(metrics.TICK)
        self._update_obstacles(metrics.TICK)
        if self.state == "playing":
            for obs in self.obstacles:
                if self.check_collision(self.player, obs, threshold=0.8):
                    print("Colisão com obstáculo!")
                    self.state = "dying"
                    self.death_timer = 0.0
                    self.game_over = True
                    break

        self._spawn_collectibles(metrics.TICK)
        self._update_collectibles(metrics.TICK)
        for coin in self.collectibles:
            if self.check_collision(self.player, coin, threshold=0.5):
                coin.collected = True
                self.hud.update_coins(1)
                print("Moeda coletada! Total:", self.hud.coin_count)

        self.collectibles = [c for c in self.collectibles if not c.collected]

    def _spawn_obstacles(self, delta_time):
        self.spawn_timer += delta_time
        if self.spawn_timer > 1.5:
            lane = random.choice(self.lanes)

            name, model = random.choice(
                [(n, m) for n, m in self.models.items() if n not in ("player", "coin")]
            )

            scale = self.obstacle_scales.get(name, None)

            obs = Obstacle(model, scale=scale)
            obs.set_transform(translation=[lane, 0.0, -20.0], scale=scale)
            self.obstacles.append(obs)

            self.spawn_timer = 0.0

    def _update_obstacles(self, delta_time):
        for obs in self.obstacles:
            obs.update(delta_time)
        self.obstacles = [obs for obs in self.obstacles if obs.position[2] < 2.0]

    def _spawn_collectibles(self, delta_time):
        self.collectible_timer += delta_time
        if self.collectible_timer > self.collectible_frequency:
            lane = random.choice(self.lanes)
            if self.obstacles and self.obstacles[-1].position[0] == lane:
                lanes_available = [l for l in self.lanes if l != lane]
                lane = random.choice(lanes_available)

            for i in range(self.collectible_batch):
                z_offset = -20.0 - i * 2.0
                coin = Collectible(
                    self.models["coin"],
                    scale=[1.0, 1.0, 1.0],
                    color=[1.0, 0.84, 0.0],
                )
                coin.set_transform([lane, 0.3, z_offset], [1.0, 1.0, 1.0])
                self.collectibles.append(coin)

            self.collectible_timer = 0.0

    def _update_collectibles(self, delta_time):
        for coin in self.collectibles:
            coin.update(delta_time)
        self.collectibles = [
            coin
            for coin in self.collectibles
            if coin.position[2] < 2.0 and not coin.collected
        ]

    def check_collision(self, obj1, obj2, *, threshold=0.5):
        dist = np.linalg.norm(obj1.position - obj2.position)
        return dist < threshold
