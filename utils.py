import PyPDF2
import docx
import os
import nltk

nltk.download('punkt')

# Define some sample keywords for filtering
REQUIRED_SKILLS = {"python", "flask", "sql", "machine learning"}

def extract_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""

    if ext == ".pdf":
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    elif ext in [".docx", ".doc"]:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.lower()

def check_eligibility(text):
    words = set(nltk.word_tokenize(text))
    matches = REQUIRED_SKILLS & words
    return len(matches) >= 3  # e.g. must match at least 3 skills
