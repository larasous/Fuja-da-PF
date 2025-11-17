def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> tuple:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Hex color must be in format #RRGGBB")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b, alpha)


def lerp_color(c1, c2, t):
    """Interpola entre duas cores RGBA com fator t (0 a 1)."""
    return tuple(c1[i] + (c2[i] - c1[i]) * t for i in range(4))
