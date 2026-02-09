import streamlit as st
from groq import Groq
from tavily import TavilyClient

# Tes identifiants vérifiés (image_919606.png)
ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
GROQ_KEY = "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"
TAVILY_KEY = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

if "connected" not in st.session_state:
    st.session_state.connected = False

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.connected:
    st.title("IA KLN 🤖")
    st.write("Connecte-toi pour activer ton IA privée.")
    
    # Lien Google avec scope 'openid' uniquement (le plus simple pour éviter 403)
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={ID}&"
        f"response_type=token&"
        f"scope=openid&"
        f"redirect_uri=https://killian.streamlit.app"
    )
    
    st.markdown(f'''
        <a href="{auth_url}" target="_self" style="text-decoration:none;">
            <div style="background-color:#4285F4;color:white;padding:15px;border-radius:5px;text-align:center;font-weight:bold;cursor:pointer;">
                Se connecter avec Google
            </div>
        </a>
    ''', unsafe_allow_html=True)
    
    if st.button("Mode Secours (Accès direct)"):
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
                context = f"\n\n[Web : {search}]"
            except: context = ""
            
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es IA KLN. Réponds en français." + context}] + st.session_state.messages,
            stream=True
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
