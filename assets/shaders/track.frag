#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D trackTex;
uniform float scroll;

void main() {
    vec2 scrolledUV = vec2(TexCoord.x, TexCoord.y + scroll);
    FragColor = texture(trackTex, scrolledUV);
}