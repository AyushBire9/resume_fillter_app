import PyPDF2
import docx
import os
import nltk

nltk.download('punkt')

# Define required skills (can be updated anytime)
REQUIRED_SKILLS = {"python", "flask", "sql", "machine learning", "html", "css", "data analysis"}

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""

    if ext == ".pdf":
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    elif ext in [".docx", ".doc"]:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    
    return text.lower()

def check_eligibility(text):
    # Tokenize resume text into words
    words = set(nltk.word_tokenize(text.lower()))
    
    # Normalize REQUIRED_SKILLS to lowercase
    required = set(skill.lower() for skill in REQUIRED_SKILLS)
    
    # Check how many skills match
    matches = required & words
    return len(matches) >= 3
