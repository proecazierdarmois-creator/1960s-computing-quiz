import streamlit as st
import requests
import json

# ---------------------------------------------------
# 🔧 CONFIG FIREBASE
# ---------------------------------------------------
FIREBASE_API_KEY = "AIzaSyAwnYSZooGNchbW7APmeykNP8SuuRGVc1Q"   # ← Mets ta vraie clé ici


# ---------------------------------------------------
# 🔐 FONCTIONS AUTH FIREBASE (REST API)
# ---------------------------------------------------

# Email + Password : REGISTER
def firebase_register(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    res = requests.post(url, json=data)
    return res.json()


# Email + Password : LOGIN
def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    res = requests.post(url, json=data)
    return res.json()


# Google Provider : LOGIN (token manuel)
def firebase_google_login(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_API_KEY}"
    data = {
        "postBody": f"id_token={id_token}&providerId=google.com",
        "requestUri": "http://localhost",
        "returnIdpCredential": True,
        "returnSecureToken": True
    }
    res = requests.post(url, json=data)
    return res.json()


# ---------------------------------------------------
# 🧠 SESSION UTILISATEUR
# ---------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "step" not in st.session_state:
    st.session_state.step = 0


# ---------------------------------------------------
# 🔐 LOGIN / REGISTER UI
# ---------------------------------------------------
if st.session_state.user is None:

    st.title("🔐 Login / Register (Firebase)")

    tab_login, tab_register, tab_google = st.tabs(["Login", "Register", "Google Login"])

    # ---------------- LOGIN ----------------
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


    # ---------------- GOOGLE PROVIDER ----------------
    with tab_google:
        st.write("Pour Google Login, colle ici ton **ID Token Google** (fourni par Firebase).")

        google_token = st.text_input("Google ID Token")

        if st.button("Login with Google"):
            res = firebase_google_login(google_token)

            if "idToken" in res:
                st.session_state.user = res
                st.success("Connexion Google réussie !")
                st.rerun()
            else:
                st.error("Erreur Google Login")

    st.stop()


# ---------------------------------------------------
# 🎉 UTILISATEUR CONNECTÉ
# ---------------------------------------------------
st.sidebar.title("User Menu")
st.sidebar.write(f"👤 Connecté en tant que : {st.session_state.user.get('email', 'Google User')}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.session_state.step = 0
    st.session_state.score = 0
    st.rerun()

st.title("🎮 Quiz : Computing 1960s")


# ---------------------------------------------------
# 📚 QUIZ QUESTIONS
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
