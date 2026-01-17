#version 330 core

in vec3 FragPos;
in vec3 Normal;

out vec4 FragColor;

uniform vec3 objectColor;  // cor da moeda (Kd do MTL)
uniform vec3 lightDir;     // direção da luz no mundo
uniform vec3 lightColor;   // cor da luz
uniform vec3 viewPos;      // posição da câmera no mundo

void main()
{
    // normalizada
    vec3 norm = normalize(Normal);

    // direção da luz (invertida porque lightDir aponta de onde vem a luz)
    vec3 L = normalize(-lightDir);

    // componente difusa
    float diff = max(dot(norm, L), 0.0);

    // direção da câmera
    vec3 V = normalize(viewPos - FragPos);

    // reflexão da luz
    vec3 R = reflect(-L, norm);

    // componente especular
    float spec = pow(max(dot(V, R), 0.0), 32.0);

    // componentes da iluminação
    vec3 ambient  = 0.1 * lightColor;
    vec3 diffuse  = 0.6 * diff * lightColor;
    vec3 specular = 0.3 * spec * lightColor;

    // usa apenas a cor do material (sem textura)
    vec3 baseColor = objectColor;

    // resultado final
    vec3 result = (ambient + diffuse + specular) * baseColor;

    FragColor = vec4(result, 1.0);
}