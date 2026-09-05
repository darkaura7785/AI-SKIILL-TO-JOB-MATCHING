"""
Keyword Extractor Module — v2 (India-aware, timestamp-based experience)
=========================================================================
Extracts skills, work experience (professional + internship), and education
from resumes using lightweight NLP (regex + rule-based parsing).

Key improvements over v1:
• pdfplumber primary PDF reader (better layout) with PyPDF2 fallback
• Date-timestamp scanning to calculate experience from actual job history
• Internship experience tracked separately
• India-specific degree patterns (BTech, MTech, BCA, MCA, BCom, MCom, etc.)
• Skills taxonomy enriched from india_professional_skills_intelligence.csv
• All fields default to 0 / "Not Specified" — never None on resume upload
"""

import io
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# ── Optional heavy imports ──────────────────────────────────────────────────
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

try:
    import pandas as pd
except ImportError:
    pd = None


# ── Path helpers ────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INDIA_CSV = os.path.join(
    os.path.dirname(_BASE_DIR),          # project root
    "india_professional_skills_intelligence.csv"
)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SKILLS TAXONOMY  (core + enriched from India dataset)                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Core technology skills (unchanged from v1, extended)
TECH_SKILLS_TAXONOMY: set = {
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "c", "go",
    "golang", "rust", "ruby", "php", "swift", "kotlin", "r", "scala",
    "dart", "shell", "bash", "sql", "vba",
    # Frontend
    "react", "react.js", "next.js", "vue", "vue.js", "angular", "svelte",
    "html", "html5", "css", "css3", "tailwind", "tailwind css", "bootstrap",
    "sass", "scss", "redux", "graphql", "rest api", "restful apis", "webpack",
    "vite", "webgl", "ui design", "responsive design",
    # Backend
    "node.js", "express", "express.js", "django", "flask", "fastapi",
    "spring boot", "asp.net", "rails", "microservices", "grpc", "serverless",
    "system design", "rest apis",
    # Databases
    "postgresql", "postgres", "mysql", "mongodb", "redis", "elasticsearch",
    "sqlite", "dynamodb", "cassandra", "oracle", "mariadb", "firebase",
    "supabase", "prisma",
    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud", "docker",
    "kubernetes", "terraform", "ci/cd", "github actions", "jenkins",
    "gitlab ci", "ansible", "prometheus", "grafana", "linux", "nginx",
    "helm", "devops", "cloud computing", "sre", "cloud security",
    # Data Science & ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "pytorch", "tensorflow", "keras", "scikit-learn",
    "sklearn", "pandas", "numpy", "matplotlib", "seaborn", "data analysis",
    "data science", "tableau", "power bi", "spark", "hadoop", "airflow",
    "databricks", "llm", "llms", "transformers", "hugging face", "mlops",
    "prompt engineering", "statistics", "data visualization",
    "r", "excel", "statistical analysis",
    # Product & Agile
    "agile", "scrum", "kanban", "product management", "jira",
    "figma", "user research", "wireframing", "prototyping", "ux research",
    "product strategy", "a/b testing", "roadmapping", "stakeholder management",
    # Security
    "cybersecurity", "network security", "penetration testing", "siem",
    "incident response", "vulnerability assessment", "cryptography", "owasp",
    "soc 2", "compliance", "ethical hacking", "iso 27001", "risk assessment",
    # Finance & Accounting (India-relevant)
    "tally", "sap", "gst", "taxation", "auditing", "financial modeling",
    "financial analysis", "accounting", "ifrs", "gaap",
    # Digital Marketing (India-relevant)
    "seo", "sem", "google analytics", "social media marketing",
    "content marketing", "email marketing", "performance marketing",
    "content writing", "copywriting", "seo writing", "content strategy",
    # HR
    "talent acquisition", "hris", "performance management",
    "employee engagement", "labour law compliance", "payroll",
    # Sales & BD
    "salesforce", "crm", "b2b sales", "lead generation", "account management",
    "negotiation",
    # Core Engineering
    "autocad", "solidworks", "mechanical design", "quality control",
    "project management", "six sigma", "supply chain management",
    "logistics", "vendor management", "process improvement",
    # Soft skills / Tools
    "git", "github",
}

# India domain skills pulled from the CSV's top_skills column (pre-compiled set)
INDIA_DOMAIN_SKILLS: set = {
    # Software Engineering
    "system design", "rest apis", "spring boot", "microservices", "java",
    "node.js", "react", "sql", "git", "python", "javascript",
    # AI/ML
    "pytorch", "tensorflow", "nlp", "llms", "mlops", "deep learning",
    "computer vision", "prompt engineering",
    # Data
    "power bi", "tableau", "r", "statistics", "excel",
    "data visualization", "machine learning",
    # Cloud
    "aws", "gcp", "azure", "kubernetes", "terraform", "docker",
    "ci/cd", "linux",
    # Product
    "agile", "scrum", "jira", "product strategy", "user research",
    "roadmapping", "stakeholder management",
    # Design
    "figma", "wireframing", "prototyping", "design systems",
    # Marketing
    "seo", "sem", "google analytics", "social media marketing",
    "content marketing", "email marketing", "performance marketing",
    # Finance
    "tally", "sap", "gst", "auditing", "financial modeling", "taxation",
    # HR
    "talent acquisition", "hris", "performance management",
    "employee engagement", "labour law compliance", "payroll",
    # Sales
    "salesforce", "crm", "b2b sales", "lead generation",
    "account management", "negotiation",
    # Engineering
    "autocad", "solidworks", "mechanical design", "quality control",
    # Cybersecurity
    "siem", "ethical hacking", "cloud security", "iso 27001",
    "risk assessment", "penetration testing",
    # Content
    "content writing", "copywriting", "seo writing", "content strategy",
    "editing",
    # Operations
    "six sigma", "supply chain management", "logistics",
    "vendor management", "process improvement",
}

# Merge both sets
TECH_SKILLS_TAXONOMY = TECH_SKILLS_TAXONOMY | INDIA_DOMAIN_SKILLS

# ── Canonical display name map ───────────────────────────────────────────────
CANONICAL_SKILL_MAP: Dict[str, str] = {
    "react.js": "React", "react": "React",
    "next.js": "Next.js",
    "vue.js": "Vue", "vue": "Vue",
    "express.js": "Express", "express": "Express",
    "golang": "Go", "go": "Go",
    "node.js": "Node.js",
    "tailwind css": "Tailwind CSS", "tailwind": "Tailwind CSS",
    "sklearn": "Scikit-Learn", "scikit-learn": "Scikit-Learn",
    "amazon web services": "AWS", "aws": "AWS",
    "google cloud": "GCP", "gcp": "GCP",
    "natural language processing": "NLP", "nlp": "NLP",
    "html5": "HTML", "html": "HTML",
    "css3": "CSS", "css": "CSS",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "rest apis": "REST APIs", "rest api": "REST APIs",
    "restful apis": "REST APIs",
    "llms": "LLMs", "llm": "LLMs",
    "b2b sales": "B2B Sales",
    "seo": "SEO", "sem": "SEM",
    "hris": "HRIS", "crm": "CRM",
    "gst": "GST", "sap": "SAP",
    "ci/cd": "CI/CD",
    "iso 27001": "ISO 27001",
    "siem": "SIEM",
    "six sigma": "Six Sigma",
}


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  EDUCATION PATTERNS  (India-aware)                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Ordered from highest to lowest — first match wins
EDUCATION_PATTERNS: List[Tuple[str, str]] = [
    # Doctorate
    (r'\b(ph\.?d|doctor\s+of\s+philosophy|doctorate|d\.?phil)\b',
     "Doctorate (Ph.D.)"),
    # Masters — Indian + international
    (r'\b(m\.?tech|mtech|master\s+of\s+technology)\b', "Master's (M.Tech)"),
    (r'\b(m\.?e\.?\b|master\s+of\s+engineering)\b', "Master's (M.E.)"),
    (r'\b(m\.?c\.?a|master\s+of\s+computer\s+applications)\b', "Master's (MCA)"),
    (r'\b(m\.?sc|master\s+of\s+science)\b', "Master's (M.Sc)"),
    (r'\b(m\.?b\.?a|master\s+of\s+business)\b', "Master's (MBA)"),
    (r'\b(m\.?com|master\s+of\s+commerce)\b', "Master's (M.Com)"),
    (r'\b(m\.?a\.?\b|master\s+of\s+arts)\b', "Master's (M.A.)"),
    (r'\b(masters?|master\'?s|ms\b|m\.s\.?\b|msc\b|m\.tech)\b',
     "Master's Degree"),
    # Bachelors — Indian
    (r'\b(b\.?tech|btech|bachelor\s+of\s+technology)\b', "Bachelor's (B.Tech)"),
    (r'\b(b\.?e\.?\b|bachelor\s+of\s+engineering)\b', "Bachelor's (B.E.)"),
    (r'\b(b\.?c\.?a|bachelor\s+of\s+computer\s+applications)\b',
     "Bachelor's (BCA)"),
    (r'\b(b\.?sc|bachelor\s+of\s+science)\b', "Bachelor's (B.Sc)"),
    (r'\b(b\.?b\.?a|bachelor\s+of\s+business)\b', "Bachelor's (BBA)"),
    (r'\b(b\.?com|bachelor\s+of\s+commerce)\b', "Bachelor's (B.Com)"),
    (r'\b(b\.?a\.?\b|bachelor\s+of\s+arts)\b', "Bachelor's (B.A.)"),
    (r'\b(bachelors?|bachelor\'?s|b\.?s\.?\b|bsc\b|undergraduate)\b',
     "Bachelor's Degree"),
    # Diploma / Associate
    (r'\b(diploma\b|polytechnic)\b', "Diploma"),
    (r'\b(associate\'?s?|associate\s+degree)\b', "Associate's Degree"),
    # Bootcamp / Cert
    (r'\b(bootcamp|certificate|certification)\b',
     "Bootcamp / Professional Certification"),
]

# Degree field mapping for India disciplines
DEGREE_FIELD_PATTERNS: Dict[str, str] = {
    r'\b(computer\s*science|cs\b|cse|c\.?s\.?e|information\s*technology|i\.?t\.?\b)\b':
        "Computer Science / IT",
    r'\b(electronics|electrical|e\.?c\.?e|e\.?e\.?e|vlsi|embedded)\b':
        "Electronics / Electrical",
    r'\b(mechanical|mechatronics|production\s+engineering)\b':
        "Mechanical Engineering",
    r'\b(civil\s+engineering|civil)\b':
        "Civil Engineering",
    r'\b(commerce|finance|accounting|bcom|mcom|ca\b|cfa\b)\b':
        "Commerce / Finance",
    r'\b(business\s+administration|management|mba\b|bba\b)\b':
        "Business Administration",
    r'\b(arts|humanities|literature|history|political\s+science|sociology)\b':
        "Arts / Humanities",
    r'\b(life\s+sciences?|biology|biotechnology|biochemistry|pharmacy)\b':
        "Life Sciences",
    r'\b(data\s+science|data\s+analytics|statistics)\b':
        "Data Science / Analytics",
}


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  DATE / TIMESTAMP EXPERIENCE EXTRACTION                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

_MONTH_MAP: Dict[str, int] = {
    "jan": 1, "january": 1, "feb": 2, "february": 2,
    "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

# Patterns for date ranges like "Jun 2021 – Present", "2019 – 2022", "Jan'20 - Mar'22"
_DATE_RANGE_PATTERN = re.compile(
    r"""
    (?:
        # Month-Year (start)
        (?P<sm>[A-Za-z]{3,9})[\s'\-\.]*(?P<sy>\d{4})
        |
        # Year only (start)
        (?P<sy2>\d{4})
    )
    \s*[-–—/to]+\s*
    (?:
        # Present / Current / Ongoing
        (?P<end_present>present|current|ongoing|now|till\s+date|till\s+now)
        |
        # Month-Year (end)
        (?P<em>[A-Za-z]{3,9})[\s'\-\.]*(?P<ey>\d{4})
        |
        # Year only (end)
        (?P<ey2>\d{4})
    )
    """,
    re.VERBOSE | re.IGNORECASE
)

# Internship section markers
_INTERNSHIP_MARKERS = re.compile(
    r'\b(intern(?:ship)?|trainee|apprentice|industrial\s+training|summer\s+project|winter\s+project)\b',
    re.IGNORECASE
)


def _parse_month_year(month_str: Optional[str], year_str: Optional[str]) -> Optional[datetime]:
    """Converts a matched month (name or None) and year string to a datetime."""
    if not year_str:
        return None
    try:
        year = int(year_str.strip())
        if year < 1980 or year > datetime.now().year + 1:
            return None
        month = 1
        if month_str:
            month = _MONTH_MAP.get(month_str.strip().lower()[:3], 1)
        return datetime(year, month, 1)
    except (ValueError, AttributeError):
        return None


def _extract_date_ranges(text: str) -> List[Dict]:
    """
    Returns list of dicts:  {start: datetime, end: datetime, is_present: bool}
    by scanning all date-range patterns in the text.
    """
    ranges = []
    for m in _DATE_RANGE_PATTERN.finditer(text):
        g = m.groupdict()
        # Parse start
        start = _parse_month_year(g.get("sm"), g.get("sy") or g.get("sy2"))
        # Parse end
        is_present = bool(g.get("end_present"))
        end = datetime.now() if is_present else _parse_month_year(
            g.get("em"), g.get("ey") or g.get("ey2")
        )
        if start and end and end >= start:
            ranges.append({"start": start, "end": end, "is_present": is_present})
    return ranges


def _ranges_near_internship(text: str) -> List[Dict]:
    """
    Heuristic: date ranges that appear within 300 characters of an
    internship marker are treated as internship periods.
    """
    internship_positions = [m.start() for m in _INTERNSHIP_MARKERS.finditer(text)]

    all_ranges = []
    for m in _DATE_RANGE_PATTERN.finditer(text):
        g = m.groupdict()
        start = _parse_month_year(g.get("sm"), g.get("sy") or g.get("sy2"))
        is_present = bool(g.get("end_present"))
        end = datetime.now() if is_present else _parse_month_year(
            g.get("em"), g.get("ey") or g.get("ey2")
        )
        if start and end and end >= start:
            # Check proximity to any internship marker
            is_internship = any(
                abs(m.start() - pos) <= 400 for pos in internship_positions
            )
            all_ranges.append({
                "start": start, "end": end,
                "is_present": is_present,
                "is_internship": is_internship
            })
    return all_ranges


def _calculate_experience_from_ranges(
    ranges: List[Dict]
) -> Tuple[float, float]:
    """
    Merges overlapping date ranges and returns (professional_years, internship_years).
    Durations are rounded to 1 decimal place.
    """
    professional = [r for r in ranges if not r.get("is_internship")]
    internships  = [r for r in ranges if r.get("is_internship")]

    def total_months(range_list: List[Dict]) -> float:
        """Merge overlapping intervals and sum months."""
        if not range_list:
            return 0.0
        sorted_r = sorted(range_list, key=lambda x: x["start"])
        merged = [sorted_r[0].copy()]
        for r in sorted_r[1:]:
            if r["start"] <= merged[-1]["end"]:
                merged[-1]["end"] = max(merged[-1]["end"], r["end"])
            else:
                merged.append(r.copy())
        months = sum(
            (r["end"].year - r["start"].year) * 12
            + (r["end"].month - r["start"].month)
            for r in merged
        )
        return round(max(0.0, months / 12.0), 1)

    return total_months(professional), total_months(internships)


# ── Fallback: text-regex experience extractor (if no date ranges found) ─────
def _extract_experience_years_from_text(text: str) -> Optional[float]:
    """
    Extracts a stated experience claim like '5+ years of experience' as a float.
    Used when no date-stamp ranges are found.
    """
    patterns = [
        r'(\d{1,2}(?:\.\d)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s*'
        r'(?:experience|work\s+experience|professional\s+experience|industry\s+experience)',
        r'(?:experience|worked\s+for)\s*(?:of)?\s*:?\s*(\d{1,2}(?:\.\d)?)\+?\s*(?:years?|yrs?)',
        r'(\d{1,2}(?:\.\d)?)\s*\+\s*(?:years?|yrs?)',
        r'(?:total|overall)\s+experience\s*:?\s*(\d{1,2}(?:\.\d)?)'
    ]
    found = []
    for pattern in patterns:
        for match in re.findall(pattern, text.lower()):
            try:
                yr = float(match)
                if 0 <= yr <= 40:
                    found.append(yr)
            except ValueError:
                pass
    return max(found) if found else None


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  EDUCATION EXTRACTION                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def extract_education_level(text: str) -> str:
    """
    Identifies the highest level of education using India-aware patterns.
    Returns the most specific matched label (ordered highest → lowest).
    """
    text_check = text.lower()
    for pattern, label in EDUCATION_PATTERNS:
        if re.search(pattern, text_check):
            return label
    return "Not Specified"


def extract_degree_field(text: str) -> str:
    """Best-effort extraction of the candidate's degree specialisation."""
    text_check = text.lower()
    for pattern, field in DEGREE_FIELD_PATTERNS.items():
        if re.search(pattern, text_check, re.IGNORECASE):
            return field
    return ""


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SKILLS EXTRACTION                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def extract_skills_from_text(text: str) -> List[str]:
    """
    Scans input text for known skills using boundary-aware regex.
    Returns deduplicated, sorted canonical skill names.
    """
    found: set = set()
    # Pad text to ease boundary matching at start/end
    text_lower = f" {text.lower()} "

    # Sort by length desc so longer phrases are matched before substrings
    sorted_skills = sorted(TECH_SKILLS_TAXONOMY, key=len, reverse=True)
    multi_word = [s for s in sorted_skills if " " in s or "." in s or "/" in s or "-" in s]
    single_word = [s for s in sorted_skills if s not in multi_word]

    for skill in multi_word:
        escaped = re.escape(skill)
        if re.search(rf'(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])', text_lower):
            found.add(CANONICAL_SKILL_MAP.get(skill, skill.title()))

    for skill in single_word:
        escaped = re.escape(skill)
        if re.search(rf'\b{escaped}\b', text_lower):
            found.add(CANONICAL_SKILL_MAP.get(skill, skill.title()))

    return sorted(found)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FILE TEXT EXTRACTION                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def extract_text_from_file(file_obj, filename: str) -> str:
    """
    Extracts raw text from PDF, DOCX, TXT, or CSV upload.
    PDF: tries pdfplumber first (better layout), falls back to PyPDF2.
    All errors return a non-empty string describing the problem.
    """
    ext = filename.lower()
    text = ""

    try:
        if ext.endswith(".pdf"):
            text = _extract_pdf_text(file_obj)

        elif ext.endswith(".docx"):
            if docx is None:
                return "python-docx not installed — cannot parse DOCX file."
            doc = docx.Document(file_obj)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())

        elif ext.endswith(".csv"):
            if pd is not None:
                df = pd.read_csv(file_obj)
                text = df.to_string()
            else:
                raw = file_obj.read() if hasattr(file_obj, "read") else file_obj
                text = raw.decode("utf-8", errors="ignore")

        else:  # .txt and fallback
            raw = file_obj.read() if hasattr(file_obj, "read") else file_obj
            text = raw if isinstance(raw, str) else raw.decode("utf-8", errors="ignore")

    except Exception as exc:
        return f"Error parsing {filename}: {exc}"

    return text


def _extract_pdf_text(file_obj) -> str:
    """
    Attempts pdfplumber (preserves columns/layout better than PyPDF2).
    Falls back to PyPDF2 if pdfplumber is absent or fails.
    """
    # Make the stream seekable for two-pass attempts
    raw_bytes = file_obj.read() if hasattr(file_obj, "read") else file_obj
    if isinstance(raw_bytes, str):
        return raw_bytes  # Already plain text, unusual edge case

    pages_text: List[str] = []

    # ── Pass 1: pdfplumber ──────────────────────────────────────────────────
    if pdfplumber is not None:
        try:
            with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text(x_tolerance=2, y_tolerance=3)
                    if extracted:
                        pages_text.append(extracted)
            if pages_text:
                return "\n".join(pages_text)
        except Exception:
            pages_text = []  # Fall through to PyPDF2

    # ── Pass 2: PyPDF2 ─────────────────────────────────────────────────────
    if PyPDF2 is not None:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pages_text.append(extracted)
            if pages_text:
                return "\n".join(pages_text)
        except Exception as exc:
            return f"PDF extraction failed: {exc}"

    return "No PDF library available (install pdfplumber or PyPDF2)."


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  MAIN PARSE ENTRY POINT                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

def parse_resume(file_or_text, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Parses a resume and returns a complete profile dict.  ALL numeric fields
    default to 0 (never None); all string fields default to "Not Specified".

    Returns
    -------
    {
        "skills"             : List[str]   — canonical skill names
        "experience_years"   : float       — professional years (0 if unknown)
        "internship_years"   : float       — internship years (0 if none)
        "education"          : str         — highest degree label
        "degree_field"       : str         — specialisation / discipline
        "raw_text_preview"   : str
        "word_count"         : int
        "raw_text"           : str
    }
    """
    # ── 1. Obtain raw text ──────────────────────────────────────────────────
    if filename and hasattr(file_or_text, "read"):
        raw_text = extract_text_from_file(file_or_text, filename)
    else:
        raw_text = str(file_or_text)

    # ── 2. Skills ───────────────────────────────────────────────────────────
    skills = extract_skills_from_text(raw_text)

    # ── 3. Experience (timestamp-first, text-regex fallback) ─────────────────
    date_ranges = _ranges_near_internship(raw_text)
    professional_yrs: float = 0.0
    internship_yrs: float = 0.0

    if date_ranges:
        professional_yrs, internship_yrs = _calculate_experience_from_ranges(date_ranges)

    # If timestamp parsing gave 0 professional years, try text-stated claim
    if professional_yrs == 0.0:
        stated = _extract_experience_years_from_text(raw_text)
        if stated is not None:
            professional_yrs = float(stated)

    # ── 4. Education ─────────────────────────────────────────────────────────
    education = extract_education_level(raw_text)
    degree_field = extract_degree_field(raw_text)

    # ── 5. Return complete profile ────────────────────────────────────────────
    words = raw_text.split()
    return {
        "skills": skills,
        "experience_years": professional_yrs,        # 0.0 default, never None
        "internship_years": internship_yrs,          # separate internship count
        "education": education,
        "degree_field": degree_field,
        "raw_text_preview": raw_text[:300].strip() + ("..." if len(raw_text) > 300 else ""),
        "word_count": len(words),
        "raw_text": raw_text
    }
