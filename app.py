import os
import re
import sqlite3
from functools import wraps
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "careerbridge.db"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                education TEXT NOT NULL,
                career_interest TEXT NOT NULL,
                skills TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                job_title TEXT NOT NULL,
                company TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Saved',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, job_id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)


JOBS = [
    {
        "id": 1, "title": "Junior Python Developer", "company": "Fresher opportunity search",
        "category": "IT", "education": "BCA, B.Sc, B.Tech or relevant skills",
        "skills": ["Python", "SQL", "Problem Solving"],
        "url": "https://www.linkedin.com/jobs/search/?keywords=junior%20python%20developer%20fresher"
    },
    {
        "id": 2, "title": "Web Developer Intern", "company": "Internship search",
        "category": "IT", "education": "Any degree with web-development skills",
        "skills": ["HTML", "CSS", "JavaScript"],
        "url": "https://internshala.com/internships/"
    },
    {
        "id": 3, "title": "Data Analyst Trainee", "company": "Fresher opportunity search",
        "category": "Data Analytics", "education": "Any degree; analytical skills helpful",
        "skills": ["Excel", "SQL", "Power BI"],
        "url": "https://www.naukri.com/data-analyst-fresher-jobs"
    },
    {
        "id": 4, "title": "Accounts Assistant", "company": "Fresher opportunity search",
        "category": "Accounts", "education": "B.Com or relevant commerce/accounting background",
        "skills": ["Excel", "Accounting", "Tally"],
        "url": "https://www.naukri.com/accounts-assistant-jobs"
    },
    {
        "id": 5, "title": "MIS Executive Trainee", "company": "Fresher opportunity search",
        "category": "Office", "education": "Any degree with Excel/reporting skills",
        "skills": ["Excel", "Reports", "Communication"],
        "url": "https://www.linkedin.com/jobs/search/?keywords=MIS%20executive%20fresher"
    },
    {
        "id": 6, "title": "Customer Support Associate", "company": "Fresher opportunity search",
        "category": "Customer Support", "education": "Any degree; communication skills helpful",
        "skills": ["Communication", "Email", "Problem Solving"],
        "url": "https://www.naukri.com/customer-support-fresher-jobs"
    },
    {
        "id": 7, "title": "HR Assistant", "company": "Fresher opportunity search",
        "category": "Business", "education": "Any degree; HR/business background helpful",
        "skills": ["Communication", "Excel", "Organization"],
        "url": "https://www.linkedin.com/jobs/search/?keywords=HR%20assistant%20fresher"
    },
    {
        "id": 8, "title": "Digital Marketing Intern", "company": "Internship search",
        "category": "Marketing", "education": "Any degree with interest in digital media",
        "skills": ["Content Writing", "Social Media", "Analytics"],
        "url": "https://internshala.com/internships/"
    }
]

CAREER_SKILLS = {
    "IT": ["Python or Java", "SQL", "Git and GitHub", "Problem solving", "One project"],
    "Data Analytics": ["Excel", "SQL", "Power BI", "Basic statistics", "Portfolio dashboard"],
    "Accounts": ["Excel", "Accounting basics", "Tally or equivalent software", "GST basics", "Accuracy"],
    "Office": ["Excel", "Email writing", "Word processing", "Reports", "Communication"],
    "Customer Support": ["Communication", "Email etiquette", "Problem solving", "Typing", "Customer service"],
    "Business": ["Communication", "Excel", "Organization", "Recruitment basics", "Professional email"],
    "Marketing": ["Content writing", "Social media", "Basic design", "Analytics", "Campaign planning"],
    "Any Suitable Career": ["Communication", "Excel", "Digital skills", "Resume writing", "Interview practice"]
}

ALL_SKILLS = [
    "Python", "Java", "SQL", "HTML", "CSS", "JavaScript", "React",
    "Excel", "Power BI", "Data Analysis", "Machine Learning", "Tally",
    "Accounting", "Communication", "Git", "Content Writing", "Social Media",
    "Email", "Problem Solving", "Reports", "Organization"
]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    if "user_id" not in session:
        return None
    with get_db() as conn:
        return conn.execute(
            "SELECT id, full_name, email, education, career_interest, skills FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        education = request.form.get("education", "").strip()
        career_interest = request.form.get("career_interest", "").strip()

        if not all([full_name, email, password, education, career_interest]):
            flash("Please complete every field.")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect(url_for("register"))
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            flash("Please enter a valid email address.")
            return redirect(url_for("register"))

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (full_name, email, password, education, career_interest) VALUES (?, ?, ?, ?, ?)",
                    (full_name, email, generate_password_hash(password), education, career_interest)
                )
            flash("Account created successfully. Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("This email is already registered. Please log in instead.")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            flash("Welcome back!")
            return redirect(url_for("dashboard"))
        flash("Email or password is incorrect.")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.")
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    user_skills = [s.strip().lower() for s in (user["skills"] or "").split(",") if s.strip()]
    target_skills = CAREER_SKILLS.get(user["career_interest"], CAREER_SKILLS["Any Suitable Career"])
    missing = [skill for skill in target_skills if skill.lower() not in user_skills]
    with get_db() as conn:
        applications = conn.execute(
            "SELECT * FROM applications WHERE user_id = ? ORDER BY created_at DESC",
            (session["user_id"],)
        ).fetchall()
    recommended_jobs = [job for job in JOBS if user["career_interest"] in ("Any Suitable Career", job["category"])]
    if not recommended_jobs:
        recommended_jobs = JOBS[:4]
    return render_template(
        "dashboard.html", user=user, missing=missing,
        jobs=recommended_jobs[:4], applications=applications
    )


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        skills = request.form.get("skills", "").strip()
        with get_db() as conn:
            conn.execute("UPDATE users SET skills = ? WHERE id = ?", (skills, session["user_id"]))
        flash("Your skills have been updated.")
        return redirect(url_for("profile"))
    return render_template("profile.html", user=current_user(), all_skills=ALL_SKILLS)


@app.route("/jobs")
def jobs():
    category = request.args.get("category", "").strip()
    filtered_jobs = [job for job in JOBS if not category or job["category"].lower() == category.lower()]
    categories = sorted({job["category"] for job in JOBS})
    return render_template("jobs.html", jobs=filtered_jobs, categories=categories, selected_category=category)


@app.route("/apply/<int:job_id>", methods=["POST"])
@login_required
def apply(job_id):
    job = next((item for item in JOBS if item["id"] == job_id), None)
    if not job:
        flash("Job not found.")
        return redirect(url_for("jobs"))
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO applications (user_id, job_id, job_title, company) VALUES (?, ?, ?, ?)",
                (session["user_id"], job["id"], job["title"], job["company"])
            )
        flash("Job saved to your application tracker.")
    except sqlite3.IntegrityError:
        flash("You have already saved this job.")
    return redirect(url_for("dashboard"))


@app.route("/resume", methods=["GET", "POST"])
@login_required
def resume():
    found_skills = []
    text_preview = ""
    if request.method == "POST":
        file = request.files.get("resume_file")
        if not file or not file.filename:
            flash("Choose a .txt resume file first.")
            return redirect(url_for("resume"))
        if not file.filename.lower().endswith(".txt"):
            flash("For this starter version, upload a plain .txt resume file.")
            return redirect(url_for("resume"))
        content = file.read(500001)
        if len(content) > 500000:
            flash("File is too large. Maximum size is 500 KB.")
            return redirect(url_for("resume"))
        text_preview = content.decode("utf-8", errors="ignore")
        searchable = text_preview.lower()
        found_skills = [skill for skill in ALL_SKILLS if skill.lower() in searchable]
        flash("Resume keyword scan completed. This is a basic keyword checker, not a full AI evaluation.")
    return render_template("resume.html", found_skills=found_skills, text_preview=text_preview)


@app.route("/career")
@login_required
def career():
    user = current_user()
    target = user["career_interest"]
    roadmap = CAREER_SKILLS.get(target, CAREER_SKILLS["Any Suitable Career"])
    return render_template("career.html", user=user, roadmap=roadmap, careers=CAREER_SKILLS)


@app.route("/update-status/<int:application_id>", methods=["POST"])
@login_required
def update_status(application_id):
    status = request.form.get("status", "Saved")
    allowed = {"Saved", "Applied", "Interview", "Rejected", "Offer"}
    if status not in allowed:
        flash("Invalid application status.")
        return redirect(url_for("dashboard"))
    with get_db() as conn:
        conn.execute(
            "UPDATE applications SET status = ? WHERE id = ? AND user_id = ?",
            (status, application_id, session["user_id"])
        )
    flash("Application status updated.")
    return redirect(url_for("dashboard"))


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


init_db()

if __name__ == "__main__":
    app.run(debug=True)
