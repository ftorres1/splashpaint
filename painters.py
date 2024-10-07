import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import requests

# Configuración de Discord
DISCORD_CLIENT_ID = st.secrets["client_id"]
DISCORD_CLIENT_SECRET = st.secrets["client_secret"]
DISCORD_REDIRECT_URI = "https://splashplace.streamlit.app/"
DISCORD_API_URL = 'https://discord.com/api/v10'

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
            st.success(f"Te has registrado como invitado: {guest_username}")
        else:
            st.error("Por favor, ingresa un nombre de usuario.")

    # Mostrar el lienzo
    draw_canvas()

    # Verificar si el usuario ha iniciado sesión o si hay un nombre de usuario de invitado
    if st.session_state.user is None and st.session_state.guest_username is None:
        st.error("Debes iniciar sesión o registrarte como invitado para colocar píxeles.")
        return  # Salimos de la función si no hay sesión activa ni usuario invitado

    # Seleccionar color
    color = st.color_picker('Elige un color', '#000000')

    # Seleccionar fila y columna
    fila = st.selectbox('Selecciona la fila (1-20)', range(1, GRID_SIZE + 1))
    columna = st.selectbox('Selecciona la columna (1-20)', range(1, GRID_SIZE + 1))

    # Lógica para pintar en el lienzo
    if st.button('Pintar'):
        # Convertimos fila y columna a índices de matriz (0-19)
        st.session_state.canvas[fila - 1, columna - 1] = [int(color[1:3], 16) / 255.0, int(color[3:5], 16) / 255.0, int(color[5:7], 16) / 255.0]
        save_canvas()  # Guardar el estado del lienzo
        st.success("Píxel colocado.")

# Función principal
def main():
    handle_auth()  # Manejar la autenticación de usuario
    paint_page()   # Mostrar la página de pintura

if __name__ == "__main__":
    main()
