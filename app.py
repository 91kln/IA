refait le code en entier je te r'envoie mon code 

import streamlit as st
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN - Live", page_icon="🌐", layout="centered")
st.markdown("<style>.stApp { background-color: #131314; color: #ffffff; }</style>", unsafe_allow_html=True)

# Tes Clés
GROQ_KEY = "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"
TAVILY_KEY = "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" # <--- METS TA CLÉ ICI

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = "multi_chats_kln.json"

SYSTEM_PROMPT = "Tu es IA KLN. Tu as accès au web. Si une question demande une info récente (sport, actu, dates), utilise les données de recherche fournies pour répondre en français."

# --- GESTION MÉMOIRE ---
def charger_tous_les_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        with open(FICHIER_MEMOIRE, "r") as f: return json.load(f)
    return {"Nouveau Chat": []}

def sauvegarder_tous_les_chats(chats):
    with open(FICHIER_MEMOIRE, "w") as f: json.dump(chats, f)

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
        if st.button(nom_chat, key=f"s_{nom_chat}", use_container_width=True):
            st.session_state.chat_actuel = nom_chat
            st.rerun()

# --- CHAT ---
messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]
for msg in messages_actuels:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

st.divider()
uploaded_file = st.file_uploader("➕ Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Pose n'importe quelle question..."):
    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    reponse_ia = ""
    with st.chat_message("assistant"):
        # 1. Recherche Web si besoin
        context_web = ""
        mots_cles_actu = ["match", "quand", "aujourd'hui", "score", "météo", "prix", "nouvelle", "pop up"]
        if any(mot in prompt.lower() for mot in mots_cles_actu):
            with st.spinner("Recherche sur le web..."):
                search_res = tavily.search(query=prompt, search_depth="advanced")
                context_web = "\n\nInfos trouvées sur le web : " + str(search_res)

        # 2. Vision ou Texte
        if uploaded_file:
            img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
            res = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "system", "content": SYSTEM_PROMPT},
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
        sauvegarder_tous_les_chats(st.session_state.tous_chats)
