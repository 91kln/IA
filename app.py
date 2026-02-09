import streamlit as st
try:
    from streamlit_google_oauth import login_button
except ImportError:
    st.error("Installation en cours... Patiente 1 minute et rafraîchis la page.")
    st.stop()

from groq import Groq
from tavily import TavilyClient

# --- CONFIGURATION (Tes clés vérifiées) ---
CLIENT_ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
CLIENT_SECRET = "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"
GROQ_KEY = "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"
TAVILY_KEY = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

if "connected" not in st.session_state:
    st.session_state.connected = False

# --- SYSTÈME DE CONNEXION ---
if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Clique sur le bouton pour te connecter avec Google :")
    
    # On utilise ton URL finale killian.streamlit.app
    login_data = login_button(CLIENT_ID, CLIENT_SECRET, "https://killian.streamlit.app")
    
    if login_data:
        st.session_state.connected = True
        st.session_state.user_info = login_data
        st.rerun()
    st.stop()

# --- INTERFACE IA ---
st.success(f"Bienvenue {st.session_state.user_info.get('name')} !")

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
        # Recherche web rapide
        search = tavily.search(query=prompt)
        # Réponse IA
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Tu es IA KLN. Web: {search}"}] + st.session_state.messages
        )
        response = chat_completion.choices[0].message.content
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
