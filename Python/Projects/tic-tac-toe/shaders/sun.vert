#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform float frame;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 texcoord;

vec3 random3(vec3 st){
    st=vec3(dot(st,vec3(127.1,311.7,74.7)),
    dot(st,vec3(269.5,183.3,246.1)),
    dot(st,vec3(113.5,271.9,124.6)));
    return-1.+2.*fract(sin(st)*43758.5453123);
}

float perlinNoise(vec3 uvw){
    vec3 i=floor(uvw);
    vec3 f=fract(uvw);
    float a=dot(random3(i),f-vec3(0.,0.,0.));
    float b=dot(random3(i+vec3(1.,0.,0.)),f-vec3(1.,0.,0.));
    float c=dot(random3(i+vec3(0.,1.,0.)),f-vec3(0.,1.,0.));
    float d=dot(random3(i+vec3(1.,1.,0.)),f-vec3(1.,1.,0.));
    float e=dot(random3(i+vec3(0.,0.,1.)),f-vec3(0.,0.,1.));
    float f1=dot(random3(i+vec3(1.,0.,1.)),f-vec3(1.,0.,1.));
    float g=dot(random3(i+vec3(0.,1.,1.)),f-vec3(0.,1.,1.));
    float h=dot(random3(i+vec3(1.,1.,1.)),f-vec3(1.,1.,1.));
    vec3 u=f*f*(3.-2.*f);
    return mix(mix(mix(a,b,u.x),mix(c,d,u.x),u.y),
    mix(mix(e,f1,u.x),mix(g,h,u.x),u.y),u.z);
}

void main() {
    float x = p3d_Vertex.x;
    float y = p3d_Vertex.y;
    float z = p3d_Vertex.z;
    float w = p3d_Vertex.w;
    float noise = perlinNoise(vec3(x, y, z)* 0.005 + vec3(frame * 1.2, 0.0, 0.0)) *0.075;
    gl_Position = p3d_ModelViewProjectionMatrix * (vec4(x, y, z, w) + vec4(noise));
    texcoord = p3d_MultiTexCoord0;
}

