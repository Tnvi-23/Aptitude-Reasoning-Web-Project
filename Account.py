import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import os

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

  # or "user"
#if "menu_choice" not in st.session_state:
#    st.session_state.menu_choice = "Login"    
#if "account_created" not in st.session_state:
#    st.session_state.account_created = False    

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT,
    role TEXT CHECK(role IN ('user', 'host')) NOT NULL DEFAULT 'user'           
)
''')
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS host_user_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    host_username TEXT NOT NULL,
    user_username TEXT NOT NULL
)
''')
conn.commit()
cursor.execute('''
CREATE TABLE IF NOT EXISTS quiz_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    quiz_name TEXT NOT NULL,
    score INTEGER,
    total INTEGER,
    date_taken TEXT,
    host_username TEXT NOT NULL
)
''')
conn.commit()
def add_user(username, email, password, role):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (username, email, password_hash, role)
    )
    conn.commit()

def login_user(username, password):
    cursor.execute("SELECT password_hash, role FROM users WHERE username=?", (username,))
    record = cursor.fetchone()
    
    if record:
        hashed_pw, role = record
        if bcrypt.checkpw(password.encode('utf-8'), hashed_pw):
            return True, role
    return False, None

def user_exists(username, email):
    cursor.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
    return cursor.fetchone() is not None

# --- Initialize Session State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username_logged_in" not in st.session_state:
    st.session_state["username_logged_in"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = ""
if "logout_flag" not in st.session_state:
    st.session_state["logout_flag"] = False  
if "skip_reload" not in st.session_state:
    st.session_state["skip_reload"] = False   
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False       
if os.path.exists("session.txt") and not st.session_state["logged_in"] and not st.session_state["logout_flag"]:
    with open("session.txt", "r") as f:
        data = f.read().strip().split(",")
        if len(data) == 2:
            st.session_state["logged_in"] = True
            st.session_state["username_logged_in"] = data[0]
            st.session_state["user_role"] = data[1]
def login_page():
    st.subheader("Login to Your Account")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
      success, role = login_user(username, password)
      if success:
        st.session_state["username_logged_in"] = username
        st.session_state["logged_in"] = True  # "host" / "student"
        st.session_state["username"] = username
        st.session_state["user_role"] = role 
        with open("session.txt", "w") as f:
                f.write(f"{username},{role}")

        #st.query_params.update({"user": username})
        st.success(f"Welcome, {username}! Logged in as **{role}**.")
        st.rerun()
      else:
        st.error(" Invalid username or password.")

# --- Registration Page ---
def registration_page():
    st.subheader("Create a New Account")

    username = st.text_input("Username", key="username")
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
    
    # Role selection
    role = st.selectbox("Select Role", ["user", "host"])

    # If registering as a user, select which host they belong to
    assigned_host = None
    if role == "user":
        cursor.execute("SELECT username FROM users WHERE role='host'")
        host_list = [r[0] for r in cursor.fetchall()]
        if host_list:
            assigned_host = st.selectbox("Assign to Host", host_list)
        else:
            st.warning("No hosts available yet. Please create a host account first.")

    if st.button("Create Account"):
        if not username or not email or not password or not confirm_password:
            st.error("Please fill in all fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif user_exists(username, email):
            st.warning("Username or Email already exists. Try another.")
        elif role == "user" and not assigned_host:
            st.error("Please assign the user to a host.")
        else:
            # Add the user with role
            add_user(username, email, password, role)

            # If it's a user, map them to their host
            if role == "user" and assigned_host:
                cursor.execute(
                    "INSERT INTO host_user_map (host_username, user_username) VALUES (?, ?)",
                    (assigned_host, username)
                )
                conn.commit()

            st.success("Account created successfully! You can now log in.")

def dashboard_page():

    st.title(" Your Quiz Dashboard")
    st.write(f"Hello, **{st.session_state['username_logged_in']}**!")

    cursor.execute("""
    SELECT quiz_name, score, total, date_taken
    FROM quiz_scores
    WHERE username = ?
    ORDER BY date_taken ASC
""", (st.session_state["username_logged_in"],))
    rows = cursor.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["Quiz Name", "Score", "Total", "Date taken"])
        df["Marks"] = df["Score"].astype(str) + "/" + df["Total"].astype(str)
        df.insert(0, "Sr No", range(1, len(df) + 1))
        df = df[["Sr No", "Quiz Name", "Marks", "Date taken"]]
        st.subheader("Your Quiz Results")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("You haven’t taken any quizzes yet.")

    st.markdown("---")
    if st.button("Go to Attempt a Quiz"):
        st.switch_page("pages/Quiz.py")

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username_logged_in"] = ""
        st.session_state["user_role"] = ""
        st.session_state["skip_reload"] = True
        try:
            os.remove("session.txt")
        except FileNotFoundError:
            pass
        st.success("You have been logged out.")
        st.rerun()
def host_dashboard(cursor):
    """Dashboard for hosts - shows assigned users and their quiz performance"""
    host = st.session_state.get("username_logged_in", None)
    if not host:
        st.error(" No host logged in!")
        return

    st.title("Host Dashboard")
    st.write(f"Welcome, **{host}**! Here’s a summary of your assigned users and their quiz results:")

    # ✅ Fetch assigned users for this host
    cursor.execute("SELECT user_username FROM host_user_map WHERE host_username=?", (host,))
    assigned_users = [r[0] for r in cursor.fetchall()]

    if not assigned_users:
        st.warning(" You don’t have any assigned users yet.")
        if st.button(" Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username_logged_in"] = ""
            st.session_state["user_role"] = ""
            st.session_state["logout_flag"] = True
            try:
                os.remove("session.txt")
            except FileNotFoundError:
                pass
            st.success("You have been logged out.")
            st.rerun()
        return

    st.markdown(f"  Assigned Users ({len(assigned_users)})")
    st.write("**Users assigned to you:** " + ", ".join(assigned_users))

    # ✅ Fetch quiz data for assigned users, only for quizzes assigned by this host
    placeholders = ",".join("?" * len(assigned_users))
    query = f"""
        SELECT username, quiz_name, score, total, date_taken
        FROM quiz_scores
        WHERE username IN ({placeholders}) AND host_username = ?
        ORDER BY date_taken DESC
    """
    cursor.execute(query, assigned_users + [host])
    rows = cursor.fetchall()

    if not rows:
        st.info("📭 None of your assigned users have taken a quiz yet.")
    else:
        df = pd.DataFrame(rows, columns=["Username", "Quiz Name", "Score", "Total", "Date Taken"])
        df["Marks"] = df["Score"].astype(str) + "/" + df["Total"].astype(str)
        df.insert(0, "Sr No", range(1, len(df) + 1))
        df = df[["Sr No", "Username", "Quiz Name", "Marks", "Date Taken"]]

        # ✅ Filter section
        st.markdown("### 🔍 Filter Results")
        selected_user = st.selectbox("Select a User", ["All"] + sorted(set(df["Username"])))
        if selected_user != "All":
            df = df[df["Username"] == selected_user]

        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    if st.button(" Logout"):
        st.session_state["logged_in"] = False
        st.session_state["username_logged_in"] = ""
        st.session_state["user_role"] = ""
        st.session_state["logout_flag"] = True
        try:
            os.remove("session.txt")
        except FileNotFoundError:
            pass
        st.success("You have been logged out.")
        st.rerun()

# --- Main App Flow ---
def main():
    if st.session_state.get("skip_reload", False):
        st.session_state["skip_reload"] = False

    if not st.session_state["logged_in"]:
        st.title(" Login & Registration System")
        menu = st.selectbox("Choose an option:", ["Login", "Create Account"])
        if menu == "Login":
            login_page()
        elif menu == "Create Account":
            registration_page()
    else:
        role = st.session_state.get("user_role", "user")
        if role == "host":
            host_dashboard(cursor)
        else:
            dashboard_page()
if __name__ == "__main__":
    main()