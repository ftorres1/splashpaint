import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import requests

# Cargar credenciales desde secrets.toml
DISCORD_CLIENT_ID = st.secrets["discord"]["client_id"]
DISCORD_CLIENT_SECRET = st.secrets["discord"]["client_secret"]
DISCORD_REDIRECT_URI = st.secrets["discord"]["redirect_uri"]
DISCORD_OAUTH2_URL = 'https://discord.com/api/oauth2/authorize'
DISCORD_TOKEN_URL = 'https://discord.com/api/oauth2/token'
DISCORD_USER_URL = 'https://discord.com/api/users/@me'

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

# Función para mostrar el lienzo
def draw_canvas():
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(st.session_state.canvas, interpolation='nearest')
    ax.set_xticks([])
    ax.set_yticks([])
    st.pyplot(fig)

# Función para manejar el inicio de sesión con Discord
def discord_login():
    # Si no hay token en la sesión, redirige al usuario a Discord
    if 'token' not in st.session_state:
        # Construir la URL de autorización
        auth_url = f"{DISCORD_OAUTH2_URL}?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
        st.sidebar.markdown(f"[Iniciar sesión con Discord]({auth_url})")
    else:
        # Si hay un token, muestra el usuario
        headers = {
            'Authorization': f'Bearer {st.session_state.token}'
        }
        response = requests.get(DISCORD_USER_URL, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            st.sidebar.write(f"¡Hola, {user_data['username']}!")
            st.sidebar.write("Puedes empezar a pintar en el lienzo.")
        else:
            st.error("Error al obtener los datos del usuario. Intenta iniciar sesión nuevamente.")

# Función para manejar el callback de Discord
def handle_callback():
    code = st.query_params.get('code')  # Usando st.query_params
    if code:
        code = code[0]  # Convertir de lista a cadena si es necesario
        token_url = DISCORD_TOKEN_URL
        data = {
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': DISCORD_REDIRECT_URI
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.post(token_url, data=data, headers=headers)
        response_data = response.json()
        st.write("Response data:", response_data)  # Ayuda a depurar la respuesta de Discord

        # Manejar la respuesta para obtener el token
        if response.status_code == 200 and 'access_token' in response_data:
            st.session_state.token = response_data['access_token']
        else:
            st.error("Error al obtener el token de acceso. Revisa la respuesta.")

# Función para la página de pintura
def paint_page():
    st.title("Pinta en el lienzo")
    st.write("Antes de jugar, por favor ve al menú e inicia sesión o registra tu nombre (en dispositivos móviles, toca la flecha de arriba en el lado izquierdo de tu pantalla).")

    # Mostrar el lienzo
    draw_canvas()

    # Solo permitir la pintura si el usuario ha iniciado sesión
    if 'token' in st.session_state:
        # Seleccionar color
        color = st.color_picker('Elige un color', '#000000')

        # Seleccionar fila y columna
        fila = st.selectbox('Selecciona la fila (1-20)', range(1, GRID_SIZE + 1))
        columna = st.selectbox('Selecciona la columna (1-20)', range(1, GRID_SIZE + 1))

        # Lógica para pintar en el lienzo
        if st.button('Pintar'):
            # Convertimos fila y columna a índices de la matriz
            x = columna - 1  # Ajustar a 0-index
            y = fila - 1     # Ajustar a 0-index

            # Cambiamos el color del píxel seleccionado
            selected_color = np.array([int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]) / 255
            st.session_state.canvas[y, x] = selected_color
            
            # Guardar el estado del lienzo después de pintar
            save_canvas()
    else:
        st.warning("Por favor, inicia sesión para pintar en el lienzo.")

def main():
    discord_login()  # Manejar el inicio de sesión
    handle_callback()  # Manejar el callback de Discord
    paint_page()  # Mostrar la página de pintura

if __name__ == "__main__":
    main()
