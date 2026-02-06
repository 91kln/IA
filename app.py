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

# --- INSTRUCTION STRICTE ---
SYSTEM_PROMPT = "Tu es IA KLN, l'assistant personnel de Killian. Tu dois répondre EXCLUSIVEMENT en français, de manière claire et concise. Ne réponds jamais en anglais."

# --- GESTION MÉMOIRE ---
def charger_tous_les_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r") as f: return json.load(f)
    return {"Nouveau Chat": []}

def sauvegarder_tous_les_chats(chats):
    with open(FICHIER_MEMOIRE, "w") as f: json.dump(chats, f)

def generer_titre(premier_message):
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Réponds par un titre de 3 mots en français uniquement."},
                      {"role": "user", "content": f"Titre pour : {premier_message}"}]
        )
        return res.choices[0].message.content.strip().replace('"', '')
    except: return premier_message[:15] + "..."

if "tous_chats" not in st.session_state: st.session_state.tous_chats = charger_tous_les_chats()
if "chat_actuel" not in st.session_state: st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

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
    if not messages_actuels and (st.session_state.chat_actuel.startswith("Nouveau Chat") or st.session_state.chat_actuel.startswith("Discussion")):
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
            with st.spinner("Analyse en français..."):
                img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}
                    ]
                )
                reponse_ia = res.choices[0].message.content
                st.markdown(reponse_ia)
        else:
            # On ajoute le SYSTEM_PROMPT ici pour le texte normal
            historique_avec_system = [{"role": "system", "content": SYSTEM_PROMPT}] + messages_actuels
            stream = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=historique_avec_system, stream=True)
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
        st.rerun()
