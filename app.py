import streamlit as st
import requests
import json
import urllib.parse

# ---------------------------------------------------
# 🔧 CONFIG FIREBASE + GOOGLE
# ---------------------------------------------------
FIREBASE_API_KEY = "AIzaSyAwnYSZooGNchbW7APmeykNP8SuuRGVc1Q"        # ← Mets ta vraie clé
GOOGLE_CLIENT_ID = "383229073387-jq82lcm8b6mpsu1k4afi4s67hhah8n17.apps.googleusercontent.com"       # ← Mets ton vrai client ID
REDIRECT_URI = "https://1960s-computing-quiz-ijmzegakljwqmpxrd5d83p.streamlit.app/"  # ← Mets ton URL Streamlit Cloud


# ---------------------------------------------------
# 🔐 EXCHANGE GOOGLE CODE → ID TOKEN
# ---------------------------------------------------
def exchange_google_code(code):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": "",
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    res = requests.post(token_url, data=data).json()
    return res.get("id_token")


# ---------------------------------------------------
# 🔐 LOGIN GOOGLE → FIREBASE
# ---------------------------------------------------
def firebase_google_login(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}"
    payload = {
        "postBody": f"id_token={id_token}&providerId=google.com",
        "requestUri": REDIRECT_URI,
        "returnIdpCredential": True,
        "returnSecureToken": True
    }
    res = requests.post(url, json=payload).json()
    return res


# ---------------------------------------------------
# 🔐 LOGIN / REGISTER EMAIL
# ---------------------------------------------------
def firebase_register(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    data = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(url, json=data).json()

def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    data = {"email": email, "password": password, "returnSecureToken": True}
    return requests.post(url, json=data).json()


# ---------------------------------------------------
# 🧠 SESSION
# ---------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "step" not in st.session_state:
    st.session_state.step = 0


# ---------------------------------------------------
# 🔍 CHECK SI GOOGLE A RENVOYÉ UN CODE
# ---------------------------------------------------
query_params = st.query_params

if "code" in query_params:
    code = query_params["code"]
    id_token = exchange_google_code(code)

    if id_token:
        res = firebase_google_login(id_token)
        if "idToken" in res:
            st.session_state.user = res
            st.success("Connexion Google réussie !")
            st.rerun()
        else:
            st.error("Erreur Firebase après Google Login")


# ---------------------------------------------------
# 🔐 LOGIN UI
# ---------------------------------------------------
if st.session_state.user is None:

    st.title("🔐 Connexion")

    tab_login, tab_register, tab_google = st.tabs(["Email Login", "Register", "Google Login"])

    # ---------------- EMAIL LOGIN ----------------
    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = firebase_login(email, password)
            if "idToken" in res:
                st.session_state.user = res
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Email ou mot de passe incorrect")

    # ---------------- REGISTER ----------------
    with tab_register:
        new_email = st.text_input("Nouvel email")
        new_password = st.text_input("Nouveau mot de passe", type="password")

        if st.button("Register"):
            res = firebase_register(new_email, new_password)
            if "idToken" in res:
                st.success("Compte créé ! Vérifie ton email.")
            else:
                st.error("Erreur lors de l'inscription")

    # ---------------- GOOGLE LOGIN ----------------
    with tab_google:

        google_auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={GOOGLE_CLIENT_ID}&"
            f"redirect_uri={REDIRECT_URI}&"
            "response_type=code&"
            "scope=openid%20email%20profile"
        )

        google_button = f"""
        <style>
        .google-btn {{
            display: flex;
            align-items: center;
            gap: 10px;
            background-color: white;
            border: 1px solid #dadce0;
            padding: 10px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            color: #3c4043;
            transition: 0.2s;
        }}
        .google-btn:hover {{
            background-color: #f7f8f8;
        }}
        .google-logo {{
            width: 20px;
            height: 20px;
        }}
        </style>

        <a href="{google_auth_url}">
            <div class="google-btn">
                <img class="google-logo" src="https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg">
                Se connecter avec Google
            </div>
        </a>
        """

        st.markdown(google_button, unsafe_allow_html=True)

    st.stop()


# ---------------------------------------------------
# 🎉 UTILISATEUR CONNECTÉ
# ---------------------------------------------------
st.sidebar.title("Menu")
st.sidebar.write(f"👤 Connecté : {st.session_state.user.get('email', 'Google User')}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.session_state.step = 0
    st.session_state.score = 0
    st.rerun()

st.title("🎮 Quiz : Computing 1960s")


# ---------------------------------------------------
# 📚 QUESTIONS
# ---------------------------------------------------
questions = [
    {
        "question": "Quel ordinateur est considéré comme le premier mini‑ordinateur commercial ?",
        "options": ["IBM 7090", "DEC PDP‑1", "UNIVAC I", "Honeywell 200"],
        "answer": "DEC PDP‑1"
    },
    {
        "question": "Quel langage a été inventé en 1964 au Dartmouth College ?",
        "options": ["C", "BASIC", "Pascal", "COBOL"],
        "answer": "BASIC"
    },
    {
        "question": "Quel système a introduit le concept de 'time‑sharing' ?",
        "options": ["UNIX", "CTSS", "MS‑DOS", "MULTICS"],
        "answer": "CTSS"
    },
    {
        "question": "Quel projet militaire a mené à la création d’ARPANET ?",
        "options": ["DARPA", "NASA", "NSA", "CIA"],
        "answer": "DARPA"
    },
    {
        "question": "Quel ordinateur a été utilisé pour les missions Apollo ?",
        "options": ["IBM System/360", "Apollo Guidance Computer", "PDP‑8", "CDC 6600"],
        "answer": "Apollo Guidance Computer"
    }
]


# ---------------------------------------------------
# 🧩 LOGIQUE DU QUIZ
# ---------------------------------------------------
step = st.session_state.step

if step < len(questions):
    q = questions[step]

    st.subheader(f"Question {step + 1} / {len(questions)}")
    st.write(q["question"])

    choice = st.radio("Choisis une réponse :", q["options"])

    if st.button("Valider"):
        if choice == q["answer"]:
            st.session_state.score += 1
            st.success("Bonne réponse !")
        else:
            st.error(f"Mauvaise réponse ! La bonne réponse était : {q['answer']}")

        st.session_state.step += 1
        st.rerun()

else:
    st.header("🎉 Résultat final")
    st.write(f"Score : **{st.session_state.score} / {len(questions)}**")

    if st.button("Rejouer"):
        st.session_state.step = 0
        st.session_state.score = 0
        st.rerun()
