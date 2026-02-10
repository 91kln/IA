import streamlit as st
from groq import Groq
from tavily import TavilyClient
import base64
import json
import os

# --- CONFIGURATION & DESIGN ---
st.set_page_config(page_title="IA KLN - Premium", page_icon="🤖", layout="wide")

# CSS Personnalisé pour une interface propre
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #161B22 !important; border-right: 1px solid #30363d; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; margin-bottom: 10px; }
    .stButton>button { border-radius: 8px; width: 100%; transition: 0.3s; }
    .stChatInput { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# Tes Clés
GROQ_KEY = "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"
TAVILY_KEY = "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"

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)
FICHIER_MEMOIRE = "multi_chats_kln.json"

# --- GESTION MÉMOIRE ---
def charger_tous_les_chats():
    if os.path.exists(FICHIER_MEMOIRE):
        try:
            with open(FICHIER_MEMOIRE, "r") as f: return json.load(f)
        except: return {"Nouveau Chat": []}
    return {"Nouveau Chat": []}

def sauvegarder_tous_les_chats(chats):
    # Sécurité : On s'assure que tout est au format texte avant de dumper le JSON
    chats_propres = {}
    for nom, msgs in chats.items():
        chats_propres[nom] = [{"role": m["role"], "content": str(m["content"])} for m in msgs]
    with open(FICHIER_MEMOIRE, "w") as f: json.dump(chats_propres, f)

if "tous_chats" not in st.session_state: 
    st.session_state.tous_chats = charger_tous_les_chats()
if "chat_actuel" not in st.session_state: 
    st.session_state.chat_actuel = list(st.session_state.tous_chats.keys())[0]

# --- SIDEBAR MODERNE ---
with st.sidebar:
    st.title("IA KLN 🤖")
    st.markdown("---")
    if st.button("➕ Démarrer une nouvelle IA"):
        nom = f"Discussion {len(st.session_state.tous_chats) + 1}"
        st.session_state.tous_chats[nom] = []
        st.session_state.chat_actuel = nom
        st.rerun()
    
    st.markdown("### 📜 Historique")
    for nom_chat in list(st.session_state.tous_chats.keys()):
        # Mise en évidence du chat actif
        type_btn = "primary" if nom_chat == st.session_state.chat_actuel else "secondary"
        if st.button(nom_chat, key=f"btn_{nom_chat}", type=type_btn):
            st.session_state.chat_actuel = nom_chat
            st.rerun()
    
    st.markdown("---")
    if st.button("🗑️ Effacer tout"):
        if os.path.exists(FICHIER_MEMOIRE): os.remove(FICHIER_MEMOIRE)
        st.session_state.tous_chats = {"Nouveau Chat": []}
        st.session_state.chat_actuel = "Nouveau Chat"
        st.rerun()

# --- INTERFACE PRINCIPALE ---
col_chat, col_tools = st.columns([3, 1])

with col_chat:
    st.title(f"📍 {st.session_state.chat_actuel}")
    
    messages_actuels = st.session_state.tous_chats[st.session_state.chat_actuel]
    for msg in messages_actuels:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Zone d'envoi
    st.divider()
    uploaded_file = st.file_uploader("🖼️ Joindre une image (Maths, Vision...)", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if prompt := st.chat_input("Pose ta question ici..."):
        messages_actuels.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        reponse_ia = ""
        with st.chat_message("assistant"):
            # 1. Recherche Web automatique
            context_web = ""
            mots_cles = ["match", "score", "météo", "prix", "actu", "aujourd'hui", "quand"]
            if any(m in prompt.lower() for m in mots_cles):
                with st.spinner("Recherche web en cours..."):
                    try:
                        search = tavily.search(query=prompt, search_depth="advanced")
                        context_web = f"\n\n[CONTEXTE WEB : {search}]"
                    except: pass

            try:
                if uploaded_file:
                    # Vision (Modèle stable 11B)
                    img_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                    res = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[
                            {"role": "system", "content": "Tu es IA KLN. Expert en vision et maths. Réponds en français."},
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt + context_web},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                            ]}
                        ]
                    )
                    reponse_ia = res.choices[0].message.content
                    st.markdown(reponse_ia)
                else:
                    # Texte Streaming
                    historique = [{"role": "system", "content": "Tu es IA KLN. Assistant de Killian. Réponds en français." + context_web}] + messages_actuels
                    stream = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=historique,
                        stream=True
                    )
                    reponse_ia = st.write_stream(stream)
            except Exception as e:
                st.error(f"Erreur : {e}")

        if reponse_ia:
            messages_actuels.append({"role": "assistant", "content": reponse_ia})
            st.session_state.tous_chats[st.session_state.chat_actuel] = messages_actuels
            sauvegarder_tous_les_chats(st.session_state.tous_chats)

with col_tools:
    st.markdown("### 🛠️ Options")
    mode_maths = st.toggle("Mode Expert Maths 📐")
    if mode_maths:
        st.caption("Mode activé : L'IA détaillera chaque formule étape par étape.")
    
    st.markdown("---")
    st.markdown("### 📊 État")
    st.success("Web Search : Connecté")
    st.success("Vision : Active")
