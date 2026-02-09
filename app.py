import streamlit as st
from groq import Groq
from tavily import TavilyClient

# Tes infos
ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
GROQ_KEY = "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"
TAVILY_KEY = "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"

st.set_page_config(page_title="IA KLN", page_icon="🤖")

if "connected" not in st.session_state:
    st.session_state.connected = False

# --- CONNEXION ---
if not st.session_state.connected:
    st.title("IA KLN 🤖")
    
    # Scope réduit au maximum pour éviter le 403
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
    
    if st.button("Accès Direct (Secours)"):
        st.session_state.connected = True
        st.rerun()
    st.stop()

# --- CHAT IA ---
st.title("IA KLN 🤖")
# ... (le reste du code Groq/Tavily reste identique)
