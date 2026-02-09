import streamlit as st
from streamlit_google_oauth import login_button

# Clés en dur pour éviter les erreurs de fichiers JSON
ID = "1067398544382-cnf0oaqct1u8dkukken7ergftk7k8jut.apps.googleusercontent.com"
SECRET = "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"

st.title("IA KLN 🤖")

if "connected" not in st.session_state:
    st.session_state.connected = False

if not st.session_state.connected:
    # L'URL doit être EXACTEMENT celle-là
    user_data = login_button(ID, SECRET, "https://killian.streamlit.app")
    if user_data:
        st.session_state.connected = True
        st.session_state.user = user_data
        st.rerun()
else:
    st.write(f"Bravo {st.session_state.user['name']}, tu es connecté !")
    if st.button("Déconnexion"):
        st.session_state.connected = False
        st.rerun()
