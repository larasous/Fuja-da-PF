#version 330 core
out vec4 FragColor;

uniform float time; // passado pelo seu código Python

void main()
{
    vec3 black  = vec3(0.0, 0.0, 0.0);
    vec3 red    = vec3(0.8, 0.0, 0.0);
    vec3 brown  = vec3(0.4, 0.2, 0.1);

    float t = (sin(time * 2.0) * 0.5) + 0.5;

    vec3 mix1 = mix(black, red, t);

    vec3 finalColor = mix(mix1, brown, t);

    FragColor = vec4(finalColor, 1.0);
}