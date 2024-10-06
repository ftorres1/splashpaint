import streamlit as st
import requests

def main():
    # Comprobar si el usuario ya ha iniciado sesión
    if "user" not in st.session_state:
        # Mostrar el botón de inicio de sesión
        st.button("Iniciar sesión con Discord", on_click=login_with_discord)

    # Aquí va el resto de tu aplicación

def login_with_discord():
    # URL de autorización de Discord
    discord_auth_url = f"https://discord.com/api/oauth2/authorize?client_id={st.secrets['discord']['client_id']}&redirect_uri=http://localhost:8501/callback&response_type=code&scope=identify"
    st.write("Por favor, inicia sesión en Discord haciendo clic en el siguiente enlace:")
    st.write(f"[Iniciar sesión]({discord_auth_url})")

if __name__ == "__main__":
    main()
