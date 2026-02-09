import streamlit as st
from streamlit_google_oauth import login_button
from groq import Groq
from tavily import TavilyClient
import json
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="IA KLN", page_icon="🤖")

# Tes identifiants Google (directement intégrés pour éviter l'erreur JSON)
CLIENT_ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
CLIENT_SECRET = "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"

# --- 2. CONNEXION ---
if "connected" not in st.session_state:
    st.session_state.connected = False

if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Connecte-toi avec Google pour accéder à ton IA privée.")
    
    # Bouton Google - L'URL doit être celle configurée dans ta console Google
    login_data = login_button(CLIENT_ID, CLIENT_SECRET, "https://killian.streamlit.app")
    
    if login_data:
        st.session_state.connected = True
        st.session_state.user_info = login_data
        st.rerun()
    st.stop()

# --- 3. SI CONNECTÉ : L'IA S'ACTIVE ---
user_info = st.session_state.user_info
user_name = user_info.get('name', 'Killian')
user_id = user_info.get('sub', 'default')

# Tes clés API
GROQ_KEY = "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"
TAVILY_KEY = "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" 

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = f"memoire_{user_id}.json"

# Style Dark Gemini
st.markdown("<style>.stApp { background-color: #131314; color: #ffffff; }</style>", unsafe_allow_html=True)

# Gestion de la mémoire par utilisateur
if "messages" not in st.session_state:
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r") as f: st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

# Barre latérale
with st.sidebar:
    if 'picture' in user_info:
        st.image(user_info['picture'], width=60)
    st.write(f"Salut **{user_name}** !")
    if st.button("🚪 Déconnexion"):
        st.session_state.connected = False
        st.rerun()

# Affichage du chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Zone d'écriture
if prompt := st.chat_input("Pose ta question à IA KLN..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        context_web = ""
        # Déclenchement de la recherche web pour l'actu ou le sport
        mots_cles = ["match", "score", "foot", "actu", "meteo", "quand", "aujourd'hui"]
        if any(m in prompt.lower() for m in mots_cles):
            with st.spinner("Recherche web en temps réel..."):
                try:
                    search = tavily.search(query=prompt)
                    context_web = f"\n\n[Infos Web : {search}]"
                except:
                    context_web = ""
        
        # Réponse de l'IA
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Tu es IA KLN. L'utilisateur est {user_name}." + context_web}] + st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    
    # Sauvegarde
    st.session_state.messages.append({"role": "assistant", "content": response})
    with open(FICHIER_MEMOIRE, "w") as f: json.dump(st.session_state.messages, f)

