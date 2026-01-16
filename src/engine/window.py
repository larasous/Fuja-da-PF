import glfw
from OpenGL.GL import *
import time
import json
import imgui
from imgui.integrations.glfw import GlfwRenderer
from src.constants import metrics, objects_path, textures_path, shaders_path
from src.engine.shader import Shader
from src.engine.skybox import Skybox
from src.engine.input import InputManager
from src.engine.camera import CameraManager
from src.objects.model import Model
from src.scene.start_scene import StartScene
from src.scene.lore_scene import LoreScene
from src.ui.hud import HUD
from src.scene.game_scene import GameScene
from src.engine.scene import SceneManager


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

        imgui.create_context()
        self.imgui_renderer = GlfwRenderer(self.window, attach_callbacks=False)

        self._init_shaders()
        self._init_models()

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

        self.camera = CameraManager()
        self.input = InputManager()
        self.input.register_callbacks(self.window)

        self._update_metrics()

        glEnable(GL_DEPTH_TEST)

        self.scene_manager = SceneManager(
            self.window,
            self.input,
            self.camera,
            self.hud,
            self.shaders,
            self.models,
            self.skybox,
            self.imgui_renderer,
        )

        self.start_scene = self.scene_manager.create_start_scene()
        self.state = "start"
        self.lore_scene = None
        self.game_scene = None

    def _init_shaders(self):
        self.shaders = {
            "skybox": Shader(
                vertex_path=shaders_path.VERTEX_SKYBOX,
                fragment_path=shaders_path.FRAGMENT_SKYBOX,
            ),
            "player": Shader(
                vertex_path=shaders_path.VERTEX_PLAYER,
                fragment_path=shaders_path.FRAGMENT_PLAYER,
            ),
            "coin": Shader(
                vertex_path=shaders_path.VERTEX_COIN,
                fragment_path=shaders_path.FRAGMENT_COIN,
            ),
            "obstacle": Shader(
                vertex_path=shaders_path.VERTEX_FRENCH_FRIES,
                fragment_path=shaders_path.FRAGMENT_FRENCH_FRIES,
            ),
            "hud": Shader(
                vertex_path=shaders_path.VERTEX_HUD,
                fragment_path=shaders_path.FRAGMENT_HUD,
            ),
        }
        self.hud = HUD(self.shaders["hud"])

    def _init_models(self):
        self.models = {
            "player": Model(objects_path.CAKE_PATH),
            "coin": Model(objects_path.COIN_PATH),
            "french_fries": Model(objects_path.FRENCH_FRIES_PATH),
        }

    def _update_metrics(self):
        width, height = glfw.get_framebuffer_size(self.window)
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)

    def _on_resize(self, window, width, height):
        metrics.WINDOW_WIDTH = width
        metrics.WINDOW_HEIGHT = height
        glViewport(0, 0, width, height)

    def run(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()

            if self.state == "start" and self.start_scene.finished:
                print("Mudando para LORE...")
                self.lore_scene = self.scene_manager.create_lore_scene(
                    "assets/lore/intro.json"
                )
                self.state = "lore"

            elif self.state == "lore" and self.lore_scene and self.lore_scene.finished:
                print("Mudando para PLAYING...")
                self.game_scene = self.scene_manager.create_game_scene()
                self.state = "playing"

            self.scene_manager.update()
            self.scene_manager.render()

            self.input.update()
            glfw.swap_buffers(self.window)

        glfw.terminate()
