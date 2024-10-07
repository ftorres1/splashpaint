import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
from matplotlib.colors import hex2color  # Importar la función hex2color desde matplotlib

# Configuración de Discord
DISCORD_CLIENT_ID = st.secrets["client_id"]
DISCORD_CLIENT_SECRET = st.secrets["client_secret"]
DISCORD_REDIRECT_URI = "https://splashplace.streamlit.app/"
DISCORD_API_URL = 'https://discord.com/api/v10'
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1292564820016627855/akZ08vnkPWqHu-__UAxzlgB2f4T6ogyxkK8JoV8qhkB5hYz0i0zQ076JW9NI0Tow7sFe'  # URL del webhook

# Definimos el tamaño del lienzo
GRID_SIZE = 20
DATABASE_FILE = 'canvas_state.json'

# Función para cargar el estado del lienzo desde el archivo JSON
def load_canvas():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
            return np.array(data['canvas'], dtype=float)
    else:
        return np.ones((GRID_SIZE, GRID_SIZE, 3))  # Blanco (1,1,1 en RGB)

# Función para guardar el estado del lienzo en el archivo JSON
def save_canvas():
    with open(DATABASE_FILE, 'w') as f:
        json.dump({'canvas': st.session_state.canvas.tolist()}, f)

# Inicializamos el lienzo como una matriz de colores (en blanco)
if 'canvas' not in st.session_state:
    st.session_state.canvas = load_canvas()

# Inicializamos el usuario
if 'user' not in st.session_state:
    st.session_state.user = None

# Inicializamos el nombre de usuario para modo invitado
if 'guest_username' not in st.session_state:
    st.session_state.guest_username = None

# Función para mostrar el lienzo
def draw_canvas():
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(st.session_state.canvas, interpolation='nearest')
    ax.set_xticks([])  # Ocultar marcas del eje X
    ax.set_yticks([])  # Ocultar marcas del eje Y
    st.pyplot(fig)

# Función para obtener el token de acceso
def get_access_token(code):
    payload = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
    }
    response = requests.post(f'{DISCORD_API_URL}/oauth2/token', data=payload)
    return response.json()

# Función para obtener el usuario de Discord
def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f'{DISCORD_API_URL}/users/@me', headers=headers)
    return response.json()

# Función para manejar la autenticación
def handle_auth():
    if "code" in st.query_params:
        code = st.query_params["code"]
        token_response = get_access_token(code)
        if 'access_token' in token_response:
            access_token = token_response['access_token']
            user_info = get_user_info(access_token)
            st.session_state.user = user_info  # Guardar información del usuario en la sesión

# Función para enviar mensaje al webhook de Discord
def send_webhook_message(user_id, row, col):
    if user_id:
        username = user_id["username"]  # Obtener el nombre de usuario de Discord
        message = f"{username} (Discord) ha puesto un píxel en la fila {row} y columna {col}."
    else:
        username = st.session_state.guest_username
        message = f"{username} (Invitado) ha puesto un píxel en la fila {row} y columna {col}."

    payload = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

# Función para la página de pintura
def paint_page():
    st.title("Pinta en el lienzo")
    st.write("Todos pueden ver el lienzo, pero solo los usuarios que inician sesión pueden colocar píxeles.")

    # Enlace para iniciar sesión
    login_url = f"https://discord.com/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&scope=identify&response_type=code&redirect_uri={DISCORD_REDIRECT_URI}"
    st.sidebar.markdown(f"[Iniciar sesión con Discord]({login_url})")

    # Opción de registro de nombre de usuario
    st.sidebar.subheader("O Registrar nombre de usuario")
    guest_username = st.sidebar.text_input("Ingresa un nombre de usuario")
    if st.sidebar.button("Registrar como invitado"):
        if guest_username:
            st.session_state.guest_username = guest_username
            st.success("¡Bienvenido, invitado!")

    # Selección de color, fila y columna
    color = st.color_picker("Selecciona un color", value='#000000')
    fila = st.number_input("Fila (1-20)", min_value=1, max_value=GRID_SIZE)
    columna = st.number_input("Columna (1-20)", min_value=1, max_value=GRID_SIZE)

    # Botón para pintar en el lienzo
    if st.button("Pintar"):
        fila_idx = fila - 1
        col_idx = columna - 1
        st.session_state.canvas[fila_idx, col_idx] = np.array(hex2color(color))
        save_canvas()  # Guardar el estado del lienzo
        send_webhook_message(st.session_state.user, fila_idx, col_idx)  # Enviar mensaje al webhook
        st.success("Píxel pintado en el lienzo.")

    draw_canvas()  # Mostrar el lienzo

# Manejar la autenticación
handle_auth()  # Manejar la autenticación de usuario

# Mostrar la página de pintura
paint_page()
