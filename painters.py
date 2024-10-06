import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Inicializamos el lienzo como una matriz de colores (en blanco)
GRID_SIZE = 20
if 'canvas' not in st.session_state:
    st.session_state.canvas = np.ones((GRID_SIZE, GRID_SIZE, 3))  # Blanco (1,1,1 en RGB)

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
        st.session_state.canvas[y, x] = np.array([int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]) / 255
        
    # Mostrar el lienzo
    draw_canvas()

# Función para la página de inicio
def home_page():
    st.title("¡Bienvenido a SplashPlace!")
    st.write("SplashPlace es un lienzo colaborativo entre mas usuarios, con el proposito de que todos se pongan de acuerdo para crear algo realmente impresionante")
    st.write("Utiliza el menú para navegar a la página de pintura. En caso de estar en dispositivos moviles, toca la flecha de hasta arriba a la izquierda de tu pantalla, tambien debes de iniciar sesion en el menu para colocar pixeles")
    st.write("Si quieres ver los registros publicos, unete a nuestro servidor de Discord oficial! https://discord.gg/EQ33kn8e5N")

# Función principal
def main():
    # Menú de navegación
    menu = st.sidebar.selectbox("Selecciona una opción", ["Inicio", "Pintar"])

    if menu == "Inicio":
        home_page()
    elif menu == "Pintar":
        paint_page()

# Ejecutamos la aplicación
if __name__ == "__main__":
    main()
