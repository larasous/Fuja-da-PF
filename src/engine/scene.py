import json
from src.scene.game_scene import GameScene
from src.scene.lore_scene import LoreScene
from src.scene.start_scene import StartScene


class SceneManager:
    def __init__(
        self,
        window,
        input_manager,
        camera,
        hud,
        shaders,
        models,
        skybox,
        imgui_renderer,
        track,
    ):
        self.window = window
        self.input = input_manager
        self.camera = camera
        self.hud = hud
        self.shaders = shaders
        self.models = models
        self.skybox = skybox
        self.imgui_renderer = imgui_renderer
        self.track = track

        self.current_scene = None

    def set_scene(self, scene):
        self.current_scene = scene

    def update(self):
        if self.current_scene and hasattr(self.current_scene, "update"):
            self.current_scene.update()

    def render(self):
        if self.current_scene:
            if hasattr(self.current_scene, "render"):
                self.current_scene.render()
            elif hasattr(self.current_scene, "draw"):
                self.current_scene.draw()

    def create_start_scene(self):

        scene = StartScene(self.window, self.input, self.imgui_renderer)
        self.set_scene(scene)
        return scene

    def create_lore_scene(self, path, typing_speed=0.05, pause=2.5):
        with open(path, "r", encoding="utf-8") as file:
            blocks = json.load(file)
        scene = LoreScene(self.window, blocks, self.imgui_renderer, typing_speed, pause)
        self.set_scene(scene)
        return scene

    def create_game_scene(self):
        scene = GameScene(
            self.window,
            self.input,
            self.camera,
            self.hud,
            self.shaders,
            self.models,
            self.skybox,
            self.track,
        )
        self.set_scene(scene)
        return scene
