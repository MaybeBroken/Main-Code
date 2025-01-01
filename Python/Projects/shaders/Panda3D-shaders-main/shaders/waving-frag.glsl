#version 330

// fragment-pixel output color
out vec4 outColor;

// texture coordinates input from the vertex shader
in vec2 texcoord;

uniform sampler2D p3d_Texture0;

void main() {

    outColor = texture(p3d_Texture0, texcoord);
}