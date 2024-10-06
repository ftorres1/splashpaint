import os
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
import time

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
    ax.set_xticks([])  # Quitar las marcas del eje X
    ax.set_yticks([])  # Quitar las marcas del eje Y
    st.pyplot(fig)

# Función para la página de pintura
def paint_page():
    st.title("Pinta en el lienzo")
    st.write("Puedes pintar en el lienzo seleccionando un color y eligiendo una posición.")
    
    # Mostrar el lienzo
    draw_canvas()

    # Cooldown para limitar la frecuencia de pintura (15 segundos entre cada acción de pintura)
    if 'last_paint_time' not in st.session_state:
        st.session_state.last_paint_time = 0

    time_since_last_paint = time.time() - st.session_state.last_paint_time

    if time_since_last_paint < 15:
        st.warning(f"Debes esperar {int(15 - time_since_last_paint)} segundos antes de pintar de nuevo.")
    else:
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
            
            # Actualizar el tiempo del último pintado
            st.session_state.last_paint_time = time.time()

# Lógica principal de la aplicación
def main():
    st.sidebar.title("Opciones de Pintura")
    paint_page()

if __name__ == '__main__':
    main()
