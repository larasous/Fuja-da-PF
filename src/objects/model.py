from OpenGL.GL import *


class Model:
    def __init__(self, path):
        self.vertices, self.texcoords, self.normals = self._load_obj(path)
        self.vao, self.vbo_vertices, self.vbo_texcoords, self.vbo_normals = (
            self._create_vao()
        )

    def _load_obj(self, path: str):
        vertices_raw = []
        texcoords_raw = []
        normals_raw = []
        faces = []

        with open(path, "r") as file:
            for line in file:
                if line.startswith("v "):
                    parts = line.strip().split()[1:]
                    vertices_raw.append([float(p) for p in parts])
                elif line.startswith("vt "):
                    parts = line.strip().split()[1:]
                    texcoords_raw.append([float(p) for p in parts])
                elif line.startswith("vn "):
                    parts = line.strip().split()[1:]
                    normals_raw.append([float(p) for p in parts])
                elif line.startswith("f "):
                    parts = line.strip().split()[1:]
                    faces.append(parts)

        vertices, texcoords, normals = self._expand_faces(
            vertices_raw, texcoords_raw, normals_raw, faces
        )
        return vertices, texcoords, normals

    def _expand_faces(self, vertices_raw, texcoords_raw, normals_raw, faces):
        vertices = []
        texcoords = []
        normals = []

        for face in faces:
            # triangulação simples: se vier quad, divide em 2 triângulos
            indices = [vert.split("/") for vert in face]
            if len(indices) == 4:
                tri_sets = [indices[:3], [indices[0], indices[2], indices[3]]]
            else:
                tri_sets = [indices]

            for tri in tri_sets:
                for vtn in tri:
                    v = int(vtn[0]) if vtn[0] else 0
                    t = int(vtn[1]) if len(vtn) > 1 and vtn[1] else 0
                    n = int(vtn[2]) if len(vtn) > 2 and vtn[2] else 0

                    vertices.extend(vertices_raw[v - 1])
                    if t:
                        texcoords.extend(texcoords_raw[t - 1])
                    if n:
                        normals.extend(normals_raw[n - 1])

        return vertices, texcoords, normals

    def _create_vao(self):
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

        return vao, vbo_vertices, vbo_texcoords, vbo_normals

    def render(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 3)
        glBindVertexArray(0)
