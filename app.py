import streamlit as st
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from groq import Groq

# Load API Key
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Study Assistant", page_icon="🎓")

# -------------------- SESSION STATE --------------------
if "notes_count" not in st.session_state:
    st.session_state["notes_count"] = 0

if "quiz_count" not in st.session_state:
    st.session_state["quiz_count"] = 0


# -------------------- PREMIUM BACKGROUND --------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg, #667eea, #764ba2, #6a11cb, #2575fc);
    background-size: 300% 300%;
    animation: gradientMove 10s ease infinite;
}

@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.block-container {
    background: rgba(255, 255, 255, 0.15);
    padding: 2rem;
    border-radius: 25px;
    backdrop-filter: blur(15px);
}

h1, h2, h3, p, label {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)


# -------------------- HEADER --------------------
st.title("🎓 AI Smart Study Assistant")
st.markdown("### 📊 Learning Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📚 Notes Uploaded", st.session_state["notes_count"])

with col2:
    st.metric("📝 Quizzes Generated", st.session_state["quiz_count"])

with col3:
    progress_percent = min(st.session_state["quiz_count"] * 10, 100)
    st.metric("📈 Study Progress", f"{progress_percent}%")


st.write("Upload your notes and let AI summarize, generate quiz & solve doubts!")


# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader("📄 Upload your PDF Notes", type="pdf")

text = ""

if uploaded_file is not None:

    # increase only once per upload
    st.session_state["notes_count"] += 1

    pdf_reader = PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()

    st.success("PDF Uploaded Successfully!")

    # -------- SUMMARY --------
    if st.button("📚 Generate Summary"):
        with st.spinner("Generating Summary..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": f"Summarize this text in simple points:\n{text[:3000]}"}
                ],
            )

            summary = response.choices[0].message.content
            st.subheader("📌 Summary")
            st.write(summary)

    # -------- QUIZ --------
    if st.button("❓ Generate Quiz"):

        # increment ONLY when clicked
        st.session_state["quiz_count"] += 1

        with st.spinner("Creating Quiz..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": f"Create 5 MCQ questions from this content:\n{text[:3000]}"}
                ],
            )

            quiz = response.choices[0].message.content
            st.subheader("📝 Quiz Questions")
            st.write(quiz)


# -------------------- PROGRESS BAR --------------------
st.subheader("📈 Study Progress Tracker")

progress = min(st.session_state["quiz_count"] * 10, 100)
st.progress(progress / 100)
st.write(f"Completion Level: {progress}%")

if progress == 100:
    st.success("🎉 Study Goal Completed!")


# -------------------- CHATBOT --------------------
st.subheader("💬 Ask Your Doubts")

user_question = st.text_input("Enter your question:")

if st.button("Ask AI"):
    if user_question:
        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": user_question}
                ],
            )

            answer = response.choices[0].message.content
            st.write("🤖 AI Answer:")
            st.write(answer)
