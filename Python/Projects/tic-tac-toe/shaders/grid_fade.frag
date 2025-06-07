#version 330

uniform vec3 gridCenter;
uniform float fadeDistance;

in vec3 worldPos;

out vec4 fragColor;

void main() {
    float distance = length(worldPos.xy - gridCenter.xy);  // Use 2D distance for grid fading
    float alpha = clamp(1.0 - (distance / fadeDistance), 0.0, 1.0);
    fragColor = vec4(1.0, 1.0, 1.0, alpha);  // White color with fading alpha
}
