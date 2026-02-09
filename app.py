import streamlit as st
from streamlit_google_oauth import login_button
from groq import Groq
from tavily import TavilyClient

# --- CONFIGURATION ---
CLIENT_ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
CLIENT_SECRET = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

if "connected" not in st.session_state:
    st.session_state.connected = False

# --- AUTHENTIFICATION ---
if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Connecte-toi avec Google pour accéder à ton IA.")
    
    # Cette fonction est la plus stable. L'URL doit être EXACTEMENT celle de Google Cloud.
    login_info = login_button(CLIENT_ID, CLIENT_SECRET, "https://killian.streamlit.app")
    
    if login_info:
        st.session_state.connected = True
        st.session_state.user_info = login_info
        st.rerun()
    st.stop()

# --- SI CONNECTÉ ---
user_name = st.session_state.user_info.get('name', 'Killian')
st.sidebar.write(f"Connecté : {user_name}")
if st.sidebar.button("Déconnexion"):
    st.session_state.connected = False
    st.rerun()

# IA & Recherche
client = Groq(api_key="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")
tavily = TavilyClient(api_key="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")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Dis-moi tout..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        search = tavily.search(query=prompt)
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Tu es IA KLN. Web: {search}"}] + st.session_state.messages
        )
        response = res.choices[0].message.content
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
