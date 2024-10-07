import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
from urllib.parse import urlencode

# Configuración de Discord
DISCORD_CLIENT_ID = st.secrets["client_id"]
DISCORD_CLIENT_SECRET = st.secrets["client_secret"]
DISCORD_REDIRECT_URI = "https://splashplace.streamlit.app/"  # URL de Streamlit Cloud
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

# Función para la página de pintura
def paint_page():
    st.title("Pinta en el lienzo")
    st.write("Antes de jugar, por favor ve al menú e inicia sesión o registra tu nombre (en dispositivos móviles, toca la flecha de arriba en el lado izquierdo de tu pantalla).")

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
        
    # Mostrar el lienzo
    draw_canvas()

# Función para la página de inicio
def home_page():
    st.title("¡Bienvenido a SplashPlace!")
    st.write("SplashPlace es un lienzo colaborativo para todos los usuarios, con el propósito de que todos se pongan de acuerdo para crear algo realmente impresionante.")
    st.write("Utiliza el menú para navegar a la página de pintura. En caso de estar en dispositivos móviles, toca la flecha de hasta arriba a la izquierda de tu pantalla. También debes de iniciar sesión en el menú para colocar píxeles.")

# Función principal
def main():
    # Menú de navegación
    menu = st.sidebar.selectbox("Visita una página", ["Inicio", "Pintar"])

    # Opción de inicio de sesión
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify',
    }
    auth_url = f'https://discord.com/api/oauth2/authorize?{urlencode(params)}'
    
    st.sidebar.markdown(f"[Iniciar sesión con Discord]({auth_url})")

    # Manejo del inicio de sesión
    query_params = st.query_params
    if 'code' in query_params:
        code = query_params['code']
        token_data = get_access_token(code)
        access_token = token_data.get('access_token')

        if access_token:
            user_info = get_user_info(access_token)
            st.session_state.user = user_info  # Guardamos la información del usuario
            st.experimental_set_query_params()  # Limpiar los parámetros de consulta después del inicio de sesión
        else:
            st.error("Error al obtener el token de acceso.")

    # Mostrar nombre de usuario si está disponible
    if st.session_state.user:
        st.sidebar.write(f"Bienvenido, {st.session_state.user['username']}!")

    # Mostrar las páginas correspondientes
    if menu == "Inicio":
        home_page()
    elif menu == "Pintar":
        paint_page()

# Ejecutamos la función principal
if __name__ == "__main__":
    main()
