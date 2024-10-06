import streamlit as st
import numpy as np
import requests
import time

# Configuración inicial
st.set_page_config(page_title="SplashPlace", layout="wide")

# Función para enviar notificaciones a Discord
def send_discord_notification(username, position, color):
    webhook_url = "https://discord.com/api/webhooks/1292564820016627855/akZ08vnkPWqHu-__UAxzlgB2f4T6ogyxkK8JoV8qhkB5hYz0i0zQ076JW9NI0Tow7sFe"
    content = f"{username} pintó en la posición {position} con el color {color}."
    requests.post(webhook_url, json={"content": content})

# Verifica si el usuario está autenticado
if "user" not in st.session_state:
    st.session_state.user = None

# Función para iniciar sesión con Discord
def login_with_discord():
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={st.secrets['discord']['client_id']}"
        f"&redirect_uri=https://splashplace.streamlit.app/callback"
        f"&response_type=code"
        f"&scope=identify"
    )
    st.write("Por favor, inicia sesión en Discord haciendo clic en el siguiente enlace:")
    st.write(f"[Iniciar sesión]({discord_auth_url})")

# Manejo del callback
def handle_callback():
    if "code" in st.query_params:
        code = st.query_params["code"]
        token_url = "https://discord.com/api/oauth2/token"
        data = {
            "client_id": st.secrets["discord"]["client_id"],
            "client_secret": st.secrets["discord"]["client_secret"],
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://splashplace.streamlit.app/callback"
        }
        response = requests.post(token_url, data=data)
        if response.ok:
            access_token = response.json().get("access_token")
            user_info_url = "https://discord.com/api/users/@me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info = requests.get(user_info_url, headers=headers)
            if user_info.ok:
                st.session_state.user = user_info.json()
                st.success("Has iniciado sesión correctamente.")
            else:
                st.error("No se pudo obtener información del usuario.")
        else:
            st.error("Error al intercambiar el código por un token.")

# Manejo del inicio de sesión y callback
if st.session_state.user is None:
    login_with_discord()
else:
    st.write("Ya has iniciado sesión como:", st.session_state.user["username"])
    handle_callback()

# Configuración del lienzo
canvas_size = (16, 16)  # Dimensiones del lienzo
if 'canvas' not in st.session_state:
    st.session_state.canvas = np.zeros(canvas_size, dtype=int)

# Selección de color
color = st.color_picker("Selecciona un color", "#000000")

# Pintar en el lienzo
if st.button("Pintar"):
    if st.session_state.user is None or 'username' not in st.session_state.user:
        st.error("Por favor, ingresa tu nombre de usuario o inicia sesión con Discord.")
    else:
        position = st.selectbox("Selecciona la posición", [f"{chr(65 + i)}{j + 1}" for j in range(canvas_size[0]) for i in range(canvas_size[1])])
        selected_row = ord(position[0]) - 65
        selected_col = int(position[1]) - 1

        # Actualizar el lienzo
        st.session_state.canvas[selected_row, selected_col] = color

        # Enviar notificación a Discord
        send_discord_notification(st.session_state.user["username"], position, color)

# Mostrar el lienzo
st.write("Mural:")
for row in range(canvas_size[0]):
    cols = []
    for col in range(canvas_size[1]):
        pixel_color = st.session_state.canvas[row, col]
        cols.append(st.color_picker("", pixel_color, key=f"color_{row}_{col}"))
    st.columns(cols)

# Panel de administración
def is_admin(user):
    admin_users = st.secrets["admin"]["users"]
    return user["username"] in admin_users

if is_admin(st.session_state.user):
    st.write("Panel de Administración")
    # Aquí puedes agregar más funcionalidades de administración
