import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests
from urllib.parse import urlencode

# Configuración de Discord
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = 'https://splashplace.streamlit.app/'  # Ajusta esto con tu URL de Streamlit Cloud
DISCORD_API_URL = 'https://discord.com/api/v10'

# Webhook de Discord
DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1292564820016627855/akZ08vnkPWqHu-__UAxzlgB2f4T6ogyxkK8JoV8qhkB5hYz0i0zQ076JW9NI0Tow7sFe'

# Inicializamos el lienzo como una matriz de colores (en blanco)
GRID_SIZE = 20
if 'canvas' not in st.session_state:
    st.session_state.canvas = np.ones((GRID_SIZE, GRID_SIZE, 3))  # Blanco (1,1,1 en RGB)

# Función para mostrar el lienzo
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

# Función para enviar notificación a Discord
def send_discord_notification(user, position, color):
    message = {
        "content": f"{user['username']} pintó en la posición {position} con el color {color}."
    }
    requests.post(DISCORD_WEBHOOK_URL, json=message)

# Función principal
def main():
    st.sidebar.title("Menú")
    option = st.sidebar.radio("Selecciona una opción", ["Pintar", "Administración"])

    query_params = st.query_params  # Uso actualizado para obtener los parámetros de consulta
    if 'code' in query_params:
        code = query_params['code']
        token_data = get_access_token(code)
        access_token = token_data.get('access_token')

        if access_token:
            user_info = get_user_info(access_token)
            st.session_state.user = user_info
            st.query_params.clear()  # Limpiar los parámetros de consulta después del inicio de sesión
        else:
            st.error("Error al obtener el token de acceso.")

    if 'user' not in st.session_state:
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
        # Lógica de pintura aquí
        color = st.color_picker('Selecciona un color', '#000000')
        selected_color = np.array([int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]) / 255

        selected_row = st.selectbox('Selecciona la fila (letra)', [chr(i) for i in range(65, 65 + GRID_SIZE)])  # A-T
        selected_col = st.selectbox('Selecciona la columna (número)', [str(i) for i in range(1, GRID_SIZE + 1)])  # 1-20

        row_idx = ord(selected_row) - 65
        col_idx = int(selected_col) - 1

        # Lógica para pintar en el lienzo
        if st.button("Pintar"):
            st.session_state.canvas[row_idx, col_idx] = selected_color
            position = f"{selected_row}{selected_col}"
            color_hex = color
            send_discord_notification(st.session_state.user, position, color_hex)  # Notificación a Discord
            st.success("Pintura realizada con éxito.")

        draw_canvas(st.session_state.canvas)

if __name__ == "__main__":
    main()
