import streamlit as st
from groq import Groq
import base64
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN", page_icon="⚡", layout="centered")

# Style Gemini
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #ffffff; }
    .stChatInputContainer { padding-bottom: 20px; }
    [data-testid="stSidebar"] { background-color: #1e1f20; }
    </style>
    """, unsafe_allow_html=True)

CLE_API = "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"
client = Groq(api_key=CLE_API)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BARRE LATÉRALE (GESTION IMAGE) ---
with st.sidebar:
    st.title("IA KLN")
    st.subheader("Multimodal")
    
    # Le petit "Plus" pour ajouter une image
    uploaded_file = st.file_uploader("➕ Ajouter une image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        # VISUALISATION de l'image avant envoi
        st.image(uploaded_file, caption="Image prête à être envoyée", use_container_width=True)
        if st.button("❌ Supprimer l'image"):
            uploaded_file = None
            st.rerun()

    st.divider()
    if st.button("🗑️ Effacer la discussion"):
        st.session_state.messages = []
        st.rerun()

# --- AFFICHAGE DU CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- LOGIQUE D'ENVOI ---
if prompt := st.chat_input("Décris cette image ou pose une question..."):
    
    # 1. Afficher le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Secret Anissa
    if "amoureuse de ton créateur" in prompt.lower():
        with st.chat_message("assistant"):
            reponse = "Anissa ❤️"
            st.markdown(reponse)
        st.session_state.messages.append({"role": "assistant", "content": reponse})

    # 3. ANALYSE PHOTO (Si une image est chargée)
    elif uploaded_file is not None:
        with st.chat_message("assistant"):
            with st.spinner("IA KLN analyse l'image..."):
                try:
                    # Conversion de l'image en base64
                    bytes_data = uploaded_file.getvalue()
                    base64_image = base64.b64encode(bytes_data).decode('utf-8')
                    
                    # Appel au modèle VISION
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

    # 4. CHAT TEXTE NORMAL
    else:
        with st.chat_message("assistant"):
            try:
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
            except Exception as e:
                st.error(f"Erreur : {e}")
