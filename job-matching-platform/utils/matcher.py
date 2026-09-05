"""
Role Matcher & Compatibility Scoring — v2 (India-aware)
=========================================================
Scores a candidate profile against a comprehensive set of job role benchmarks
that reflect the full Indian professional landscape
(Software, Data/AI, Cloud, Cybersecurity, Design, Product, Marketing,
Finance, HR, Sales & BD, Core Engineering, Content, Operations).

Scoring weights:
  65%  Required skills overlap
  20%  Preferred skills overlap
  10%  Experience alignment  (professional years + partial credit for internship)
   5%  Education alignment   (India-aware degree hierarchy)
"""

from typing import List, Dict, Any

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ROLE PROFILES  (expanded for India market)                             ║
# ╚══════════════════════════════════════════════════════════════════════════╝

ROLE_PROFILES: List[Dict[str, Any]] = [

    # ── Software Engineering ────────────────────────────────────────────────
    {
        "role_id": "junior_software_engineer",
        "title": "Junior Software Engineer",
        "category": "Software Engineering",
        "description": "Develops and maintains software features under guidance, writes unit tests, and collaborates in agile sprints.",
        "required_skills": ["Python", "JavaScript", "Git", "SQL", "HTML", "CSS"],
        "preferred_skills": ["React", "Node.js", "REST APIs", "System Design", "Java"],
        "min_experience_years": 0,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "high",
        "typical_salary_lpa": "4–8",
    },
    {
        "role_id": "software_engineer",
        "title": "Software Engineer",
        "category": "Software Engineering",
        "description": "Designs and ships production features, participates in code reviews, and ensures system reliability.",
        "required_skills": ["Python", "JavaScript", "Git", "SQL", "REST APIs", "System Design"],
        "preferred_skills": ["React", "Node.js", "Java", "Spring Boot", "Microservices", "Docker"],
        "min_experience_years": 2,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "high",
        "typical_salary_lpa": "8–18",
    },
    {
        "role_id": "senior_software_engineer",
        "title": "Senior Software Engineer",
        "category": "Software Engineering",
        "description": "Architects complex features, mentors juniors, and drives technical decisions for high-scale systems.",
        "required_skills": ["Python", "Java", "System Design", "Microservices", "SQL", "Git", "REST APIs"],
        "preferred_skills": ["Spring Boot", "Docker", "Kubernetes", "AWS", "Node.js", "React"],
        "min_experience_years": 5,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "high",
        "typical_salary_lpa": "20–45",
    },
    {
        "role_id": "fullstack",
        "title": "Full Stack Engineer",
        "category": "Software Engineering",
        "description": "Builds end-to-end web applications — UI components, REST APIs, databases, and cloud deployments.",
        "required_skills": ["React", "JavaScript", "TypeScript", "Node.js", "Python", "SQL", "Git"],
        "preferred_skills": ["Docker", "AWS", "PostgreSQL", "Tailwind CSS", "Next.js", "GraphQL", "CI/CD"],
        "min_experience_years": 2,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "high",
        "typical_salary_lpa": "10–30",
    },
    {
        "role_id": "frontend",
        "title": "Frontend Developer",
        "category": "Software Engineering",
        "description": "Crafts responsive, performant user interfaces, component libraries, and browser client logic.",
        "required_skills": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Git"],
        "preferred_skills": ["Next.js", "Redux", "GraphQL", "Tailwind CSS", "Vite", "Responsive Design", "Vue"],
        "min_experience_years": 1,
        "ideal_education": "Bachelor's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "6–20",
    },
    {
        "role_id": "backend",
        "title": "Backend Systems Engineer",
        "category": "Software Engineering",
        "description": "Architects resilient distributed backends, REST/gRPC microservices, data storage layers, and caching.",
        "required_skills": ["Python", "Java", "Node.js", "SQL", "REST APIs", "Microservices", "Git"],
        "preferred_skills": ["Spring Boot", "Docker", "Kubernetes", "Redis", "AWS", "FastAPI", "Django"],
        "min_experience_years": 2,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "high",
        "typical_salary_lpa": "10–35",
    },

    # ── Cloud & DevOps ──────────────────────────────────────────────────────
    {
        "role_id": "devops",
        "title": "DevOps & Cloud Engineer",
        "category": "Cloud & DevOps",
        "description": "Automates deployment pipelines, provisions infrastructure as code, and maintains high-availability clusters.",
        "required_skills": ["Docker", "Kubernetes", "AWS", "Linux", "CI/CD", "Terraform", "Git"],
        "preferred_skills": ["GCP", "Azure", "Ansible", "Prometheus", "Grafana", "Python", "Bash", "SRE"],
        "min_experience_years": 3,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "high",
        "typical_salary_lpa": "15–40",
    },
    {
        "role_id": "cloud_architect",
        "title": "Cloud Infrastructure Architect",
        "category": "Cloud & DevOps",
        "description": "Designs enterprise-grade multi-cloud topology, security guardrails, disaster recovery, and networking.",
        "required_skills": ["AWS", "Azure", "Terraform", "Kubernetes", "Linux", "Cloud Computing"],
        "preferred_skills": ["GCP", "Docker", "CI/CD", "Network Security", "Ansible", "Python"],
        "min_experience_years": 6,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "medium",
        "typical_salary_lpa": "30–80",
    },

    # ── Data & AI ────────────────────────────────────────────────────────────
    {
        "role_id": "data_analyst",
        "title": "Data Analyst",
        "category": "Data & AI",
        "description": "Synthesises KPIs using SQL, interactive dashboards, and exploratory data analysis to drive decisions.",
        "required_skills": ["SQL", "Python", "Excel", "Power BI", "Data Visualization", "Statistics"],
        "preferred_skills": ["Tableau", "R", "Machine Learning", "A/B Testing", "Data Science"],
        "min_experience_years": 1,
        "ideal_education": "Bachelor's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "5–18",
    },
    {
        "role_id": "data_scientist",
        "title": "Data Scientist",
        "category": "Data & AI",
        "description": "Extracts predictive insights from structured/unstructured datasets via statistical modelling and ML.",
        "required_skills": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-Learn", "Statistics"],
        "preferred_skills": ["PyTorch", "TensorFlow", "Tableau", "Deep Learning", "NLP", "A/B Testing", "R"],
        "min_experience_years": 2,
        "ideal_education": "Master's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "10–30",
    },
    {
        "role_id": "ml_engineer",
        "title": "Machine Learning Engineer",
        "category": "Data & AI",
        "description": "Deploys, optimises, and monitors deep learning architectures and generative models at production scale.",
        "required_skills": ["Python", "PyTorch", "TensorFlow", "Deep Learning", "Machine Learning", "MLOps"],
        "preferred_skills": ["NLP", "LLMs", "Transformers", "Docker", "Kubernetes", "AWS", "Computer Vision", "Prompt Engineering"],
        "min_experience_years": 3,
        "ideal_education": "Master's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "15–50",
    },
    {
        "role_id": "ai_research_scientist",
        "title": "AI Research Scientist",
        "category": "Data & AI",
        "description": "Publishes fundamental research and develops multimodal generative intelligence models.",
        "required_skills": ["Python", "PyTorch", "Deep Learning", "NLP", "Machine Learning", "Statistics"],
        "preferred_skills": ["TensorFlow", "Computer Vision", "LLMs", "Transformers", "Research", "Mathematics"],
        "min_experience_years": 4,
        "ideal_education": "Doctorate (Ph.D.)",
        "india_relevance": "medium",
        "typical_salary_lpa": "20–60",
    },

    # ── Cybersecurity ────────────────────────────────────────────────────────
    {
        "role_id": "cybersecurity_analyst",
        "title": "Cybersecurity Analyst",
        "category": "Cybersecurity",
        "description": "Defends infrastructure against cyber attacks, conducts penetration testing, and handles incident response.",
        "required_skills": ["Network Security", "Linux", "SIEM", "Incident Response", "Vulnerability Assessment"],
        "preferred_skills": ["Python", "Ethical Hacking", "ISO 27001", "Penetration Testing", "Cloud Security", "Risk Assessment"],
        "min_experience_years": 2,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "high",
        "typical_salary_lpa": "6–20",
    },

    # ── Product & Design ─────────────────────────────────────────────────────
    {
        "role_id": "product_manager",
        "title": "Product Manager",
        "category": "Product",
        "description": "Aligns product strategy, user discovery, stakeholder requirements, sprint execution, and KPIs.",
        "required_skills": ["Product Management", "Agile", "Scrum", "User Research", "Product Strategy", "JIRA"],
        "preferred_skills": ["Stakeholder Management", "Roadmapping", "SQL", "A/B Testing", "Figma", "Data Analysis"],
        "min_experience_years": 3,
        "ideal_education": "Bachelor's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "12–40",
    },
    {
        "role_id": "junior_product_manager",
        "title": "Junior / Associate Product Manager",
        "category": "Product",
        "description": "Supports product discovery, writes user stories, and tracks sprint metrics under senior PM guidance.",
        "required_skills": ["Agile", "Scrum", "JIRA", "User Research", "Product Strategy"],
        "preferred_skills": ["Stakeholder Management", "Roadmapping", "Data Analysis", "Figma"],
        "min_experience_years": 0,
        "ideal_education": "Bachelor's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "6–14",
    },
    {
        "role_id": "ui_ux_designer",
        "title": "UI/UX Product Designer",
        "category": "Design",
        "description": "Designs intuitive user journeys, high-fidelity prototypes, design tokens, and user research protocols.",
        "required_skills": ["Figma", "UI Design", "Wireframing", "Prototyping", "Responsive Design"],
        "preferred_skills": ["UX Research", "Design Systems", "User Research", "HTML", "CSS", "Tailwind CSS"],
        "min_experience_years": 2,
        "ideal_education": "Bachelor's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "5–20",
    },

    # ── Digital Marketing ────────────────────────────────────────────────────
    {
        "role_id": "digital_marketer",
        "title": "Digital Marketing Specialist",
        "category": "Digital Marketing",
        "description": "Drives traffic and conversions through SEO, SEM, social media, and performance marketing campaigns.",
        "required_skills": ["SEO", "SEM", "Google Analytics", "Social Media Marketing", "Content Marketing", "Email Marketing"],
        "preferred_skills": ["Performance Marketing", "Content Strategy", "Data Analysis", "A/B Testing", "CRM"],
        "min_experience_years": 2,
        "ideal_education": "Bachelor's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "4–18",
    },

    # ── Content & Communication ──────────────────────────────────────────────
    {
        "role_id": "content_strategist",
        "title": "Content Strategist / Writer",
        "category": "Content & Communication",
        "description": "Plans, produces, and optimises written content across blogs, social media, and marketing materials.",
        "required_skills": ["Content Writing", "Content Strategy", "SEO Writing", "Editing", "Copywriting"],
        "preferred_skills": ["Social Media Marketing", "SEO", "Email Marketing", "Data Analysis"],
        "min_experience_years": 1,
        "ideal_education": "Bachelor's (B.A.)",
        "india_relevance": "high",
        "typical_salary_lpa": "4–15",
    },

    # ── Finance & Accounting ─────────────────────────────────────────────────
    {
        "role_id": "finance_analyst",
        "title": "Finance Analyst",
        "category": "Finance & Accounting",
        "description": "Handles financial reporting, GST compliance, auditing, and strategic financial analysis.",
        "required_skills": ["Excel", "Tally", "SAP", "GST", "Financial Modeling", "Taxation"],
        "preferred_skills": ["Auditing", "SQL", "Python", "Power BI", "IFRS", "Data Visualization"],
        "min_experience_years": 1,
        "ideal_education": "Bachelor's (B.Com)",
        "india_relevance": "high",
        "typical_salary_lpa": "4–20",
    },

    # ── Human Resources ──────────────────────────────────────────────────────
    {
        "role_id": "hr_executive",
        "title": "HR Executive",
        "category": "Human Resources",
        "description": "Manages talent acquisition, employee lifecycle, payroll, and HR compliance in Indian labour law context.",
        "required_skills": ["Talent Acquisition", "HRIS", "Employee Engagement", "Labour Law Compliance", "Payroll"],
        "preferred_skills": ["Performance Management", "Data Analysis", "Excel", "Stakeholder Management"],
        "min_experience_years": 1,
        "ideal_education": "Master's (MBA)",
        "india_relevance": "high",
        "typical_salary_lpa": "4–15",
    },

    # ── Sales & Business Development ─────────────────────────────────────────
    {
        "role_id": "business_development",
        "title": "Business Development Executive",
        "category": "Sales & Business Development",
        "description": "Generates leads, manages B2B sales pipelines, and builds long-term client relationships.",
        "required_skills": ["B2B Sales", "Lead Generation", "CRM", "Negotiation", "Account Management"],
        "preferred_skills": ["Salesforce", "Data Analysis", "Email Marketing", "Product Strategy"],
        "min_experience_years": 1,
        "ideal_education": "Bachelor's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "4–16",
    },

    # ── Core / Mechanical Engineering ────────────────────────────────────────
    {
        "role_id": "design_engineer",
        "title": "Design Engineer",
        "category": "Core Engineering",
        "description": "Creates mechanical designs and technical drawings; ensures quality control and manufacturing feasibility.",
        "required_skills": ["AutoCAD", "SolidWorks", "Mechanical Design", "Quality Control", "Project Management"],
        "preferred_skills": ["Six Sigma", "Supply Chain Management", "Vendor Management", "Process Improvement"],
        "min_experience_years": 1,
        "ideal_education": "Bachelor's (B.Tech)",
        "india_relevance": "high",
        "typical_salary_lpa": "4–18",
    },

    # ── Operations & Supply Chain ────────────────────────────────────────────
    {
        "role_id": "operations_executive",
        "title": "Operations Executive",
        "category": "Operations & Supply Chain",
        "description": "Streamlines supply chain, logistics, and vendor operations to improve efficiency and reduce costs.",
        "required_skills": ["Supply Chain Management", "Logistics", "Vendor Management", "Process Improvement"],
        "preferred_skills": ["Six Sigma", "Excel", "SAP", "Data Analysis", "Project Management"],
        "min_experience_years": 1,
        "ideal_education": "Bachelor's Degree",
        "india_relevance": "high",
        "typical_salary_lpa": "4–16",
    },
]


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  EDUCATION WEIGHT TABLE  (India-aware)                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

EDU_WEIGHTS: Dict[str, float] = {
    # Doctorate
    "Doctorate (Ph.D.)": 1.0,
    # Masters variety
    "Master's (M.Tech)": 0.97,
    "Master's (M.E.)": 0.97,
    "Master's (MCA)": 0.95,
    "Master's (MBA)": 0.95,
    "Master's (M.Sc)": 0.95,
    "Master's (M.Com)": 0.93,
    "Master's (M.A.)": 0.90,
    "Master's Degree": 0.95,
    # Bachelors variety
    "Bachelor's (B.Tech)": 0.92,
    "Bachelor's (B.E.)": 0.92,
    "Bachelor's (BCA)": 0.88,
    "Bachelor's (B.Sc)": 0.88,
    "Bachelor's (BBA)": 0.85,
    "Bachelor's (B.Com)": 0.85,
    "Bachelor's (B.A.)": 0.82,
    "Bachelor's Degree": 0.88,
    # Lower / non-degree
    "Diploma": 0.75,
    "Associate's Degree": 0.75,
    "Bootcamp / Professional Certification": 0.75,
    "Not Specified": 0.60,
}


def normalize_skill(skill: str) -> str:
    """Normalises a skill string for case-insensitive comparison."""
    return skill.strip().lower()


def compute_role_compatibility(
    user_skills: List[str],
    user_experience: float = 0.0,
    user_education: str = "Not Specified",
    internship_years: float = 0.0,
    role: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Computes a fine-grained compatibility score between candidate and a role.

    Weights
    -------
    65%  Required skills overlap
    20%  Preferred skills overlap
    10%  Experience alignment  (professional + 0.4× internship credit)
     5%  Education alignment

    Internship years count partially (40 %) toward the experience threshold.
    """
    if role is None:
        return {}

    user_norm   = {normalize_skill(s) for s in user_skills}
    req_norm    = {normalize_skill(s) for s in role["required_skills"]}
    pref_norm   = {normalize_skill(s) for s in role.get("preferred_skills", [])}

    # ── Skill overlaps ───────────────────────────────────────────────────────
    matched_req  = req_norm  & user_norm
    matched_pref = pref_norm & user_norm

    req_ratio  = len(matched_req)  / len(req_norm)  if req_norm  else 1.0
    pref_ratio = len(matched_pref) / len(pref_norm) if pref_norm else 0.5

    # ── Experience factor ────────────────────────────────────────────────────
    min_exp = role.get("min_experience_years", 0)
    # Give partial credit for internship (40 %)
    effective_exp = user_experience + internship_years * 0.4

    if min_exp == 0:
        exp_score = 1.0
    elif effective_exp >= min_exp:
        exp_score = 1.0
    elif effective_exp > 0:
        exp_score = max(0.4, effective_exp / min_exp)
    else:
        exp_score = 0.3

    # ── Education factor ─────────────────────────────────────────────────────
    edu_score = EDU_WEIGHTS.get(user_education, 0.60)

    # ── Composite score ──────────────────────────────────────────────────────
    raw = (req_ratio * 65.0) + (pref_ratio * 20.0) + (exp_score * 10.0) + (edu_score * 5.0)
    compatibility_score = round(min(99.0, max(12.0, raw)), 1)

    # ── Build display lists ───────────────────────────────────────────────────
    all_role_skills = role["required_skills"] + role.get("preferred_skills", [])
    matched_display: List[str] = []
    missing_display: List[str] = []

    for s in all_role_skills:
        if normalize_skill(s) in user_norm:
            if s not in matched_display:
                matched_display.append(s)
        elif s in role["required_skills"] and s not in missing_display:
            missing_display.append(s)

    return {
        "role_id": role["role_id"],
        "title": role["title"],
        "category": role["category"],
        "description": role["description"],
        "compatibility_score": compatibility_score,
        "matched_skills": matched_display,
        "missing_skills": missing_display[:5],
        "required_skills_count": len(role["required_skills"]),
        "matched_required_count": len(matched_req),
        "min_experience": min_exp,
        "typical_salary_lpa": role.get("typical_salary_lpa", "—"),
    }


def rank_top_roles(
    user_skills: List[str],
    user_experience: float = 0.0,
    user_education: str = "Not Specified",
    internship_years: float = 0.0,
    top_n: int = 4,
) -> List[Dict[str, Any]]:
    """
    Scores every role profile and returns the top_n best matches
    sorted descending by compatibility_score.
    """
    scored = [
        compute_role_compatibility(
            user_skills=user_skills,
            user_experience=user_experience,
            user_education=user_education,
            internship_years=internship_years,
            role=role,
        )
        for role in ROLE_PROFILES
    ]
    scored.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return scored[:top_n]
