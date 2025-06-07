#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;

in vec4 p3d_Vertex;

out vec3 worldPos;

void main() {
    worldPos = (p3d_ModelMatrix * p3d_Vertex).xyz;  // Calculate world-space position
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
