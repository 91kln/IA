import streamlit as st
from streamlit_google_oauth import login_button
from groq import Groq
from tavily import TavilyClient

# --- TES CLÉS ---
CLIENT_ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
CLIENT_SECRET = "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"
GROQ_KEY = "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"
TAVILY_KEY = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

if "connected" not in st.session_state:
    st.session_state.connected = False

# --- ÉCRAN DE CONNEXION GOOGLE ---
if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Connecte-toi avec Google pour accéder à l'IA.")
    
    # Utilisation du bouton Google officiel
    login_info = login_button(CLIENT_ID, CLIENT_SECRET, "https://killian.streamlit.app")
    
    if login_info:
        st.session_state.connected = True
        st.session_state.user_info = login_info
        st.rerun()
    st.stop()

# --- INTERFACE IA (UNE FOIS CONNECTÉ) ---
user_name = st.session_state.user_info.get('name', 'Killian')
st.sidebar.write(f"Connecté : **{user_name}**")
if st.sidebar.button("Déconnexion"):
    st.session_state.connected = False
    st.rerun()

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
        with st.spinner("Recherche..."):
            try:
                search = tavily.search(query=prompt)
                context = f"\n\nInfos Web : {search}"
            except:
                context = ""
        
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": f"Tu es IA KLN assistant de {user_name}." + context}] + st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
