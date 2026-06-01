import streamlit as st
import random
import time
from supabase import create_client, Client

SUPABASE_URL = "https://amlknipqbdjvgmimphkl.supabase.co"
SUPABASE_KEY = "sb_publishable_HXxYN_dWvgtLR1_t9j5NXQ_pbuNymbM"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


st.set_page_config(page_title="1960s Computing Quiz", page_icon="💾")

st.title("💾 Quiz: Computing in the 1960s")

# --- SUPABASE AUTH SYSTEM ---

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🔐 Login / Register")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    # --- LOGIN ---
    with tab_login:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = res.user
                st.success("Logged in!")
                st.rerun()
            except Exception:
                st.error("Invalid email or password")

    # --- REGISTER ---
    with tab_register:
        new_email = st.text_input("New email")
        new_password = st.text_input("New password", type="password")

        if st.button("Register"):
            try:
                supabase.auth.sign_up({
                    "email": new_email,
                    "password": new_password
                })
                st.success("Account created! Check your email to confirm.")
            except Exception:
                st.error("Registration failed")

    st.stop()

# --- USER IS LOGGED IN ---
if st.session_state.user is not None:

    # --- SIDEBAR ---
    st.sidebar.title("User Menu")
    st.sidebar.write(f"👤 Logged in as: {st.session_state.user.email}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()


# --- QUIZ DATA WITH CATEGORIES ---
questions = [
    {
        "q": "Who created the C programming language in 1969?",
        "options": ["Dennis Ritchie", "Ken Thompson", "John McCarthy", "Edsger Dijkstra"],
        "answer": "Dennis Ritchie",
        "category": "Languages"
    },
    {
        "q": "Which early programming language, created in 1964, was designed to be easy for students to learn?",
        "options": ["BASIC", "Pascal", "Ada", "Logo"],
        "answer": "BASIC",
        "category": "Languages"
    },
    {
        "q": "Which programming language was widely used in the 1960s for business applications?",
        "options": ["COBOL", "FORTRAN", "ALGOL", "LISP"],
        "answer": "COBOL",
        "category": "Languages"
    },
    {
        "q": "Which programming language introduced many ideas used in modern functional programming and was popular in the 1960s?",
        "options": ["LISP", "C", "Java", "Python"],
        "answer": "LISP",
        "category": "Languages"
    },
    {
        "q": "Which operating system project began in 1969 at Bell Labs and later influenced Linux?",
        "options": ["UNIX", "MS-DOS", "Mac OS", "CP/M"],
        "answer": "UNIX",
        "category": "Operating Systems"
    },
    {
        "q": "Which early computer network project started in 1969 and became the foundation of the Internet?",
        "options": ["ARPANET", "Ethernet", "World Wide Web", "Bitnet"],
        "answer": "ARPANET",
        "category": "Networking"
    },
    {
        "q": "Which influential programming language, created in 1968, later inspired Pascal and C?",
        "options": ["ALGOL 68", "FORTRAN II", "COBOL-68", "PL/I"],
        "answer": "ALGOL 68",
        "category": "Languages"
    },
    {
        "q": "Who co-created the BASIC programming language in 1964?",
        "options": ["John Kemeny and Thomas Kurtz", "Dennis Ritchie and Ken Thompson", "Grace Hopper and John Backus", "Alan Kay and Adele Goldberg"],
        "answer": "John Kemeny and Thomas Kurtz",
        "category": "Pioneers"
    },
    {
        "q": "Which computer scientist published the famous 'Go To Statement Considered Harmful' letter in 1968?",
        "options": ["Edsger Dijkstra", "Donald Knuth", "Alan Turing", "Niklaus Wirth"],
        "answer": "Edsger Dijkstra",
        "category": "Pioneers"
    },
    {
        "q": "Which pioneering computer scientist created LISP, widely used in AI research during the 1960s?",
        "options": ["John McCarthy", "Marvin Minsky", "Claude Shannon", "Grace Hopper"],
        "answer": "John McCarthy",
        "category": "Pioneers"
    }
]

# --- CATEGORY SELECTION ---
categories = ["All", "Languages", "Operating Systems", "Networking", "Pioneers"]
selected_category = st.selectbox("Choose a category:", categories)

# Filter questions
if selected_category == "All":
    filtered_questions = questions
else:
    filtered_questions = [q for q in questions if q["category"] == selected_category]

# --- SESSION STATE INITIALIZATION ---
if "shuffled_questions" not in st.session_state or st.session_state.get("last_category") != selected_category:
    st.session_state.shuffled_questions = random.sample(filtered_questions, len(filtered_questions))
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.last_category = selected_category

# --- HIGH SCORE SYSTEM ---
if "high_scores" not in st.session_state:
    st.session_state.high_scores = {}

if selected_category not in st.session_state.high_scores:
    st.session_state.high_scores[selected_category] = 0

st.info(
    f"🏆 High Score for '{selected_category}': "
    f"{st.session_state.high_scores[selected_category]}/{len(st.session_state.shuffled_questions)}"
)


# --- PROGRESS BAR ---
progress = st.session_state.index / len(st.session_state.shuffled_questions)
st.progress(progress)

# --- CURRENT QUESTION ---
q = st.session_state.shuffled_questions[st.session_state.index]

shuffled_options = q["options"].copy()
random.shuffle(shuffled_options)

st.subheader(f"Category: {q['category']}")
st.subheader(f"Question {st.session_state.index + 1} / {len(st.session_state.shuffled_questions)}")
user_answer = st.radio(q["q"], shuffled_options, key=f"q{st.session_state.index}")

# --- VALIDATION ---
if st.button("Validate"):
    if not st.session_state.answered:
        st.session_state.answered = True

        if user_answer == q["answer"]:
            st.success("Correct!")
            st.session_state.score += 1
        else:
            st.error(f"Wrong! The correct answer was: {q['answer']}")

        # Next question or end
        if st.session_state.index < len(st.session_state.shuffled_questions) - 1:
            time.sleep(1)
            st.session_state.index += 1
            st.session_state.answered = False
            st.rerun()
        else:
            st.write("---")
            st.header("🎉 Quiz completed!")
            st.subheader(f"Your final score: {st.session_state.score} / {len(st.session_state.shuffled_questions)}")

            # --- UPDATE HIGH SCORE ---
            if st.session_state.score > st.session_state.high_scores[selected_category]:
                st.session_state.high_scores[selected_category] = st.session_state.score
                st.success("🏆 New High Score!")

            st.balloons()

# --- RESTART BUTTON ---
if st.button("Restart Quiz"):
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.answered = False
    st.session_state.shuffled_questions = random.sample(filtered_questions, len(filtered_questions))
    st.session_state.last_category = selected_category
    st.rerun()
