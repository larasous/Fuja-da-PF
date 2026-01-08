#version 330 core
out vec4 FragColor;

in vec2 TexCoord;          // Recebe coordenadas do vertex shader
uniform sampler2D texture1; // Textura difusa

void main()
{
    FragColor = texture(texture1, TexCoord);
}