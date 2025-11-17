import OpenGL.GL as gl
from PIL import Image


def load_ui_texture(image_path):
    image = Image.open(image_path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
    img_data = image.tobytes()
    width, height = image.size

    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        width,
        height,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        img_data,
    )

    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    return texture_id, width, height
