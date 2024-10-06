import streamlit as st
import requests

# Función para generar la URL de autenticación
def login_with_discord():
    discord_auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={st.secrets['discord']['client_id']}"
        f"&redirect_uri=https://splashplace.streamlit.app/callback"
        f"&response_type=code"
        f"&scope=identify"
    )
    st.write("Por favor, inicia sesión en Discord haciendo clic en el siguiente enlace:")
    st.write(f"[Iniciar sesión]({discord_auth_url})")

# Función para manejar el callback
def handle_callback():
    if "code" in st.query_params:
        code = st.query_params["code"]
        # Intercambia el código por un token de acceso
        token_url = "https://discord.com/api/oauth2/token"
        data = {
            "client_id": st.secrets["discord"]["client_id"],
            "client_secret": st.secrets["discord"]["client_secret"],
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://splashplace.streamlit.app/callback"
        }
        response = requests.post(token_url, data=data)
        if response.ok:
            access_token = response.json().get("access_token")
            # Obtén la información del usuario
            user_info_url = "https://discord.com/api/users/@me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_info = requests.get(user_info_url, headers=headers)
            if user_info.ok:
                st.session_state.user = user_info.json()
                st.success("Has iniciado sesión correctamente.")
            else:
                st.error("No se pudo obtener información del usuario.")
        else:
            st.error("Error al intercambiar el código por un token.")

# Verifica si el usuario ya está autenticado o si se requiere iniciar sesión
if "user" not in st.session_state:
    login_with_discord()
else:
    st.write("Ya has iniciado sesión como:", st.session_state.user["username"])

# Maneja el callback
handle_callback()
