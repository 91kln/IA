import streamlit as st
from groq import Groq
from tavily import TavilyClient
import base64

# --- CONFIGURATION ---
st.set_page_config(page_title="IA KLN", page_icon="🤖")

# Tes Clés validées
GROQ_KEY = "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"
TAVILY_KEY = "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"

client = Groq(api_key=GROQ_KEY)
tavily = TavilyClient(api_key=TAVILY_KEY)

st.title("IA KLN 🤖")

# Mémoire de session (Zéro erreur JSON)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

st.divider()
uploaded_file = st.file_uploader("➕ Ajouter une image", type=["jpg", "png", "jpeg"])

if prompt := st.chat_input("Pose ta question..."):
    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reponse_ia = ""
    with st.chat_message("assistant"):
        # Recherche web
        context_web = ""
        try:
            search = tavily.search(query=prompt)
            context_web = f"\n\n[Infos Web : {search}]"
        except:
            pass

        try:
            if uploaded_file:
                # Modèle Vision ACTIF (Llama 3.2 11B)
                img_b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                res = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {"role": "system", "content": "Tu es IA KLN. Réponds en français."},
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt + context_web},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]}
                    ]
                )
                reponse_ia = res.choices[0].message.content
                st.markdown(reponse_ia)
            else:
