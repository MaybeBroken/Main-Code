#version 120

uniform vec2 resolution;

void main() {
    vec2 pos = gl_FragCoord.xy / resolution.xy;

    gl_FragColor = vec4(0.3, 0.5, pos.y, 1.0);
}
