import streamlit as st
from groq import Groq
import base64

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN", page_icon="⚡", layout="centered")

# Style "Ultra Clean" (Barre de texte et bouton image)
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #ffffff; }
    .stChatInputContainer { padding-bottom: 20px; }
    /* Style pour le bouton d'upload */
    div.stFileUploader { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

CLE_API = "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"
client = Groq(api_key=CLE_API)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BARRE LATÉRALE (Uniquement historique) ---
with st.sidebar:
    st.title("IA KLN")
    if st.button("🗑️ Effacer la discussion"):
        st.session_state.messages = []
        st.rerun()

# --- AFFICHAGE DU CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ZONE D'ACTION (Directement dans la discussion) ---
st.divider()
# On met l'uploader ici pour qu'il soit juste au-dessus du texte
uploaded_file = st.file_uploader("➕ Ajouter une photo à analyser", type=["jpg", "png", "jpeg"], label_visibility="collapsed")

if uploaded_file:
    # LA PRÉVISUALISATION : On l'affiche en plein milieu
    st.image(uploaded_file, caption="Image sélectionnée", width=250)

# --- LOGIQUE D'ENVOI ---
if prompt := st.chat_input("Décris cette image ou pose une question..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Secret Anissa
    if "amoureuse de ton créateur" in prompt.lower():
        with st.chat_message("assistant"):
            reponse = "Anissa ❤️"
            st.markdown(reponse)
        st.session_state.messages.append({"role": "assistant", "content": reponse})

    # ANALYSE PHOTO
    elif uploaded_file is not None:
        with st.chat_message("assistant"):
            with st.spinner("IA KLN analyse l'image..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    
                    response = client.chat.completions.create(
                        model="llama-3.2-11b-vision-preview",
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                            ]
                        }]
                    )
                    reponse_ia = response.choices[0].message.content
                    st.markdown(reponse_ia)
                    st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
                except Exception as e:
                    st.error(f"Erreur d'analyse : {e}")

    # CHAT TEXTE
    else:
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Tu es IA KLN."}, *st.session_state.messages],
                stream=True
            )
            full_res = ""
            placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_res += chunk.choices[0].delta.content
                    placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
