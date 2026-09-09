import os
import streamlit as st
from google import genai
from pydantic import BaseModel, Field
from typing import List

# Fetch API key securely from Streamlit secrets or environment variables
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# --- Structured Output Schema ---
class Question(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="4 distinct choices")
    correct_answer: str = Field(description="The exact text of the correct choice")
    explanation: str = Field(description="Brief explanation of why the answer is correct")

class Quiz(BaseModel):
    questions: List[Question]

# --- Core Generator Functions ---
import time  # Make sure 'import time' is at the top of generator.py

def generate_summary(chunks: List[str]) -> str:
    # Handle single chunk or short documents
    if len(chunks) == 1:
        prompt = f"Provide a comprehensive, highly detailed academic summary of the following text:\n\n{chunks[0]}"
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )
        return response.text

    # Map Step: Summarize each chunk with a brief delay
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        map_prompt = f"Summarize key facts, methodologies, and findings from this section (Part {i+1}):\n\n{chunk}"
        res = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=map_prompt
        )
        chunk_summaries.append(res.text)
        time.sleep(2)  # Pauses for 2 seconds to respect Free Tier API limits

    # Reduce Step: Combine all summaries into a master summary
    combined_text = "\n\n".join(chunk_summaries)
    reduce_prompt = (
        "You are an academic research assistant. Below are section summaries of a full document. "
        "Combine them into a single, cohesive, thorough academic summary. "
        "Organize it with clear sections: Overview/Context, Main Concepts, Key Findings, and Conclusion:\n\n"
        f"{combined_text}"
    )

    final_response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=reduce_prompt
    )
    return final_response.text

def generate_practice_questions(chunks: List[str], num_questions: int = 5) -> Quiz:
    # Combine chunks (or take the primary content) to give the model full context
    combined_text = "\n\n".join(chunks[:3]) # Takes main content without overloading
    
    prompt = f"Based on the following document context, generate exactly {num_questions} multiple-choice revision questions:\n\n{combined_text}"
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Quiz,
        )
    )
    return response.parsed

if __name__ == "__main__":
    sample_file = "sample.docx"
    
    try:
        print("Parsing document...")
        text = parse_document(sample_file)
        chunks = create_chunks(text)
        
        print(f"Loaded {len(chunks)} chunk(s). Processing Chunk 1 via Gemini API...\n")
        
        print("--- GENERATING SUMMARY ---")
        summary = generate_summary(chunks[0])
        print(summary)
        
        print("\n--- GENERATING PRACTICE QUESTIONS (STRUCTURED) ---")
        quiz_data = generate_practice_questions(chunks[0])
        
        for idx, q in enumerate(quiz_data.questions, 1):
            print(f"\nQ{idx}: {q.question}")
            for opt in q.options:
                print(f"  - {opt}")
            print(f"Answer: {q.correct_answer}")
            print(f"Explanation: {q.explanation}")
            
    except Exception as e:
        print(f"Error executing API pipeline: {e}")



