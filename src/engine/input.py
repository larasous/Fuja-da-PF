import glfw

class InputManager:
    def __init__(self):
        self.keys_down = set()
        self.keys_pressed = set()
        self.keys_released = set()

    def register_callbacks(self, window):
        glfw.set_key_callback(window, self._key_callback)

    def _key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.keys_down.add(key)
            self.keys_pressed.add(key)
        elif action == glfw.RELEASE:
            self.keys_down.discard(key)
            self.keys_released.add(key)

    def update(self):
        self.keys_pressed.clear()
        self.keys_released.clear()

    def is_down(self, key):
        return key in self.keys_down

    def was_pressed(self, key):
        return key in self.keys_pressed
    
    def enter_pressed(self):
        return (glfw.KEY_ENTER in self.keys_pressed) or (glfw.KEY_KP_ENTER in self.keys_pressed)
    def any_key_pressed(self):
        return len(self.keys_pressed) > 0
