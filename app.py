import streamlit as st
from streamlit_google_oauth import login_button
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- 1. CONFIGURATION INITIALE ---
st.set_page_config(page_title="IA KLN", page_icon="🤖", layout="centered")

# Chargement des identifiants depuis ton fichier JSON
try:
    with open('google_credentials.json') as f:
        credentials = json.load(f)
        CLIENT_ID = credentials['web']['1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com']
        CLIENT_SECRET = credentials['web']['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']
except FileNotFoundError:
    st.error("Le fichier google_credentials.json est introuvable sur GitHub.")
    st.stop()

# --- 2. GESTION DE LA CONNEXION ---
if "connected" not in st.session_state:
    st.session_state.connected = False

if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Bienvenue Killian. Connecte-toi avec Google pour accéder à ton espace.")
    
    # Le bouton de connexion Google
    # L'URL doit être EXACTEMENT celle de ton site Streamlit
    login_data = login_button(CLIENT_ID, CLIENT_SECRET, "https://ia-kln.streamlit.app")
    
    if login_data:
        st.session_state.connected = True
        st.session_state.user_info = login_data
        st.rerun()
    st.stop()

# --- 3. SI CONNECTÉ : ACCÈS À L'IA ---
user_info = st.session_state.user_info
user_name = user_info.get('name', 'Utilisateur')
user_id = user_info.get('sub', 'default') # ID unique Google

# Style Dark Gemini
st.markdown("<style>.stApp { background-color: #131314; color: #ffffff; }</style>", unsafe_allow_html=True)

# Tes Clés API (Remets bien TA vraie clé Tavily !)
GROQ_KEY = "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"
TAVILY_KEY = "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" 

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = f"memoire_{user_id}.json"

# --- 4. CHARGEMENT DE LA MÉMOIRE ---
if "messages" not in st.session_state:
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

# Barre latérale avec infos utilisateur
with st.sidebar:
    if 'picture' in user_info:
        st.image(user_info['picture'], width=60)
    st.write(f"Connecté en tant que : **{user_name}**")
    if st.button("🚪 Déconnexion"):
        st.session_state.connected = False
        st.rerun()

# --- 5. INTERFACE DE CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Recherche web automatique pour les infos récentes
        context_web = ""
        mots_clés = ["match", "score", "météo", "actu", "quand", "aujourd'hui"]
        if any(m in prompt.lower() for m in mots_clés):
            with st.spinner("Recherche web en cours..."):
                search = tavily.search(query=prompt)
                context_web = f"\n\nInfos récentes du Web : {search}"
        
        # Réponse de l'IA (Llama 3.3)
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Tu es IA KLN. L'utilisateur est {user_name}. Réponds en français." + context_web}] + st.session_state.messages,
            stream=True
        )
        full_response = st.write_stream(stream)
    
    # Sauvegarde automatique
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    with open(FICHIER_MEMOIRE, "w") as f:
        json.dump(st.session_state.messages, f)
