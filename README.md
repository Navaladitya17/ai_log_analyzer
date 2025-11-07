AI Log Analyzer — Intelligent Log File Anomaly Detection

Overview : 
AI Log Analyzer is a Flask-based web application that uses machine learning (Isolation Forest) to detect anomalies or irregularities in large log files.
It helps security analysts and developers identify potential issues, security threats, or unusual activity in log data quickly — with interactive dashboards, charts, and PDF/CSV reports.

🚀 Features

📁 Upload any CSV log file (up to 200 MB)

🤖 AI-powered anomaly detection using IsolationForest

📊 Interactive charts with Chart.js

📈 Risk level indicators (Low / Medium / High / Critical)

📑 Downloadable PDF & CSV reports

🧱 Secure architecture with HTTPS & strong Flask headers

🌙 Responsive modern UI with dark-themed dashboard

⚙️ Handles both small and large CSVs (chunked processing for big files)

🧰 Tech Stack
Component	Technology
Frontend	HTML5, CSS3, JavaScript, Chart.js
Backend	Flask (Python 3), Pandas, scikit-learn
ML Model	Isolation Forest
Deployment	Render (Free Tier)
Reporting	FPDF for PDF generation
🏗️ Project Structure
ai_log_analyzer/
│
├── app.py                 # Main Flask app
├── analyzer.py            # Core ML logic
├── requirements.txt       # Python dependencies
├── Procfile               # For Render deployment
│
├── templates/             # Jinja2 HTML templates
│   ├── index.html
│   └── report.html
│
├── static/                # CSS, JS, and images
│   ├── style.css
│   └── script.js
│
└── uploads/               # Temporary uploaded files (auto-created)

🧪 Local Setup

To run this project locally on your system:

# 1️⃣ Clone the repository
git clone https://github.com/YOUR_USERNAME/ai_log_analyzer.git
cd ai_log_analyzer

# 2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate   # (on Windows)
# or
source venv/bin/activate  # (on macOS/Linux)

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run the app
python app.py


Then open your browser and visit:
👉 https://127.0.0.1:5000/

☁️ Deployment (Render)

Push your repository to GitHub.

Go to Render.com
.

Click New → Web Service.

Connect your GitHub repo.

Fill these fields:

Build Command: pip install -r requirements.txt

Start Command: gunicorn app:app

Deploy 🚀 — your site will be live at
(https://ai-log-analyzer-culk.onrender.com/)

🛡️ Security Highlights

Enforced HTTPS via Flask redirect middleware

Added secure headers (CSP, HSTS, X-Frame-Options, etc.)

Limited uploads to CSV only

Max upload size: 200 MB

Auto cleanup of temporary files

🧑‍💻 Author

Aditya Yewatikar
📫 LinkedIn

🔗 Project Live : https://ai-log-analyzer-culk.onrender.com

⭐ Support

If you find this project useful — please star the repository ⭐
and share it with others!
