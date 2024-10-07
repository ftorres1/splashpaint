import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
import time

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

# Inicializamos el cooldown
if 'last_action_time' not in st.session_state:
    st.session_state.last_action_time = 0

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

    # Verificar si el usuario ha iniciado sesión
    if st.session_state.user is None:
        st.error("Debes iniciar sesión para colocar píxeles.")
        return  # Salimos de la función si el usuario no ha iniciado sesión

    # Verificar cooldown
    current_time = time.time()
    if current_time - st.session_state.last_action_time < 15:
        remaining_time = 15 - (current_time - st.session_state.last_action_time)
        st.error(f"Espera {int(remaining_time)} segundos antes de colocar otro píxel.")
        # Mostrar botón "Continuar" que no hace nada
        st.button("Continuar")
        return  # Salimos de la función si no ha pasado el cooldown
        draw_canvas()

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
        
        # Actualizar el tiempo de la última acción
        st.session_state.last_action_time = time.time()
        
    # Mostrar el lienzo nuevamente
    draw_canvas()

# Función para la página de inicio
def home_page():
    st.title("¡Bienvenido a SplashPlace!")
    st.write("SplashPlace es un lienzo colaborativo para todos los usuarios, con el propósito de que todos se pongan de acuerdo para crear algo realmente impresionante.")
    st.write("Utiliza el menú para navegar a la página de pintura. En caso de estar en dispositivos móviles, toca la flecha de hasta arriba a la izquierda de tu pantalla. También debes de iniciar sesión en el menú para colocar píxeles.")
    st.write("Si quieres ver los registros públicos, [¡únete a nuestro servidor de Discord oficial!](https://discord.gg/EQ33kn8e5)")

    st.title("Términos de Uso")
    st.write("Al colocar tu primer píxel bajo un nombre de usuario o iniciando sesión con Discord, estás comprometiéndote a seguir estas reglas:")
    st.write("1. Sin contenido inapropiado (no dibujar ningún contenido de tipo sexual, gore y demás).")
    st.write("2. Respeto mutuo: Trata a todos los usuarios con respeto. No se tolerarán insultos ni acoso.")
    st.write("3. Colaboración: Este es un espacio colaborativo; respeta las contribuciones de otros.")
    st.write("4. Limitaciones de uso: No intentes explotar o manipular el sistema.")
    st.write("5. Uso de recursos: Limita el uso de la plataforma a actividades artísticas.")
    st.write("6. Responsabilidad: Cada usuario es responsable de su comportamiento en la plataforma.")
    st.write("7. Disfruta y diviértete: Este es un espacio para la creatividad. Disfruta de la experiencia.")

# Función principal
def main():
    # Manejar la autenticación de usuario
    handle_auth()

    # Menú de navegación
    menu = st.sidebar.selectbox("Visita una página", ["Inicio", "Pintar"])

    if menu == "Inicio":
        home_page()
    elif menu == "Pintar":
        paint_page()

# Ejecutamos la función principal
if __name__ == "__main__":
    main()
