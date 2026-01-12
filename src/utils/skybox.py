import numpy as np

def create_cube_vertices(size=1.0):
    s = size
    vertices = [
        # frente
        -s, -s,  s,  s, -s,  s,  s,  s,  s,
        s,  s,  s, -s,  s,  s, -s, -s,  s,
        # trás
        -s, -s, -s, -s,  s, -s,  s,  s, -s,
        s,  s, -s,  s, -s, -s, -s, -s, -s,
        # esquerda
        -s,  s,  s, -s,  s, -s, -s, -s, -s,
        -s, -s, -s, -s, -s,  s, -s,  s,  s,
        # direita
         s,  s,  s,  s, -s, -s,  s,  s, -s,
         s, -s, -s,  s,  s,  s,  s, -s,  s,
        # topo
        -s,  s, -s, -s,  s,  s,  s,  s,  s,
        s,  s,  s,  s,  s, -s, -s,  s, -s,
        # base
        -s, -s, -s,  s, -s, -s,  s, -s,  s,
        s, -s,  s, -s, -s,  s, -s, -s, -s,
    ]
    return np.array(vertices, dtype=np.float32)