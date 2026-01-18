import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer
from src.constants import metrics, objects_path, textures_path, shaders_path
from src.engine.shader import Shader
from src.engine.skybox import Skybox
from src.engine.input import InputManager
from src.engine.camera import CameraManager
from src.objects.model import Model
from src.ui.hud import HUD
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
                vertex_path=shaders_path.VERTEX_OBSTACLES,
                fragment_path=shaders_path.FRAGMENT_OBSTACLES,
            ),
            "hud": Shader(
                vertex_path=shaders_path.VERTEX_HUD,
                fragment_path=shaders_path.FRAGMENT_HUD,
            ),
        }
        self.hud = HUD(self.shaders["hud"])

    def _init_models(self):
        self.models = {
            "player": Model(objects_path.PLAYER_PATH),
            "coin": Model(objects_path.COIN_PATH),
            "french_fries": Model(objects_path.FRENCH_FRIES_PATH),
            "burger": Model(objects_path.BURGER_PATH),
            "sushi": Model(objects_path.SUSHI_PATH),
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

    def _reset_gl_state(self):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_CULL_FACE)
        
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, 0)
        
        glUseProgram(0)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, metrics.WINDOW_WIDTH, metrics.WINDOW_HEIGHT)
        
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
            
            if self.state == "playing" and self.game_scene and self.game_scene.state == "game_over":
                print("Mudando para GAME OVER...")
                self._reset_gl_state()
                self.lore_scene = self.scene_manager.create_lore_scene(
                    "assets/lore/game_over.json"
                )
                self.state = "game_over"
            
            elif self.state == "game_over" and self.lore_scene and self.lore_scene.finished:
                print("Reiniciando jogo...")
                self.state = "start"
                self.start_scene = self.scene_manager.create_start_scene()
                self.lore_scene = None
                self.game_scene = None


            self.scene_manager.update()
            self.scene_manager.render()

            self.input.update()
            glfw.swap_buffers(self.window)

        glfw.terminate()
