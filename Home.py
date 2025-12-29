import streamlit as st
import time

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username_logged_in" not in st.session_state:
    st.session_state["username_logged_in"] = ""    

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #301934;
            color: #301934;  /* Indigo text */
            
        }

        [data-testid="stSidebar"] .css-1v3fvcr {
            color: #4b0082;
        }

        [data-testid="stSidebar"] a:hover {
            color: #ff1493;
        }
    </style>
""", unsafe_allow_html=True)

import streamlit as st

st.markdown("""
    <style>
        /* Remove top border from the main app container */
        .stApp {
            border-top: none;
        }

        /* Optional: remove header shadow or separator */
        [data-testid="stHeader"] {
            border-bottom: none;
            box-shadow: none;
        }
    </style>
""", unsafe_allow_html=True)

# Create a placeholder for the animated sentence
placeholder = st.empty()

# Inject CSS for smooth left-to-right reveal and button styling
placeholder.markdown("""
    <style>
    .fade-in-text {
        opacity: 0;
        transform: translateX(-50px);
        animation: fadeInLeft 2s ease forwards;
        font-size: 28px;
        font-weight: bold;
        color: #FF69B4;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 40px;
        margin-left: 0%;             
    }

    @keyframes fadeInLeft {
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    div.stButton > button {
        background-color: #FF69B4;
        color: white;
        font-size: 16px;
        padding: 8px 20px;
        border-radius: 6px;
        border: none;
        margin-top: 0px;
        margin-bottom: 20px;
    }
    </style>

    <div class="fade-in-text">Welcome to the Aptitude Arena!</div>
""", unsafe_allow_html=True)

# Wait for animation to finish
time.sleep(2.2)

# Button placed directly below the sentence
col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 2, 1, 1, 1])
with col4:
    if st.button("Go to Attend Quiz!"):
        st.switch_page("pages/Quiz.py")  # Adjust to your actual page name
st.markdown("""
<style>
.footer {
    width: 81vw;   /* ✅ increase width (try 90vw–100vw for your preference) */
    margin-left: calc(-40.5vw + 50%);  /* ✅ centers it perfectly */
    background-color: #111418;
    color: #ddd;
    text-align: center;
    border-top: 1px solid #333;
    padding: 25px 0 15px 0;
    font-size: 15px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.footer-links {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 25px;
    margin-top: 10px;
}

.footer-links a {
    color: #4da3ff;
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s ease, transform 0.2s ease;
}

.footer-links a:hover {
    color: #79bfff;
    text-decoration: underline;
    transform: translateY(-2px);
}
.about{
        display:flex;
        justify-content:center;
        margin-top: 30px;
        padding: 20px;
        height: 45vh;
        gap:20px; 
        bottom: 0;             /* attach to bottom */
        left: 0;
        z-index: 9999;
        background-color: #353839;
        display: flex;
        padding: 20px 80px;
        width: 81vw;   /* ✅ increase width (try 90vw–100vw for your preference) */
        margin-left: calc(-40.5vw + 50%)
       }

.section1{
            width: 300px;            /* Fixed width ensures alignment */
  height: 280px;
  color: white;
  align-items: right;
  font-weight: bold;
  flex-shrink: 0;
  padding:20px; }
</style>

<div class="footer">
    <div>© 2025 QuizMaster Platform. All rights reserved.</div>
    <div class="footer-links">
        <a href="#aboutsection" onclick="window.location.href='?show_about=true'">About Us</a>
        <a href="#contactsection">Contact Us</a>
        <a href="#privacysection">Privacy Policy</a>
        <a href="#termssection">Terms of Use</a>
    </div>
    </div>   
</div>
<div class="about">
<div class="section1">
    <a name="aboutsection"></a>  
    <h4>About Us</h4>
     <p>Aptitude Arena is a dynamic learning platform designed to make aptitude and reasoning practice engaging, personalized, and data-driven. Whether you're a student preparing for competitive exams or an educator.
</p>
</div>    
<div class="section1">
    <a name="contactsection"></a>  
    <h4>Contact Us</h4>
    <p>Email- tanvibidve6@gmail.com</p>
    <p>Phone- +91-1234567890</p>
    <p>Monday to Friday
10:00 AM – 6:00 PM IST
Closed on weekends and public holidays.
</p>
</div>
<div class="section1">
    <a name="privacysection"></a>  
    <h4>Privacy</h4>
    <p>At Aptitude Arena, we are committed to protecting your personal information and ensuring a safe, secure learning environment.
</p><p>If you have questions or concerns about your privacy, contact us at:
Email: privacy@quizmaster.com
Phone: +91-1234567890
</p>
      </div>
<div class="section1">
    <a name="termssection"></a>  
    <h4>Terms of Use</h4>
    <p>By accessing and using Aptitude Arena, you agree to comply with the following terms and conditions.
</p>
      </div>
 
</div>
""", unsafe_allow_html=True)