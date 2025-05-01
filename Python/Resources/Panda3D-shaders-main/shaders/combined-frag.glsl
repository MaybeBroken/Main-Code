#version 330

// window resolution
uniform vec2 resolution;

// fragment-pixel output color
out vec4 outColor;

// vignette constants
const float outerRadius = 0.65;
const float innerRadius = 0.3;
const float vignette_intensity = 0.6;

// mix intensity-weight
const float mix_intensity = 0.55;


void main() {
    // vertical gradient
    vec2 pos = gl_FragCoord.xy / resolution;

    // vignette
    vec4 color = vec4(1.0);
    vec2 relativePosition = gl_FragCoord.xy / resolution - 0.5;
    float len = length(relativePosition);
    float vignette = smoothstep(outerRadius, innerRadius, len);
    color.rgb = mix(color.rgb, color.rgb * vignette, vignette_intensity);

    // combining-mixing the gradient with vignette
    color.rgb = mix(vec3(0.3, 0.5, pos.y), color.rgb, mix_intensity);
    outColor = color;
}