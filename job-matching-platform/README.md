# AI-Powered Skill-to-Job Matching Platform

A production-ready, minimalistic career intelligence and job recommendation platform built with **Streamlit**, lightweight **NLP keyword parsing**, and multi-factor **compatibility ranking**.

Mindful of GitHub repository constraints and Streamlit Cloud free-tier memory ceilings (< 1GB RAM), this application avoids multi-gigabyte models while delivering sub-second resume parsing, actionable skill-gap analysis, and direct live job recommendations.

---

## 🎯 Workflow & System Architecture

The pipeline processes user profiles through four consecutive stages:

```
[Candidate Input]
  ├── Option A: Manual Entry (Skills, Experience Years, Education)
  └── Option B: Resume Upload (.pdf, .docx, .txt, .csv)
         │
         ▼
[Keyword Extraction Engine]
  ├── Document decoding (PyPDF2, python-docx, pandas)
  ├── 100+ Node Tech Skills Taxonomy Matching (Regex boundary checks)
  ├── Experience parsing (Regex duration extraction)
  └── Education level detection (Degree keyword classification)
         │
         ▼
[Role Compatibility Matcher]
  ├── Evaluates 11+ predefined market role benchmarks
  ├── Multi-factor weighted score calculation:
  │     • 65% Required Skills Match
  │     • 20% Preferred Skills Match
  │     • 10% Experience Alignment
  │     •  5% Education Degree Factor
  └── Sorts and outputs Top 4 Compatible Roles + Skill Gap Analysis
         │
         ▼
[Job Recommendation Layer]
  ├── Filters curated openings from sample dataset (`sample_jobs.csv`)
  ├── Generates direct outbound application links
  └── Builds live search queries for LinkedIn & Indeed
```

---

## 📂 Project Folder Structure

```
job-matching-platform/
│── app.py                    # Main Streamlit web application & interface
│── requirements.txt          # Lightweight pip package dependencies
│── README.md                 # Complete documentation & deployment guide
│── data/
│   └── sample_jobs.csv       # Curated market dataset of tech job openings
│── models/
│   └── keyword_extractor.py  # Resume text extraction, regex & NLP keyword parsing
│── utils/
│   ├── matcher.py            # Role benchmark definitions & compatibility scoring
│   └── job_fetcher.py        # Dataset querying & live job search link generator
│── assets/
│   └── style.css             # Minimalist typography, cards, and badge stylesheet
```

---

## 🚀 Quickstart (Local Machine)

### 1. Clone or Extract the Project
```bash
git clone https://github.com/your-username/job-matching-platform.git
cd job-matching-platform
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ☁️ Deploying to Streamlit Cloud

1. Push your repository to **GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: skill to job matching platform"
   git branch -M main
   git remote add origin https://github.com/your-username/job-matching-platform.git
   git push -u origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"**, select your repository, set the Main file path to `app.py`, and click **"Deploy"**.
4. The application boots in under 60 seconds because dependencies in `requirements.txt` are ultra-lightweight and well within Streamlit Cloud resource quotas.

---

## 🔍 Step-by-Step Functioning

1. **User Profile Ingestion**:
   - **Upload Mode**: Supports binary document streams. `PyPDF2` scans all pages for text blocks; `python-docx` iterates through XML document paragraphs; `pandas` handles tabular CV logs; plain UTF-8 streams parse text files.
   - **Manual Mode**: Structured multiselect selector for users with specific skills, alongside years of experience and highest degree attained.

2. **Keyword Extraction**:
   - Compares raw text against a standardized tech taxonomy (languages, frontend, backend, databases, cloud, DevOps, AI/ML, and design).
   - Normalizes synonyms (e.g. `React.js` ➔ `React`, `AWS` ➔ `AWS`, `Postgres` ➔ `PostgreSQL`).
   - Identifies candidate's years of experience and highest degree attained.

3. **Role Compatibility Matcher**:
   - Ranks the profile against standard profiles (e.g., *Full Stack Engineer, Machine Learning Engineer, DevOps Specialist, Frontend Developer*).
   - Flags **Matched Skills** (affirming competencies) and **Missing Skills** (constructive learning roadmap).

4. **Job Fetching & Outbound Routing**:
   - Matches vacancies from `sample_jobs.csv` with filtering by job arrangement (Remote, Hybrid, On-site).
   - Outbound links route to real companies (Stripe, Airbnb, Cloudflare, Spotify, Anthropic, Figma) and dynamically generated search URLs for LinkedIn and Indeed.
