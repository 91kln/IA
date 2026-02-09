import streamlit as st
from streamlit_google_oauth import login_button
from groq import Groq
from tavily import TavilyClient
import json
import os

# --- 1. TES CODES PRIVÉS ---
CLIENT_ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
CLIENT_SECRET = "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"
GROQ_KEY = "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"
TAVILY_KEY = "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"

# --- 2. CONFIGURATION ---
st.set_page_config(page_title="IA KLN", page_icon="🤖")

if "connected" not in st.session_state:
    st.session_state.connected = False

# --- 3. CONNEXION GOOGLE ---
if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Connecte-toi avec Google pour accéder à ton IA.")
    
    # URL MISE À JOUR : DOIT ÊTRE LA MÊME DANS GOOGLE CLOUD
    login_data = login_button(CLIENT_ID, CLIENT_SECRET, "https://killian.streamlit.app")
    
    if login_data:
        st.session_state.connected = True
        st.session_state.user_info = login_data
        st.rerun()
    st.stop()

# --- 4. INTERFACE CHAT ---
user_name = st.session_state.user_info.get('name', 'Killian')
st.sidebar.write(f"Salut {user_name} !")

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        # Recherche web auto
        context_web = ""
        if any(w in prompt.lower() for w in ["psg", "foot", "actu", "score"]):
            search = tavily.search(query=prompt)
            context_web = f"\n\n[Infos Web : {search}]"
        
        # Réponse Llama
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es IA KLN." + context_web}] + st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
