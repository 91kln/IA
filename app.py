import streamlit as st
from groq import Groq
import base64
from gtts import gTTS
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN Voice", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

CLE_API = "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"
client = Groq(api_key=CLE_API)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("IA KLN 🎙️")
    if st.button("🗑️ Effacer la discussion"):
        st.session_state.messages = []
        st.rerun()

# --- FONCTION VOCALE ---
def parler(texte):
    tts = gTTS(text=texte, lang='fr')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp

# --- AFFICHAGE DU CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Si c'est l'IA, on peut remettre l'audio si besoin (optionnel)

# --- ZONE IMAGE ---
st.divider()
uploaded_file = st.file_uploader("➕ Ajoute une photo", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
if uploaded_file:
    st.image(uploaded_file, width=250)

# --- LOGIQUE D'ENVOI ---
if prompt := st.chat_input("Dis-moi quelque chose..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reponse_finale = ""

    with st.chat_message("assistant"):
        # 1. Cas Secret Anissa
        if "amoureuse de ton créateur" in prompt.lower():
            reponse_finale = "Anissa ❤️"
            st.markdown(reponse_finale)
        
        # 2. Cas Vision
        elif uploaded_file is not None:
            with st.spinner("IA KLN analyse l'image..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]}]
                    )
                    reponse_finale = response.choices[0].message.content
                    st.markdown(reponse_finale)
                except Exception as e:
                    st.error(f"Erreur : {e}")
        
        # 3. Cas Texte Normal
        else:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es IA KLN."}, *st.session_state.messages],
                stream=True
            )
            placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    reponse_finale += chunk.choices[0].delta.content
                    placeholder.markdown(reponse_finale + "▌")
            placeholder.markdown(reponse_finale)

        # --- PARTIE VOCALE (S'affiche sous la réponse) ---
        if reponse_finale:
            st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
            audio_fp = parler(reponse_finale)
            st.audio(audio_fp, format="audio/mp3")
