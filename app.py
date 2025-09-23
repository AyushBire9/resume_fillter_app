from flask import Flask, render_template, request, redirect, url_for
import os
import smtplib
from email.message import EmailMessage
import nltk
from utils import extract_text, check_eligibility
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from models import db, Resume

# Load environment variables
load_dotenv()

# Download tokenizer
nltk.download('punkt')

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Gmail credentials (disabled)
# SENDER_EMAIL = os.getenv("SENDER_EMAIL")
# SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/create-resume')
def create_resume():
    return render_template('create-resume.html')

@app.route('/check-resume')
def check_resume():
    return render_template('check-resume.html')

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        profession = request.form.get('profession')
        job_level = request.form.get('jobLevel')
        file = request.files.get('resume')

        if file and file.filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            text = extract_text(filepath)
            eligible = check_eligibility(text)

            # Generate ATS score based on profession and job level
            ats_score = calculate_ats_score(text, profession, job_level)

            # Save to database
            resume = Resume(
                filename=file.filename,
                original_filename=file.filename,
                name=f"ATS Check - {profession}",
                profession=profession,
                job_level=job_level,
                resume_text=text,
                eligible=eligible,
                ats_score=ats_score
            )
            db.session.add(resume)
            db.session.commit()

            # Redirect to result page with query params
            return redirect(url_for('result_page', name=f"ATS Check - {profession}", eligible=str(eligible).lower(), text=text, ats_score=ats_score, profession=profession, job_level=job_level))

        return render_template('check-resume.html', error="❌ No file uploaded.")

    except Exception as e:
        print("❌ Internal Error:", e)
        return render_template('check-resume.html', error=f"❌ Internal Error: {e}")

def calculate_ats_score(text, profession, job_level):
    """Calculate ATS score based on resume content and target criteria"""
    score = 60  # Base score

    # Profession-specific keywords
    profession_keywords = {
        'web-development': ['javascript', 'html', 'css', 'react', 'node', 'python', 'framework', 'api'],
        'data-science': ['python', 'machine learning', 'statistics', 'pandas', 'numpy', 'sql', 'analysis'],
        'digital-marketing': ['seo', 'sem', 'google analytics', 'social media', 'campaign', 'content'],
        'software-engineering': ['java', 'python', 'git', 'agile', 'testing', 'design patterns'],
        'ui-ux-design': ['figma', 'adobe', 'wireframe', 'prototype', 'user research', 'usability']
    }

    # Job level requirements
    level_multipliers = {
        'entry': 1.0,
        'mid': 1.2,
        'senior': 1.4,
        'lead': 1.6,
        'executive': 1.8
    }

    # Check for profession-specific keywords
    keywords = profession_keywords.get(profession, [])
    keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text.lower())
    score += min(keyword_matches * 5, 25)  # Max 25 points for keywords

    # Check for basic requirements
    if len(text.split()) > 100:  # Minimum word count
        score += 10

    if any(section in text.lower() for section in ['experience', 'education', 'skills']):
        score += 5

    # Apply job level multiplier
    multiplier = level_multipliers.get(job_level, 1.0)
    score = int(score * multiplier)

    return min(score, 100)  # Cap at 100

@app.route('/result')
def result_page():
    name = request.args.get("name")
    eligible = request.args.get("eligible") == "true"
    text = request.args.get("text", "")
    ats_score = request.args.get("ats_score", 0)
    profession = request.args.get("profession", "")
    job_level = request.args.get("job_level", "")
    return render_template('result.html', name=name, eligible=eligible, resume_text=text, ats_score=int(ats_score), profession=profession, job_level=job_level)

@app.route('/admin/resumes')
def view_resumes():
    # Clean up corrupted data before displaying
    cleanup_corrupted_data()

    resumes = Resume.query.order_by(Resume.upload_date.desc()).all()
    eligible_count = Resume.query.filter_by(eligible=True).count()
    not_eligible_count = Resume.query.filter_by(eligible=False).count()
    ats_resumes_count = Resume.query.filter(Resume.profession.isnot(None)).count()
    return render_template('resumes.html', resumes=resumes, eligible_count=eligible_count, not_eligible_count=not_eligible_count, ats_resumes_count=ats_resumes_count)

def cleanup_corrupted_data():
    """Clean up corrupted resume data where resume_text contains SQL instead of actual content"""
    try:
        corrupted_resumes = Resume.query.filter(
            Resume.resume_text.like('%SELECT%') |
            Resume.resume_text.like('%INSERT%') |
            Resume.resume_text.like('%UPDATE%') |
            Resume.resume_text.like('%DELETE%') |
            Resume.resume_text.like('%FROM%') |
            Resume.resume_text.like('%WHERE%') |
            Resume.resume_text.like('%sqlite%')
        ).all()

        for resume in corrupted_resumes:
            # Remove corrupted entries
            db.session.delete(resume)

        if corrupted_resumes:
            db.session.commit()
            print(f"✅ Cleaned up {len(corrupted_resumes)} corrupted resume entries")

    except Exception as e:
        print(f"❌ Error cleaning up corrupted data: {e}")
        db.session.rollback()

@app.route('/admin/cleanup-corrupted')
def cleanup_corrupted_route():
    """Manual route to clean up corrupted data"""
    cleanup_corrupted_data()
    return redirect(url_for('view_resumes'))

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

            # Save to database
            resume = Resume(
                filename=file.filename,
                original_filename=file.filename,
                name=name,
                email=email,
                resume_text=text,
                eligible=eligible
            )
            db.session.add(resume)
            db.session.commit()

            # send_email(email, name, eligible)  # Email functionality disabled

            # Redirect to result page with query params
            return redirect(url_for('result_page', name=name, eligible=str(eligible).lower(), text=text))

        return render_template('index.html', result="❌ No file uploaded.")

    except Exception as e:
        print("❌ Internal Error:", e)
        return render_template('index.html', result=f"❌ Internal Error: {e}")

# def send_email(to_email, name, eligible):
#     try:
#         msg = EmailMessage()
#         msg['Subject'] = 'Resume Eligibility Result'
#         msg['From'] = SENDER_EMAIL
#         msg['To'] = to_email
#
#         status = "✅ You are Eligible!" if eligible else "❌ You are Not Eligible."
#         body = f"""Hello {name},
#
# Thank you for submitting your resume.
#
# Your eligibility status: {status}
#
# Regards,
# Resume Filter Bot"""
#
#         msg.set_content(body)
#
#         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
#             smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
#             smtp.send_message(msg)
#
#         print(f"✅ Email sent to {to_email}")
#     except Exception as e:
#         print(f"❌ Email send failed: {e}")

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(host='0.0.0.0', port=5000, debug=True)
