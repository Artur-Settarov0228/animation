from ursina import *
import math

# macOS uchun grafik sozlama
from panda3d.core import loadPrcFileData
loadPrcFileData("", "load-display pandagl")

app = Ursina()

# --- CUSTOM PHONG SHADER (GLSL) ---
phong_shader = Shader(language=Shader.GLSL, 
vertex='''
#version 330
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec3 v_world_pos;
out vec3 v_normal;
out vec2 v_uv;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    v_world_pos = vec3(p3d_ModelMatrix * p3d_Vertex);
    v_normal = normalize(vec3(p3d_ModelMatrix * vec4(p3d_Normal, 0.0)));
    v_uv = p3d_MultiTexCoord0;
}
''',
fragment='''
#version 330
uniform vec3 light_pos;
uniform vec3 cam_pos;
uniform vec4 p3d_Color;
uniform float shininess;
uniform float specular_strength;

in vec3 v_world_pos;
in vec3 v_normal;
in vec2 v_uv;
out vec4 fragColor;

void main() {
    // 1. Ambient (Fon yorug'ligi)
    float ambient = 0.15;

    // 2. Diffuse (Lambert - Tarqoq yorug'lik)
    vec3 light_dir = normalize(light_pos - v_world_pos);
    float diff = max(dot(v_normal, light_dir), 0.0);
    vec3 diffuse = diff * p3d_Color.rgb;

    // 3. Specular (Phong - Yaltiroq nuqta)
    vec3 view_dir = normalize(cam_pos - v_world_pos);
    vec3 reflect_dir = reflect(-light_dir, v_normal);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), shininess);
    vec3 specular = specular_strength * spec * vec3(1.0, 1.0, 1.0);

    vec3 result = (ambient + diffuse + specular);
    fragColor = vec4(result, 1.0);
}
''')

# --- SAHNA ---
Sky(color=color.black)
sun = Entity(model='sphere', color=color.yellow, scale=3, unlit=True)
sun_glow = Entity(model='sphere', scale=3.5, color=color.rgba(255, 255, 0, 50), unlit=True)

# --- SAYYORA KLASSI ---
class CustomPlanet(Entity):
    def __init__(self, name, dist, speed, color_val):
        super().__init__(
            model='sphere',
            color=color_val,
            scale=1.2,
            shader=phong_shader,
            position=(dist, 0, 0)
        )
        self.dist = dist
        self.speed = speed
        self.angle = 0
        
        # Shader parametrlarini yuboramiz
        self.set_shader_input("light_pos", sun.position)
        self.set_shader_input("shininess", 32.0)
        self.set_shader_input("specular_strength", 0.5)

    def update(self):
        # Orbita harakati
        self.angle += time.dt * self.speed
        self.x = math.cos(self.angle) * self.dist
        self.z = math.sin(self.angle) * self.dist
        
        # Har kadrda kamera pozitsiyasini shaderga yangilab turish (Specular uchun muhim)
        self.set_shader_input("cam_pos", camera.world_position)

# --- OBYEKTLARNI YARATISH ---
earth = CustomPlanet("Yer", 8, 0.5, color.blue)
mars = CustomPlanet("Mars", 12, 0.4, color.red)
venus = CustomPlanet("Venera", 5, 0.7, color.orange)

# Kamera sozlamalari
EditorCamera()
camera.z = -30

# Ma'lumot matni
Text(text="Custom GLSL Shader: Phong Model (Diffuse + Specular)", position=(-0.5, 0.45), color=color.green)

app.run()