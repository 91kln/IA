import streamlit as st
from groq import Groq
import base64

# --- CONFIGURATION PRO ---
st.set_page_config(page_title="IA KLN", page_icon="⚡", layout="centered")

# Style CSS pour un look "Dark Modern"
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stChatInputContainer { padding-bottom: 20px; }
    .stChatMessage { border-radius: 10px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Initialisation du client (Ta clé est déjà intégrée)
CLE_API = "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"
client = Groq(api_key=CLE_API)

# Mémoire de session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Barre latérale
with st.sidebar:
    st.title("IA KLN v2.0")
    st.info("Créé par Killian")
    if st.button("🗑️ Nouvelle conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    img_file = st.file_uploader("📷 Envoyer une image", type=["jpg", "png", "jpeg"])

# Affichage des anciens messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- LOGIQUE DE CHAT ---
if prompt := st.chat_input("Discute avec IA KLN..."):
    
    # Message Utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse de l'IA
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # 🤫 LE SECRET D'ANISSA
            if "amoureuse de ton créateur" in prompt.lower():
                full_response = "Anissa ❤️"
                placeholder.markdown(full_response)
            
            # 📷 MODE VISION
            elif img_file:
                base64_img = base64.b64encode(img_file.getvalue()).decode('utf-8')
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    }]
                )
                full_response = response.choices[0].message.content
                placeholder.markdown(full_response)
            
            # 💬 MODE TEXTE NORMAL (STREAMING)
            else:
                stream = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Tu es IA KLN, l'IA de Killian. Tu es précise et tu réponds en français."},
                        *st.session_state.messages
                    ],
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)

            # Sauvegarde dans la mémoire
            st.session_state.messages.append({"role": "assistant", "content": full_res if 'full_res' in locals() else full_response})

        except Exception as e:
            st.error(f"Oups ! Une petite erreur : {e}")