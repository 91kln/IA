import streamlit as st
from groq import Groq
from tavily import TavilyClient

# --- CONFIGURATION ---
GROQ_KEY = "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"
TAVILY_KEY = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

# --- SYSTÈME DE SÉCURITÉ SIMPLE ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("IA KLN 🤖")
    password = st.text_input("Entre ton mot de passe Killian :", type="password")
    if password == "kln2026": # Ton mot de passe provisoire
        st.session_state.authenticated = True
        st.rerun()
    st.stop()

# --- INTERFACE IA ---
st.title("IA KLN 🤖")
client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pose ta question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Recherche web
        with st.spinner("Recherche..."):
            search = tavily.search(query=prompt)
            context = f"\n\nInfos Web : {search}"
        
        # Réponse IA
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es IA KLN." + context}] + st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
