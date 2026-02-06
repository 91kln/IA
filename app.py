import streamlit as st
from groq import Groq
import base64

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN", page_icon="⚡", layout="centered")

# Style Gemini
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #ffffff; }
    .stChatInputContainer { padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

CLE_API = "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"
client = Groq(api_key=CLE_API)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("IA KLN")
    if st.button("🗑️ Nouveau Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    # On place l'upload ici pour plus de clarté
    uploaded_file = st.file_uploader("📷 Choisis une image...", type=["jpg", "png", "jpeg"])

# Affichage du chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- LOGIQUE D'ENVOI ---
if prompt := st.chat_input("Discute avec IA KLN..."):
    
    # 1. Secret Anissa
    if "amoureuse de ton créateur" in prompt.lower():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            reponse = "Anissa ❤️"
            st.markdown(reponse)
        st.session_state.messages.append({"role": "assistant", "content": reponse})

    # 2. Analyse d'Image (Vision)
    elif uploaded_file:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            # Transformation de l'image pour l'IA
            bytes_data = uploaded_file.getvalue()
            base64_image = base64.b64encode(bytes_data).decode('utf-8')
            
            try:
                # Utilisation du modèle vision stable llama-3.2-11b
                chat_completion = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }]
                )
                reponse = chat_completion.choices[0].message.content
                st.markdown(reponse)
                st.session_state.messages.append({"role": "assistant", "content": reponse})
            except Exception as e:
                st.error(f"Erreur Vision : {e}")

    # 3. Chat normal (Texte)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es IA KLN."}, *st.session_state.messages],
                stream=True
            )
            full_response = ""
            resp_container = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    resp_container.markdown(full_response + "▌")
            resp_container.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
