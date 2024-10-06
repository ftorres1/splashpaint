import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import requests
import time

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
        st.sidebar.markdown(f"[Iniciar sesión con Discord](https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify)")
    else:
        # Si hay un token, muestra el usuario
        headers = {
            'Authorization': f'Bearer {st.session_state.token}'
        }
        response = requests.get(DISCORD_USER_URL, headers=headers)
        user_data = response.json()
        st.sidebar.write(f"¡Hola, {user_data['username']}!")
        st.sidebar.write("Puedes empezar a pintar en el lienzo.")

# Función para manejar el callback de Discord
def handle_callback():
    query_params = st.query_params
    if 'code' in query_params:
        code = query_params['code'][0]
        data = {
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': DISCORD_REDIRECT_URI,
            'scope': 'identify'
        }
        # Solicitar un token de acceso
        response = requests.post(DISCORD_TOKEN_URL, data=data)
        response_data = response.json()
        st.session_state.token = response_data['access_token']
        st.experimental_rerun()

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
        st.error("Debes iniciar sesión con Discord para poder pintar en el lienzo.")

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
    # Comprobar si el callback de Discord está presente
    handle_callback()
    
    # Menú de navegación
    menu = st.sidebar.selectbox("Visita una página", ["Pintar", "Inicio"])

    # Mostrar la opción para iniciar sesión con Discord
    discord_login()

    if menu == "Pintar":
        paint_page()
    elif menu == "Inicio":
        home_page()

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
