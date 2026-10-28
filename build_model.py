"""
Smart Flood — Procedural GLB Model Generator

Membuat model 3D Smart Flood dan menyimpannya sebagai
smart_flood.glb di direktori yang sama dengan script ini.

Dependensi:
    pip install Pillow
"""

import io
import json
import math
import os
import pathlib
import random
import struct

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 1. INISIALISASI DATA GLTF DAN BUFFER
# ============================================================

P = pathlib.Path(__file__).parent

D = {
    "asset": {
        "version": "2.0",
        "generator": "Smart Flood procedural prototype",
    },
    "scene": 0,
    "scenes": [{"nodes": [0]}],
    "nodes": [{"name": "SmartFlood", "children": []}],
    "meshes": [],
    "materials": [],
    "accessors": [],
    "bufferViews": [],
    "buffers": [],
}

buf = bytearray()
mats = {}
cache = {}


# ============================================================
# 2. MATERIAL DAN WARNA
# ============================================================

def mat(name, color, metal=0, rough=0.65):
    """Membuat material PBR berdasarkan kode warna hexadecimal."""
    rgb = [
        int(color[i:i + 2], 16) / 255
        for i in (0, 2, 4)
    ]

    mats[name] = len(D["materials"])

    D["materials"].append({
        "name": name,
        "pbrMetallicRoughness": {
            "baseColorFactor": rgb + [1],
            "metallicFactor": metal,
            "roughnessFactor": rough,
        },
    })


MATERIAL_COLORS = [
    ("base", "153449"),
    ("soil", "88775d"),
    ("grass", "70a57b"),
    ("water", "158fba"),
    ("concrete", "b5c3c7"),
    ("white", "e5edf0"),
    ("black", "17242d"),
    ("pcb", "176c78"),
    ("redpcb", "aa3046"),
    ("gold", "d9b265"),
    ("green", "25b76b"),
    ("yellow", "ffc53c"),
    ("red", "f45456"),
]

for name, color in MATERIAL_COLORS:
    mat(name, color)

mat("metal", "a9bbc7", metal=0.75, rough=0.3)


# ============================================================
# 3. ACCESSOR DAN GEOMETRI DASAR
# ============================================================

def acc(vals, typ):
    """Menyimpan data vertex ke buffer dan membuat accessor GLTF."""
    flat = [value for row in vals for value in row]
    offset = len(buf)

    buf.extend(
        struct.pack("<" + "f" * len(flat), *flat)
    )

    view_index = len(D["bufferViews"])

    D["bufferViews"].append({
        "buffer": 0,
        "byteOffset": offset,
        "byteLength": len(flat) * 4,
        "target": 34962,
    })

    accessor = {
        "bufferView": view_index,
        "componentType": 5126,
        "count": len(vals),
        "type": typ,
        "min": [
            min(row[i] for row in vals)
            for i in range(len(vals[0]))
        ],
        "max": [
            max(row[i] for row in vals)
            for i in range(len(vals[0]))
        ],
    }

    D["accessors"].append(accessor)

    return len(D["accessors"]) - 1


def geom(kind):
    """Membuat geometri kotak atau silinder."""
    vertices = []
    normals = []

    def tri(a, b, c, normal):
        vertices.extend([a, b, c])
        normals.extend([normal] * 3)

    if kind == "box":
        faces = [
            ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
            ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
            ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
            ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
            ((0, 0, -1), (0, 1, 0), (1, 0, 0)),
        ]

        for normal, u, v in faces:
            points = [
                tuple(
                    (normal[i] + a * u[i] + b * v[i]) * 0.5
                    for i in range(3)
                )
                for a, b in [
                    (-1, -1),
                    (1, -1),
                    (1, 1),
                    (-1, 1),
                ]
            ]

            tri(points[0], points[1], points[2], normal)
            tri(points[0], points[2], points[3], normal)

    else:
        for j in range(32):
            a = j * math.tau / 32
            b = (j + 1) * math.tau / 32

            x, z = math.cos(a), math.sin(a)
            X, Z = math.cos(b), math.sin(b)

            normal = (
                math.cos((a + b) / 2),
                0,
                math.sin((a + b) / 2),
            )

            tri(
                (x, -0.5, z),
                (x, 0.5, z),
                (X, 0.5, Z),
                normal,
            )

            tri(
                (x, -0.5, z),
                (X, 0.5, Z),
                (X, -0.5, Z),
                normal,
            )

            tri(
                (0, 0.5, 0),
                (X, 0.5, Z),
                (x, 0.5, z),
                (0, 1, 0),
            )

            tri(
                (0, -0.5, 0),
                (x, -0.5, z),
                (X, -0.5, Z),
                (0, -1, 0),
            )

    return (
        acc(vertices, "VEC3"),
        acc(normals, "VEC3"),
    )


g = {
    kind: geom(kind)
    for kind in ["box", "cyl"]
}


# ============================================================
# 4. FUNGSI GROUP DAN OBJECT
# ============================================================

def group(name, pos=(0, 0, 0), parent=0):
    """Membuat grup node untuk mengelompokkan komponen."""
    index = len(D["nodes"])

    D["nodes"].append({
        "name": name,
        "translation": list(pos),
        "children": [],
    })

    D["nodes"][parent]["children"].append(index)

    return index


def obj(
    name,
    pos,
    size,
    material,
    kind="box",
    parent=0,
    rx=0,
):
    """Membuat objek 3D dengan posisi, ukuran, dan material."""
    key = (kind, material)

    if key not in cache:
        cache[key] = len(D["meshes"])

        position_accessor, normal_accessor = g[kind]

        D["meshes"].append({
            "primitives": [{
                "attributes": {
                    "POSITION": position_accessor,
                    "NORMAL": normal_accessor,
                },
                "material": mats[material],
            }],
        })

    node = {
        "name": name,
        "mesh": cache[key],
        "translation": list(pos),
        "scale": list(size),
    }

    if rx:
        node["rotation"] = [
            math.sin(rx / 2),
            0,
            0,
            math.cos(rx / 2),
        ]

    index = len(D["nodes"])
    D["nodes"].append(node)
    D["nodes"][parent]["children"].append(index)

    return index


# ============================================================
# 5. TEKSTUR DAN LABEL KOMPONEN
# ============================================================

D["images"] = []
D["textures"] = []

D["samplers"] = [{
    "magFilter": 9729,
    "minFilter": 9729,
    "wrapS": 33071,
    "wrapT": 33071,
}]


def mesh(name, vertices, normals, material, parent=0):
    """Membuat mesh khusus dan memasukkannya ke dalam grup."""
    position_accessor = acc(vertices, "VEC3")
    normal_accessor = acc(normals, "VEC3")

    mesh_index = len(D["meshes"])

    D["meshes"].append({
        "name": name,
        "primitives": [{
            "attributes": {
                "POSITION": position_accessor,
                "NORMAL": normal_accessor,
            },
            "material": mats[material],
        }],
    })

    node_index = len(D["nodes"])

    D["nodes"].append({
        "name": name,
        "mesh": mesh_index,
    })

    D["nodes"][parent]["children"].append(node_index)


def label(text, pos, w, h, bg, parent=0):
    """Membuat label gambar bertekstur pada model 3D."""
    image = Image.new("RGB", (768, 192), "#" + bg)
    draw = ImageDraw.Draw(image)

    font_path = os.environ.get(
        "FLOOD_FONT",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    )

    if pathlib.Path(font_path).exists():
        font = ImageFont.truetype(font_path, 65)
    else:
        font = ImageFont.load_default(size=65)

    bounds = draw.textbbox((0, 0), text, font=font)

    draw.text(
        (
            (768 - bounds[2]) / 2,
            (192 - (bounds[3] - bounds[1])) / 2 - bounds[1],
        ),
        text,
        font=font,
        fill="white",
    )

    stream = io.BytesIO()
    image.save(stream, format="PNG")
    image_data = stream.getvalue()

    buf.extend(b"\x00" * (-len(buf) % 4))
    offset = len(buf)
    buf.extend(image_data)

    view_index = len(D["bufferViews"])

    D["bufferViews"].append({
        "buffer": 0,
        "byteOffset": offset,
        "byteLength": len(image_data),
    })

    buf.extend(b"\x00" * (-len(buf) % 4))

    texture_index = len(D["textures"])

    D["images"].append({
        "bufferView": view_index,
        "mimeType": "image/png",
    })

    D["textures"].append({
        "source": texture_index,
        "sampler": 0,
    })

    material_index = len(D["materials"])

    D["materials"].append({
        "name": "Label_" + text,
        "pbrMetallicRoughness": {
            "baseColorTexture": {
                "index": texture_index,
            },
            "metallicFactor": 0,
            "roughnessFactor": 1,
        },
    })

    vertices = [
        (-w / 2, -h / 2, 0),
        (w / 2, -h / 2, 0),
        (w / 2, h / 2, 0),
        (-w / 2, -h / 2, 0),
        (w / 2, h / 2, 0),
        (-w / 2, h / 2, 0),
    ]

    uv = [
        (0, 1),
        (1, 1),
        (1, 0),
        (0, 1),
        (1, 0),
        (0, 0),
    ]

    mesh_index = len(D["meshes"])

    D["meshes"].append({
        "primitives": [{
            "attributes": {
                "POSITION": acc(vertices, "VEC3"),
                "NORMAL": acc([(0, 0, 1)] * 6, "VEC3"),
                "TEXCOORD_0": acc(uv, "VEC2"),
            },
            "material": material_index,
        }],
    })

    node_index = len(D["nodes"])

    D["nodes"].append({
        "name": "Label_" + text,
        "mesh": mesh_index,
        "translation": list(pos),
    })

    D["nodes"][parent]["children"].append(node_index)


# ============================================================
# 6. DASAR, SUNGAI, DAN DINDING
# ============================================================

obj(
    "Base",
    (0, -0.32, 0.5),
    (6, 0.5, 5),
    "base",
)

obj(
    "Riverbed",
    (0, -0.05, 1),
    (5.8, 0.16, 3.8),
    "soil",
)

water = group("Water")

obj(
    "Water_Surface",
    (0, 0.18, 1),
    (5.8, 0.12, 3.8),
    "water",
    parent=water,
)

obj(
    "Concrete_Wall",
    (0, 1.65, -0.48),
    (5.8, 3.8, 0.35),
    "concrete",
)

obj(
    "Bank",
    (0, 0.12, -1.5),
    (5.8, 0.9, 1.4),
    "soil",
)

obj(
    "Grass",
    (0, 0.61, -1.5),
    (5.8, 0.08, 1.4),
    "grass",
)

# Sambungan pada permukaan dinding.
for row in range(7):
    obj(
        "Wall_Joint",
        (0, row * 0.5, -0.298),
        (5.8, 0.012, 0.009),
        "white",
    )

    for x in [-2, -0.8, 0.4, 1.6, 2.8]:
        obj(
            "Wall_Joint",
            (x + row % 2 * 0.3, row * 0.5 + 0.25, -0.298),
            (0.012, 0.49, 0.009),
            "white",
        )


# ============================================================
# 7. TIANG SENSOR DAN TINGKAT AIR
# ============================================================

post = group("Level_Mast")

obj(
    "Mast",
    (0, 1.75, -0.05),
    (0.12, 3.5, 0.12),
    "metal",
    parent=post,
)

for y, color in [
    (0.7, "green"),
    (1.6, "yellow"),
    (2.5, "red"),
]:
    obj(
        "Mast_Band",
        (0, y, 0.025),
        (0.13, 0.9, 0.02),
        color,
        parent=post,
    )

levels = [
    ("Water_Level_Aman", -0.65, 0.75, "green", "AMAN"),
    ("Water_Level_Waspada", 0.65, 1.65, "yellow", "WASPADA"),
    ("Water_Level_Bahaya", -0.65, 2.55, "red", "BAHAYA"),
]

for key, x, y, color, text in levels:
    sensor = group(key, (x, y, 0.12))

    D["nodes"][sensor]["extras"] = {
        "component": key,
        "levelHeight": y,
    }

    obj(
        "Bracket",
        (-x / 2, 0, -0.06),
        (abs(x) + 0.15, 0.1, 0.1),
        color,
        parent=sensor,
    )

    obj(
        "Sensor_Mount",
        (0, 0, 0),
        (0.39, 0.58, 0.05),
        "white",
        parent=sensor,
    )

    obj(
        "Water_Level_PCB",
        (0, 0, 0.055),
        (0.29, 0.48, 0.035),
        "redpcb",
        parent=sensor,
    )

    for j in range(7):
        obj(
            "Water_Trace",
            (-0.105 + j * 0.035, -0.055, 0.078),
            (0.012, 0.34, 0.008),
            "gold",
            parent=sensor,
        )

    obj(
        "Connector",
        (0, 0.19, 0.09),
        (0.18, 0.075, 0.07),
        "black",
        parent=sensor,
    )

    obj(
        "Signal_Cable",
        (0, 0.34, 0.03),
        (0.024, 0.24, 0.024),
        "black",
        parent=sensor,
    )

    label(
        text,
        (-0.02, -0.43, 0.03),
        1.0,
        0.24,
        {
            "green": "13845b",
            "yellow": "bd8b10",
            "red": "b83a45",
        }[color],
        sensor,
    )

    obj(
        "Cable_Horizontal",
        (x / 2, y + 0.44, 0.015),
        (abs(x), 0.02, 0.02),
        "black",
    )

    obj(
        "Cable_Vertical",
        (x, y + 0.34, 0.015),
        (0.02, 0.2, 0.02),
        "black",
    )

obj(
    "Cable_Trunk",
    (0.085, 1.85, -0.06),
    (0.045, 2.8, 0.045),
    "black",
)


# ============================================================
# 8. KOTAK KONTROL DAN LUBANG SENSOR ULTRASONIK
# ============================================================

box = group("Control_Box", (0, 3.8, 0.22))

D["nodes"][box]["extras"] = {
    "component": "Control_Box",
}

obj(
    "Enclosure_Back",
    (0, 0, -0.36),
    (1.28, 1.3, 0.08),
    "white",
    parent=box,
)

for x in [-0.6, 0.6]:
    obj(
        "Enclosure_Side",
        (x, 0, 0),
        (0.08, 1.3, 0.8),
        "white",
        parent=box,
    )

obj(
    "Enclosure_Top",
    (0, 0.61, 0),
    (1.28, 0.08, 0.8),
    "white",
    parent=box,
)

# Membuat dua lubang berbentuk lingkaran pada pelat bawah.
for center in [-0.32, 0.32]:
    vertices = []
    normals = []

    def tri(a, b, c, normal):
        vertices.extend([a, b, c])
        normals.extend([normal] * 3)

    for k in range(64):
        a = k * math.tau / 64
        b = (k + 1) * math.tau / 64

        def pt(theta, outer, y):
            dx = math.cos(theta)
            dz = math.sin(theta)

            if outer:
                radius = min(
                    0.32 / max(abs(dx), 1e-9),
                    0.4 / max(abs(dz), 1e-9),
                )
            else:
                radius = 0.148

            return (
                center + radius * dx,
                y,
                radius * dz,
            )

        for y, normal in [
            (-0.61, (0, 1, 0)),
            (-0.69, (0, -1, 0)),
        ]:
            ia = pt(a, False, y)
            ib = pt(b, False, y)
            oa = pt(a, True, y)
            ob = pt(b, True, y)

            if y == -0.61:
                tri(ia, ib, ob, normal)
                tri(ia, ob, oa, normal)
            else:
                tri(ia, oa, ob, normal)
                tri(ia, ob, ib, normal)

        ia = pt(a, False, -0.69)
        ib = pt(b, False, -0.69)
        ja = pt(a, False, -0.61)
        jb = pt(b, False, -0.61)

        normal = (
            -math.cos((a + b) / 2),
            0,
            -math.sin((a + b) / 2),
        )

        tri(ia, ib, jb, normal)
        tri(ia, jb, ja, normal)

    mesh(
        "Bottom_Plate_Circular_Hole",
        vertices,
        normals,
        "white",
        box,
    )


# ============================================================
# 9. PINTU KOTAK, LED, DAN BUZZER
# ============================================================

door = group("Door_Hinge", (-0.64, 0, 0.43), box)

obj(
    "Door",
    (0.64, 0, 0),
    (1.28, 1.3, 0.055),
    "white",
    parent=door,
)

obj(
    "Door_Inset",
    (0.64, 0.1, 0.035),
    (1.12, 0.88, 0.025),
    "base",
    parent=door,
)

label(
    "SMART FLOOD",
    (0.64, 0.37, 0.052),
    1.0,
    0.22,
    "153449",
    door,
)

leds = [
    ("LED_Aman", 0.3, "green", "AMAN"),
    ("LED_Waspada", 0.64, "yellow", "WASPADA"),
    ("LED_Bahaya", 0.98, "red", "BAHAYA"),
]

for key, x, color, text in leds:
    led = group(key, (x, 0.06, 0.06), door)

    obj(
        "LED_Rim",
        (0, 0, 0),
        (0.105, 0.04, 0.105),
        "black",
        "cyl",
        led,
        math.pi / 2,
    )

    obj(
        "LED_Lens",
        (0, 0, 0.04),
        (0.075, 0.06, 0.075),
        color,
        "cyl",
        led,
        math.pi / 2,
    )

    label(
        text,
        (0, -0.18, 0.03),
        0.31,
        0.08,
        "153449",
        led,
    )

buzzer = group("Buzzer", (0.64, -0.38, 0.07), door)

obj(
    "Buzzer_Body",
    (0, 0, 0),
    (0.115, 0.12, 0.115),
    "black",
    "cyl",
    buzzer,
    math.pi / 2,
)

obj(
    "Buzzer_Opening",
    (0, 0, 0.064),
    (0.037, 0.004, 0.037),
    "metal",
    "cyl",
    buzzer,
    math.pi / 2,
)

obj(
    "Door_Handle",
    (1.16, -0.37, 0.08),
    (0.045, 0.22, 0.08),
    "metal",
    parent=door,
)


# ============================================================
# 10. MODUL ESP32
# ============================================================

esp = group("ESP32", (-0.15, 0.14, -0.22), box)

obj(
    "ESP32_PCB",
    (0, 0, 0),
    (0.42, 0.7, 0.065),
    "pcb",
    parent=esp,
)

obj(
    "ESP32_Shield",
    (0, 0.06, 0.06),
    (0.3, 0.29, 0.055),
    "metal",
    parent=esp,
)

obj(
    "USB",
    (0, -0.32, 0.055),
    (0.15, 0.12, 0.09),
    "metal",
    parent=esp,
)

for j in range(8):
    for x in [-0.24, 0.24]:
        obj(
            "Pin",
            (x, -0.23 + j * 0.065, 0.03),
            (0.065, 0.025, 0.035),
            "gold",
            parent=esp,
        )

for j in range(4):
    obj(
        "Antenna_Trace",
        (-0.1 + j * 0.06, 0.28, 0.041),
        (0.025, 0.12, 0.01),
        "gold",
        parent=esp,
    )

label(
    "ESP32",
    (0, 0.05, 0.091),
    0.26,
    0.08,
    "536878",
    esp,
)


# ============================================================
# 11. SENSOR ULTRASONIK
# ============================================================

ultrasonic = group("Ultrasonic", (0, -0.45, 0), box)

obj(
    "Ultrasonic_PCB",
    (0, 0, 0),
    (0.98, 0.045, 0.35),
    "pcb",
    parent=ultrasonic,
)

for x in [-0.32, 0.32]:
    obj(
        "Transducer",
        (x, -0.15, 0),
        (0.132, 0.27, 0.132),
        "metal",
        "cyl",
        ultrasonic,
    )

    obj(
        "Transducer_Face",
        (x, -0.287, 0),
        (0.11, 0.008, 0.11),
        "black",
        "cyl",
        ultrasonic,
    )

    for j in range(5):
        obj(
            "Grille",
            (x - 0.07 + j * 0.035, -0.293, 0),
            (0.006, 0.008, 0.14),
            "metal",
            parent=ultrasonic,
        )

obj(
    "Internal_Wire",
    (0.38, -0.08, -0.18),
    (0.025, 0.65, 0.025),
    "red",
    parent=box,
)


# ============================================================
# 12. SENSOR HUJAN
# ============================================================

rain = group("Rain_Sensor", (0, 4.62, 0.22))

D["nodes"][rain]["rotation"] = [
    math.sin(0.16),
    0,
    0,
    math.cos(0.16),
]

obj(
    "Rain_PCB",
    (0, 0, 0),
    (0.95, 0.05, 0.58),
    "black",
    parent=rain,
)

for j in range(13):
    obj(
        "Rain_Trace",
        (-0.41 + j * 0.067, 0.03, 0),
        (0.024, 0.009, 0.47),
        "gold",
        parent=rain,
    )

obj(
    "Rain_Trace_Bus",
    (0, 0.03, -0.22),
    (0.85, 0.009, 0.025),
    "gold",
    parent=rain,
)

for x in [-0.35, 0.35]:
    obj(
        "Rain_Stand",
        (x, 4.48, 0.22),
        (0.025, 0.22, 0.025),
        "metal",
        "cyl",
    )


# ============================================================
# 13. RIak AIR DAN PENGUNCI TIANG
# ============================================================

random.seed(8)

for j in range(24):
    obj(
        "Ripple",
        (
            random.uniform(-2.7, 2.7),
            0.244,
            random.uniform(0.4, 2.7),
        ),
        (
            random.uniform(0.08, 0.28),
            0.005,
            0.013,
        ),
        "white",
        parent=water,
    )

for y in [0.4, 1.35, 2.3, 3.15]:
    obj(
        "Mast_Clamp",
        (0, y, -0.08),
        (0.3, 0.055, 0.1),
        "metal",
    )

    for x in [-0.12, 0.12]:
        obj(
            "Bolt",
            (x, y, -0.015),
            (0.026, 0.02, 0.026),
            "metal",
            "cyl",
            rx=math.pi / 2,
        )


# ============================================================
# 14. EKSPOR MODEL KE FORMAT GLB
# ============================================================

D["buffers"] = [{
    "byteLength": len(buf),
}]

# Serialisasi data JSON GLTF dan padding 4-byte.
js = json.dumps(
    D,
    separators=(",", ":"),
).encode()

js += b" " * (-len(js) % 4)

buf += b"\x00" * (-len(buf) % 4)

# Header GLB, chunk JSON, dan chunk data biner.
out = (
    struct.pack(
        "<III",
        0x46546C67,
        2,
        28 + len(js) + len(buf),
    )
    + struct.pack("<II", len(js), 0x4E4F534A)
    + js
    + struct.pack("<II", len(buf), 0x004E4942)
    + buf
)

output_file = P / "smart_flood.glb"
output_file.write_bytes(out)

print(
    f"Model berhasil dibuat: {output_file}\n"
    f"Ukuran file: {len(out):,} bytes\n"
    f"Jumlah node: {len(D['nodes'])}"
)