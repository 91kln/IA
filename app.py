import streamlit as st
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="IA KLN - Premium", page_icon="🤖", layout="wide")

# CSS pour un look moderne et sombre
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #30363d; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; margin-bottom: 10px; }
    .stButton>button { border-radius: 8px; width: 100%; transition: 0.3s; }
</style>
""", unsafe_allow_html=True)

# Tes Clés
GROQ_KEY = "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"
TAVILY_KEY = "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"

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = "multi_chats_kln.json"

# --- GESTION MÉMOIRE ---
def charger_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        try:
            with open(FICHIER_MEMOIRE, "r") as f: return json.load(f)
        except: return {"Nouveau Chat": []}
    return {"Nouveau Chat": []}

def sauvegarder_chats(chats):
    chats_propres = {}
    for nom, msgs in chats.items():
        # On force la conversion en texte pour éviter l'erreur JSON
        chats_propres[nom] = [{"role": m["role"], "content": str(m["content"])} for m in msgs]
    with open(FICHIER_MEMOIRE, "w") as f: json.dump(chats_propres, f)

if "tous_chats" not in st.session_state: st.session_state.tous_chats = charger_chats()
if "chat_actuel" not in st.session_state: st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

# --- SIDEBAR ---
with st.sidebar:
    st.title("IA KLN 🤖")
    if st.button("➕ Nouvelle IA"):
        nom = f"Discussion {len(st.session_state.tous_chats) + 1}"
        st.session_state.tous_chats[nom] = []
        st.session_state.chat_actuel = nom
        st.rerun()
    st.markdown("---")
    for nom_chat in list(st.session_state.tous_chats.keys()):
        type_btn = "primary" if nom_chat == st.session_state.chat_actuel else "secondary"
        if st.button(nom_chat, key=f"s_{nom_chat}", type=type_btn):
            st.session_state.chat_actuel = nom_chat
            st.rerun()

# --- INTERFACE PRINCIPALE ---
st.title(f"📍 {st.session_state.chat_actuel}")
messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]

for msg in messages_actuels:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

st.divider()
uploaded_file = st.file_uploader("🖼️ Joindre une image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Pose ta question..."):
    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    reponse_ia = ""
    with st.chat_message("assistant"):
        context_web = ""
        # Recherche web si nécessaire
        if any(m in prompt.lower() for m in ["match", "score", "météo", "actu", "aujourd'hui"]):
            with st.spinner("Recherche web..."):
                try:
                    search = tavily.search(query=prompt)
                    context_web = f"\n\n[Infos Web : {search}]"
                except: pass

        try:
            if uploaded_file:
                # Mode Vision
                img_b64 =
