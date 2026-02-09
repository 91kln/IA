import streamlit as st
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN - Live", page_icon="🌐", layout="centered")
st.markdown("<style>.stApp { background-color: #131314; color: #ffffff; }</style>", unsafe_allow_html=True)

# Tes Clés Validées
GROQ_KEY = "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"
TAVILY_KEY = "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"

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = "multi_chats_kln.json"

SYSTEM_PROMPT = "Tu es IA KLN. Tu as accès au web. Réponds toujours en français."

# --- GESTION MÉMOIRE ---
def charger_tous_les_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        try:
            with open(FICHIER_MEMOIRE, "r") as f:
                return json.load(f)
        except:
            return {"Nouveau Chat": []}
    return {"Nouveau Chat": []}

def sauvegarder_tous_les_chats(chats):
    with open(FICHIER_MEMOIRE, "w") as f:
        json.dump(chats, f)

if "tous_chats" not in st.session_state:
    st.session_state.tous_chats = charger_tous_les_chats()
if "chat_actuel" not in st.session_state:
    st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

# --- SIDEBAR (HISTORIQUE) ---
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
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()
uploaded_file = st.file_uploader("➕ Ajouter une image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if prompt := st.chat_input("Pose n'importe quelle question..."):
    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reponse_ia = ""
    with st.chat_message("assistant"):
        context_web = ""
        mots_actu = ["match", "score", "météo", "actu", "aujourd'hui"]
        if any(m in prompt.lower() for m in mots_actu):
            with st.spinner("Recherche web..."):
                try:
                    search_res = tavily.search(query=prompt)
                    context_web = f"\n\n[Recherche Web : {search_res}]"
                except:
                    pass

        try:
            if uploaded_file:
                # Modèle de vision
                img_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="llama-3.2-90b-vision-preview",
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
                # Modèle texte normal
                historique = [{"role": "system", "content": SYSTEM_PROMPT + context_web}] + messages_actuels
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=historique,
                    stream=True
                )
                reponse_ia = st.write_stream(stream)
        except Exception as e:
            st.error(f"Erreur Groq : {e}")

    # SAUVEGARDE DU TEXTE UNIQUEMENT (pour éviter l'erreur JSON)
    if reponse_ia:
        messages_actuels.append({"role": "assistant", "content": str(reponse_ia)})
        st.session_state.tous_chats[st.session_state.chat_actuel] = messages_actuels
        sauvegarder_tous_les_chats(st.session_state.tous_chats)
