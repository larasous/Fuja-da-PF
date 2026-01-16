from OpenGL.GL import *
import os
from PIL import Image


class Model:
    def __init__(self, obj_path):
        # Carrega dados do OBJ
        self.material_groups, self.materials_used, mtl_file = self._load_obj(obj_path)

        # Carrega materiais e texturas
        self.textures = {}
        if mtl_file:
            base_dir = os.path.dirname(obj_path)
            mtl_path = os.path.join(base_dir, mtl_file)
            mats = self._load_mtl(mtl_path)
            self._create_textures(mats, base_dir)

        # Cria VAOs
        self.vaos = {}
        self._create_vaos()

    def _load_obj(self, path: str):
        vertices_raw, texcoords_raw, normals_raw = [], [], []
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

        # Agrupa faces por material
        material_groups = {}
        for face, mat in faces:
            if mat not in material_groups:
                material_groups[mat] = {"vertices": [], "texcoords": [], "normals": []}

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

                    material_groups[mat]["vertices"].extend(vertices_raw[v - 1])
                    if t:
                        material_groups[mat]["texcoords"].extend(texcoords_raw[t - 1])
                    if n:
                        material_groups[mat]["normals"].extend(normals_raw[n - 1])

        return material_groups, materials_used, mtl_file

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
        return materials

    def _create_textures(self, mats, base_dir):
        for mat_name, props in mats.items():
            if "diffuse" in props:
                tex_path = props["diffuse"].replace("\\", "/")
                if not os.path.isabs(tex_path) and not tex_path.startswith("assets/"):
                    tex_path = os.path.join(base_dir, tex_path)
                tex_path = os.path.normpath(tex_path)

                if not os.path.exists(tex_path):
                    print(f"[WARN] Textura não encontrada: {tex_path}")
                else:
                    self.textures[mat_name] = self._load_texture(tex_path)

    def _load_texture(self, path):
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

    def _create_vaos(self):
        for mat, data in self.material_groups.items():
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)

            # VBO de vértices
            vbo_vertices = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
            vertex_data = (GLfloat * len(data["vertices"]))(*data["vertices"])
            glBufferData(
                GL_ARRAY_BUFFER, len(vertex_data) * 4, vertex_data, GL_STATIC_DRAW
            )
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

            # VBO de texcoords
            if data["texcoords"]:
                vbo_texcoords = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
                texcoord_data = (GLfloat * len(data["texcoords"]))(*data["texcoords"])
                glBufferData(
                    GL_ARRAY_BUFFER,
                    len(texcoord_data) * 4,
                    texcoord_data,
                    GL_STATIC_DRAW,
                )
                glEnableVertexAttribArray(1)
                glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

            # VBO de normais
            if data["normals"]:
                vbo_normals = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
                normal_data = (GLfloat * len(data["normals"]))(*data["normals"])
                glBufferData(
                    GL_ARRAY_BUFFER, len(normal_data) * 4, normal_data, GL_STATIC_DRAW
                )
                glEnableVertexAttribArray(2)
                glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)

            glBindVertexArray(0)
            self.vaos[mat] = (vao, len(data["vertices"]) // 3)

    def render(self, shader_program):
        for mat, (vao, count) in self.vaos.items():
            glBindVertexArray(vao)

            if mat in self.textures:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.textures[mat])
                tex_loc = glGetUniformLocation(shader_program.program, "texture1")
                glUniform1i(tex_loc, 0)

            glDrawArrays(GL_TRIANGLES, 0, count)

            if mat in self.textures:
                glBindTexture(GL_TEXTURE_2D, 0)

            glBindVertexArray(0)
