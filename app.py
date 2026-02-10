import streamlit as st
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="IA KLN", page_icon="🤖", layout="centered")

# Design Simple et Propre (Pas de colonnes pour éviter les bugs sur téléphone)
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    [data-testid="stChatMessage"] { border-radius: 15px; border: 1px solid #30363d; }
    section[data-testid="stSidebar"] { background-color: #161B22 !important; }
</style>
""", unsafe_allow_html=True)

# Tes Clés Validées
GROQ_KEY = "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"
TAVILY_KEY = "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"

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = "multi_chats_kln.json"

# --- 2. GESTION MÉMOIRE ---
def charger_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        try:
            with open(FICHIER_MEMOIRE, "r") as f: return json.load(f)
        except: return {"Nouveau Chat": []}
    return {"Nouveau Chat": []}

def sauvegarder_chats(chats):
    try:
        chats_propres = {}
        for nom, msgs in chats.items():
            chats_propres[nom] = [{"role": m["role"], "content": str(m["content"])} for m in msgs]
        with open(FICHIER_MEMOIRE, "w") as f: json.dump(chats_propres, f)
    except: pass

if "tous_chats" not in st.session_state: st.session_state.tous_chats = charger_chats()
if "chat_actuel" not in st.session_state: st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

# --- 3. MENU (SIDEBAR) ---
with st.sidebar:
    st.title("IA KLN 🤖")
    mode_maths = st.toggle("📐 Mode Expert Maths")
    st.divider()
    if st.button("➕ Nouveau Chat", use_container_width=True):
        nom = f"Discussion {len(st.session_state.tous_chats) + 1}"
        st.session_state.tous_chats[nom] = []
        st.session_state.chat_actuel = nom
        st.rerun()
    st.divider()
    for nom_chat in list(st.session_state.tous_chats.keys()):
        if st.button(nom_chat, key=f"s_{nom_chat}", use_container_width=True):
            st.session_state.chat_actuel = nom_chat
            st.rerun()
    st.divider()
    if st.button("🗑️ Vider ce chat", type="primary", use_container_width=True):
        st.session_state.tous_chats[st.session_state.chat_actuel] = []
        sauvegarder_chats(st.session_state.tous_chats)
        st.rerun()

# --- 4. CHAT ---
st.title(f"📍 {st.session_state.chat_actuel}")

prompt_final = "Tu es IA KLN. Réponds en français."
if mode_maths:
    prompt_final += " MODE MATHS : Utilise LaTeX et sois très détaillé."

messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]
for msg in messages_actuels:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

st.divider()
uploaded_file = st.file_uploader("📷 Image", type=["jpg", "png", "jpeg"])

if prompt := st.chat_input("Pose ta question..."):
    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    reponse_ia = ""
    with st.chat_message("assistant"):
        context_web = ""
        if any(m in prompt.lower() for m in ["match", "score", "météo", "actu"]):
            with st.spinner("Recherche web..."):
                try:
                    res = tavily.search(query=prompt)
                    context_web = f"\n\n[Web : {res}]"
                except: pass

        try:
            if uploaded_file:
                img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{"role": "system", "content": prompt_final},
                              {"role":"user","content":[{"type":"text","text":prompt + context_web},
                                                       {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]
                )
                reponse_ia = res.choices[0].message.content
                st.markdown(reponse_ia)
            else:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": prompt_final + context_web}] + messages_actuels,
                    stream=True
                )
                reponse_ia = st.write_stream(stream)
        except Exception as e:
            st.error(f"Erreur : {e}")

    if reponse_ia:
        messages_actuels.append({"role": "assistant", "content": reponse_ia})
        st.session_state.tous_chats[st.session_state.chat_actuel] = messages_actuels
        sauvegarder_chats(st.session_state.tous_chats)
