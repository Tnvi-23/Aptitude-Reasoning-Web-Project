import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

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
    st.session_state["user_role"] = None  # or "user" / "host" if you want a default

# --- Access Control ---
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("You must be logged in to access this page.")
    st.stop()

if st.session_state["user_role"] != "host":
    st.error("Only hosts can upload quizzes.")
    st.stop()

if "upload_done" in st.session_state and st.session_state.upload_done:
    del st.session_state.upload_done

# --- Session Initialization ---
for key in ["active_df", "active_section", "upload_done", "user_answers"]:
    if key not in st.session_state:
        st.session_state[key] = pd.DataFrame() if key == "active_df" else {} if key == "user_answers" else None

# --- DB Connection ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# --- Ensure Tables Exist ---
cursor.execute('''CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_name TEXT,
    quiz_type TEXT,
    file_path TEXT,
    host_username TEXT,
    upload_time TEXT
)''')
cursor.execute("PRAGMA table_info(quizzes)")
quiz_cols = [col[1] for col in cursor.fetchall()]
if "upload_time" not in quiz_cols:
    cursor.execute("ALTER TABLE quizzes ADD COLUMN upload_time TEXT")
conn.commit()


cursor.execute('''CREATE TABLE IF NOT EXISTS host_quiz_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_name TEXT,
    host_username TEXT
)''')

cursor.execute("PRAGMA table_info(quiz_ranges)")
columns = [col[1] for col in cursor.fetchall()]
if "filename" not in columns:
    cursor.execute("ALTER TABLE quiz_ranges ADD COLUMN filename TEXT")
conn.commit()

# --- UI ---
st.title(" Upload a New Quiz")

quiz_name = st.text_input("Enter quiz name (e.g., Aptitude Test 3)")
quiz_type = st.selectbox("Select quiz type", ["aptitude", "reasoning"])
uploaded_file = st.file_uploader("Upload quiz CSV", type=["csv"])

# --- Upload Button ---
if st.button("Upload Quiz"):
    if uploaded_file and quiz_name and quiz_type:
        try:
            df = pd.read_csv(uploaded_file, sep=";")
            df.columns = df.columns.str.strip().str.replace('\ufeff', '')
            st.session_state.active_df = df

            host_username = st.session_state["username_logged_in"]
            filename = f"quizzes/{quiz_type}_{quiz_name.replace(' ', '_')}_{host_username}.csv"
            df.to_csv(filename, sep=";", index=False)

            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO quiz_ranges (quiz_name, quiz_type, start, end, filename)
                VALUES (?, ?, ?, ?, ?)
            """, (quiz_name, quiz_type, 0, len(df), filename))

            cursor.execute("""
                INSERT OR REPLACE INTO host_quiz_map (quiz_name, host_username)
                VALUES (?, ?)
            """, (quiz_name, host_username))

            cursor.execute("""
                INSERT OR REPLACE INTO quizzes (quiz_name, quiz_type, file_path, host_username, upload_time)
                VALUES (?, ?, ?, ?, ?)
            """, (quiz_name, quiz_type, filename, host_username, upload_time))

            conn.commit()
            st.success(f"Quiz '{quiz_name}' uploaded successfully.")
            st.session_state.upload_done = True
        except Exception as e:
            st.error(f"Upload failed: {e}")
    else:
        st.warning(" Please fill all fields and upload a file.")


st.markdown("---")
st.subheader(" Your Uploaded Quizzes")

cursor.execute("""
    SELECT quiz_name, quiz_type, file_path, upload_time FROM quizzes
    WHERE host_username = ?
""", (st.session_state["username_logged_in"],))
uploaded_quizzes = cursor.fetchall()

if uploaded_quizzes:
    
    # Table header
    header_cols = st.columns([3, 2, 1, 1])
    header_cols[0].markdown("**Quiz Name**")
    header_cols[1].markdown("**Upload Time**")
    header_cols[2].markdown("**View**")
    header_cols[3].markdown("**Delete**")

    # Table rows
    for idx, (quiz_name, quiz_type, path, upload_time) in enumerate(uploaded_quizzes):
        row_cols = st.columns([3, 2, 1, 1])
        row_cols[0].markdown(f"**{quiz_name}** ({quiz_type})")
        row_cols[1].markdown(f"{upload_time}")
        if row_cols[2].button("View", key=f"view_{quiz_name}_{idx}"):
            try:
                df = pd.read_csv(path, sep=";")
                st.dataframe(df.head())
            except Exception as e:
                st.error(f" Could not load quiz: {e}")
        if row_cols[3].button("Delete", key=f"delete_{quiz_name}_{idx}"):
            try:
                cursor.execute("DELETE FROM quizzes WHERE quiz_name = ? AND host_username = ?", (quiz_name, st.session_state["username_logged_in"]))
                conn.commit()
                st.success(f" Quiz '{quiz_name}' deleted.")
                st.rerun()
            except Exception as e:
                st.error(f" Delete failed: {e}")
else:
    st.info("You haven't uploaded any quizzes yet.")