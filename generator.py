import os
import time
import streamlit as st
from google import genai
from google.genai import errors
from pydantic import BaseModel, Field
from typing import List

# Initialize Gemini Client
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Structured Output Schema for Quiz
class Question(BaseModel):
    question: str = Field(description="The question text")
    options: List[str] = Field(description="List of 4 options")
    correct_answer: str = Field(description="The correct option")

class Quiz(BaseModel):
    questions: List[Question]

def generate_summary(chunks: List[str]) -> str:
    combined_text = "\n\n".join(chunks)
    prompt = f"Provide a detailed, well-structured summary of the following material:\n\n{combined_text}"
    
    # Retry loop for 503 server errors
    for attempt in range(3):
        try:
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return res.text
        except errors.ServerError as e:
            if attempt < 2:
                time.sleep(2)
                continue
            raise e

def generate_practice_questions(summary_text: str) -> Quiz:
    prompt = f"Generate 5 multiple-choice practice questions based on this summary:\n\n{summary_text}"
    
    # Retry loop for 503 server errors
    for attempt in range(3):
        try:
            res = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Quiz,
                }
            )
            return res.parsed
        except errors.ServerError as e:
            if attempt < 2:
                time.sleep(2)
                continue
            raise e
