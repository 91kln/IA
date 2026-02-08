import streamlit as st
from streamlit_google_auth import Authenticate
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- 1. CONFIGURATION INITIALE ---
if 'connected' not in st.session_state:
    st.session_state.connected = False

# Initialisation de l'authentification avec ton fichier JSON
authenticator = Authenticate(
    secret_path='google_credentials.json',
    cookie_name='ia_kln_session',
    cookie_key='une_phrase_tres_longue_et_securisee_kln_2026',
    redirect_uri='https://ia-kln.streamlit.app',
)

# Vérification automatique de la session
authenticator.check_authentification()

# --- 2. VERROU DE CONNEXION ---
if not st.session_state.connected:
    st.set_page_config(page_title="IA KLN - Connexion", page_icon="🔐")
    st.title("IA KLN 🤖")
    st.write("### Bienvenue Killian")
    st.write("Veuillez vous connecter avec Google pour accéder à votre interface privée.")
    authenticator.login()
    st.stop() # Bloque l'accès au reste du code

# --- 3. SI CONNECTÉ : RÉCUPÉRATION DES INFOS ---
user_info = st.session_state.get('user_info', {})
user_id = user_info.get('id', 'default')
user_name = user_info.get('name', 'Utilisateur')

st.set_page_config(page_title=f"IA KLN - {user_name}", page_icon="🤖", layout="centered")

# Style Dark Mode
st.markdown("<style>.stApp { background-color: #131314; color: #ffffff; }</style>", unsafe_allow_html=True)

# Clés API (Remets bien TA clé Tavily ici)
GROQ_KEY = "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"
TAVILY_KEY = "tvly-XXXXXXXXXXXX" # <--- TA CLÉ TAVILY ICI

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

# Fichier mémoire UNIQUE par utilisateur Google
FICHIER_MEMOIRE = f"memoire_{user_id}.json"
SYSTEM_PROMPT = f"Tu es IA KLN, l'assistant de {user_name}. Réponds en français. Tu as accès au web."

# --- 4. GESTION DE LA MÉMOIRE ---
def charger_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        try:
            with open(FICHIER_MEMOIRE, "r") as f: return json.load(f)
        except: return {"Nouveau Chat": []}
    return {"Nouveau Chat": []}

def sauvegarder_chats(chats):
    with open(FICHIER_MEMOIRE, "w") as f: json.dump(chats, f)

if "tous_chats" not in st.session_state:
    st.session_state.tous_chats = charger_chats()
if "chat_actuel" not in st.session_state:
    st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

# --- 5. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    if user_info.get('picture'):
        st.image(user_info.get('picture'), width=60)
    st.write(f"**{user_name}**")
    
    if st.button("➕ Nouveau Chat", use_container_width=True):
        nom = f"Discussion {len(st.session_state.tous_chats) + 1}"
        st.session_state.tous_chats[nom] = []
        st.session_state.chat_actuel = nom
        st.rerun()
    
    st.divider()
    st.subheader("Tes discussions")
    for nom_chat in list(st.session_state.tous_chats.keys()):
        col1, col2 = st.columns([4, 1])
        if col1.button(nom_chat, key=f"s_{nom_chat}", use_container_width=True):
            st.session_state.chat_actuel = nom_chat
            st.rerun()
        if col2.button("🗑️", key=f"d_{nom_chat}"):
            if len(st.session_state.tous_chats) > 1:
                del st.session_state.tous_chats[nom_chat]
                st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]
                sauvegarder_chats(st.session_state.tous_chats)
                st.rerun()
    
    st.divider()
    if st.button("🚪 Déconnexion"):
        authenticator.logout()

# --- 6. ZONE DE CHAT ---
messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]

for msg in messages_actuels:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

uploaded_file = st.file_uploader("📷 Analyser une image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
if uploaded_file:
    st.image(uploaded_file, width=200)

if prompt := st.chat_input("Pose ta question à IA KLN..."):
    # Renommer automatiquement le chat au premier message
    if not messages_actuels and st.session_state.chat_actuel.startswith("Nouveau Chat"):
        nouveau_nom = prompt[:25] + "..." if len(prompt) > 25 else prompt
        st.session_state.tous_chats[nouveau_nom] = st.session_state.tous_chats.pop(st.session_state.chat_actuel)
        st.session_state.chat_actuel = nouveau_nom

    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reponse_ia = ""
    with st.chat_message("assistant"):
        # Recherche Web automatique pour l'actualité
        context_web = ""
        mots_clés = ["match", "score", "météo", "prix", "aujourd'hui", "actu", "quand", "qui est"]
        if any(m in prompt.lower() for m in mots_clés):
            with st.spinner("Recherche sur le web..."):
                try:
                    search = tavily.search(query=prompt)
                    context_web = f"\n\n[Infos trouvées sur le Web : {search}]"
                except:
                    context_web = ""

        # Logique Vision ou Texte normal
        try:
            if uploaded_file:
                img_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt + context_web},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}
                    ]
                )
                reponse_ia = res.choices[0].message.content
                st.markdown(reponse_ia)
            else:
                historique = [{"role": "system", "content": SYSTEM_PROMPT + context_web}] + messages_actuels
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=historique,
                    stream=True
                )
                placeholder = st.empty()
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        reponse_ia += chunk.choices[0].delta.content
                        placeholder.markdown(reponse_ia + "▌")
                placeholder.markdown(reponse_ia)
        except Exception as e:
            st.error(f"Erreur IA : {e}")

    if reponse_ia:
        messages_actuels.append({"role": "assistant", "content": reponse_ia})
        st.session_state.tous_chats[st.session_state.chat_actuel] = messages_actuels
        sauvegarder_chats(st.session_state.tous_chats)
