import os
import re
import pdfplumber
import docx

def clean_text(text):
    """
    Cleans up raw extracted text:
    - Rejoins words split across lines by hyphens (e.g., 'infrastru-\ncture' -> 'infrastructure')
    - Removes excessive spaces and repeated newline characters
    """
    # Fix broken hyphens across newlines
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
    return extracted_text.strip()

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return "\n".join(full_text).strip()

def parse_document(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        raw_text = extract_text_from_docx(file_path)
    elif file_extension == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")
        
    # Clean and normalize text before returning
    return clean_text(raw_text)

def create_chunks(text, chunk_size=5000, chunk_overlap=150):
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - chunk_overlap
        
    return chunks

# Test Parser & Chunker
if __name__ == "__main__":
    sample_file = "sample.docx"
    
    try:
        raw_text = parse_document(sample_file)
        print(f"Total raw characters extracted: {len(raw_text)}")
        
        chunks = create_chunks(raw_text)
        print(f"Total chunks created: {len(chunks)}")
        print("\n--- Preview of Cleaned Chunk 1 ---")
        print(chunks[0])
        
    except Exception as e:
        print(f"Error: {e}")