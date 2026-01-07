import pygame
import numpy as np
from OpenGL.GL import *
from pyrr import Matrix44
from src.constants import metrics

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
        self.level_thresholds = {1:10,2:20,3:30,4:40,5:50,6:60,7:70}
        self.level_names = {1:"Preguiça",2:"Gula",3:"Luxúria",4:"Avareza",5:"Ira",6:"Inveja",7:"Orgulho"}
        self.timer_active = False

        # recursos de render
        self.text_shader = text_shader_program
        self.text_tex = glGenTextures(1)
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        # quad unitário em pixels (será escalado pelo tamanho do texto)
        # aPos (x,y) em pixels, aUV (u,v)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        # buffer vazio inicial; vamos atualizar por frame com glBufferSubData
        glBufferData(GL_ARRAY_BUFFER, 16 * 4, None, GL_DYNAMIC_DRAW)  # 4 vértices * (x,y,u,v) * 4 bytes

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * 4, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        indices = np.array([0,1,2, 2,3,0], dtype=np.uint32)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def start_timer(self): self.timer_active = True
    def stop_timer(self): self.timer_active = False

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
        level_name = self.level_names.get(self.current_level, f"Nível {self.current_level}")
        print(f"Avançou para o nível {level_name}!")

    def _update_text_texture(self, text):
        surface = self.font.render(text, True, (255, 255, 255))
        width, height = surface.get_size()
        data = pygame.image.tostring(surface, "RGBA", True)

        glBindTexture(GL_TEXTURE_2D, self.text_tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        return width, height

    def draw(self, window_width, window_height):
        level_name = self.level_names.get(self.current_level, f"Nível {self.current_level}")
        entries = [
            ("Moedas:", str(self.coin_count)),
            ("Tempo:", f"{self.game_time:.2f}s"),
            ("Distância:", f"{self.distance:.1f}m"),
            ("Pecado:", level_name)
        ]

        # cores em RGB normalizado (0.0–1.0)
        name_colors = {
            "Moedas:":    (0.0, 1.0, 0.0),  # verde
            "Tempo:":     (0.2, 0.6, 1.0),  # azul
            "Distância:": (0.2, 0.6, 1.0),  # azul
            "Pecado:":    (1.0, 0.2, 0.2)   # vermelho
        }
        value_color = (1.0, 0.6, 0.0)       # laranja

        # projeção ortográfica (uma vez por draw)
        ortho = Matrix44.orthogonal_projection(0, window_width, 0, window_height, -1, 1)

        y_offset = window_height - 10  # começa do topo

        # estado GL para overlay
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glUseProgram(self.text_shader)
        glUniformMatrix4fv(glGetUniformLocation(self.text_shader, "ortho"), 1,
                        GL_FALSE, np.array(ortho, dtype=np.float32))
        glUniform1i(glGetUniformLocation(self.text_shader, "textTex"), 0)

        for name, value in entries:
            # superfícies pygame
            name_surface = self.font.render(name, True, (255, 255, 255))
            value_surface = self.font.render(value, True, (255, 255, 255))

            name_w, name_h = name_surface.get_size()
            value_w, value_h = value_surface.get_size()

            name_data = pygame.image.tostring(name_surface, "RGBA", False)
            value_data = pygame.image.tostring(value_surface, "RGBA", False)

            # posição
            x_name = 10
            x_value = x_name + name_w + 8  # pequeno espaçamento
            y = y_offset - name_h
            y_offset = y  # próxima linha parte daqui

            # desenha nome
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.text_tex)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, name_w, name_h, 0,
                        GL_RGBA, GL_UNSIGNED_BYTE, name_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            verts_name = np.array([
                x_name,          y+name_h,   0.0, 0.0,
                x_name+name_w,   y+name_h,   1.0, 0.0,
                x_name+name_w,   y,          1.0, 1.0,
                x_name,          y,          0.0, 1.0
            ], dtype=np.float32)

            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferSubData(GL_ARRAY_BUFFER, 0, verts_name.nbytes, verts_name)

            glBindVertexArray(self.vao)
            glUniform3f(glGetUniformLocation(self.text_shader, "color"), *name_colors[name])
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

            # desenha valor (laranja)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, value_w, value_h, 0,
                        GL_RGBA, GL_UNSIGNED_BYTE, value_data)

            verts_value = np.array([
                x_value,          y+value_h,  0.0, 0.0,
                x_value+value_w,  y+value_h,  1.0, 0.0,
                x_value+value_w,  y,          1.0, 1.0,
                x_value,          y,          0.0, 1.0
            ], dtype=np.float32)

            glBufferSubData(GL_ARRAY_BUFFER, 0, verts_value.nbytes, verts_value)
            glUniform3f(glGetUniformLocation(self.text_shader, "color"), *value_color)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # limpa estado
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)