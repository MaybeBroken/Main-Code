#version 330

uniform sampler2D p3d_Texture0;

in vec2 texcoord;
in float frame;
in vec4 fragPos;
out vec4 p3d_FragColor;

void main(){
    vec4 color=texture(p3d_Texture0,texcoord);
    
    // Set edge thickness (in UV space)
    float edge=.05;
    
    // If near any edge, blend with red
    float edgeFactor=smoothstep(0.,edge,texcoord.x)
    *smoothstep(0.,edge,1.-texcoord.x)
    *smoothstep(0.,edge,texcoord.y)
    *smoothstep(0.,edge,1.-texcoord.y);
    
    // edgeFactor is 1.0 in the center, 0.0 at the edge
    float edgeMask=1.-edgeFactor;
    
    // Red color for edge, with transparency
    vec4 red=vec4(1.,0.,0.,.5);// 0.5 alpha for semi-transparent red
    
    // Blend red at the edges, original color elsewhere
    vec4 result=mix(color,red,edgeMask);
    
    // Make fully transparent at the very edge (optional, for a fade-out)
    float alphaFade=smoothstep(0.,.01,min(min(texcoord.x,1.-texcoord.x),min(texcoord.y,1.-texcoord.y)));
    result.a*=alphaFade;
    
    p3d_FragColor=result;
}
