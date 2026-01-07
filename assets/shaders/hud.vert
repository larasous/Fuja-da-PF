#version 330 core
layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aUV;

uniform mat4 ortho;   // projeção ortográfica (tela)
uniform vec2 offset;  // posição do quad em pixels

out vec2 TexCoords;

void main() {
    vec2 pos = aPos + offset;            // aplica posição em pixels
    gl_Position = ortho * vec4(pos, 0.0, 1.0);
    TexCoords = aUV;
}
