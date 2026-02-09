import streamlit as st
from streamlit_google_oauth import login_button
from groq import Groq
from tavily import TavilyClient
import json
import os

# --- 1. CONFIGURATION (Tes clés sont ici) ---
CLIENT_ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
CLIENT_SECRET = "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"
GROQ_KEY = "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"
TAVILY_KEY = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

# --- 2. GESTION CONNEXION ---
if "connected" not in st.session_state:
    st.session_state.connected = False

if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Connecte-toi avec Google pour accéder à ton IA.")
    
    # URL EXACTE DE TON SITE
    login_data = login_button(CLIENT_ID, CLIENT_SECRET, "https://killian.streamlit.app")
    
    if login_data:
        st.session_state.connected = True
        st.session_state.user_info = login_data
        st.rerun()
    st.stop()

# --- 3. INTERFACE IA (Connecté) ---
user_name = st.session_state.user_info.get('name', 'Killian')
st.sidebar.write(f"Utilisateur : {user_name}")

if st.sidebar.button("Déconnexion"):
    st.session_state.connected = False
    st.rerun()

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Zone d'écriture
if prompt := st.chat_input("Pose ta question à IA KLN..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context_web = ""
        # Recherche web auto pour l'actualité
        mots_cles = ["match", "score", "foot", "actu", "meteo", "quand", "aujourd'hui"]
        if any(m in prompt.lower() for m in mots_cles):
            with st.spinner("Recherche web..."):
                try:
                    search = tavily.search(query=prompt)
                    context_web = f"\n\n[Infos Web : {search}]"
                except:
                    context_web = ""
        
        # Réponse IA
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Tu es IA KLN. L'utilisateur est {user_name}." + context_web}] + st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
