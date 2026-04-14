from ursina import *
import math
import random

# macOS grafik xatolarini oldini olish
from panda3d.core import loadPrcFileData
loadPrcFileData("", "load-display pandagl")

app = Ursina()

# --- INTERFEYS ---
info_panel = WindowPanel(
    title='Sayyora Ma\'lumotlari',
    content=(
        Text(id='name_text', text='Nomi: --', color=color.cyan),
        Text(id='speed_text', text='Tezligi: --'),
        Text(id='dist_text', text='Masofasi: --'),
    ),
    enabled=False,
    popup=True,
    x=0.4, y=0.3,
    color=color.black66
)

def show_info(p_name, p_speed, p_dist):
    info_panel.enabled = True
    info_panel.content[0].text = f'Nomi: {p_name}'
    info_panel.content[1].text = f'Tezligi: {p_speed} km/s'
    info_panel.content[2].text = f'Masofasi: {p_dist} mln km'

# --- YULDUZLAR (Koinot foni) ---
def create_stars():
    for i in range(1500): # Yulduzlar soni ko'paytirildi
        pos = Vec3(
            random.uniform(-150, 150),
            random.uniform(-150, 150),
            random.uniform(-150, 150)
        )
        if pos.length() < 50: pos *= 2 
        
        Entity(
            model='sphere',
            position=pos,
            scale=random.uniform(0.05, 0.2),
            color=color.white,
            unlit=True 
        )

create_stars()
Sky(color=color.black)

# --- QUYOSH (YORQIN SARIQ) ---
sun = Entity(
    model='sphere', 
    color=color.yellow,   # Sof sariq rang
    scale=5, 
    collider='sphere',
    unlit=True,           # Yorug'likdan oqarib ketmasligi uchun
)

# Quyosh atrofidagi nur (Halo effekti)
sun_glow = Entity(
    model='sphere', 
    scale=6, 
    color=color.rgba(255, 255, 0, 40), # Shaffof sariq tuman
    double_sided=True,
    unlit=True
)

# Sayyoralarni yoritish uchun markaziy nur
sun_light = PointLight(parent=sun, color=color.white, range=60)
sun.on_click = lambda: show_info("Quyosh", "0", "0")

# --- SAYYORA KLASSI ---
class Planet(Entity):
    def __init__(self, name, distance, speed, size, color_val):
        super().__init__(
            model='sphere',
            color=color_val,
            scale=size,
            collider='sphere'
        )
        self.name = name
        self.distance = distance
        self.speed = speed
        self.angle = random.uniform(0, math.tau)

        # Orbita chizig'i
        self.orbit_line = Entity(model=Mesh(vertices=[], mode='line'), color=color.rgba(255,255,255,40))
        steps = 120
        for i in range(steps + 1):
            theta = (i / steps) * math.tau
            self.orbit_line.model.vertices.append(Vec3(math.cos(theta)*distance, 0, math.sin(theta)*distance))
        self.orbit_line.model.generate()

    def update(self):
        self.angle += time.dt * self.speed * 0.2
        self.x = math.cos(self.angle) * self.distance
        self.z = math.sin(self.angle) * self.distance
        self.rotation_y += 40 * time.dt

    def on_click(self):
        show_info(self.name, self.speed, self.distance)
        self.animate_scale(self.scale * 1.3, duration=0.1)
        invoke(setattr, self, 'scale', self.scale, delay=0.1)

# --- SAYYORALAR ---
Planet("Merkuriy", 8, 3.5, 0.6, color.light_gray)
Planet("Venera", 12, 2.5, 0.9, color.orange)
Planet("Yer", 16, 1.8, 1.0, color.blue)
Planet("Mars", 20, 1.2, 0.8, color.red)
Planet("Yupiter", 28, 0.7, 2.5, color.brown)
# Saturnga halqa qo'shamiz
saturn = Planet("Saturn", 36, 0.5, 2.1, color.gold)
saturn_ring = Entity(parent=saturn, model='torus', scale=(1.5, 0.05, 1.5), color=color.rgba(200, 200, 100, 150), rotation_x=90)

# --- KAMERA ---
ec = EditorCamera()
ec.y = 20
ec.z = -50
ec.rotation_x = 30

def input(key):
    if key == 'left mouse down' and not mouse.hovered_entity:
        info_panel.enabled = False

app.run()