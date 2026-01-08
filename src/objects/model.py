from OpenGL.GL import *
from PIL import Image
import os


class Model:
    def __init__(self, obj_path):
        self.vertices, self.texcoords, self.normals, self.materials_used, mtl_file = (
            self._load_obj(obj_path)
        )

        self.vao, self.vbo_vertices, self.vbo_texcoords, self.vbo_normals = (
            self._create_vao()
        )

        # Carrega materiais automaticamente
        self.textures = {}
        if mtl_file:
            base_dir = os.path.dirname(obj_path)
            mtl_path = os.path.join(base_dir, mtl_file)
            mats = self._load_mtl(mtl_path)
            for mat_name, props in mats.items():
                if "diffuse" in props:
                    tex_path = props["diffuse"]

                    # Corrige duplicação de caminho
                    if not os.path.isabs(tex_path):
                        if not tex_path.startswith(
                            "assets/"
                        ) and not tex_path.startswith("assets\\"):
                            tex_path = os.path.join(base_dir, tex_path)

                    tex_path = os.path.normpath(tex_path)

                    self.textures[mat_name] = self._load_texture(tex_path)

        # Define material atual (primeiro encontrado)
        self.current_material = None
        if self.materials_used and self.textures:
            for m in self.materials_used:
                if m in self.textures:
                    self.current_material = m
                    break

    def _load_obj(self, path: str):
        vertices_raw = []
        texcoords_raw = []
        normals_raw = []
        faces = []
        materials_used = []
        mtl_file = None

        with open(path, "r") as file:
            current_material = None
            for line in file:
                if line.startswith("mtllib "):
                    mtl_file = line.strip().split()[1]
                elif line.startswith("v "):
                    parts = line.strip().split()[1:]
                    vertices_raw.append([float(p) for p in parts])
                elif line.startswith("vt "):
                    parts = line.strip().split()[1:]
                    texcoords_raw.append([float(p) for p in parts])
                elif line.startswith("vn "):
                    parts = line.strip().split()[1:]
                    normals_raw.append([float(p) for p in parts])
                elif line.startswith("usemtl "):
                    current_material = line.strip().split()[1]
                    materials_used.append(current_material)
                elif line.startswith("f "):
                    parts = line.strip().split()[1:]
                    faces.append((parts, current_material))

        vertices, texcoords, normals = self._expand_faces(
            vertices_raw, texcoords_raw, normals_raw, faces
        )
        return vertices, texcoords, normals, materials_used, mtl_file

    def _load_mtl(self, path):
        materials = {}
        current = None
        with open(path, "r") as f:
            for line in f:
                if line.startswith("newmtl"):
                    current = line.split()[1]
                    materials[current] = {}
                elif line.startswith("map_Kd") and current:
                    tex_path = line.split()[1]
                    materials[current]["diffuse"] = tex_path
                elif line.startswith("map_Bump") and current:
                    tex_path = line.split()[-1]
                    materials[current]["normal"] = tex_path
        return materials

    def _load_texture(self, path):
        from PIL import Image

        img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM)
        img_data = img.convert("RGBA").tobytes()
        width, height = img.size

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data,
        )

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        return tex_id

    def _expand_faces(self, vertices_raw, texcoords_raw, normals_raw, faces):
        vertices = []
        texcoords = []
        normals = []

        for face, mat in faces:
            # face já é uma lista de strings, então cada vert é "v/t/n"
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

        # VBO de vértices (location = 0)
        vbo_vertices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
        vertex_data = (GLfloat * len(self.vertices))(*self.vertices)
        glBufferData(GL_ARRAY_BUFFER, len(vertex_data) * 4, vertex_data, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # VBO de coordenadas de textura (location = 1)
        vbo_texcoords = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
        texcoord_data = (GLfloat * len(self.texcoords))(*self.texcoords)
        glBufferData(
            GL_ARRAY_BUFFER, len(texcoord_data) * 4, texcoord_data, GL_STATIC_DRAW
        )
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        # VBO de normais (location = 2)
        vbo_normals = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
        normal_data = (GLfloat * len(self.normals))(*self.normals)
        glBufferData(GL_ARRAY_BUFFER, len(normal_data) * 4, normal_data, GL_STATIC_DRAW)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        return vao, vbo_vertices, vbo_texcoords, vbo_normals

    def render(self, shader_program):
        glBindVertexArray(self.vao)

        if self.current_material and self.current_material in self.textures:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.textures[self.current_material])

            # Passa o uniform "texture1" para o fragment shader
            tex_loc = glGetUniformLocation(shader_program.program, "texture1")
            glUniform1i(tex_loc, 0)

        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices) // 3)

        if self.current_material and self.current_material in self.textures:
            glBindTexture(GL_TEXTURE_2D, 0)

        glBindVertexArray(0)
