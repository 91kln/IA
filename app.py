import streamlit as st
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- 1. CONFIGURATION & DESIGN (REMPLACÉ) ---
st.set_page_config(page_title="IA KLN - Expert", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    [data-testid="stChatMessage"] {
        border-radius: 20px;
        margin-bottom: 15px;
        padding: 15px;
        border: 1px solid #30363d;
    }
    section[data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid #30363d;
    }
    .stButton>button {
        border-radius: 10px;
        border: 1px solid #30363d;
        background-color: #21262d;
        color: #c9d1d9;
        transition: 0.3s;
    }
    .stButton>button:hover {
        border-color: #8b949e;
        background-color: #30363d;
    }
</style>
""", unsafe_allow_html=True)

# Tes Clés
GROQ_KEY = "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"
TAVILY_KEY = "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"

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = "multi_chats_kln.json"

SYSTEM_PROMPT = "Tu es IA KLN. Tu as accès au web. Si une question demande une info récente, utilise les données fournies pour répondre en français."

# --- 2. GESTION MÉMOIRE ---
def charger_tous_les_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        try:
            with open(FICHIER_MEMOIRE, "r") as f: return json.load(f)
        except: return {"Nouveau Chat": []}
    return {"Nouveau Chat": []}

def sauvegarder_tous_les_chats(chats):
    with open(FICHIER_MEMOIRE, "w") as f: json.dump(chats, f)

if "tous_chats" not in st.session_state: st.session_state.tous_chats = charger_tous_les_chats()
if "chat_actuel" not in st.session_state: st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

# --- 3. SIDEBAR ---
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

# --- 4. LAYOUT AVEC COLONNES ---
col_main, col_info = st.columns([3, 1])

with col_info:
    st.subheader("🛠️ Outils & Infos")
    st.info("Utilisez **Vision** pour les maths ou la recherche **Web** pour l'actu.")
    if st.button("🗑️ Effacer l'historique actuel"):
        st.session_state.tous_chats[st.session_state.chat_actuel] = []
        sauvegarder_tous_les_chats(st.session_state.tous_chats)
        st.rerun()

with col_main:
    st.title(f"📍 {st.session_state.chat_actuel}")
    
    messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]
    for msg in messages_actuels:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    st.divider()
    uploaded_file = st.file_uploader("➕ Image", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

    if prompt := st.chat_input("Pose ta question ici..."):
        messages_actuels.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        reponse_ia = ""
        with st.chat_message("assistant"):
            # Recherche Web
            context_web = ""
            mots_cles_actu = ["match", "quand", "aujourd'hui", "score", "météo", "prix", "nouvelle"]
            if any(mot in prompt.lower() for mot in mots_cles_actu):
                with st.spinner("Recherche sur le web..."):
                    try:
                        search_res = tavily.search(query=prompt, search_depth="advanced")
                        context_web = "\n\nInfos web : " + str(search_res)
                    except: pass

            try:
                if uploaded_file:
                    img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    res = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                                  {"role":"user","content":[{"type":"text","text":prompt + context_web},
                                                           {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]
                    )
                    reponse_ia = res.choices[0].message.content
                    st.markdown(reponse_ia)
                else:
                    historique = [{"role": "system", "content": SYSTEM_PROMPT + context_web}] + messages_actuels
                    stream = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=historique, stream=True)
                    reponse_ia = st.write_stream(stream)
            except Exception as e:
                st.error(f"Erreur : {e}")

        if reponse_ia:
            messages_actuels.append({"role": "assistant", "content": reponse_ia})
            st.session_state.tous_chats[st.session_state.chat_actuel] = messages_actuels
            sauvegarder_tous_les_chats(st.session_state.tous_chats)
