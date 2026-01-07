#version 330 core
in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D textTex;   // textura do texto (RGBA)
uniform vec3 color;          // multiplicador de cor, se quiser tonalizar

void main() {
    vec4 texColor = texture(textTex, TexCoords);
    // Premultiply opcional: assume texto com fundo transparente
    FragColor = vec4(color, 1.0) * texColor;
}