import streamlit as st
from streamlit_google_auth import Authenticate
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- 1. AUTHENTIFICATION GOOGLE ---
# Utilise le fichier JSON que tu viens de créer
authenticator = Authenticate(
    secret_path='google_credentials.json',
    cookie_name='ia_kln_session',
    cookie_key='une_phrase_tres_longue_et_securisee_kln', # Tu peux laisser ça
    redirect_uri='https://ia-kln.streamlit.app',
)

# Vérification de la connexion
authenticator.check_authentification()

# Si l'utilisateur n'est pas connecté, on affiche l'accueil et le bouton Login
if not st.session_state.get('connected'):
    st.set_page_config(page_title="IA KLN - Connexion", page_icon="🔐")
    st.title("IA KLN 🤖")
    st.write("Bienvenue Killian. Connecte-toi avec Google pour accéder à ton IA.")
    authenticator.login()
    st.stop()

# --- 2. SI CONNECTÉ : CONFIGURATION ---
user_info = st.session_state['user_info']
user_id = user_info.get('id')
user_name = user_info.get('name')

st.set_page_config(page_title=f"IA KLN - {user_name}", page_icon="🤖", layout="centered")

# --- STYLE DARK ---
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #ffffff; }
    .stSidebar { background-color: #1e1f20; }
    </style>
    """, unsafe_allow_html=True)

# Tes Clés API (Pense à mettre ta clé Tavily)
GROQ_KEY = "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"
TAVILY_KEY = "tvly-XXXXXXXXXXXX" # <--- METS TA CLÉ TAVILY ICI

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

# Fichier mémoire UNIQUE par utilisateur Google
FICHIER_MEMOIRE = f"memoire_{user_id}.json"
SYSTEM_PROMPT = f"Tu es IA KLN, l'assistant de {user_name}. Réponds toujours en français. Tu as accès au web."

# --- 3. GESTION DE LA MÉMOIRE ---
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

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    st.image(user_info.get('picture'), width=50)
    st.write(f"Salut, {user_name} !")
    
    if st.button("➕ Nouveau Chat"):
        nom = f"Discussion {len(st.session_state.tous_chats) + 1}"
        st.session_state.tous_chats[nom] = []
        st.session_state.chat_actuel = nom
        st.rerun()
    
    st.divider()
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
    authenticator.logout()

# --- 5. ZONE DE CHAT ---
messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]
for msg in messages_actuels:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

uploaded_file = st.file_uploader("📷 Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
if uploaded_file: st.image(uploaded_file, width=200)

if prompt := st.chat_input("Pose ta question..."):
    # Renommer le chat au premier message
    if not messages_actuels and st.session_state.chat_actuel.startswith("Nouveau Chat"):
        st.session_state.tous_chats[prompt[:20]] = st.session_state.tous_chats.pop(st.session_state.chat_actuel)
        st.session_state.chat_actuel = prompt[:20]

    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    reponse_ia = ""
    with st.chat_message("assistant"):
        # Recherche Web si nécessaire
        context_web = ""
        mots_cles = ["match", "score", "météo", "prix", "aujourd'hui", "actu", "quand"]
        if any(m in prompt.lower() for m in mots_cles):
            with st.spinner("Recherche web..."):
                search = tavily.search(query=prompt)
                context_web = f"\n\nInfos Web : {search}"

        # Vision ou Texte
        if uploaded_file:
            img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            res = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role":"system","content":SYSTEM_PROMPT},
                          {"role":"user","content":[{"type":"text","text":prompt + context_web},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]
            )
            reponse_ia = res.choices[0].message.content
        else:
            historique = [{"role": "system", "content": SYSTEM_PROMPT + context_web}] + messages_actuels
            stream = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=historique, stream=True)
            placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    reponse_ia += chunk.choices[0].delta.content
                    placeholder.markdown(reponse_ia + "▌")
        
        placeholder.markdown(reponse_ia)

    if reponse_ia:
        messages_actuels.append({"role": "assistant", "content": reponse_ia})
        st.session_state.tous_chats[st.session_state.chat_actuel] = messages_actuels
        sauvegarder_chats(st.session_state.tous_chats)
        st.rerun()
