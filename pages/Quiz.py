import streamlit as st
import pandas as pd
import sqlite3
import datetime


st.markdown("""
<style>
.stApp, .stApp * {
    color: #290907 !important;  /* change this hex color */
}

 /* ============================================
    GLOBAL BACKGROUND (Blue → Beige Gradient)
    ============================================ */
.stApp {
    background: linear-gradient(135deg, #2F4A60 0%, #E7E5DD 100%);
    background-attachment: fixed;
    color: #1A1A1A;
}

 /* ============================================
    GLASS BLOCK / CARD DESIGN
    ============================================ */
.block-container {
    background: rgba(255, 255, 255, 0.35);
    backdrop-filter: blur(12px);
    border-radius: 18px;
    border: 1px solid rgba(26, 26, 26, 0.2);
    padding: 2rem;
    margin-top: 90px;
    box-shadow: 0 6px 25px rgba(0,0,0,0.25);
}

 /* ============================================
    HEADINGS
    ============================================ */
h1, h2, h3 {
    color: #1A1A1A;
    font-weight: 700;
}

 /* ============================================
    PRIMARY BUTTON (Blue → Sage Green Gradient)
    ============================================ */
button[kind="primary"] {
    background: linear-gradient(90deg, #2F4A60, #70846A);
    color: #E7E5DD !important;
    border-radius: 8px;
    border: none;
    font-weight: 600;
    transition: 0.3s ease;
    box-shadow: 0 3px 10px rgba(0,0,0,0.25);
}

button[kind="primary"]:hover {
    background: linear-gradient(90deg, #6D4F45, #1A1A1A);
    transform: scale(1.05);
}

 /* ============================================
    SECONDARY BUTTON
    ============================================ */
button:not([kind="primary"]) {
    background: rgba(111, 93, 85, 0.2);
    color: #1A1A1A !important;
    border-radius: 6px;
    border: 1px solid rgba(109, 79, 69, 0.4);
}

button:not([kind="primary"]):hover {
    background: rgba(109, 79, 69, 0.35);
}

 /* ============================================
    SIDEBAR
    ============================================ */
section[data-testid="stSidebar"] {
    background: #1A1A1A;
    border-right: 2px solid #6D4F45;
}

section[data-testid="stSidebar"] * {
    color: #E7E5DD !important;
}

 /* ============================================
    INPUT FIELDS
    ============================================ */
input, select, textarea {
    background: rgba(255,255,255,0.4) !important;
    border: 1px solid #2F4A60 !important;
    color: #1A1A1A !important;
    border-radius: 6px;
}

 /* ============================================
    LINKS
    ============================================ */
a {
    color: #70846A !important;
    font-weight: 600;
}
a:hover {
    color: #1A1A1A !important;
}

 /* ============================================
    FOOTER
    ============================================ */
.footer-wrapper {
    width: 100vw;
    margin-left: calc(-50vw + 50%);
    background: rgba(231, 229, 221, 0.9);
    padding: 18px 0;
    text-align: center;
    border-top: 1px solid #6D4F45;
    color: #1A1A1A;
}

.footer-wrapper a {
    color: #70846A !important;
}
.footer-wrapper a:hover {
    color: #1A1A1A !important;
}

 /* ============================================
    CUSTOM SCROLLBAR
    ============================================ */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb { background: #6D4F45; border-radius: 4px; }

</style>
""", unsafe_allow_html=True)
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if st.session_state["user_role"] == "host":
    st.error("🚫 Hosts are not allowed to attempt quizzes.")
    st.stop()
def reset_session_on_login_change():
    """Clear session state when a new user logs in or logs out."""
    if "last_logged_user" not in st.session_state:
        st.session_state["last_logged_user"] = None

    current_user = st.session_state.get("username_logged_in", None)
    previous_user = st.session_state["last_logged_user"]

    # If a different user logs in, clear previous quiz data
    if current_user and current_user != previous_user:
        for key in list(st.session_state.keys()):
            if key not in ["logged_in", "username_logged_in", "last_logged_user"]:
                del st.session_state[key]
        st.session_state["last_logged_user"] = current_user

    # If user logs out, clear everything
    if not st.session_state.get("logged_in", False):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["logged_in"] = False
        st.session_state["username_logged_in"] = ""
        st.session_state["last_logged_user"] = None

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.info(" You must be logged in to access the quiz page.")
    if st.button("Go to Login Page"):
        st.switch_page("pages/Account.py")
    st.stop()
reset_session_on_login_change()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username_logged_in" not in st.session_state:
    st.session_state["username_logged_in"] = ""
if "selected_quiz" not in st.session_state:
    st.session_state["selected_quiz"] = None    
    
# Connect to SQLite DB
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Create quiz_scores table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS quiz_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    sr_no TEXT,
    quiz_name TEXT,
    score INTEGER,
    total INTEGER,
    date INTEGER,
    date_taken TEXT
)
''')
try:
    cursor.execute("ALTER TABLE quiz_scores ADD COLUMN host_username TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass  # Column already exists
conn.commit()
df = pd.read_csv("aptitude.csv", sep=';')
df.columns = df.columns.str.strip()  
df1 = pd.read_csv("reasoning.csv",sep=';')
df1.columns = df1.columns.str.strip()
for key in ["page", "active_section", "user_answers", "score", "results"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key in ["user_answers", "results"] else None
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "submitted" not in st.session_state:
    st.session_state.submitted = False    
sections = df['Section'].dropna().unique().tolist()
df_section = df[df['Section'] == st.session_state]
aptitude_ranges = {
    "Aptitude Test 1": (0, 30),
    "Aptitude Test 2": (30, 60),
    "Aptitude Test 3": (60, 90),
    "Aptitude Test 4": (90, 120),
    "Aptitude Test 5": (120, 150)
}
reasoning_range = {
    "Reasoning Test 1": (0, 30),
    "Reasoning Test 2": (30, 60),
    "Reasoning Test 3": (60, 90),
    "Reasoning Test 4": (90, 120),
    "Reasoning Test 5": (120, 150),
    "Reasoning Test 6": (150, 180),
    "Reasoning Test 7": (180, 210),
    "Reasoning Test 8": (210, 240),
    "Reasoning Test 9": (240, 270),
    "Reasoning Test 10": (270, 300),
}

def show_home():
    st.title("Welcome To The Aptitude Arena!")
    st.subheader("Click here to start the test")
    if st.button("Start Quiz"):
        st.session_state.page = "select_section"
        st.rerun()
def show_section_selector():
    st.title("Choose Your Quiz Section")

    quiz_type = st.radio("Select quiz type:", ["aptitude", "reasoning"])

    # Load public quizzes
    if quiz_type == "aptitude":
        public_sections = list(aptitude_ranges.keys())
        df_public = df
    else:
        public_sections = list(reasoning_range.keys())
        df_public = df1

    # Get assigned host for the logged-in user
    cursor.execute("SELECT host_username FROM host_user_map WHERE user_username=?", 
                   (st.session_state["username_logged_in"],))
    result = cursor.fetchone()
    assigned_host = result[0] if result else None

    uploaded_sections = []
    uploaded_meta = []

    # --- Load quizzes uploaded by the assigned host ---
    if assigned_host:
        cursor.execute("""
            SELECT q.quiz_name, q.quiz_type, q.file_path
            FROM quizzes q
            WHERE q.quiz_type = ? AND q.host_username = ?
        """, (quiz_type, assigned_host))
        uploaded_meta = cursor.fetchall()
        uploaded_sections = [q[0] for q in uploaded_meta]

    # Combine public and uploaded quizzes
    all_sections = public_sections + uploaded_sections
    if not all_sections:
        st.info(" No quizzes available for this type.")
        return

    selected_section = st.selectbox("Select a section:", all_sections)

    # --- When user clicks Proceed ---
    if st.button("Proceed to Quiz"):
        if selected_section in public_sections:
            # Public quiz
            st.session_state.active_section = selected_section
            st.session_state.active_df = df_public
            st.session_state.active_ranges = (
                aptitude_ranges if quiz_type == "aptitude" else reasoning_range
            )
        else:
            # Uploaded quiz → load directly from file_path
            try:
                selected_meta = next(q for q in uploaded_meta if q[0] == selected_section)
                _, _, file_path = selected_meta  # unpack the tuple
    
                df_uploaded = pd.read_csv(file_path, sep=";")
                df_uploaded.columns = df_uploaded.columns.str.strip()
                section_df = df_uploaded.reset_index(drop=True)

                st.session_state.active_section = selected_section
                st.session_state.active_df = section_df
                st.session_state.active_ranges = {selected_section: (0, len(section_df))}

            except Exception as e:
                st.error(f"Could not load quiz file: {e}")
                return

        st.session_state.page = "quiz"
        st.rerun()

def show_quiz():
    if "active_df" not in st.session_state or st.session_state.active_df is None:
        st.error("No quiz loaded!")
        return

    df = st.session_state.active_df.copy()
    selected_section = st.session_state.active_section

    if st.session_state.active_ranges and selected_section in st.session_state.active_ranges:
        start, end = st.session_state.active_ranges[selected_section]
        df_section = df.iloc[start:end].reset_index(drop=True)
    else:
        df_section = df.reset_index(drop=True)

    st.header(f"{selected_section}")
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    for i, row in df_section.iterrows():
        question_text = row.get("Question", f"Question {i+1}")
        st.subheader(f"Q{i+1}: {question_text}")

        options = []
        option_labels = ["Option A", "Option B", "Option C", "Option D"]
        for label in option_labels:
            if label in df_section.columns and pd.notna(row[label]):
                options.append(f"{label[-1]}. {row[label]}")

        if not options:
            st.warning("⚠️ No options found for this question.")
            continue

        key = f"{selected_section}_q{i}_answer"
        user_choice = st.radio("Choose your answer:", options, index=None, key=key)
        st.session_state.user_answers[key] = user_choice

    if st.button(" Submit Quiz"):
        score = 0
        total_questions = len(df_section)
        for i, row in df_section.iterrows():
            key = f"{selected_section}_q{i}_answer"
            user_choice = st.session_state.user_answers.get(key, "")
            correct_answer = str(row.get("Answer", "")).strip().upper()
            if user_choice and correct_answer:
                selected_label = user_choice.split(".")[0].strip().upper()
                if selected_label == correct_answer:
                    score += 2

        save_quiz_result(
            username=st.session_state["username_logged_in"],
            quiz_name=selected_section,
            score=score,
            total=total_questions * 2
        )

        st.session_state.score = score
        st.session_state.results[selected_section] = {"score": score, "total": total_questions * 2}
        st.session_state.page = "results"
        st.rerun()

    if st.button(" End Quiz Without Submitting"):
        st.session_state.page = "home"
        st.session_state.active_section = None
        st.session_state.user_answers = {}
        st.session_state.score = 0
        st.rerun()
        
def save_quiz_result(username, quiz_name, score, total):
    date_taken = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get the host who uploaded this quiz
    cursor.execute("SELECT host_username FROM quizzes WHERE quiz_name=?", (quiz_name,))
    result = cursor.fetchone()
    host_username = result[0] if result else None

    # Skip saving if current user is a host
    if st.session_state.get("user_role") == "host":
        return

    cursor.execute("""
        INSERT INTO quiz_scores (username, quiz_name, score, total, date_taken, host_username)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, quiz_name, score, total, date_taken, host_username))
    conn.commit()
def show_results():    
    selected_section = st.session_state.active_section
    section_ranges = st.session_state.active_ranges
    df = st.session_state.active_df
    start, end = section_ranges[selected_section]
    result = st.session_state.results.get(selected_section, {})
    st.title(" Quiz Completed!")
    st.markdown(f"### Your Score: **{result.get('score', 0)}**")
    if st.button(" Restart"):
        st.session_state.page = "home"
        st.session_state.active_section = None
        st.session_state.user_answers = {}
        st.session_state.score = 0
        st.rerun()
    if st.button("Go to Home page"):
        st.switch_page("Home.py")    
if st.session_state.page == "results":
    section_ranges = st.session_state.active_ranges
    selected_section = st.session_state.active_section
    start, end = section_ranges[selected_section]
    df_section = df.iloc[start:end].reset_index(drop=True)
    show_results()
elif st.session_state.page == "quiz":
    show_quiz()
elif st.session_state.page == "select_section":
    show_section_selector()
else:
    show_home()
    