import pygame
import numpy as np
from OpenGL.GL import *
from pyrr import Matrix44
from src.constants.colors import COLOR_PALETTE


class HUD:
    def __init__(self, text_shader_program):
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial Black", 20)

        # estado
        self.coin_count = 0
        self.game_time = 0
        self.distance = 0
        self.current_level = 1
        self.level_thresholds = {1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60, 7: 70}
        self.level_names = {
            1: "Preguiça",
            2: "Gula",
            3: "Luxúria",
            4: "Avareza",
            5: "Ira",
            6: "Inveja",
            7: "Orgulho",
        }
        self.timer_active = False

        self.text_shader = text_shader_program
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, 16 * 4, None, GL_DYNAMIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        glBindVertexArray(0)

        # cache de texturas
        self.text_cache = {}

    def start_timer(self):
        self.timer_active = True

    def stop_timer(self):
        self.timer_active = False

    def update_time(self, dt):
        if self.timer_active:
            self.game_time += dt

    def update_coins(self, amount):
        self.coin_count += amount
        self.check_level_completion()

    def update_distance(self, dd):
        self.distance += dd

    def check_level_completion(self):
        req = self.level_thresholds.get(self.current_level)
        if req and self.coin_count >= req:
            self.advance_level()

    def advance_level(self):
        self.current_level += 1
        level_name = self.level_names.get(
            self.current_level, f"Nível {self.current_level}"
        )
        print(f"Avançou para o nível {level_name}!")

    # --- renderização de texto com cache ---
    def _get_text_texture(self, text):
        if text in self.text_cache:
            return self.text_cache[text]

        surface = self.font.render(text, True, (255, 255, 255))
        width, height = surface.get_size()

        data = pygame.image.tostring(surface, "RGBA", False)

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        self.text_cache[text] = (tex, width, height)
        return tex, width, height

    def draw(self, window_width, window_height):
        level_name = self.level_names.get(
            self.current_level, f"Nível {self.current_level}"
        )
        entries = [
            ("Moedas:", str(self.coin_count)),
            ("Tempo:", f"{int(self.game_time)}s"),
            ("Distância:", f"{int(self.distance)}m"),
            ("Pecado:", level_name),
        ]

        name_colors = {
            "Moedas:": COLOR_PALETTE[4],  # Green
            "Tempo:": COLOR_PALETTE[5],  # Blue
            "Distância:": COLOR_PALETTE[6],  # Soft blue
            "Pecado:": COLOR_PALETTE[10],  # Red-orange
        }
        value_color = COLOR_PALETTE[12]

        ortho = Matrix44.orthogonal_projection(0, window_width, window_height, 0, -1, 1)
        y_offset = 10

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glUseProgram(self.text_shader)
        glUniformMatrix4fv(
            glGetUniformLocation(self.text_shader, "ortho"),
            1,
            GL_FALSE,
            np.array(ortho, dtype=np.float32),
        )
        glUniform1i(glGetUniformLocation(self.text_shader, "textTex"), 0)

        for name, value in entries:
            tex_name, nw, nh = self._get_text_texture(name)
            tex_value, vw, vh = self._get_text_texture(value)

            x_name = 10
            x_value = x_name + nw + 8
            y = y_offset

            glBindTexture(GL_TEXTURE_2D, tex_name)
            verts_name = np.array(
                [
                    x_name,
                    y,
                    0.0,
                    0.0,
                    x_name + nw,
                    y,
                    1.0,
                    0.0,
                    x_name + nw,
                    y + nh,
                    1.0,
                    1.0,
                    x_name,
                    y + nh,
                    0.0,
                    1.0,
                ],
                dtype=np.float32,
            )
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, verts_name.nbytes, verts_name)
            glBindVertexArray(self.vao)
            glUniform4f(
                glGetUniformLocation(self.text_shader, "color"), *name_colors[name]
            )
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

            glBindTexture(GL_TEXTURE_2D, tex_value)
            verts_value = np.array(
                [
                    x_value,
                    y,
                    0.0,
                    0.0,
                    x_value + vw,
                    y,
                    1.0,
                    0.0,
                    x_value + vw,
                    y + vh,
                    1.0,
                    1.0,
                    x_value,
                    y + vh,
                    0.0,
                    1.0,
                ],
                dtype=np.float32,
            )
            glBufferSubData(GL_ARRAY_BUFFER, 0, verts_value.nbytes, verts_value)
            glUniform4f(glGetUniformLocation(self.text_shader, "color"), *value_color)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

            y_offset += nh + 4  # próxima linha

        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
