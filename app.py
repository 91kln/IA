import streamlit as st
from streamlit_google_auth import Authenticate
from groq import Groq
from tavily import TavilyClient

# --- CONFIGURATION DES CLÉS ---
CLIENT_ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
CLIENT_SECRET = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

# --- AUTHENTIFICATION GOOGLE ---
# On crée l'objet d'authentification manuellement pour éviter les bugs
if 'connected' not in st.session_state:
    st.session_state.connected = False

authenticator = Authenticate(
    secret_path=None, # On ne passe pas par le JSON pour éviter les erreurs de chemin
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="https://killian.streamlit.app",
    cookie_name="ia_kln_cookie",
    cookie_key="secret_cookie_kln_2026",
)

# Vérifie si l'utilisateur vient de se connecter
authenticator.check_authentification()

if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Connecte-toi avec Google pour accéder à ton IA.")
    authenticator.login()
    st.stop()

# --- INTERFACE IA (Si connecté) ---
user_name = st.session_state.user_info.get('name', 'Killian')
st.sidebar.write(f"Salut {user_name} !")
if st.sidebar.button("Déconnexion"):
    authenticator.logout()

# Initialisation Groq et Tavily
client = Groq(api_key="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")
tavily = TavilyClient(api_key="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")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Dis-moi tout..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        search = tavily.search(query=prompt)
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Tu es IA KLN. Web: {search}"}] + st.session_state.messages
        )
        response = res.choices[0].message.content
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
