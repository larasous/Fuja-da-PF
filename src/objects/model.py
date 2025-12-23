from OpenGL.GL import *


class Model:
    def __init__(self, path):
        self.vertices, self.texcoords, self.normals = self._load_obj(path)
        self.vao = self._create_vao()

    def _load_obj(self, path: str):
        # retorna listas de vértices SEM aplicar transformações
        with open(path, "r") as file:
            line = file.readline()
            vertices = []
            texcoords = []
            normals = []
            faces = []
            while line:
                if line.startswith("v "):
                    parts = line.strip().split()[1:]
                    vertices.extend([float(p) for p in parts])
                elif line.startswith("vt "):
                    parts = line.strip().split()[1:]
                    texcoords.extend([float(p) for p in parts])
                elif line.startswith("vn "):
                    parts = line.strip().split()[1:]
                    normals.extend([float(p) for p in parts])
                elif line.startswith("f "):
                    parts = line.strip().split()[1:]
                    faces.extend(parts)
                line = file.readline()
                print(line)
            return vertices, texcoords, normals

    def _create_vao(self):
        # cria buffers
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        # VBO de vértices
        vbo_vertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
        vertex_data = (GLfloat * len(self.vertices))(*self.vertices)
        glBufferData(GL_ARRAY_BUFFER, len(vertex_data) * 4, vertex_data, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # VBO de coordenadas de textura
        vbo_texcoords = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
        texcoord_data = (GLfloat * len(self.texcoords))(*self.texcoords)
        glBufferData(
            GL_ARRAY_BUFFER, len(texcoord_data) * 4, texcoord_data, GL_STATIC_DRAW
        )
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        # VBO de normais
        vbo_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
        normal_data = (GLfloat * len(self.normals))(*self.normals)
        glBufferData(GL_ARRAY_BUFFER, len(normal_data) * 4, normal_data, GL_STATIC_DRAW)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        return vao

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
