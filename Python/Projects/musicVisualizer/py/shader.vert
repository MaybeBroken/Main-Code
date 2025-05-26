#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;

uniform float Frame;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 texCoord;
out float frame;
out vec4 fragPos;

void main() {
    float x = p3d_Vertex.x;
    float y = p3d_Vertex.y;
    float z = p3d_Vertex.z;
    float w = p3d_Vertex.w;
    gl_Position = p3d_ModelViewMatrix * vec4(x, y, z, w);
    texCoord = p3d_MultiTexCoord0;
    frame = Frame;
    fragPos = vec4(x, y, z, w);
}
