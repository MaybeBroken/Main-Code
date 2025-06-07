#version 330

uniform sampler2D p3d_Texture0;
uniform float density;

in vec2 texcoord;
in float frame;
in vec4 fragPos;

out vec4 p3d_FragColor;

float getHologramNoise(float x,float y){
    return fract(sin(dot(vec2(x,y)*frame,vec2(12.9898,78.233)))*43758.5453)*(density+.5);
}

void main(){
    vec4 color=texture(p3d_Texture0,texcoord);
    float hologramEffect=getHologramNoise(fragPos.x,fragPos.y);
    float roundedHologramEffect=hologramEffect>.5?1.:0.;
    p3d_FragColor=vec4(.4,.75,1.,color.a*roundedHologramEffect);
}
