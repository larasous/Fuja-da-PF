from src.utils.colors import hex_to_rgba

HEX_PALETTE = [
    "#1a1a1a",  # Dark gray
    "#34568B",  # Blue
    "#FF6F61",  # Coral
    "#6B5B95",  # Purple
    "#88B04B",  # Green
    "#F7CAC9",  # Pink
    "#92A8D1",  # Soft blue
    "#955251",  # Burgundy
    "#B565A7",  # Lavender
    "#009B77",  # Teal
    "#DD4124",  # Red-orange
    "#45B8AC",  # Aqua
    "#EFC050",  # Yellow
    "#5B5EA6",  # Indigo
]

COLOR_PALETTE = [hex_to_rgba(color) for color in HEX_PALETTE]
