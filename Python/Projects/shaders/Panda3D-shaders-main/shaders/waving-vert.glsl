#version 330

// Vertex inputs
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

// Output to fragment shader
out vec2 texcoord;

// frame time in seconds, since the program started.
uniform float time;

// Uniform inputs
uniform mat4 p3d_ModelViewProjectionMatrix;

void main() {

    vec4 pos = p3d_Vertex;

    pos.y += sin(time + pos.x + pos.z) * 0.5;
    pos.z += cos(time + pos.z + pos.x) * 0.5;

    gl_Position = p3d_ModelViewProjectionMatrix * pos;
    texcoord = p3d_MultiTexCoord0;
}