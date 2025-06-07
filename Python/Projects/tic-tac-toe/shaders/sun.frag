#version 330

uniform sampler2D p3d_Texture0;
uniform float frame;

in vec2 texcoord;
in vec4 fragPos;

out vec4 p3d_FragColor;

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

void main(){
    vec2 uv=texcoord*10.;
    vec3 uvw1=vec3(uv,frame*.25);
    vec3 uvw2=vec3(uv.yx,frame*.35);
    vec3 uvw3=vec3(uv*1.5,frame*.15);
    
    float noise1=perlinNoise(uvw1)+perlinNoise(uvw1*2.)*.5+perlinNoise(uvw1*4.)*.25;
    float noise2=perlinNoise(uvw2)+perlinNoise(uvw2*2.)*.5+perlinNoise(uvw2*4.)*.25;
    float noise3=perlinNoise(uvw3)+perlinNoise(uvw3*2.)*.5+perlinNoise(uvw3*4.)*.25;
    
    vec3 color1=vec3(noise1,noise1*.2,noise1*.03)*.8+vec3(1.,.5098,.5098)*.2;
    vec3 color2=vec3(noise2,noise2*.2,noise2*.03)*.6+vec3(.8,.4,.4)*.2;
    vec3 color3=vec3(noise3,noise3*.2,noise3*.03)*.4+vec3(.6,.3,.3)*.2;
    
    vec3 finalColor=color1+color2+color3;
    finalColor=finalColor*vec3(.8,.5,.5);
    p3d_FragColor=vec4(finalColor*2,1)+vec4(.4314,0.,0.,0.);
}
