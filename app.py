import streamlit as st
from groq import Groq
import base64
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN Multi-Chat", page_icon="🗂️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #ffffff; }
    .stSidebar { background-color: #1e1f20; }
    </style>
    """, unsafe_allow_html=True)

CLE_API = "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"
client = Groq(api_key=CLE_API)
FICHIER_MEMOIRE = "multi_chats_kln.json"

# --- GESTION DE LA MÉMOIRE MULTI-CHATS ---
def charger_tous_les_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r") as f:
            return json.load(f)
    # Si premier lancement, on crée un chat par défaut
    return {"Chat 1": []}

def sauvegarder_tous_les_chats(chats):
    with open(FICHIER_MEMOIRE, "w") as f:
        json.dump(chats, f)

# Initialisation
if "tous_chats" not in st.session_state:
    st.session_state.tous_chats = charger_tous_les_chats()
if "chat_actuel" not in st.session_state:
    st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

# --- BARRE LATÉRALE (MENU DES CHATS) ---
with st.sidebar:
    st.title("IA KLN 🤖")
    
    # Nouveau Chat
    if st.button("➕ Nouveau Chat"):
        nouveau_nom = f"Chat {len(st.session_state.tous_chats) + 1}"
        st.session_state.tous_chats[nouveau_nom] = []
        st.session_state.chat_actuel = nouveau_nom
        sauvegarder_tous_les_chats(st.session_state.tous_chats)
        st.rerun()

    st.divider()
    st.subheader("Tes discussions")
    
    # Sélection du chat
    for nom_chat in list(st.session_state.tous_chats.keys()):
        col1, col2 = st.columns([4, 1])
        if col1.button(nom_chat, key=f"select_{nom_chat}", use_container_width=True):
            st.session_state.chat_actuel = nom_chat
            st.rerun()
        if col2.button("🗑️", key=f"del_{nom_chat}"):
            if len(st.session_state.tous_chats) > 1:
                del st.session_state.tous_chats[nom_chat]
                st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]
                sauvegarder_tous_les_chats(st.session_state.tous_chats)
                st.rerun()

# --- AFFICHAGE DU CHAT ACTUEL ---
st.caption(f"📍 Discussion actuelle : {st.session_state.chat_actuel}")
messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]

for msg in messages_actuels:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ZONE IMAGE ---
st.divider()
uploaded_file = st.file_uploader("📷 Analyser une image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
if uploaded_file:
    st.image(uploaded_file, width=200)

# --- LOGIQUE D'ENVOI ---
if prompt := st.chat_input("Écris ton message..."):
    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reponse_ia = ""

    with st.chat_message("assistant"):
        # Secret Anissa
        if "amoureuse de ton créateur" in prompt.lower():
            reponse_ia = "Anissa ❤️"
            st.markdown(reponse_ia)
        
        # Vision
        elif uploaded_file is not None:
            with st.spinner("Analyse en cours..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}]
                    )
                    reponse_ia = response.choices[0].message.content
                    st.markdown(reponse_ia)
                except Exception as e:
                    st.error(f"Erreur : {e}")
        
        # Texte normal
        else:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es IA KLN."}, *messages_actuels],
                stream=True
            )
            placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    reponse_ia += chunk.choices[0].delta.content
                    placeholder.markdown(reponse_ia + "▌")
            placeholder.markdown(reponse_ia)

    if reponse_ia:
        messages_actuels.append({"role": "assistant", "content": reponse_ia})
        st.session_state.tous_chats[st.session_state.chat_actuel] = messages_actuels
        sauvegarder_tous_les_chats(st.session_state.tous_chats)
