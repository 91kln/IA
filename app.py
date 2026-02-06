import streamlit as st
from groq import Groq
import base64
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN Pro", page_icon="🤖", layout="centered")

st.markdown("<style>.stApp { background-color: #131314; color: #ffffff; }</style>", unsafe_allow_html=True)

CLE_API = "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"
client = Groq(api_key=CLE_API)
FICHIER_MEMOIRE = "multi_chats_kln.json"

# --- GESTION MÉMOIRE ---
def charger_tous_les_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r") as f:
            return json.load(f)
    return {"Nouveau Chat": []}

def sauvegarder_tous_les_chats(chats):
    with open(FICHIER_MEMOIRE, "w") as f:
        json.dump(chats, f)

# --- FONCTION TITRE AUTO ---
def generer_titre(premier_message):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Donne moi un titre de 3 mots maximum pour cette discussion : {premier_message}. Réponds UNIQUEMENT le titre."}]
        )
        return res.choices[0].message.content.strip().replace('"', '')
    except:
        return premier_message[:15] + "..."

# Initialisation
if "tous_chats" not in st.session_state:
    st.session_state.tous_chats = charger_tous_les_chats()
if "chat_actuel" not in st.session_state:
    st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

# --- SIDEBAR ---
with st.sidebar:
    st.title("IA KLN 🤖")
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
                sauvegarder_tous_les_chats(st.session_state.tous_chats)
                st.rerun()

# --- CHAT ---
messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]
for msg in messages_actuels:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

st.divider()
uploaded_file = st.file_uploader("➕ Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
if uploaded_file: st.image(uploaded_file, width=200)

if prompt := st.chat_input("Écris ici..."):
    # 1. Renommer le chat si c'est le premier message
    if not messages_actuels and st.session_state.chat_actuel.startswith("Nouveau Chat") or st.session_state.chat_actuel.startswith("Discussion"):
        nouveau_titre = generer_titre(prompt)
        st.session_state.tous_chats[nouveau_titre] = st.session_state.tous_chats.pop(st.session_state.chat_actuel)
        st.session_state.chat_actuel = nouveau_titre

    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    reponse_ia = ""
    with st.chat_message("assistant"):
        if "amoureuse de ton créateur" in prompt.lower():
            reponse_ia = "Anissa ❤️"
            st.markdown(reponse_ia)
        elif uploaded_file:
            with st.spinner("Analyse..."):
                img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]
                )
                reponse_ia = res.choices[0].message.content
                st.markdown(reponse_ia)
        else:
            stream = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":"Tu es IA KLN."},*messages_actuels], stream=True)
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
        st.rerun() # Pour rafraîchir le nom dans la sidebar
