from ursina import *
import math
import collections

# macOS grafik xatolarini oldini olish
from panda3d.core import loadPrcFileData
loadPrcFileData("", "load-display pandagl")

app = Ursina()

# --- SOZLAMALAR ---
a = 15  # Katta yarim o'q
b = 10  # Kichik yarim o'q
e = math.sqrt(1 - (b**2 / a**2))  # Ekssentrisitet
c = a * e  # Fokus masofasi (Quyosh shu nuqtada)

# Tezlik tarixini saqlash (Grafik uchun)
speed_history = collections.deque([0]*100, maxlen=100)

# --- QUYOSH (Fokusda joylashgan) ---
sun = Entity(model='sphere', color=color.yellow, scale=3, unlit=True)
sun_glow = Entity(model='sphere', scale=3.5, color=color.rgba(255, 255, 0, 50), unlit=True)
PointLight(parent=sun, color=color.white, range=50)

# --- GRAFIK (UI elementlari) ---
graph_parent = Entity(parent=camera.ui, position=(-0.5, -0.3), scale=(0.5, 0.2))
graph_bg = Entity(parent=graph_parent, model='quad', color=color.black66, scale=(1.1, 1.1), z=0.1)
graph_line = Entity(parent=graph_parent, model=Mesh(vertices=[], mode='line'), color=color.lime)
graph_text = Text(text="Tezlik grafigi: t -> v(t)", parent=graph_parent, y=0.6, scale=1.5)

def update_graph(current_speed):
    speed_history.append(current_speed)
    verts = []
    for i, s in enumerate(speed_history):
        # x: 0 dan 1 gacha, y: tezlikka qarab (normallashtirilgan)
        verts.append(Vec3(i/100, s * 0.1, 0)) 
    graph_line.model.vertices = verts
    graph_line.model.generate()

# --- KEPLER SAYYORASI ---
class KeplerPlanet(Entity):
    def __init__(self):
        super().__init__(model='sphere', color=color.cyan, scale=0.8, collider='sphere')
        self.angle = 0
        self.base_speed = 5.0
        
        # Orbitani chizish
        self.orbit_line = Entity(model=Mesh(vertices=[], mode='line'), color=color.gray)
        steps = 100
        for i in range(steps + 1):
            theta = (i / steps) * math.tau
            # Ellips formulasi (fokus Quyoshda bo'lishi uchun surilgan)
            x = a * math.cos(theta) - c
            z = b * math.sin(theta)
            self.orbit_line.model.vertices.append(Vec3(x, 0, z))
        self.orbit_line.model.generate()

    def update(self):
        # 1. Masofani hisoblash (Quyosh 0,0,0 da)
        # r = a(1-e^2) / (1 + e*cos(theta))
        r = math.sqrt(self.x**2 + self.z**2)
        
        # 2. Keplerning 2-qonuni (Soddalashtirilgan): 
        # Burchak tezligi dTheta/dt = Const / r^2
        # Bu perigeliyda tez, afeliyda sekin harakatni ta'minlaydi
        angular_velocity = (self.base_speed * 10) / (max(r, 1)**2)
        self.angle += angular_velocity * time.dt
        
        # 3. Yangi pozitsiya (Ellips bo'ylab)
        self.x = a * math.cos(self.angle) - c
        self.z = b * math.sin(self.angle)
        
        # 4. Haqiqiy chiziqli tezlikni hisoblash (grafik uchun)
        # v = sqrt( GM * (2/r - 1/a) ) formulasi o'rniga delta masofa ishlatamiz
        current_v = angular_velocity * r
        update_graph(current_v)

planet = KeplerPlanet()

# --- KAMERA ---
EditorCamera()
camera.position = (0, 40, -1)
camera.rotation_x = 90

Sky(color=color.black)
# Yulduzlar
for i in range(200):
    Entity(model='sphere', scale=0.1, color=color.white, 
           position=(random.uniform(-50,50), random.uniform(-10,10), random.uniform(-50,50)), unlit=True)

app.run()