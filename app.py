import streamlit as st
from groq import Groq
from tavily import TavilyClient

# --- CONFIGURATION (Tes infos 100% validées) ---
CLIENT_ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
CLIENT_SECRET = "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" # Ta nouvelle clé secrète
GROQ_KEY = "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"
TAVILY_KEY = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

if "connected" not in st.session_state:
    st.session_state.connected = False

# --- SYSTÈME DE CONNEXION ---
if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("L'application est en ligne ! Connecte-toi pour commencer.")
    
    # Construction de l'URL Google ultra-précise
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={CLIENT_ID}&"
        f"response_type=token&"
        f"scope=openid%20email%20profile&"
        f"redirect_uri=https://killian.streamlit.app"
    )
    
    st.markdown(f'''
        <a href="{auth_url}" target="_self" style="text-decoration:none;">
            <div style="background-color:#4285F4;color:white;padding:15px;border-radius:5px;text-align:center;font-weight:bold;cursor:pointer;">
                Se connecter avec Google
            </div>
        </a>
    ''', unsafe_allow_html=True)
    
    # Bouton de secours au cas où Google met du temps à valider la redirection
    if st.button("Activer l'IA (Mode direct)"):
        st.session_state.connected = True
        st.rerun()
    st.stop()

# --- INTERFACE IA ---
st.title("IA KLN 🤖")
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
        with st.spinner("Recherche web..."):
            try:
                search = tavily.search(query=prompt)
                context = f"\n\n[Recherche Web : {search}]"
            except: context = ""
            
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es IA KLN assistant de Killian. Réponds toujours en français." + context}] + st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
