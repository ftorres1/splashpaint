import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json

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

# Función para la página de pintura
def paint_page():
    st.title("Pinta en el lienzo")

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
    # Menú de navegación
    menu = st.sidebar.selectbox("Selecciona una opción", ["Inicio", "Pintar"])

    if menu == "Pintar":
        paint_page()
    elif menu == "Inicio":
        home_page()

# Ejecutamos la aplicación
if __name__ == "__main__":
    main()
