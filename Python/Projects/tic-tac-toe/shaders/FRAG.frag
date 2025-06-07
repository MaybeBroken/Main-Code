#version 330

uniform sampler2D p3d_Texture0;

in vec2 texcoord;
in float frame;
in vec4 fragPos;
out vec4 p3d_FragColor;

void main() {
    vec4 color = texture(p3d_Texture0, texcoord);
    p3d_FragColor = color;
}
