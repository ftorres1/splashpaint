import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import requests
from urllib.parse import urlencode

# Configuración de Discord
DISCORD_CLIENT_ID = 'YOUR_CLIENT_ID'
DISCORD_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
DISCORD_REDIRECT_URI = 'http://localhost:8501/'  # Ajusta esto según tu URL de producción
DISCORD_API_URL = 'https://discord.com/api/v10'

# Inicializamos el lienzo como una matriz de colores (en blanco)
GRID_SIZE = 20
if 'canvas' not in st.session_state:
    st.session_state.canvas = np.ones((GRID_SIZE, GRID_SIZE, 3))  # Blanco (1,1,1 en RGB)
    st.session_state.last_paint_time = 0

# Función para mostrar el lienzo sin coordenadas
def draw_canvas(canvas):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(canvas, interpolation='nearest')
    ax.set_xticks([])
    ax.set_yticks([])
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

# Función para el panel de administración
def admin_panel():
    st.title("Panel de Administración de r/place")
    draw_canvas(st.session_state.canvas)

    if st.button("Reiniciar Lienzo"):
        st.session_state.canvas = np.ones((GRID_SIZE, GRID_SIZE, 3))  # Reiniciar a blanco
        st.success("Lienzo reiniciado con éxito.")

# Función principal
def main():
    st.sidebar.title("Menú")
    option = st.sidebar.radio("Selecciona una opción", ["Pintar", "Administración"])

    # Comprobar el estado de autenticación
    if 'user' not in st.session_state:
        # URL de autorización
        params = {
            'client_id': DISCORD_CLIENT_ID,
            'redirect_uri': DISCORD_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'identify',
        }
        auth_url = f'https://discord.com/api/oauth2/authorize?{urlencode(params)}'
        st.sidebar.markdown(f"[Iniciar sesión con Discord]({auth_url})")
    else:
        st.sidebar.write(f"Bienvenido, {st.session_state.user['username']}!")

    if option == "Pintar":
        # Selector de color
        color = st.color_picker('Selecciona un color', '#000000')
        selected_color = np.array([int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]) / 255

        selected_row = st.selectbox('Selecciona la fila (letra)', [chr(i) for i in range(65, 65 + GRID_SIZE)])  # A-T
        selected_col = st.selectbox('Selecciona la columna (número)', [str(i) for i in range(1, GRID_SIZE + 1)])  # 1-20

        row_idx = ord(selected_row) - 65
        col_idx = int(selected_col) - 1

        WAIT_TIME = 15
        current_time = time.time()

        if st.button('Pintar'):
            time_since_last_paint = current_time - st.session_state.last_paint_time
            if time_since_last_paint >= WAIT_TIME:
                st.session_state.canvas[row_idx, col_idx] = selected_color
                st.session_state.last_paint_time = current_time
            else:
                st.error(f"Debes esperar {WAIT_TIME - int(time_since_last_paint)} segundos antes de pintar de nuevo.")

        draw_canvas(st.session_state.canvas)

    elif option == "Administración":
        admin_panel()

    # Manejar el callback de Discord
    if 'code' in st.experimental_get_query_params():
        code = st.experimental_get_query_params()['code'][0]
        token_info = get_access_token(code)
        if 'access_token' in token_info:
            access_token = token_info['access_token']
            user_info = get_user_info(access_token)
            st.session_state.user = user_info  # Guardar información del usuario

if __name__ == "__main__":
    main()
