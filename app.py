# app.py
import os
import tempfile
import time
import secrets
from flask import (
    Flask, render_template, request, redirect, url_for,
    send_file, flash, Response
)
from analyzer import detect, detect_large
import pandas as pd
from fpdf import FPDF
from io import BytesIO

# ---------------------------------------------------------
# Flask Configuration
# ---------------------------------------------------------
app = Flask(__name__)

# 🔐 Security Settings
# Use a random secret on each start (for production set as env var)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB limit

ALLOWED_EXTENSIONS = {"csv"}

# Secure cookie defaults. If you run without HTTPS in dev, these might be adjusted later.
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,   # set to True for production behind HTTPS
    SESSION_COOKIE_SAMESITE="Lax",
)

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.after_request
def apply_secure_headers(response: Response):
    """Apply security headers after each request."""
    # HSTS (only has effect on HTTPS)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    # modern browsers ignore X-XSS-Protection, but keep it for legacy
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
    # Tight CSP: allow self, fonts.googleapis.com/css2, fonts.gstatic.com, cdn.jsdelivr.net for Chart.js
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    return response


@app.before_request
def enforce_https():
    """Redirect HTTP -> HTTPS in production (not in debug)."""
    # Only redirect if not in debug mode
    if not app.debug and not request.is_secure:
        # Avoid redirect loops with proxy setups; if behind proxy ensure Flask knows about X-Forwarded-Proto
        url = request.url.replace("http://", "https://", 1)
        return redirect(url, code=301)


# ---------------------------------------------------------
# Auto cache-busting for static files (CSS/JS)
# ---------------------------------------------------------
@app.context_processor
def override_url_for():
    """Append timestamp query to static file URLs (CSS/JS)."""
    def new_url_for(endpoint, **values):
        if endpoint == "static":
            values["v"] = int(time.time())
        return url_for(endpoint, **values)
    return dict(url_for=new_url_for)


# ---------------------------------------------------------
# Generate PDF (FPDF)
# ---------------------------------------------------------
def make_pdf_bytes(summary_text: str, anomalies_df: pd.DataFrame) -> BytesIO:
    """Create a simple text-based PDF report and return BytesIO."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "AI LOG ANALYZER - REPORT", ln=True, align="C")
    pdf.ln(8)
    pdf.set_font("Arial", "", 11)

    # Summary text
    for line in summary_text.split("\n"):
        pdf.multi_cell(0, 8, line)

    pdf.ln(6)
    pdf.cell(0, 8, f"Total anomalies: {len(anomalies_df)}", ln=True)
    pdf.ln(6)

    # Add top anomalies sample (keeps original column names)
    if not anomalies_df.empty:
        cols = anomalies_df.columns.tolist()
        sample = anomalies_df.head(15).fillna("").astype(str)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 8, "Sample Anomalies:", ln=True)
        pdf.set_font("Arial", "", 9)
        for _, row in sample.iterrows():
            # join safely (if less columns, avoid KeyError)
            pieces = []
            for c in cols[:6]:
                pieces.append(str(row.get(c, "")))
            pdf.multi_cell(0, 6, " | ".join(pieces))

    # Return buffer
    pdf_bytes = pdf.output(dest="S").encode("latin1")
    buf = BytesIO(pdf_bytes)
    buf.seek(0)
    return buf


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Homepage (upload form)."""
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Handle uploaded CSV & run anomaly detection."""
    if "file" not in request.files:
        flash("No file uploaded", "error")
        return redirect(url_for("index"))

    file = request.files["file"]
    if not file.filename or not allowed_file(file.filename):
        flash("Invalid file type. Please upload a CSV file.", "error")
        return redirect(url_for("index"))

    # Save uploaded file securely to uploads dir (unique temp file)
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".csv", dir=app.config["UPLOAD_FOLDER"])
    os.close(tmp_fd)
    file.save(tmp_path)
    file_size_mb = os.path.getsize(tmp_path) / (1024 * 1024)

    try:
        # Use in-memory detection for small files, chunked for large files
        if file_size_mb < 30:
            df = pd.read_csv(tmp_path, low_memory=False)
            df_all, anomalies = detect(df, contamination=0.05)
        else:
            anomalies = detect_large(tmp_path, contamination=0.05)
            df_all = None

        # Try to restore original column names only if counts match
        try:
            original_cols = pd.read_csv(tmp_path, nrows=0).columns.tolist()
            if len(anomalies.columns) == len(original_cols):
                anomalies.columns = original_cols
        except Exception:
            # If restoring fails, keep the anomalies DataFrame as-is
            pass

        total_rows = len(df_all) if df_all is not None else 0
        anomaly_count = len(anomalies)
        anomaly_percent = (anomaly_count / total_rows * 100) if total_rows > 0 else 0

        top_anomalies = anomalies.head(100).to_dict(orient="records")
        cols = anomalies.columns.tolist() if anomaly_count > 0 else []

        # Save CSV for download
        csv_bytes = anomalies.to_csv(index=False).encode("utf-8")
        csv_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", dir=app.config["UPLOAD_FOLDER"])
        csv_tmp.write(csv_bytes)
        csv_tmp.close()

        # Create PDF (saved as log_report.pdf)
        summary_text = (
            f"Detected anomalies: {anomaly_count}\n"
            f"Total rows: {total_rows or 'Large CSV'}"
        )
        pdf_buf = make_pdf_bytes(summary_text, anomalies)
        pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], "log_report.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_buf.read())

        # Render report page
        return render_template(
            "report.html",
            total_rows=total_rows,
            anomaly_count=anomaly_count,
            anomaly_percent=f"{anomaly_percent:.2f}%" if anomaly_percent else "N/A",
            top_anomalies=top_anomalies,
            cols=cols,
            csv_path=os.path.basename(csv_tmp.name),
            pdf_path="log_report.pdf",
            filename=file.filename,
            file_size_mb=f"{file_size_mb:.2f}",
        )

    finally:
        # remove uploaded file after processing (keep generated CSV/PDF)
        try:
            os.remove(tmp_path)
        except Exception:
            pass


@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    """Download generated CSV/PDF."""
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        flash("File not found", "error")
        return redirect(url_for("index"))
    # send as attachment
    return send_file(file_path, as_attachment=True)


# ---------------------------------------------------------
# RUN (dev or fallback)
# ---------------------------------------------------------
if __name__ == "__main__":
    # Try to enable ad-hoc HTTPS if cryptography is installed (avoids earlier error)
    ssl_available = True
    try:
        import cryptography  # presence indicates ad-hoc ssl support via werkzeug
    except Exception:
        ssl_available = False

    host = "0.0.0.0"
    port = int(os.getenv("PORT", 5000))

    if ssl_available:
        print("Starting Flask with ad-hoc HTTPS (cryptography available).")
        # Note: werkzeug will use cryptography to create ad-hoc certificate
        app.run(host=host, port=port, debug=False, ssl_context="adhoc")
    else:
        # If cryptography not installed, warn and run without adhoc SSL.
        print(
            "WARNING: 'cryptography' package not found. "
            "Ad-hoc HTTPS is unavailable. To enable HTTPS for local testing install 'cryptography', "
            "or deploy behind a reverse proxy (Nginx) with Let's Encrypt for production."
        )
        # In this fallback mode we disable SESSION_COOKIE_SECURE to avoid locking you out on HTTP
        app.config["SESSION_COOKIE_SECURE"] = False
        app.run(host=host, port=port, debug=False)
