from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()  # initialize SQLAlchemy once

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    profession = db.Column(db.String(100), nullable=True)
    job_level = db.Column(db.String(50), nullable=True)
    resume_text = db.Column(db.Text, nullable=False)
    eligible = db.Column(db.Boolean, nullable=False)
    ats_score = db.Column(db.Integer, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Resume {self.filename}>'
