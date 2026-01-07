#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

out vec4 FragColor;

uniform vec3 objectColor;   // cor base da moeda
uniform vec3 lightColor;    // cor da luz
uniform vec3 lightPos;      // posição da luz
uniform vec3 viewPos;       // posição da câmera
uniform sampler2D texture1; // textura opcional

void main()
{
    // iluminação básica Phong
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(lightPos - FragPos);

    // componente difusa
    float diff = max(dot(norm, lightDir), 0.0);

    // componente especular
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);

    vec3 ambient = 0.2 * lightColor;
    vec3 diffuse = diff * lightColor;
    vec3 specular = spec * lightColor;

    vec3 resultColor = (ambient + diffuse + specular) * objectColor;

    // se tiver textura, multiplica
    vec4 texColor = texture(texture1, TexCoord);
    if(texColor.a > 0.0)
        FragColor = vec4(resultColor, 1.0) * texColor;
    else
        FragColor = vec4(resultColor, 1.0);
}