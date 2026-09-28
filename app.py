import streamlit as st
from utils import extract_text_from_file, chunk_text
from generator import generate_summary, generate_practice_questions

st.set_page_config(page_title="Document Summarizer & Quiz Generator", layout="wide")

st.title("Generator")
st.write("Upload your lecture notes, seminar papers, or project files (.docx, .pdf, .txt) to generate summaries and practice quizzes.")

# File Uploader
uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    if "summary" not in st.session_state:
        text = extract_text_from_file(uploaded_file)
        chunks = chunk_text(text)
        st.info(f"Document split into {len(chunks)} chunk(s).")
        
        with st.spinner("Generating summary..."):
            st.session_state.summary = generate_summary(chunks)

# Display Tabs once document is processed
if "summary" in st.session_state:
    tab1, tab2 = st.tabs(["Summary", "Practice Quiz"])

    with tab1:
        st.header("Document Summary")
        st.write(st.session_state.summary)

    with tab2:
        st.header("Practice Quiz")
        num_questions = st.slider("Select number of questions:", min_value=3, max_value=10, value=5)

        if st.button("Generate Questions"):
            with st.spinner("Generating questions from summary..."):
                st.session_state.quiz = generate_practice_questions(
                    summary_text=st.session_state.summary, 
                    num_questions=num_questions
                )

        # Render Quiz Form
        if "quiz" in st.session_state and st.session_state.quiz:
            with st.form("quiz_form"):
                user_answers = {}
                for idx, q in enumerate(st.session_state.quiz.questions):
                    st.subheader(f"Q{idx+1}: {q.question}")
                    user_answers[idx] = st.radio(
                        f"Select option for Q{idx+1}:", 
                        q.options, 
                        key=f"q_{idx}"
                    )
                
                submitted = st.form_submit_button("Submit Quiz")
                if submitted:
                    st.success("Quiz Submitted!")
                    score = 0
                    for idx, q in enumerate(st.session_state.quiz.questions):
                        if user_answers[idx] == q.correct_answer:
                            score += 1
                            st.write(f"**Q{idx+1}: Correct!**")
                        else:
                            st.write(f"**Q{idx+1}: Incorrect.** Correct answer: {q.correct_answer}")
                        st.info(f"**Explanation:** {q.explanation}")
                    
                    st.write(f"### Final Score: {score} / {len(st.session_state.quiz.questions)}")
