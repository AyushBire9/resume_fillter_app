from flask import Flask, render_template, request
import os
from utils import extract_text, check_eligibility
import nltk

# Correct tokenizer download
nltk.download('punkt')

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    name = request.form.get('name')
    email = request.form.get('email')
    file = request.files['resume']

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        text = extract_text(filepath)
        eligible = check_eligibility(text)
        result = f"{name}, your result is: ✅ Eligible" if eligible else f"{name}, your result is: ❌ Not Eligible"

        return render_template('index.html', result=result, resume_text=text)

    return render_template('index.html', result="❌ File not received.")

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
