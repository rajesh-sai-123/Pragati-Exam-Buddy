import base64
import io
import json
import random
import zlib
from datetime import datetime, timedelta
import fitz  # PyMuPDF
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from streamlit_lottie import st_lottie
from supabase import create_client, Client

# --- Constants ---
SUPABASE_KEY = st.secrets["supabase"]["key"]
SUPABASE_URL = st.secrets["supabase"]["url"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_DIR = "media"
ADMIN_USERNAME = st.secrets["admin"]["username"]
ADMIN_PASSWORD = st.secrets["admin"]["password"]
# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Pragati's Exam Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session state initialization ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'page' not in st.session_state:
    st.session_state.page = "Home"


@st.cache_data
def load_lottiefile(filepath: str):
    """Load a Lottie animation JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


lottie_ani = load_lottiefile("animation1.json")


# --- Sidebar UI ---
with st.sidebar:
    st.image("prag logo.png")
    st.markdown("## Navigate")

    if st.button("🏠 Home"):
        st.session_state.page = "Home"
    if st.button("🧠 Aptitude Test"):
        st.session_state.page = "Aptitude Test"

    st.markdown(
        '<h3 style="text-align: center; font-family:Segoe UI, Tahoma, Geneva, Verdana, sans-serif; color:#5c6bc0; font-size: 1rem; font-weight:400; padding: 12px 0;">'
        "Pragati's Exam Buddy</h3>",
        unsafe_allow_html=True,
    )

    st.markdown('<p class="subheading">"Download. Practice. Conquer."</p>', unsafe_allow_html=True)

    if lottie_ani:
        st_lottie(lottie_ani, height=230, key="sidebar_animation", quality="high", speed=1)
    else:
        st.warning("⚠ Failed to load animation.")

    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 1em;'>
            🐞 Found a bug? <a href='mailto:madhavarapuchandrasekhara@gmail.com?subject=Bug Report'>Email us</a> or report it below
        </div>
        """,
        unsafe_allow_html=True,
    )

    bug_txt = st.text_input("Quick bug report:", placeholder="Briefly describe the issue...", label_visibility="collapsed")
    if st.button("Report Bug"):
        if not bug_txt.strip():
            st.error("Please fill the field or email us if you want to contact.")
        else:
            st.success("Bug reported! Email us if you want to contact.")

    st.markdown("---")

    if st.button("🔐 Admin Log In"):
        st.session_state.page = "Admin Login"

# Custom CSS
st.markdown("""
<style>
    .stButton > button,.stDownloadButton > button {
        border: 1px solid #555;
        background-color: #5c6bc0;
        color: white !important;
        font-weight: 600;
        padding: 10px 24px;
        border-radius: 12px;
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
        width: 100%;
        margin-bottom: 10px;

    }
    .stButton > button:hover,.stDownloadButton > button:hover {
        border:rgba(239, 239, 240, 0.41) solid 1px;outline:none !important;background: linear-gradient(135deg, #454cc6 2%, #8b90f1 98%);box-shadow: 5px 8px 12px rgba(148, 152, 235, 0.4);color: #ffffff !important;
    }
    .main-heading {
        color: #5c6bc0;font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;font-size: 3rem;font-weight: 700;margin-bottom: 0.2rem;text-align: center;letter-spacing: 1.2px;
    }
    .subheading {
        text-align: center;font-size: 1.25rem;color: #666;margin-bottom: 10px;font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

def home_ui():
    # Enhanced custom styling for better UX: softer colors, hover effects, and responsiveness
    st.markdown("""
        <style>
            .main-header {
                text-align: center;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 2rem;
                color: #0f62fe; 
                background: linear-gradient(to right, #f0f7ff, #ffffff);
                padding: 12px 18px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
                margin-bottom: 1.5rem;
                transition: box-shadow 0.3s ease;  /* Subtle hover effect */
            }
            .main-header:hover {
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
            }
            .stButton > button,.stDownloadButton > button {
                border: 1px solid #555;
                background-color: #5c6bc0;
                color: white !important;
                font-weight: 600;
                padding: 10px 24px;
                border-radius: 12px;
                transition: background-color 0.3s ease, box-shadow 0.3s ease;
                width: 100%;
                margin-bottom: 10px;
        
            }
            .stButton > button:hover,.stDownloadButton > button:hover {
                border:rgba(239, 239, 240, 0.41) solid 1px;
                outline:none !important;
                 background: linear-gradient(135deg, #454cc6 2%, #8b90f1 98%);
                 box-shadow: 5px 8px 12px rgba(148, 152, 235, 0.4);
                 color: #ffffff !important;
            }
            @media (max-width: 768px) {
                .main-header { font-size: 1.8rem; }  /* Responsive font sizing */
            }
        </style>
    """, unsafe_allow_html=True)

    # Hero/Welcome: More balanced layout, added subtle animation on load
    col1, col2 = st.columns([0.6, 0.4], gap="medium")  # Adjusted ratios for better mobile stacking
    with col1:
        st.markdown("""<div class='main-header'>🎓 Pragati's Exam Buddy</div>""", unsafe_allow_html=True)
        st.markdown(
            "Your personalized academic companion. Prepare for exams, manage tasks, and build skills with ease and confidence."
        )
        st.markdown(
            "*Consistency leads to progress—let's make today count.*"
        )
    with col2:
        hero_lottie = load_lottiefile("animation2.json")  # Assume this function is defined
        if hero_lottie:
            st_lottie(hero_lottie, height=180, quality="high", key="hero_animation")  # Slightly larger for impact

    st.divider()

    # Personalized nudge: Added a progress hint for returnees
    if st.session_state.get("user_first_visit", True):
        st.info("👋 First time here? Explore all tools and features designed to make your academic journey smoother.")
        st.session_state.user_first_visit = False
    else:
        sessions = st.session_state.get("user_sessions", 0) + 1  # Simple session counter
        st.session_state.user_sessions = sessions
        st.success("🎯 Welcome back! Keep up the momentum and stay on track with your goals.")

    # Study Actions: Card-based with tooltips and progress overview
    st.subheader("🎯 Learning Dashboard")
    st.caption("Focus on what matters—track your progress at a glance.")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        with st.container(border=True):
            st.markdown("#### 📄 Previous Exam Papers")
            st.caption("Explore patterns and topics from real exams.")
            if st.button("Browse Papers", key="qp", use_container_width=True, help="View past papers and solutions"):
                st.session_state.page = "Question Papers"
                st.session_state.papers_reviewed = st.session_state.get("papers_reviewed", 0) + 1
                st.rerun()
    with col_b:
        with st.container(border=True):
            st.markdown("#### 📘 Subject Notes")
            st.caption("Quick, focused revisions for better retention.")
            if st.button("Open Notes", key="notes", use_container_width=True,
                         help="Access curated notes and summaries"):
                st.session_state.page = "Subject Notes"
                st.session_state.notes_accessed = st.session_state.get("notes_accessed", 0) + 1
                st.rerun()
    with col_c:
        with st.container(border=True):
            st.markdown("#### 📂 Assignment Pdf's")
            st.caption("Organize and submit with deadlines in mind.")
            if st.button("View Assignments", key="assignments", use_container_width=True,
                         help="Manage your tasks and uploads"):
                st.session_state.page = "Assignments"
                st.session_state.assignments_done = st.session_state.get("assignments_done", 0) + 1
                st.rerun()

    st.divider()

    # Practice & Performance: Added progress bar for streaks
    st.subheader("🚀 Practice & Build Skills")
    st.caption("Track improvements and stay motivated.")

    col_x, col_y = st.columns(2)
    with col_x:
        with st.container(border=True):
            st.markdown("#### 🧩 Weekly Challenge Quiz")
            st.caption("Build habits through consistent testing.")
            streak = st.session_state.get("quiz_streak", 0)
            if streak > 0:
                st.progress(streak / 10.0)  # Visual streak progress (max 10 for scaling)
                st.info(f"🔥 {streak}-week streak! Aim higher.", icon="🌟")
            if st.button("Start Quiz", key="quiz", use_container_width=True, help="Test your knowledge now"):
                st.session_state.page = "Weekly Quiz"
                st.session_state.quiz_streak = streak + 1
                st.rerun()
    with col_y:
        with st.container(border=True):
            st.markdown("#### 🧠 Aptitude Practice")
            st.caption("Sharpen skills for placements and beyond.")
            if st.button("Begin Practice", key="aptitude", use_container_width=True,
                         help="Practice problems with hints"):
                st.session_state.page = "Aptitude Test"
                st.rerun()

    # Stress Cope: Kept empathetic, added a quick action button
    st.divider()
    with st.expander("💬 Managing Exam Stress", expanded=False):
        st.markdown("- **Break it down:** Turn big goals into small, achievable steps.")
        st.markdown("- **Breathe easy:** Try 4-7-8 breathing for instant calm.")
        st.markdown("- **Short breaks:** Every 45 minutes, stretch or walk for 5 mins.")
        st.markdown("*Remember, progress over perfection—you're capable!*")
        if st.button("Get Personalized Tips", key="stress_tips"):
            st.info("Tip: Journal one win from today to build positivity.")

    st.divider()
    st.markdown("#### 📊 Content Insights")
    st.caption("Here’s what’s currently available in Pragati’s Exam Buddy — regularly updated to support your academic journey.")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("📄 Question Papers Available", "180", delta="📥 12 added recently")
    kpi2.metric("📝 Subject Notes Available", "47", delta="📥 5 added")
    kpi3.metric("📂 Assignments Available", "153", delta="📥 23 added")


    with st.expander("Detailed Breakdown"):
        st.markdown("- **Quizzes:** Focus on weak areas for targeted improvement.")
        st.markdown("- **Community:** You're part of 5000+ students thriving together.")

    st.divider()
    st.markdown("#### ℹ️ About")
    st.markdown(
        "**Pragati's Exam Buddy** empowers students with essential tools to stay organized, practice effectively, and maintain well-being. Thoughtfully built to support every student’s unique learning journey with care and dedication."
    )
    st.divider()


    with st.expander(" 📧 Share Feedback", expanded=False):
        st.write("Help shape the app—your ideas matter!")
        bu_txt = st.text_input("Describe the suggestion...", key="bug_input")
        if st.button("Submit", key="bug_btn"):
            if not bu_txt.strip():
                st.warning("Please add details.")
            else:
                st.success("Feedback sent! Thanks for helping us improve.")

# Login function
def login():
    with st.form("admin_login"):
        st.subheader("🔐 Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.login_attempted = True
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")


# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.login_attempted = True
    st.success("🔐 Logged out")
    st.rerun()

def preview_download_pdf(file_bytes):
    try:
        with open("temp_preview.pdf", "wb") as f:
            f.write(file_bytes)
        with open("temp_preview.pdf", "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")

        pdf_display = f"""
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="200%" 
            height="600px" 
            type="application/pdf"
            style="border:none; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"
        ></iframe>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error previewing PDF: {e}")


@st.cache_data(show_spinner=False)
def get_pdf_ids(branch):
    result = supabase.table("pdf_branches").select("pdf_id").eq("branch", branch).execute()
    return [item["pdf_id"] for item in result.data]

@st.cache_data(show_spinner=False)
def get_filtered_pdfs(pdf_ids, reg, year, sem, paper_type):
    result = supabase.table("pdfs").select("*") \
        .in_("id", pdf_ids) \
        .eq("regulation", reg) \
        .eq("year", year) \
        .eq("semester", sem) \
        .eq("type", paper_type.lower()) \
        .execute()
    return result.data or []

def downloader_ui():
    st.markdown("<h1 class='main-heading'>🎓 Pragati's Exam Buddy </h1>", unsafe_allow_html=True)
    st.markdown(
        '<p class="subheading">Stress less , Score more! Download past papers, Practice hard, and Show those Exams who\'s Boss! 💪📚</p>',
        unsafe_allow_html=True)

    branch = st.selectbox("Select Your Branch",["--", "CSE", "CSE AI", "CSE AI & ML", "CSE DS", "CSE CYB", "IT", "ECE", "EEE", "Mech", "Civil"])
    reg = st.selectbox("Select Your Regulation", ["--", "R19", "R20", "R23"])
    year = st.selectbox("Select Your Year", ["--", "1st Year", "2nd Year", "3rd Year", "4th Year"])
    sem = st.selectbox("Select Your Semester", ["--", "1 Semester", "2 Semester"])
    paper_type = st.selectbox("Select Your Paper Type", ["--", "Regular", "Supplementary"])
    search_term = st.text_input("🔍 Search by Subject ...").lower()

    if "--" in [branch, reg, year, sem, paper_type]:
        st.info("Please select all fields to continue.")
        return

    try:
        with st.spinner("Fetching PDFs..."):
            pdf_ids = get_pdf_ids(branch)
            if not pdf_ids:
                st.warning("No PDFs found for the selected branch.")
                return

            pdfs = get_filtered_pdfs(pdf_ids, reg, year, sem, paper_type)
    except Exception as e:
        st.error(f"Error fetching PDFs: {e}")
        return

    seen = set()
    filtered = [pdf for pdf in pdfs if search_term in pdf["filename"].lower() and pdf["filename"] not in seen and not seen.add(pdf["filename"])]

    if filtered:
        st.success(f"Found {len(filtered)} PDF(s)")
    else:
        st.warning("No PDFs found for the selected filters or search.")

    for idx, pdf in enumerate(filtered):
        with st.expander(pdf["filename"]):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("👁 Preview", key=f"preview_btn_{idx}"):
                    file_bytes = base64.b64decode(pdf["filedata"])
                    preview_download_pdf(file_bytes)

            with col2:
                file_bytes = base64.b64decode(pdf["filedata"])
                st.download_button(
                    label="📥 Download",
                    data=file_bytes,
                    file_name=pdf["filename"],
                    mime="application/pdf",
                    key=f"download_{idx}"
                )



def subject_notes_ui():
    with st.form("filter_form"):
        st.markdown("<h1 class='main-heading'>📘 Subject Notes</h1>", unsafe_allow_html=True)
        reg = st.selectbox("Select Your Regulation", ["--","R19", "R20", "R23"], key="reg_notes")
        year = st.selectbox("Select Your Year", ["--","1st Year","2nd Year","3rd Year","4th Year"], key="year_notes")
        subject_search = st.text_input("🔍 Search by subject or filename...", key="search_notes").lower()
        st.form_submit_button("🚀 Proceed")

    try:
        result = supabase.table("subject_notes").select("*") \
            .eq("regulation", reg).eq("year", year).execute()
        notes = result.data or []
    except Exception as e:
        st.error(f"Error fetching subject notes: {e}")
        return

    filtered = [note for note in notes if
                subject_search in note.get("subject", "").lower() or subject_search in note.get("filename", "").lower()]
    st.success(f"Found {len(filtered)} note(s)")

    for note in filtered:
        file_bytes = base64.b64decode(note["filedata"])
        st.write(f"{note['filename']} — Subject: {note.get('subject', 'N/A')}")
        st.download_button(label="Download", data=file_bytes, file_name=note["filename"], mime="application/pdf")


def assignment_ui():
    st.markdown("<h1 class='main-heading'>📂 Assignments</h1>", unsafe_allow_html=True)
    with st.form("filter_form"):
        branch = st.selectbox("Select Your Branch",["--", "CSE", "CSE AI", "CSE AI & ML", "CSE DS", "CSE CYB", "IT", "ECE", "EEE", "Mech","Civil"], key="assign_branch")
        year = st.selectbox("Select Your Year", ["--", "1st Year", "2nd Year", "3rd Year", "4th Year"], key="assign_year")
        sem = st.selectbox("Select Your Semester", ["--", "1 Semester", "2 Semester"], key="assign_semester")
        unit = st.selectbox("Select Unit", ["--", "1st Unit", "2nd Unit", "3(A) Unit", "3(B) Unit", "4th Unit", "5th Unit"],key="assign_unit")
        subject = st.text_input("Enter Subject Name", key="assign_subject").strip().lower()
        st.form_submit_button("🚀 Proceed")

    if branch == "--" or year == "--" or sem == "--":
        st.warning("Please select Branch, Year and Semester")
        return

    try:
        query = supabase.table("assignments").select("*") \
            .eq("branch", branch) \
            .eq("year", year) \
            .eq("semester", sem)

        assignments = query.execute().data or []

    except Exception as e:
        st.error(f"Error fetching assignments: {e}")
        return

    # Filter client-side by subject and unit if provided
    filtered = []
    for a in assignments:
        subject_match = subject in a.get("subject", "").lower() if subject else True
        unit_match = (unit.lower() == a.get("unit", "").lower()) if unit else True
        if subject_match and unit_match:
            filtered.append(a)

    if filtered:
        st.success(f"Found {len(filtered)} assignment(s)")
    else:
        st.warning("No assignments found.")

    for assignment in filtered:
        file_bytes = base64.b64decode(assignment["filedata"])
        display_name = assignment.get("filename", "Unnamed")
        subj = assignment.get("subject", "N/A")
        unit_disp = assignment.get("unit", "N/A")
        st.write(f"{display_name} — Subject: {subj} — Unit: {unit_disp}")
        st.download_button(label="📥 Download Assignment", data=file_bytes, file_name=display_name,
                           mime="application/pdf")

def weekly_quiz():
    if st.session_state.get("page") == "Weekly Quiz":
        with st.form("filter_form"):
            year = st.selectbox("Select Your Year", ["--", "1st Year", "2nd Year", "3rd Year", "4th Year"])
            semester = st.selectbox("Select Your Semester", ["--", "1 Semester", "2 Semester"])
            branch = st.selectbox("Select Your Branch", ["--", "CSE", "CSE AI", "CSE AI & ML", "CSE DS", "CSE CYB", "IT", "ECE", "EEE", "Mech", "Civil"])
            st.form_submit_button("🚀 Proceed")

        if "--" in [year, semester, branch]:
            st.warning("Please select your year, semester, and branch to continue.")
            return

        try:
            with st.spinner("Fetching latest weekly quizzes..."):
                response = supabase.table("weekly_quiz").select("*")\
                    .eq("year", year).eq("semester", semester).eq("branch", branch)\
                    .order("uploaded_at", desc=True).limit(10).execute()

            if response.data:
                st.markdown(
                    """
                    <style>
                    .main-heading {
                        font-size: 2.8rem;
                        font-weight: 700;
                        color: #4caf50;
                        margin-bottom: 0.2rem;
                    }
                    .subheading {
                        font-size: 1.25rem;
                        color: #555;
                        margin-bottom: 1.5rem;
                        font-style: italic;
                    }
                    .topics-list li {
                        font-size: 1.1rem;
                        margin-bottom: 0.3rem;
                        color: #212121;
                    }
                    .start-btn {
                        background-color: #4caf50;
                        color: white;
                        padding: 0.8rem 2.5rem;
                        font-size: 1.15rem;
                        border: none;
                        border-radius: 10px;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2);
                    }
                    .start-btn:hover {
                        background-color: #388e3c;
                    }
                    .info-text {
                        font-size: 1rem;
                        color: #333;
                        margin-top: 1rem;
                        line-height: 1.5;
                    }
                    .quiz-container {
                        margin-bottom: 3rem;
                        padding: 1.5rem 2rem;
                        border-radius: 12px;
                        background-color: #f9fdf9;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                        border: 1px solid #d0e8d0;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                for quiz in response.data:
                    title = quiz.get("title", "Weekly Quiz")
                    description = quiz.get("description", "")
                    topics = quiz.get("topics", "")
                    duration = quiz.get("duration", "N/A")
                    total_questions = quiz.get("total_questions", "N/A")
                    form_link = quiz.get("form_link", "#")
                    expire_at = quiz.get("expire_at")

                    if expire_at:
                        expire_dt = datetime.fromisoformat(expire_at)
                        expire_str = expire_dt.strftime("%d %b %Y, %I:%M %p")
                    else:
                        expire_str = "N/A"

                    topics_html = ""
                    if topics:
                        topics_html = '<h3 class="topics-title">Topics Covered</h3><ul class="topics-list">'
                        for topic in topics.split(","):
                            topics_html += f"<li>{topic.strip()}</li>"
                        topics_html += "</ul>"

                    quiz_html = f"""
                    <div class="quiz-container">
                        <h1 class="main-heading">📘 {title}</h1>
                        <p class="subheading">{description}</p>
                        {topics_html}
                        <p class="info-text">
                            ⏱ <strong>Duration:</strong> {duration}<br>
                            📊 <strong>Total Questions:</strong> {total_questions}<br>
                            ⏳ <strong>Expires On:</strong> {expire_str}
                        </p>
                        <div style="text-align:center; margin-top: 2rem;">
                            <a href="{form_link}" target="_blank" rel="noopener noreferrer">
                                <button class="start-btn">🚀 Start Weekly Quiz</button>
                            </a>
                        </div>
                    </div>
                    """

                    st.markdown(quiz_html, unsafe_allow_html=True)

            else:
                st.info("No weekly quiz info available yet for the selected combination. Please check back later.")

        except Exception as e:
            st.error("Error fetching weekly quiz info.")
            st.exception(e)


def test():
    if st.session_state.get("page") == "Aptitude Test":
        year = st.selectbox("Select Your Year", ["--", "1st Year", "2nd Year", "3rd Year", "4th Year"])
        if year == "--":
            st.warning("Please select your year to continue.")
            return

        try:
            with st.spinner("Fetching latest aptitude test..."):
                response = supabase.table("aptitude_test").select("*").eq("year", year).order("uploaded_at", desc=True).limit(1).execute()

            if response.data:
                test = response.data[0]
                title = test.get("title", "Aptitude Test")
                description = test.get("description", "")
                topics = test.get("topics", "")
                duration = test.get("duration", "N/A")
                total_questions = test.get("total_questions", "N/A")
                form_link = test.get("form_link", "#")

                expire_at = test.get("expire_at")
                if expire_at:
                    expire_dt = datetime.fromisoformat(expire_at)
                    expire_str = expire_dt.strftime("%d %b %Y, %I:%M %p")
                else:
                    expire_str = "N/A"

                # --- Page Styling ---
                st.markdown(
                    """
                    <style>
                    .main-heading {
                        font-size: 2.8rem;
                        font-weight: 700;
                        color: #3f51b5;
                        margin-bottom: 0.2rem;
                    }
                    .subheading {
                        font-size: 1.25rem;
                        color: #555;
                        margin-bottom: 1.5rem;
                        font-style: italic;
                        background: none !important;
                        border: none !important;
                        padding: 0 !important;
                        box-shadow: none !important;
                    }
                    .topics-list li {
                        font-size: 1.1rem;
                        margin-bottom: 0.3rem;
                        color: #212121;
                    }
                    .start-btn {
                        background-color: #3f51b5;
                        color: white;
                        padding: 0.8rem 2.5rem;
                        font-size: 1.15rem;
                        border: none;
                        border-radius: 10px;
                        cursor: pointer;
                        transition: background-color 0.3s ease;
                        box-shadow: 0 4px 8px rgba(63,81,181,0.2);
                    }
                    .start-btn:hover {
                        background-color: #303f9f;
                    }
                    .info-text {
                        font-size: 1rem;
                        color: #333;
                        margin-top: 1rem;
                        line-height: 1.5;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(f'<h1 class="main-heading">🧠 {title}</h1>', unsafe_allow_html=True)
                st.markdown(f'<p class="subheading">{description}</p>', unsafe_allow_html=True)

                # Topics as bullet list
                if topics:
                    st.markdown('<h3 class="topics-title">Topics Covered</h3>', unsafe_allow_html=True)
                    topics_html = "<ul class='topics-list'>"
                    for topic in topics.split(","):
                        topics_html += f"<li>{topic.strip()}</li>"
                    topics_html += "</ul>"
                    st.markdown(topics_html, unsafe_allow_html=True)

                # Additional info including expire time
                st.markdown(
                    f"""
                    <p class="info-text">
                        ⏱ <strong>Duration:</strong> {duration}<br>
                        📊 <strong>Total Questions:</strong> {total_questions}<br>
                        ⏳ <strong>Expires On:</strong> {expire_str}
                    </p>
                    """,
                    unsafe_allow_html=True
                )

                # Start button centered
                st.markdown(
                    f"""
                    <div style="text-align:center; margin-top: 2rem;">
                        <a href="{form_link}" target="_blank" rel="noopener noreferrer">
                            <button class="start-btn">🚀 Start Aptitude Test</button>
                        </a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("No aptitude test info available yet for the selected year. Please check back later.")

        except Exception as e:
            st.error("Error fetching aptitude test info.")
            st.exception(e)

def admin_dashboard():
    st.markdown("<h1 class='main-heading'>📊 Admin Dashboard </h1>", unsafe_allow_html=True)

    # Fetch counts from Supabase
    qpaper_count = supabase.table("pdfs").select("id").execute()
    notes_count = supabase.table("subject_notes").select("id").execute()

    qpaper_total = len(qpaper_count.data) if qpaper_count.data else 0
    notes_total = len(notes_count.data) if notes_count.data else 0

    # Replace with actual queries if users and downloads tracking exist
    users_total = random.randint(100, 500)
    downloads_total = random.randint(500, 2000)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="📄 Question Papers Uploaded", value=qpaper_total)
        st.metric(label="👤 Registered Users", value=users_total)
    with col2:
        st.metric(label="📘 Subject Notes Uploaded", value=notes_total)
        st.metric(label="⬇️ Total Downloads", value=downloads_total)

    st.markdown("---")
    st.subheader("📈 Upload & Download Statistics")

    # Bar chart using Plotly
    stats_df = pd.DataFrame({
        "Category": ["Question Papers", "Subject Notes", "Users", "Downloads"],
        "Count": [qpaper_total, notes_total, users_total, downloads_total]
    })

    fig_bar = px.bar(stats_df, x="Category", y="Count", color="Category",
                     title="Current Counts by Category",
                     text="Count",
                     labels={"Count": "Total", "Category": "Category"},
                     template="plotly_white")
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.subheader("📅 Monthly Upload Trends")

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    trends_df = pd.DataFrame({
        "Month": months,
        "Question Papers": [random.randint(2, 20) for _ in months],
        "Subject Notes": [random.randint(1, 15) for _ in months],
        "Downloads": [random.randint(10, 100) for _ in months],
    })

    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=trends_df["Month"], y=trends_df["Question Papers"], mode='lines+markers', name='Question Papers'))
    fig_line.add_trace(go.Scatter(x=trends_df["Month"], y=trends_df["Subject Notes"], mode='lines+markers', name='Subject Notes'))
    fig_line.add_trace(go.Scatter(x=trends_df["Month"], y=trends_df["Downloads"], mode='lines+markers', name='Downloads'))

    fig_line.update_layout(
        title="Monthly Upload and Download Trends",
        xaxis_title="Month",
        yaxis_title="Count",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig_line, use_container_width=True)
# Admin Panel UI
def is_duplicate(table, filters: dict):
    try:
        query = supabase.table(table).select("id")
        for key, val in filters.items():
            query = query.eq(key, val)
        return bool(query.execute().data)
    except Exception as e:
        st.error(f"Error checking duplicates: {e}")
        return True


# Utility function to preview a PDF file
def preview_pdf(file_bytes):
    st.markdown("*Preview:*")
    st.download_button("📥 Download PDF", data=file_bytes, file_name="preview.pdf", mime="application/pdf",
                       key=f"preview_{datetime.now().isoformat()}")

def compress_pdf_max(pdf_bytes, letter=None):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    image_streams = []

    for page in doc:
        pix = page.get_pixmap(dpi=90)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=50)
        image_streams.append(buf.getvalue())

    compressed_pdf_io = io.BytesIO()
    c = canvas.Canvas(compressed_pdf_io, pagesize=letter)

    for img_bytes in image_streams:
        img = Image.open(io.BytesIO(img_bytes))
        img_width, img_height = img.size
        c.setPageSize((img_width, img_height))
        c.drawInlineImage(img, 0, 0, width=img_width, height=img_height)
        c.showPage()

    c.save()
    return compressed_pdf_io.getvalue()

def decompress_pdf_data(compressed_bytes):
    return zlib.decompress(compressed_bytes)

def cleanup_expired_aptitude_tests():
    now_iso = datetime.now().isoformat()
    try:
        supabase.table("aptitude_test") \
            .delete() \
            .filter("expire_at", "lt", now_iso) \
            .execute()
    except:
        pass

def cleanup_expired_quiz_tests():
    now_iso = datetime.now().isoformat()
    try:
        supabase.table("weekly_quiz") \
            .delete() \
            .filter("expire_at", "lt", now_iso) \
            .execute()
    except:
        pass

def is_duplicate_pdf(filters):
    query = supabase.table("pdfs").select("id").eq("filename", filters["filename"])\
        .eq("regulation", filters["regulation"])\
        .eq("year", filters["year"])\
        .eq("semester", filters["semester"])\
        .eq("type", filters["type"])
    result = query.execute()
    return result.data[0] if result.data else None

def uploader_and_admin_ui():
    st.header("📄 Admin Panel: Upload PDFs or Subject Notes or Assignments")
    upload_type = st.selectbox("Upload Type", ["📝 Question Papers", "📘 Subject Notes", "📂 Assignment's", "🧠 Aptitude Test", "🧩 Weekly Quiz"])
    if upload_type == "📝 Question Papers":
        selected_branches = st.multiselect("Select Branch(es)",["CSE", "CSE AI", "CSE AI & ML", "CSE DS", "CSE CYB", "IT", "ECE", "EEE","Mech", "Civil"])
        reg = st.selectbox("Regulation", ["R19", "R20", "R23"])
        year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        sem = st.selectbox("Semester", ["1 Semester", "2 Semester"])
        paper_type = st.selectbox("Paper Type", ["Regular", "Supplementary"])
        files = st.file_uploader("📄 Choose PDF files to upload", type=["pdf"], accept_multiple_files=True)

        if files and selected_branches and st.button("Upload Question Papers"):
            total_files = len(files)
            progress_bar = st.progress(0)
            status_text = st.empty()

            for index, file in enumerate(files):
                filename = file.name.strip()
                file_bytes = file.read()
                file_size_mb = len(file_bytes) / (1024 * 1024)

                if file_size_mb > 5:
                    st.warning(f"📦 {filename} is large. Compressing...")
                    file_bytes = zlib.compress(file_bytes)
                    st.success("Successfully Compressed")
                else:
                    st.info(f"Uploading {filename} as is.")

                filters = {
                    "filename": filename,
                    "regulation": reg,
                    "year": year,
                    "semester": sem,
                    "type": paper_type.lower()
                }
                if is_duplicate("pdfs", filters):
                    st.warning(f"'{filename}' already exists. Skipping upload.")
                else:
                    try:
                        encoded = base64.b64encode(file_bytes).decode("utf-8")
                        response = supabase.table("pdfs").insert({
                            **filters,
                            "filedata": encoded
                        }).execute()
                        pdf_id = response.data[0]["id"] if response.data else None
                        if pdf_id:
                            for branch in selected_branches:
                                supabase.table("pdf_branches").insert({
                                    "pdf_id": pdf_id,
                                    "branch": branch
                                }).execute()
                    except Exception as e:
                        st.error(f"❌ Upload failed for '{filename}': {e}")
                progress_bar.progress((index + 1) / total_files)
                status_text.text(f"Uploaded {index + 1} of {total_files} files")
            st.success("🎉 All files processed.")
    elif upload_type == "📘 Subject Notes":
        subject = st.text_input("Subject Name").strip().title()
        reg = st.selectbox("Regulation", ["R19", "R20", "R23"], key="reg_notes")
        year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"], key="year_notes")
        files = st.file_uploader("📄 Choose Subject Note PDFs to upload", type=["pdf"], key="subject_note_file", accept_multiple_files=True)

        if files and st.button("Upload Subject Notes"):
            total_files = len(files)
            progress_bar = st.progress(0)
            status_text = st.empty()

            for index, file in enumerate(files):
                filename = file.name.strip()
                file_bytes = file.read()
                file_size_mb = len(file_bytes) / (1024 * 1024)

                if file_size_mb > 5:
                    st.warning(f"📦 {filename} is large. Compressing...")
                    file_bytes = zlib.compress(file_bytes)
                    st.success("Successfully Compressed")
                else:
                    st.info(f"Uploading {filename} as is.")
                filters = {
                    "filename": filename,
                    "subject": subject,
                    "year": year,
                    "regulation": reg
                }
                if is_duplicate("subject_notes", filters):
                    st.warning(f"'{filename}' already exists. Skipping upload.")
                else:
                    try:
                        encoded = base64.b64encode(file_bytes).decode("utf-8")
                        supabase.table("subject_notes").insert({
                            **filters,
                            "filedata": encoded,
                            "uploaded_at": datetime.now().isoformat()
                        }).execute()
                    except Exception as e:
                        st.error(f"❌ Upload failed for '{filename}': {e}")
                progress_bar.progress((index + 1) / total_files)
                status_text.text(f"Uploaded {index + 1} of {total_files} files")
            st.success("🎉 All files processed.")
    elif upload_type == "📂 Assignment's":
        branch = st.selectbox("Select Your Branch",["CSE", "CSE AI", "CSE AI & ML", "CSE DS", "CSE CYB", "IT", "ECE", "EEE", "Mech", "Civil"])
        year = st.selectbox("Select Your Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        semester = st.selectbox("Select Your Semester", ["1 Semester", "2 Semester"])
        unit = st.selectbox("Select Unit", ["1st Unit", "2nd Unit", "3(A) Unit", "3(B) Unit", "4th Unit", "5th Unit"])
        subject = st.text_input("Subject Name").strip().title()
        files = st.file_uploader("📄 Choose Assignment PDFs to upload", type=["pdf"], accept_multiple_files=True)
        if files and st.button("Upload Assignments"):
            total_files = len(files)
            progress_bar = st.progress(0)
            status_text = st.empty()
            for index, file in enumerate(files):
                filename = file.name.strip()
                file_bytes = file.read()
                file_size_mb = len(file_bytes) / (1024 * 1024)
                if file_size_mb > 5:
                    st.warning(f"📦 {filename} is large. Compressing...")
                    file_bytes = zlib.compress(file_bytes)
                    st.success("Successfully Compressed")
                else:
                    st.info(f"Uploading {filename} as is.")
                filters = {
                    "filename": filename,
                    "branch": branch,
                    "year": year,
                    "semester": semester,
                    "subject": subject,
                    "unit": unit
                }
                if is_duplicate("assignments", filters):
                    st.warning(f"'{filename}' already exists. Skipping upload.")
                else:
                    try:
                        encoded = base64.b64encode(file_bytes).decode("utf-8")
                        supabase.table("assignments").insert({
                            **filters,
                            "filedata": encoded,
                            "uploaded_at": datetime.now().isoformat()
                        }).execute()
                    except Exception as e:
                        st.error(f"❌ Upload failed for '{filename}': {e}")

                progress_bar.progress((index + 1) / total_files)
                status_text.text(f"Uploaded {index + 1} of {total_files} files")
            st.success("🎉 All files processed.")

    elif upload_type == "🧠 Aptitude Test":
        st.subheader("Upload Aptitude Test Details")
        year = st.selectbox("Select Your Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        title = st.text_input("Test Title")
        description = st.text_area("Test Description")
        topics = st.text_area("Topics Covered (comma separated)")
        duration = st.text_input("Duration (e.g., 30 minutes)")
        total_questions = st.number_input("Total Questions", min_value=1, step=1)
        form_link = st.text_input("Google Form Link (URL)")
        expiry_hours = st.number_input("Expiry time in hours (after which test will be deleted)", min_value=1, step=1,value=24)
        if st.button("Upload Aptitude Test Info"):
            if not all([year, title, description, topics, duration, total_questions, form_link]):
                st.warning("Please fill all fields before uploading.")
            else:
                try:
                    expire_at = (datetime.now() + timedelta(hours=expiry_hours)).isoformat()
                    supabase.table("aptitude_test").insert({
                        "year": year,
                        "title": title.strip(),
                        "description": description.strip(),
                        "topics": topics.strip(),
                        "duration": duration.strip(),
                        "total_questions": total_questions,
                        "form_link": form_link.strip(),
                        "uploaded_at": datetime.now().isoformat(),
                        "expire_at": expire_at
                    }).execute()
                    st.success("✅ Aptitude test info uploaded successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to upload aptitude test info: {e}")

    elif upload_type == "🧩 Weekly Quiz":
        st.subheader("Upload Weekly Quiz")
        year = st.selectbox("Select Year", ["1st Year", "2nd Year", "3rd Year", "4th Year"])
        semester = st.selectbox("Select Semester", ["1 Semester", "2 Semester"])
        branch = st.selectbox("Select Branch",["CSE", "CSE AI", "CSE AI & ML", "CSE DS", "CSE CYB", "IT", "ECE", "EEE", "Mech","Civil"])
        title = st.text_input("Quiz Title")
        description = st.text_input("Quiz Description")
        topics = st.text_area("Topics Covered (comma separated)")
        duration = st.text_input("Duration (e.g., 20 minutes)")
        total_questions = st.number_input("Total Questions", min_value=1, step=1)
        form_link = st.text_input("Google Form Link (URL)")
        if st.button("Upload Weekly Quiz Info"):
            if not all([year, semester, branch, title, description, topics, duration, total_questions, form_link]):
                st.warning("Please fill all fields before uploading.")
            else:
                try:
                    expire_at = (datetime.now() + timedelta(days=7)).isoformat()
                    supabase.table("weekly_quiz").insert({
                        "year": year,
                        "semester": semester,
                        "branch": branch,
                        "title": title.strip(),
                        "description": description.strip(),
                        "topics": topics.strip(),
                        "duration": duration.strip(),
                        "total_questions": total_questions,
                        "form_link": form_link.strip(),
                        "uploaded_at": datetime.now().isoformat(),
                        "expire_at": expire_at
                    }).execute()

                    st.success("✅ Weekly quiz info uploaded successfully!")

                except Exception as e:
                    st.error(f"❌ Failed to upload weekly quiz info: {e}")

def main():
    st.set_page_config(page_title="🎓 Pragati's Exam Buddy")
    home_ui()
if st.session_state.page == "Home":
    home_ui()
elif st.session_state.page == "Question Papers":
    cleanup_expired_aptitude_tests()
    cleanup_expired_quiz_tests()
    downloader_ui()
elif st.session_state.page == "Subject Notes":
    subject_notes_ui()
elif st.session_state.page == "Assignments":
    assignment_ui()
elif st.session_state.page == "Aptitude Test":
    test()
elif st.session_state.page == "Weekly Quiz":
    weekly_quiz()
elif st.session_state.page == "Admin Login":
    if st.session_state.logged_in:
        uploader_and_admin_ui()
        if st.sidebar.button("📊 Dashboard"):
            st.session_state.page = "Admin Dashboard"
            st.rerun()
        if st.sidebar.button("Logout"):
            logout()
        st.header("🗑 Delete Uploaded PDFs")
        delete_type = st.selectbox("Select Table to Manage", ["Question Papers", "Subject Notes","Assignments"], key="delete_table")
        search_query = st.text_input("🔍 Search by filename to delete...", key="delete_search").lower()

        if delete_type == "Question Papers":
            if search_query:
                response = supabase.table("pdfs").select("id, filename").execute()
                files = response.data or []
                filtered_files = [file for file in files if search_query in file["filename"].lower()]

                for file in filtered_files:
                    with st.expander(file["filename"]):
                        confirm = st.checkbox(f"Are you sure you want to delete {file['filename']}?",
                                              key="chk_" + str(file["id"]))
                        if st.button(f"❌ Delete {file['filename']}", key="del_" + str(file["id"])):
                            if confirm:
                                supabase.table("pdfs").delete().eq("id", file["id"]).execute()
                                st.success(f"Deleted {file['filename']} successfully")
                                st.rerun()
        elif delete_type == "Subject Notes":
            if search_query:
                response = supabase.table("subject_notes").select("id, filename").execute()
                files = response.data or []
                filtered_files = [file for file in files if search_query in file["filename"].lower()]
                for file in filtered_files:
                    with st.expander(file["filename"]):
                        confirm = st.checkbox(f"Are you sure you want to delete {file['filename']}?",
                                              key="chk_" + str(file["id"]))
                        if st.button(f"❌ Delete {file['filename']}", key="del_" + str(file["id"])):
                            if confirm:
                                supabase.table("subject_notes").delete().eq("id", file["id"]).execute()
                                st.success(f"Deleted {file['filename']} successfully")
                                st.rerun()
        elif delete_type == "Assignments":
            if search_query:
                response = supabase.table("assignments").select("id, filename").execute()
                files = response.data or []
                filtered_files = [file for file in files if search_query in file["filename"].lower()]
                for file in filtered_files:
                    with st.expander(file["filename"]):
                        confirm = st.checkbox(f"Are you sure you want to delete {file['filename']}?",
                                              key="chk_" + str(file["id"]))
                        if st.button(f"❌ Delete {file['filename']}", key="del_" + str(file["id"])):
                            if confirm:
                                supabase.table("assignments").delete().eq("id", file["id"]).execute()
                                st.success(f"Deleted {file['filename']} successfully")
                                st.rerun()
    else:
        login()
elif st.session_state.page == "Admin Dashboard":
    if st.session_state.logged_in:
        admin_dashboard()
    else:
        st.warning("Please login as admin to access this dashboard.")

if __name__ == "_main_":
    main()

st.markdown("---", unsafe_allow_html=True)
st.markdown("""
<div style='text-align: center; font-size: 0.9em; color: #888;'>
    Designed & Developed by <strong> 22A31A4446 , 22A31A4462 .</strong><br>
    <em>✨ CSE - Data Science (2022-2026).</em>
</div>
""", unsafe_allow_html=True)
