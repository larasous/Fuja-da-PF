from OpenGL.GL import *


class Model:
    def __init__(self, path):
        self.vertices, self.texcoords, self.normals = self._load_obj(path)
        self.vao = self._create_vao()

    def _load_obj(self, path):
        # retorna listas de vértices SEM aplicar transformações
        pass

    def _create_vao(self):
        # cria buffers
        pass

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
