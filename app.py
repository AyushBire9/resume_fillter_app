from flask import Flask, render_template, request
import os
import smtplib
from email.message import EmailMessage
import nltk
from utils import extract_text, check_eligibility
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Download NLTK tokenizer (only once)
nltk.download('punkt')

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Get Gmail credentials from .env
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_resume():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        file = request.files.get('resume')

        if file and file.filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            text = extract_text(filepath)
            eligible = check_eligibility(text)

            result = f"{name}, your result is: ✅ Eligible" if eligible else f"{name}, your result is: ❌ Not Eligible"

            send_email(email, name, eligible)

            return render_template('index.html', result=result, resume_text=text)

        return render_template('index.html', result="❌ No file uploaded.")

    except Exception as e:
        print("❌ Internal Error:", e)
        return render_template('index.html', result=f"❌ Internal Error: {e}")

def send_email(to_email, name, eligible):
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Resume Eligibility Result'
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        status = "✅ You are Eligible!" if eligible else "❌ You are Not Eligible."
        body = f"""Hello {name},

Thank you for submitting your resume.

Your eligibility status: {status}

Regards,
Resume Filter Bot"""

        msg.set_content(body)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)

        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email send failed: {e}")

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
