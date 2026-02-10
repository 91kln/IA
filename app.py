import streamlit as st
from groq import Groq
from tavily import TavilyClient

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN", page_icon="🤖")

# Clés Validées
GROQ_KEY = "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"
TAVILY_KEY = "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"

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

st.title("IA KLN 🤖")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Dis-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # L'IA répond ici
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es IA KLN, réponds en français."}] + st.session_state.messages,
            stream=True
        )
        # Cette ligne magique transforme les "chunks" techniques en texte lisible
        reponse_finale = st.write_stream(stream)
    
    st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
