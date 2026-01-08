#version 330 core

layout(location = 0) in vec3 aPos;      // posição do vértice
layout(location = 1) in vec3 aNormal;   // normal
layout(location = 2) in vec2 aTexCoord; // coordenada de textura

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    // posição no mundo
    FragPos = vec3(model * vec4(aPos, 1.0));

    // normais transformadas corretamente
    Normal = mat3(transpose(inverse(model))) * aNormal;

    // passa UV
    TexCoord = aTexCoord;

    // posição final na tela
    gl_Position = projection * view * vec4(FragPos, 1.0);
}