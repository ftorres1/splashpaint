import streamlit as st
import numpy as np
from PIL import Image
import json, os, time, requests
from matplotlib.colors import hex2color

# ======================
# CONFIG
# ======================

GRID_SIZE = 30
PIXEL_SIZE = 20
SAVE_FILE = "canvas_state.json"
COOLDOWN = 5

ADMIN_ID = "768543062816456754"

CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"]
REDIRECT_URI = st.secrets["redirect_uri"]

DISCORD_API = "https://discord.com/api/v10"

WEBHOOK_URL = "https://discord.com/api/webhooks/1502851795599491115/0u94xt24W6-lRmSHoiSzwRPs6liPRLm94V7XmkdoghpUhZSS3MUUVV-rhgjzbhFlcitw"

# ======================
# PAGE
# ======================

st.set_page_config(page_title="Chaquetas")

st.title("Chaquetas")

# ======================
# CANVAS FUNCTIONS
# ======================

# crear canvas vacía
def create_blank_canvas():
    return np.ones((GRID_SIZE, GRID_SIZE, 3))

# cargar canvas
def load_canvas():

    if os.path.exists(SAVE_FILE):

        try:

            with open(SAVE_FILE, "r") as f:

                data = json.load(f)

                if "canvas" in data:

                    canvas = np.array(data["canvas"])

                    if canvas.shape == (GRID_SIZE, GRID_SIZE, 3):
                        return canvas

        except:
            pass

    return create_blank_canvas()

# guardar canvas
def save_canvas(canvas):

    with open(SAVE_FILE, "w") as f:

        json.dump(
            {
                "canvas": canvas.tolist()
            },
            f
        )

# mostrar canvas
def draw_canvas(canvas):

    img = Image.fromarray(
        (canvas * 255).astype(np.uint8)
    )

    img = img.resize(
        (
            GRID_SIZE * PIXEL_SIZE,
            GRID_SIZE * PIXEL_SIZE
        ),
        Image.NEAREST
    )

    st.image(img)

# ======================
# WEBHOOK
# ======================

def send_webhook(message):

    try:

        requests.post(
            WEBHOOK_URL,
            json={
                "content": message
            }
        )

    except:
        pass

# ======================
# DISCORD LOGIN
# ======================

# obtener token
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

# obtener usuario
def get_user(token):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    return requests.get(
        f"{DISCORD_API}/users/@me",
        headers=headers
    ).json()

# login
def handle_login():

    if "user" not in st.session_state:
        st.session_state.user = None

    if "login_sent" not in st.session_state:
        st.session_state.login_sent = False

    if "code" in st.query_params:

        token_data = get_access_token(
            st.query_params["code"]
        )

        if "access_token" in token_data:

            user_data = get_user(
                token_data["access_token"]
            )

            st.session_state.user = user_data

            # webhook login
            if not st.session_state.login_sent:

                send_webhook(
                    f"🔐 {user_data['username']} inició sesión."
                )

                st.session_state.login_sent = True

# ======================
# START
# ======================

handle_login()

user = st.session_state.user

# cargar canvas global
canvas = load_canvas()

# mostrar canvas
draw_canvas(canvas)

st.divider()

# ======================
# NO LOGIN
# ======================

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

# ======================
# USER INFO
# ======================

st.sidebar.success(
    f"Conectado como {user['username']}"
)

st.sidebar.divider()

if user is None:
st.sidebar.link_button(
    "Unirse al Discord",
    "https://discord.gg/wdYAVkey5A"
)

# ======================
# ADMIN PANEL
# ======================

if str(user["id"]) == ADMIN_ID:

    st.sidebar.divider()

    st.sidebar.title("Admin Panel")

    if st.sidebar.button("Restablecer Canvas"):

        blank = create_blank_canvas()

        save_canvas(blank)

        send_webhook(
            f"🛠️ {user['username']} restableció la canvas."
        )

        st.sidebar.success(
            "Canvas restablecida"
        )

        st.rerun()

# ======================
# COOLDOWN
# ======================

if "last_paint" not in st.session_state:
    st.session_state.last_paint = 0

# ======================
# COORDS
# ======================

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

# ======================
# COLOR
# ======================

color = st.color_picker(
    "Color",
    "#000000"
)

# ======================
# PAINT
# ======================

if st.button("Pintar Pixel"):

    current_time = time.time()

    # cooldown
    if current_time - st.session_state.last_paint < COOLDOWN:

        st.error(
            f"Espera {int(COOLDOWN - (current_time - st.session_state.last_paint))}s"
        )

        st.stop()

    # recargar canvas
    canvas = load_canvas()

    # pintar pixel
    canvas[y, x] = hex2color(color)

    # guardar
    save_canvas(canvas)

    # webhook pixel
    send_webhook(
        f"🎨 {user['username']} puso un pixel en X:{x} Y:{y} con color {color}"
    )

    # cooldown
    st.session_state.last_paint = current_time

    st.success(
        f"{user['username']} pintó en ({x}, {y})"
    )

    st.rerun()
