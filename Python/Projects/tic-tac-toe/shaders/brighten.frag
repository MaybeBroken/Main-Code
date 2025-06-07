#version 330

uniform sampler2D p3d_Texture0;
uniform float threshold;
uniform float boost;

in vec2 texcoord;
in vec4 fragPos;

out vec4 p3d_FragColor;

void main(){
    vec4 texColor=texture(p3d_Texture0,texcoord);
    
    // Check if alpha is 100% (1.0)
    if(texColor.a==1.){
        // Boost dark areas more aggressively while keeping bright areas the same
        float brightness=dot(texColor.rgb,vec3(.299,.587,.114));// Grayscale brightness
        float boostFactor=smoothstep(0.,threshold,brightness);// Apply a steeper curve to dark areas
        
        vec3 adjustedColor=mix(texColor.rgb*boost,texColor.rgb,boostFactor);// Boost only dark parts more
        adjustedColor=clamp(adjustedColor,0.,1.);// Ensure colors remain in valid range
        p3d_FragColor=vec4(adjustedColor,texColor.a);
    }else{
        // Scale alpha to 50% or below if it's not 100%
        float scaledAlpha=texColor.a*.5;
        p3d_FragColor=vec4(texColor.rgb,scaledAlpha);
    }
}
