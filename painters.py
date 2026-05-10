import streamlit as st
import numpy as np
from PIL import Image
import json, os, time, requests
from matplotlib.colors import hex2color

# tamaño de la canvas
GRID_SIZE = 30

# tamaño visual de cada pixel
PIXEL_SIZE = 20

# archivo donde se guarda la canvas
SAVE_FILE = "canvas_state.json"

# cooldown entre pixeles
COOLDOWN = 5

# TU DISCORD ID
ADMIN_ID = "768543062816456754"

# datos discord
CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"]
REDIRECT_URI = st.secrets["redirect_uri"]

DISCORD_API = "https://discord.com/api/v10"

# título página
st.set_page_config(page_title="Chaquetas")

st.title("Chaquetas")

# crear canvas blanca
def create_blank_canvas():
    return np.ones((GRID_SIZE, GRID_SIZE, 3))

# cargar canvas
def load_canvas():

    if os.path.exists(SAVE_FILE):

        with open(SAVE_FILE, "r") as f:

            return np.array(
                json.load(f)["canvas"]
            )

    return create_blank_canvas()

# guardar canvas
def save_canvas():

    with open(SAVE_FILE, "w") as f:

        json.dump(
            {
                "canvas":
                st.session_state.canvas.tolist()
            },
            f
        )

# mostrar canvas
def draw_canvas():

    img = Image.fromarray(
        (
            st.session_state.canvas * 255
        ).astype(np.uint8)
    )

    img = img.resize(
        (
            GRID_SIZE * PIXEL_SIZE,
            GRID_SIZE * PIXEL_SIZE
        ),
        Image.NEAREST
    )

    st.image(img)

# obtener token discord
def get_access_token(code):

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    return requests.post(
        f"{DISCORD_API}/oauth2/token",
        data=payload
    ).json()

# obtener usuario discord
def get_user(token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    return requests.get(
        f"{DISCORD_API}/users/@me",
        headers=headers
    ).json()

# login opcional
def handle_login():

    if "user" not in st.session_state:
        st.session_state.user = None

    if "code" in st.query_params:

        token_data = get_access_token(
            st.query_params["code"]
        )

        if "access_token" in token_data:

            st.session_state.user = get_user(
                token_data["access_token"]
            )

# cargar canvas
if "canvas" not in st.session_state:
    st.session_state.canvas = load_canvas()

# cooldown
if "last_paint" not in st.session_state:
    st.session_state.last_paint = 0

# iniciar login
handle_login()

user = st.session_state.user

# mostrar canvas aunque no haya login
draw_canvas()

st.divider()

# si NO ha iniciado sesión
if user is None:

    login_url = (
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=identify"
    )

    st.warning(
        "Inicia sesión con Discord para pintar."
    )

    st.link_button(
        "Login con Discord",
        login_url
    )

    st.stop()

# mostrar usuario
st.sidebar.success(
    f"Conectado como {user['username']}"
)

# PANEL ADMIN
if str(user["id"]) == ADMIN_ID:

    st.sidebar.divider()

    st.sidebar.title("Admin Panel")

    if st.sidebar.button("Restablecer Canvas"):

        st.session_state.canvas = create_blank_canvas()

        save_canvas()

        st.sidebar.success(
            "Canvas restablecida"
        )

        st.rerun()

# coordenadas
c1, c2 = st.columns(2)

with c1:

    x = st.number_input(
        "X",
        0,
        GRID_SIZE - 1,
        0
    )

with c2:

    y = st.number_input(
        "Y",
        0,
        GRID_SIZE - 1,
        0
    )

# selector color
color = st.color_picker(
    "Color",
    "#000000"
)

# pintar pixel
if st.button("Pintar Pixel"):

    current_time = time.time()

    # revisar cooldown
    if current_time - st.session_state.last_paint < COOLDOWN:

        st.error(
            f"Espera {int(COOLDOWN - (current_time - st.session_state.last_paint))}s"
        )

        st.stop()

    # pintar pixel
    st.session_state.canvas[y, x] = hex2color(color)

    # guardar
    save_canvas()

    # cooldown
    st.session_state.last_paint = current_time

    st.success(
        f"{user['username']} pintó en ({x}, {y})"
    )

    st.rerun()
