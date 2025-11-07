AI Log Analyzer
Intelligent Log File Analysis & Anomaly Detection Platform

Overview

AI Log Analyzer is a secure, machine-learning–driven web application designed to identify anomalies and irregular patterns in structured log data.
Built with Flask and powered by Isolation Forest, it provides an end-to-end interface for ingesting, processing, and visualizing log files through dynamic dashboards and downloadable reports.

Key Features :

- Automated Anomaly Detection – Detects unusual or suspicious entries using Isolation Forest.

- Comprehensive Reporting – Exports results to downloadable PDF and CSV formats.

- Visual Analytics – Interactive dashboards with risk-level indicators and charts powered by Chart.js.

- Large-File Support – Optimized processing for datasets exceeding 100 MB using chunked computation.

- Data Security – Strict upload validation, HTTPS enforcement, and modern security headers.

- Responsive Design – Minimalist interface optimized for both desktop and mobile browsers.

Technology Stack :
Layer	Technology
Frontend	HTML 5, CSS 3, JavaScript (Chart.js)
Backend	Python 3 / Flask
Machine Learning	Scikit-learn (Isolation Forest), Pandas
PDF Generation	FPDF
Hosting	Render (Free Tier)

Project Structure :

ai_log_analyzer/
│
├── app.py               # Flask application and routing logic
├── analyzer.py          # ML model and data-processing pipeline
├── requirements.txt     # Dependencies
├── Procfile             # Deployment configuration
│
├── templates/           # Jinja2 templates
│   ├── index.html
│   └── report.html
│
├── static/              # Front-end assets (CSS, JS, icons)
│   ├── style.css
│   └── script.js
│
└── uploads/             # Temporary storage for user uploads

Local Deployment :

# 1. Clone repository
git clone https://github.com/<your-username>/ai_log_analyzer.git
cd ai_log_analyzer

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch application
python app.py


Access the dashboard locally at:
➡ https://127.0.0.1:5000

Cloud Deployment (Render) :

1) Push the repository to GitHub.

2) In Render, select New → Web Service.

3) Connect this GitHub repository.

4) Configure:

    - Build Command → pip install -r requirements.txt

    - Start Command → gunicorn app:app

5) Choose instance type Free (for personal/demo use).

6) Deploy.

7) Access your public URL:
   https://<your-app-name>.onrender.com

Security Implementation :

- HTTPS Enforcement (automatic redirect)

- Strict-Transport-Security (HSTS)

- X-Frame-Options and X-Content-Type-Options headers

- CSP restricting external scripts and styles

- File Upload Restriction to CSV only (≤ 200 MB)

- Session Hardening via HttpOnly, Secure, and SameSite attributes

Author :

Aditya Yewatikar
Email: — officialadityayewatikar@gmail.com
LinkedIn: www.linkedin.com/in/aditya-yewatikar-02791323a
Live Demo: https://ai-log-analyzer-culk.onrender.com/

Acknowledgements :

Developed as part of a cybersecurity and AI-driven analytics initiative focusing on automated log interpretation and anomaly detection.
