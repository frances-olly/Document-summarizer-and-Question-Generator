import os
import time
import tempfile
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from parser import parse_document, create_chunks
from generator import generate_summary, generate_practice_questions

# Page Configuration
st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="wide")

st.title("📚 Intelligent Document Summarizer & Quiz Generator")
st.write("Upload your lecture notes, seminar papers, or project files (.docx, .pdf, .txt) to generate summaries and practice quizzes.")

# File Uploader Widget
uploaded_file = st.sidebar.file_uploader("Upload a Document", type=["docx", "pdf", "txt"])

if uploaded_file is not None:
    # Save uploaded file temporarily to disk
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        temp_path = tmp_file.name

    st.sidebar.success(f"File '{uploaded_file.name}' loaded successfully!")
    
    # Process Document
    with st.spinner("Parsing and chunking document..."):
        text = parse_document(temp_path)
        chunks = create_chunks(text)
        os.remove(temp_path)  # Clean up temporary file

    st.info(f"Document split into **{len(chunks)} chunk(s)**.")

    # Main Tabs Interface
    tab1, tab2 = st.tabs(["📝 Summary", "❓ Practice Quiz"])

    with tab1:
        st.header("Document Summary")
        if st.button("Generate Summary"):
            with st.spinner("Analyzing full document and generating comprehensive summary..."):
                summary = generate_summary(chunks)  # Pass all chunks
                st.write(summary)  

    with tab2:
        st.header("Practice Quiz")
        num_q = st.slider("Select number of questions:", min_value=3, max_value=100, value=5)
        
        # 1. Generate and store the quiz in session state
        if st.button("Generate Questions"):
            with st.spinner("Generating revision questions..."):
                st.session_state.quiz = generate_practice_questions(chunks, num_questions=num_q)

        # 2. Render the form if a quiz exists in session state
        if "quiz" in st.session_state:
            with st.form("quiz_form"):
                user_answers = {}
                for idx, q in enumerate(st.session_state.quiz.questions, start=1):
                    st.subheader(f"Q{idx}: {q.question}")
                    user_answers[idx] = st.radio(
                        f"Select your answer for Q{idx}:", 
                        q.options, 
                        key=f"q_{idx}"
                    )
                    st.divider()
                
                submitted = st.form_submit_button("Submit All Answers")
                
            # 3. Process answers when user clicks submit
            if submitted:
                st.success("Quiz Submitted!")
                for idx, q in enumerate(st.session_state.quiz.questions, start=1):
                    selected = user_answers[idx]
                    if selected == q.correct_answer:
                        st.write(f"**Q{idx}:** Correct! ({q.correct_answer})")
                    else:
                        st.write(f"**Q{idx}:** Incorrect. Correct answer: **{q.correct_answer}**")
                    st.info(f"**Explanation:** {q.explanation}")

else:
    st.info("Please upload a `.docx`, `.pdf`, or `.txt` file using the sidebar to begin.")
