import pdfplumber
import docx

def extract_text_from_file(uploaded_file) -> str:
    filename = uploaded_file.name.lower()
    text = ""
    
    if filename.endswith(".pdf"):
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    elif filename.endswith(".docx"):
        doc = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs if para.text])
    elif filename.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
        
    return text

def chunk_text(text: str, chunk_size: int = 3000) -> list:
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
