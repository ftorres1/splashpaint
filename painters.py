import streamlit as st
import numpy as np
from PIL import Image
import json
import os
import time

# =========================
# CONFIG
# =========================

GRID_SIZE = 30
PIXEL_SIZE = 20
SAVE_FILE = "canvas.json"
COOLDOWN = 5  # segundos

st.set_page_config(page_title="Mini r/place", layout="centered")

st.title("🎨 Mini r/place")

# =========================
# FUNCIONES
# =========================

def create_blank_canvas():
    return np.ones((GRID_SIZE, GRID_SIZE, 3), dtype=np.uint8) * 255


def load_canvas():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            return np.array(data, dtype=np.uint8)

    return create_blank_canvas()


def save_canvas():
    with open(SAVE_FILE, "w") as f:
        json.dump(st.session_state.canvas.tolist(), f)


def draw_canvas():
    img = Image.fromarray(st.session_state.canvas, "RGB")

    # ampliar imagen sin blur
    img = img.resize(
        (GRID_SIZE * PIXEL_SIZE, GRID_SIZE * PIXEL_SIZE),
        Image.NEAREST
    )

    st.image(img)


# =========================
# SESSION STATE
# =========================

if "canvas" not in st.session_state:
    st.session_state.canvas = load_canvas()

if "last_paint" not in st.session_state:
    st.session_state.last_paint = 0

if "username" not in st.session_state:
    st.session_state.username = ""


# =========================
# LOGIN SIMPLE
# =========================

st.sidebar.title("Usuario")

username = st.sidebar.text_input(
    "Nombre",
    value=st.session_state.username
)

if st.sidebar.button("Guardar nombre"):
    st.session_state.username = username
    st.sidebar.success("Nombre guardado")

# =========================
# MOSTRAR CANVAS
# =========================

draw_canvas()

st.divider()

# =========================
# CONTROLES
# =========================

col1, col2 = st.columns(2)

with col1:
    x = st.number_input(
        "X",
        min_value=0,
        max_value=GRID_SIZE - 1,
        value=0
    )

with col2:
    y = st.number_input(
        "Y",
        min_value=0,
        max_value=GRID_SIZE - 1,
        value=0
    )

color = st.color_picker(
    "Color",
    "#000000"
)

# =========================
# PINTAR
# =========================

if st.button("Pintar Pixel"):

    if st.session_state.username == "":
        st.error("Pon un nombre primero")
        st.stop()

    current_time = time.time()

    if current_time - st.session_state.last_paint < COOLDOWN:
        remaining = int(
            COOLDOWN - (current_time - st.session_state.last_paint)
        )

        st.error(f"Espera {remaining}s")
        st.stop()

    # convertir HEX a RGB
    hex_color = color.lstrip("#")

    rgb = [
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    ]

    # pintar pixel
    st.session_state.canvas[y, x] = rgb

    # guardar
    save_canvas()

    # cooldown
    st.session_state.last_paint = current_time

    st.success(
        f"{st.session_state.username} pintó en ({x}, {y})"
    )

    st.rerun()
