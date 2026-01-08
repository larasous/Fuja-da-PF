from pyrr import Matrix44
from src.constants import metrics


def create_projection_matrix(
    fov=45.0,
    width=metrics.WINDOW_WIDTH,
    height=metrics.WINDOW_HEIGHT,
    near=0.1,
    far=100.0,
):
    """
    Cria uma matriz de projeção em perspectiva.

    Args:
        fov (float): campo de visão em graus.
        width (int): largura da janela.
        height (int): altura da janela.
        near (float): plano de corte próximo.
        far (float): plano de corte distante.

    Returns:
        Matrix44: matriz de projeção.
    """
    aspect_ratio = width / height
    return Matrix44.perspective_projection(fov, aspect_ratio, near, far)
