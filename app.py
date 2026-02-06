import streamlit as st
from groq import Groq
import base64
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN - Mémoire", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

CLE_API = "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"
client = Groq(api_key=CLE_API)
FICHIER_MEMOIRE = "memoire_ia.json"

# --- FONCTIONS DE MÉMOIRE ---
def charger_memoire():
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r") as f:
            return json.load(f)
    return []

def sauvegarder_memoire(messages):
    with open(FICHIER_MEMOIRE, "w") as f:
        json.dump(messages, f)

# Initialisation de la session avec le fichier
if "messages" not in st.session_state:
    st.session_state.messages = charger_memoire()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("IA KLN 🧠")
    st.info("Mode Mémoire Longue activé. Vos discussions sont sauvegardées.")
    if st.button("🗑️ Réinitialiser la mémoire"):
        st.session_state.messages = []
        if os.path.exists(FICHIER_MEMOIRE):
            os.remove(FICHIER_MEMOIRE)
        st.rerun()

# --- AFFICHAGE DU CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ZONE IMAGE ---
st.divider()
uploaded_file = st.file_uploader("➕ Ajouter une photo", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
if uploaded_file:
    st.image(uploaded_file, width=250)

# --- LOGIQUE D'ENVOI ---
if prompt := st.chat_input("Dis-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reponse_finale = ""

    with st.chat_message("assistant"):
        # Cas Secret Anissa
        if "amoureuse de ton créateur" in prompt.lower():
            reponse_finale = "Anissa ❤️"
            st.markdown(reponse_finale)
        
        # Cas Vision
        elif uploaded_file is not None:
            with st.spinner("IA KLN analyse l'image..."):
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
                    reponse_finale = response.choices[0].message.content
                    st.markdown(reponse_finale)
                except Exception as e:
                    st.error(f"Erreur Vision : {e}")
        
        # Cas Texte Normal
        else:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es IA KLN."}, *st.session_state.messages],
                stream=True
            )
            placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    reponse_finale += chunk.choices[0].delta.content
                    placeholder.markdown(reponse_finale + "▌")
            placeholder.markdown(reponse_finale)

    # SAUVEGARDE AUTOMATIQUE
    if reponse_finale:
        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
        sauvegarder_memoire(st.session_state.messages)
