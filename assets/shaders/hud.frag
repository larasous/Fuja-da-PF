#version 330 core
in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D textTex;   // textura do texto (RGBA)
uniform vec4 color;          // multiplicador de cor, se quiser tonalizar

void main() {
    vec4 texColor = texture(textTex, TexCoords);
    FragColor = color * texColor;
}