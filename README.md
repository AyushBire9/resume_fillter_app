# Resume Filter Application

An AI-powered Flask application that analyzes resumes and determines job eligibility based on required skills using Natural Language Processing (NLP).

## Features

- 📄 **Multi-format Support**: Upload PDF and DOCX resumes
- 🤖 **AI-Powered Analysis**: Uses NLTK for intelligent text processing
- 📊 **Database Storage**: SQLite database to store all uploaded resumes
- 📧 **Email Notifications**: Automatic email results to candidates
- 🎨 **Modern UI**: Beautiful glassmorphism design
- 📈 **Admin Dashboard**: View statistics and stored resumes
- 🔒 **Secure**: Environment-based configuration

## Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd resume_filter_app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Gmail credentials
# Get App Password from: https://support.google.com/accounts/answer/185833
```

### 3. Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` to access the application.

## Project Structure

```
resume_filter_app/
├── app.py              # Main Flask application
├── models.py           # Database models
├── utils.py            # Text extraction and eligibility logic
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── templates/          # HTML templates
│   ├── home.html
│   ├── index.html
│   ├── result.html
│   └── resumes.html
└── uploads/            # Uploaded resume files
```

## Database Schema

The application uses SQLite with the following schema:

```sql
CREATE TABLE resume (
    id INTEGER PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    resume_text TEXT NOT NULL,
    eligible BOOLEAN NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

- `GET /` - Home page
- `GET /index` - Resume upload form
- `POST /upload` - Process resume upload
- `GET /result` - Display eligibility results
- `GET /admin/resumes` - Admin dashboard (view stored resumes)

## Configuration

### Required Skills
Edit `utils.py` to modify the required skills list:

```python
REQUIRED_SKILLS = {
    "python", "flask", "sql", "machine learning",
    "html", "css", "data analysis"
}
```

### Email Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Add credentials to `.env` file:
   ```
   SENDER_EMAIL=your-email@gmail.com
   SENDER_PASSWORD=your-app-password
   ```

## Features in Detail

### Resume Processing
- Extracts text from PDF/DOCX files
- Tokenizes and analyzes content
- Matches against required skills
- Requires minimum 3 skill matches for eligibility

### Admin Dashboard
- View all uploaded resumes
- Statistics on eligible vs non-eligible candidates
- Resume content preview
- Upload date tracking

### Security Features
- File type validation
- Secure file upload handling
- Environment variable configuration
- CSRF protection ready

## Development

### Adding New Features
1. Database models go in `models.py`
2. Business logic in `utils.py`
3. New routes in `app.py`
4. Templates in `templates/` directory

### Testing
```bash
# Run with debug mode
python app.py

# Access admin dashboard
# http://localhost:5000/admin/resumes
```

## Deployment

### Production Setup
1. Use production WSGI server (Gunicorn)
2. Configure production database (PostgreSQL/MySQL)
3. Set proper environment variables
4. Configure reverse proxy (Nginx)
5. Enable HTTPS

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues or questions, please open an issue on GitHub or contact the development team.

---

**Made with ❤️ for job seekers and recruiters**
