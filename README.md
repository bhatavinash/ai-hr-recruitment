# ai-hr-recruitment
# 🤖 AI-Powered HR Recruitment Automation System

An intelligent recruitment automation platform that streamlines the candidate screening workflow using **Artificial Intelligence, automation, and data-driven candidate matching**.

The system automatically processes resumes received through email, extracts candidate information using **Gemini AI**, stores structured data in **PostgreSQL**, matches candidates against job requirements, and provides an interactive **Streamlit dashboard** for HR teams to manage recruitment decisions.

---

## 🚀 Project Overview

Recruitment teams often spend significant time manually reviewing resumes, extracting candidate information, comparing skills with job requirements, and communicating decisions.

This project aims to automate and simplify that workflow.

### End-to-End Workflow

```text
📧 Candidate Sends Resume
        ↓
📨 Email Monitoring
        ↓
📄 Resume Detection (PDF / DOCX)
        ↓
📝 Resume Text Extraction
        ↓
🤖 Gemini AI Resume Parsing
        ↓
🗄️ PostgreSQL Database
        ↓
🎯 Candidate–Job Matching
        ↓
📊 Match Score & Skill Analysis
        ↓
👥 HR Dashboard
        ↓
✅ Selection / ❌ Rejection
        ↓
✉️ Automated Candidate Email
```

---

# ✨ Key Features

## 📧 Automated Resume Processing

* Monitors incoming candidate emails.
* Detects resume attachments.
* Supports **PDF and DOCX** resumes.
* Prevents the same email from being processed multiple times.
* Tracks processed emails for workflow reliability.

---

## 🤖 AI-Powered Resume Parsing

The system uses **Gemini AI** to extract structured candidate information from resumes.

Extracted information includes:

* 👤 Name
* 📧 Email
* 📱 Phone Number
* 📍 Location
* 💼 Years of Experience
* 🛠️ Technical Skills

Example structured output:

```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "location": "Bengaluru",
    "experience_years": 3,
    "skills": [
        "Python",
        "SQL",
        "PySpark",
        "AWS"
    ]
}
```

---

# 🗄️ Database Storage

Candidate information is stored in **PostgreSQL**.

### Candidates Table

Stores candidate details:

```text
id
name
email
phone
location
experience_years
resume_path
created_at
```

### Candidate Skills Table

Stores individual skills for each candidate.

```text
id
candidate_id
skill
```

This relational design allows one candidate to have multiple skills.

---

# 💼 Job Management

HR users can create job requirements directly from the dashboard.

Example:

```text
Job Title:
Data Engineer

Required Skills:
Python, SQL, PySpark, AWS, Airflow

Minimum Experience:
2 Years
```

Once a job is created, the system can automatically match existing candidates against the job requirements.

---

# 🎯 AI Candidate Matching

The matching engine compares:

* Candidate Skills
* Required Job Skills
* Candidate Experience
* Minimum Experience Requirement

The system identifies:

### ✅ Matched Skills

Skills available in both the candidate profile and job requirements.

Example:

```text
Python
SQL
PySpark
AWS
```

### ❌ Missing Skills

Skills required by the job but not found in the candidate resume.

Example:

```text
Airflow
```

---

# 📊 Match Score Calculation

The current matching logic uses:

* **80% weight → Skill Match**
* **20% weight → Experience Match**

### Skill Match

```text
Matched Skills / Required Skills × 100
```

### Final Score

```text
Final Match Score =
(Skill Match × 0.8)
+
(Experience Score × 0.2)
```

Example:

```text
Candidate Skills:
Python, SQL, PySpark, AWS

Required Skills:
Python, SQL, PySpark, AWS, Airflow

Skill Match:
4 / 5 × 100 = 80%

Experience Match:
100%

Final Score:
(80 × 0.8) + (100 × 0.2)

= 84%
```

---

# 🟢 Candidate Categorization

Candidates are automatically categorized based on their match score.

| Match Score      | Category    |
| ---------------- | ----------- |
| 🟢 80% and above | SHORTLISTED |
| 🟡 50% – 79%     | REVIEW      |
| 🔴 Below 50%     | REJECTED    |

---

# 📊 HR Dashboard

The Streamlit dashboard provides an overview of the recruitment pipeline.

### Dashboard Metrics

* 👥 Total Candidates
* 💼 Total Jobs
* 🟢 Shortlisted Candidates
* 🟡 Candidates Under Review
* 🔴 Rejected Candidates
* 🎉 Selected Candidates

The dashboard also displays top-ranked candidates based on match percentage.

---

# 👥 Candidate Profile

HR users can search and select a candidate to view their complete profile.

The profile includes:

* Name
* Email
* Phone Number
* Location
* Experience
* Resume Path
* All Extracted Skills
* Job Application History
* Match Percentage
* Matched Skills
* Missing Skills
* Experience Match Status

---

# 📋 Application Management

HR can filter applications based on:

* Job Role
* Candidate Status

Example statuses:

```text
SHORTLISTED
REVIEW
REJECTED
SELECTED
```

---

# ⚡ Bulk Candidate Actions

The system supports selecting multiple candidates simultaneously.

HR can:

* ✅ Accept multiple candidates
* ❌ Reject multiple candidates

Example:

```text
☑ Candidate A – 92%
☑ Candidate B – 87%
☑ Candidate C – 84%

Selected Candidates: 3
```

The system processes each candidate individually and sends personalized communication.

---

# ✉️ Automated Email Communication

The system sends personalized emails based on HR decisions.

### Selected Candidate

```text
Hi Candidate Name,

Congratulations!

We are pleased to inform you that you have been selected for the next stage of the recruitment process.

Our HR team will contact you shortly regarding the next steps.

Best regards,
HR Team
```

### Rejected Candidate

```text
Hi Candidate Name,

Thank you for taking the time to apply for the position.

After careful consideration, we have decided to move forward with candidates whose profiles currently align more closely with our requirements.

We sincerely appreciate your interest and wish you the very best in your future career.

Best regards,
HR Team
```

---

# 📧 Email Safety Workflow

The system follows a safe workflow:

```text
Send Email
    ↓
Email Sent Successfully?
    ↓
YES
    ↓
Update Application Status
    ↓
Save Email History
```

If the email fails:

```text
❌ Application status is not updated
❌ Email history is not recorded as successful
```

This helps maintain consistency between candidate communication and database records.

---

# 🏗️ System Architecture

```text
                    ┌───────────────┐
                    │   Candidate   │
                    └───────┬───────┘
                            │
                         Resume
                            │
                            ▼
                    ┌───────────────┐
                    │ Email Monitor │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Resume Filter │
                    │ PDF / DOCX    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Text Extractor│
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Gemini AI   │
                    │ Resume Parser │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  PostgreSQL   │
                    │   Database    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Matching Engine│
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Match Results │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │Streamlit HR UI│
                    └───────┬───────┘
                            │
                            ▼
                       HR Decision
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
             Individual             Bulk
                  │                   │
                  └─────────┬─────────┘
                            │
                            ▼
                    Email Service
                            │
                            ▼
                    Update Database
                            │
                            ▼
                     Email History
```

---

# 🛠️ Tech Stack

| Technology  | Purpose                                |
| ----------- | -------------------------------------- |
| Python      | Core application development           |
| Gemini AI   | Resume information extraction          |
| PostgreSQL  | Candidate and recruitment data storage |
| Streamlit   | HR dashboard                           |
| Gmail API   | Email monitoring and automation        |
| PyMuPDF     | PDF text extraction                    |
| python-docx | DOCX text extraction                   |
| psycopg2    | PostgreSQL database connectivity       |
| Pandas      | Data processing and dashboard tables   |

---

# 📁 Project Structure

```text
ai_hr_recruitment/
│
├── app/
│   ├── dashboard.py
│   ├── database.py
│   ├── resume_processor.py
│   ├── gemini_parser.py
│   ├── candidate_repository.py
│   ├── matching_engine.py
│   ├── auto_match.py
│   ├── email_repository.py
│   ├── email_service.py
│   ├── email_history_repository.py
│   ├── application_repository.py
│   └── job_repository.py
│
├── resumes/
├── parsed/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-hr-recruitment.git
```

```bash
cd ai-hr-recruitment
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---
Google Cloud & Gmail API Integration

The project integrates with the Gmail API through Google Cloud OAuth 2.0 to automate resume ingestion from candidate emails.

A Google Cloud project is configured to:

Enable the Gmail API.
Configure the Google OAuth consent screen.
Create OAuth 2.0 credentials for the application.
Authorize the application to access the required Gmail functionality.
Monitor incoming emails for candidate resumes.
Download relevant PDF and DOCX attachments.
Track processed emails to prevent duplicate resume processing.
## 4. Configure Environment Variables

Create a `.env` file:

```text
DB_URL=postgresql://USERNAME:PASSWORD@localhost:5432/DATABASE_NAME

GEMINI_API_KEY=your_gemini_api_key

EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_email_app_password
```

⚠️ Never commit your `.env` file to GitHub.

---

## 5. Create Database Tables

Ensure PostgreSQL is running and your database is configured.

Run the database initialization script:

```bash
python app/database.py
```

---

## 6. Start the Application

```bash
streamlit run app/dashboard.py
```

Open the Streamlit URL displayed in your terminal.

---

# 🔮 Future Improvements

* 🔐 Role-based authentication for HR users
* 📄 Resume preview directly inside the dashboard
* 📈 Advanced candidate analytics
* 🤖 Improved semantic matching using embeddings
* 🧠 Job description analysis using AI
* 🔔 Real-time notifications
* ☁️ Cloud deployment
* 🐳 Docker containerization
* 🔄 CI/CD pipeline
* 📊 Recruitment analytics and reporting
* 🌐 Multi-user support

---

# 💡 Learning Outcomes

Through this project, I explored and combined:

* AI-powered information extraction
* Generative AI integration
* Database design and normalization
* ETL-style data processing
* Candidate matching algorithms
* Email automation
* Dashboard development
* Bulk workflow automation
* End-to-end application development

---

# 👨‍💻 Author

**Avinash Bhat**

If you found this project interesting, feel free to ⭐ the repository!

---

## ⭐ If You Like This Project

Please consider giving the repository a **star ⭐**. It helps others discover the project and motivates further improvements!
