import streamlit as st
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- 1. CONFIGURATION & DESIGN PREMIUM ---
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
</style>
""", unsafe_allow_html=True)

# Tes Clés
GROQ_KEY = "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"
TAVILY_KEY = "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"

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = "multi_chats_kln.json"

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

# --- 4. LAYOUT EN COLONNES ---
col_main, col_info = st.columns([3, 1])

with col_info:
    st.subheader("🛠️ Outils & Modes")
    # LE VOICI : L'interrupteur pour le mode maths
    mode_maths = st.toggle("📐 Mode Expert Maths", help="Active une analyse mathématique détaillée")
    
    st.divider()
    st.info("Utilisez **Vision** pour les exercices ou la recherche **Web** pour l'actu.")
    
    if st.button("🗑️ Vider ce chat"):
        st.session_state.tous_chats[st.session_state.chat_actuel] = []
        sauvegarder_tous_les_chats(st.session_state.tous_chats)
        st.rerun()

with col_main:
    st.title(f"📍 {st.session_state.chat_actuel}")
    
    # Adaptation du Prompt selon le mode activé
    prompt_final = "Tu es IA KLN. Tu as accès au web. Réponds en français."
    if mode_maths:
        prompt_final += " MODE MATHS ACTIVÉ : Tu es un expert en mathématiques. Détaille chaque étape de calcul, explique les théorèmes utilisés et utilise le format LaTeX pour les formules."

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
            # Recherche Web
            context_web = ""
            if any(mot in prompt.lower() for mot in ["match", "quand", "aujourd'hui", "score", "météo", "actu"]):
                with st.spinner("Recherche sur le web..."):
                    try:
                        search_res = tavily.search(query=prompt, search_depth="advanced")
                        context_web = "\n\nInfos Web : " + str(search_res)
                    except: pass

            if uploaded_file:
                img = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[{"role": "system", "content": prompt_final},
                              {"role":"user","content":[{"type":"text","text":prompt + context_web},
                                                        {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}]}]
                )
                reponse_ia = res.choices[0].message.content
                st.markdown(reponse_ia)
            else:
                historique = [{"role": "system", "content": prompt_final + context_web}] + messages_actuels
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

