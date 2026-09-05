"""
Skill-to-Job Matching Platform — v2
====================================
AI-Powered Career Recommendation Engine built with Streamlit.

Workflow:
1. Resume Upload  →  auto-extraction of skills, experience & education
2. Lightweight NLP (regex + India-aware taxonomy)
3. Role Compatibility Scoring (Top 4 Roles)
4. Job Openings Recommendations
"""

import os
import sys

import streamlit as st

# ── Ensure package-relative imports work ────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from models.keyword_extractor import (
    parse_resume,
    TECH_SKILLS_TAXONOMY,
    CANONICAL_SKILL_MAP,
)
from utils.matcher import rank_top_roles
from utils.job_fetcher import fetch_jobs_for_role, load_dataset_jobs

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Skill-to-Job Matcher",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
_CSS = os.path.join(CURRENT_DIR, "assets", "style.css")
if os.path.exists(_CSS):
    with open(_CSS) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 System Architecture")
    st.markdown("""
    **4-Step Pipeline:**
    1. **Input Ingestion** — PDF/DOCX/TXT/CSV resume parsing or structured manual entry.
    2. **Lightweight NLP** — Regex-bounded keyword scan across 150 + India-aware taxonomy nodes.
    3. **Compatibility Engine** — Multi-factor scoring (65 % required skills, 20 % preferred, 10 % experience, 5 % education).
    4. **Job Recommendation** — Role-aligned openings with direct apply links.
    """)
    st.markdown("---")
    st.markdown("### ⚙️ Deployment Specs")
    st.caption("• Framework: Streamlit Cloud ready\n• NLP: Zero multi-GB dependencies\n• Package Size: < 50 MB (GitHub safe)")
    st.markdown("---")
    _sample = load_dataset_jobs()
    st.metric("Curated Job Database", f"{len(_sample)} Openings")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-title">Skill-to-Job Matching Platform</div>
    <div class="app-subtitle">Map candidate competencies to market roles with lightweight NLP and real-time job alignment.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="workflow-bar">
    <div class="workflow-step active"><span class="workflow-step-num">1</span> Profile Input</div>
    <div class="workflow-step active"><span class="workflow-step-num">2</span> NLP Extraction</div>
    <div class="workflow-step active"><span class="workflow-step-num">3</span> Top 4 Role Ranking</div>
    <div class="workflow-step active"><span class="workflow-step-num">4</span> Job Openings</div>
</div>
""", unsafe_allow_html=True)

# ── Initialise session defaults ───────────────────────────────────────────────
_DEFAULTS = {
    "extracted_skills": [],
    "user_experience": 0.0,
    "internship_years": 0.0,
    "user_education": "Not Specified",
    "degree_field": "",
    "source_mode": "manual",
    "analyzed": False,
}
for k, v in _DEFAULTS.items():
    st.session_state.setdefault(k, v)

# ── Input Tabs ────────────────────────────────────────────────────────────────
tab_upload, tab_manual = st.tabs([
    "📄 Upload Resume / CV",
    "✍️  Manual Skill Entry",
])

# ════════════════════════════════════════════════════════════════════════════
#  TAB 1 — Resume Upload  (primary, preferred)
# ════════════════════════════════════════════════════════════════════════════
with tab_upload:
    st.markdown("##### Upload Candidate File")
    st.info(
        "📌 **Skills, experience years, internship duration, and education are extracted automatically.**  "
        "No manual entry needed after upload.",
        icon="✅",
    )

    uploaded_file = st.file_uploader(
        "Supported formats: PDF, DOCX, TXT, CSV",
        type=["pdf", "docx", "txt", "csv"],
        help="The parser extracts skills, work-history timestamps, internship durations, and education level.",
    )

    if uploaded_file is not None:
        with st.spinner("Analysing resume — extracting skills, timeline, and education…"):
            parsed = parse_resume(uploaded_file, uploaded_file.name)

        # ── Store in session state (auto-fill everything) ─────────────────────
        st.session_state["extracted_skills"] = parsed.get("skills", [])
        st.session_state["user_experience"]  = parsed.get("experience_years", 0.0)
        st.session_state["internship_years"] = parsed.get("internship_years", 0.0)
        st.session_state["user_education"]   = parsed.get("education", "Not Specified")
        st.session_state["degree_field"]     = parsed.get("degree_field", "")
        st.session_state["source_mode"]      = "resume"

        exp_val     = st.session_state["user_experience"]
        intern_val  = st.session_state["internship_years"]
        edu_val     = st.session_state["user_education"]
        field_val   = st.session_state["degree_field"]
        skills_list = st.session_state["extracted_skills"]

        # ── Success banner ────────────────────────────────────────────────────
        st.success(
            f"✅ Parsed **{uploaded_file.name}** — {parsed['word_count']} words"
        )

        # ── Summary metrics ───────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Detected Skills", len(skills_list))
        with c2:
            st.metric("Professional Exp.", f"{exp_val} yrs")
        with c3:
            st.metric("Internship Exp.", f"{intern_val} yrs")
        with c4:
            edu_display = edu_val if edu_val != "Not Specified" else "Not detected"
            st.metric("Education", edu_display)

        if field_val:
            st.caption(f"🎓 Degree field detected: **{field_val}**")

        # ── Skill tags ────────────────────────────────────────────────────────
        if skills_list:
            st.markdown("**Identified Skills:**")
            tags_html = " ".join(
                f"<span class='skill-tag skill-tag-matched'>{s}</span>"
                for s in skills_list
            )
            st.markdown(f"<div class='tag-container'>{tags_html}</div>", unsafe_allow_html=True)
        else:
            st.warning(
                "No technical skills matched the built-in taxonomy.  "
                "Switch to **Manual Skill Entry** or ensure your resume uses standard skill names."
            )

        # ── Inline adjustments (optional, not required) ───────────────────────
        with st.expander("⚙️ Fine-tune extracted values (optional)"):
            st.caption("The fields below were auto-detected from your resume. Edit only if an extracted value is wrong.")
            adj_exp    = st.slider("Professional experience (years):", 0.0, 30.0, float(exp_val), 0.5)
            adj_intern = st.slider("Internship experience (years):", 0.0, 10.0, float(intern_val), 0.5)
            EDU_OPTIONS = [
                "Not Specified",
                "Bootcamp / Professional Certification",
                "Diploma",
                "Associate's Degree",
                "Bachelor's (B.A.)", "Bachelor's (B.Com)", "Bachelor's (BCA)",
                "Bachelor's (B.Sc)", "Bachelor's (BBA)", "Bachelor's (B.E.)",
                "Bachelor's (B.Tech)", "Bachelor's Degree",
                "Master's (M.A.)", "Master's (M.Com)", "Master's (MCA)",
                "Master's (M.Sc)", "Master's (MBA)", "Master's (M.E.)",
                "Master's (M.Tech)", "Master's Degree",
                "Doctorate (Ph.D.)",
            ]
            adj_edu = st.selectbox(
                "Highest education level:",
                options=EDU_OPTIONS,
                index=EDU_OPTIONS.index(edu_val) if edu_val in EDU_OPTIONS else 0,
            )
            if st.button("Apply adjustments"):
                st.session_state["user_experience"]  = adj_exp
                st.session_state["internship_years"] = adj_intern
                st.session_state["user_education"]   = adj_edu
                st.success("Adjustments saved.")

# ════════════════════════════════════════════════════════════════════════════
#  TAB 2 — Manual Entry  (fallback)
# ════════════════════════════════════════════════════════════════════════════
with tab_manual:
    st.markdown("##### Manual Competency Specification")

    # Only accept manual input if no resume has been uploaded this session
    if st.session_state["source_mode"] == "resume":
        st.info("A resume was uploaded — values are auto-filled. Switch to **Upload Resume** tab to view them, or clear the upload to enter manually.")
    else:
        # Build canonical skill options
        skill_options = sorted({CANONICAL_SKILL_MAP.get(s, s.title()) for s in TECH_SKILLS_TAXONOMY})

        # Safe defaults that exist in the canonicalized set
        safe_defaults = [s for s in ["Python", "Sql", "Machine Learning", "Data Analysis", "Git"] if s in skill_options]

        manual_skills = st.multiselect(
            "Select your core technical skills:",
            options=skill_options,
            default=safe_defaults,
        )

        col_exp, col_edu = st.columns(2)
        with col_exp:
            manual_exp    = st.slider("Professional experience (years):", 0.0, 20.0, 2.0, 0.5)
            manual_intern = st.slider("Internship experience (years):", 0.0, 5.0, 0.0, 0.5)
        with col_edu:
            EDU_OPTIONS_MANUAL = [
                "Not Specified",
                "Bootcamp / Professional Certification",
                "Diploma",
                "Associate's Degree",
                "Bachelor's (B.A.)", "Bachelor's (B.Com)", "Bachelor's (BCA)",
                "Bachelor's (B.Sc)", "Bachelor's (BBA)", "Bachelor's (B.E.)",
                "Bachelor's (B.Tech)", "Bachelor's Degree",
                "Master's (M.A.)", "Master's (M.Com)", "Master's (MCA)",
                "Master's (M.Sc)", "Master's (MBA)", "Master's (M.E.)",
                "Master's (M.Tech)", "Master's Degree",
                "Doctorate (Ph.D.)",
            ]
            manual_edu = st.selectbox(
                "Highest education level:",
                options=EDU_OPTIONS_MANUAL,
                index=EDU_OPTIONS_MANUAL.index("Bachelor's (B.Tech)"),
            )

        st.session_state["extracted_skills"] = manual_skills
        st.session_state["user_experience"]  = manual_exp
        st.session_state["internship_years"] = manual_intern
        st.session_state["user_education"]   = manual_edu
        st.session_state["source_mode"]      = "manual"

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
#  ANALYSE BUTTON
# ════════════════════════════════════════════════════════════════════════════
if st.button("🚀 Analyse & Match Top Roles", type="primary", use_container_width=True):
    st.session_state["analyzed"] = True

# ════════════════════════════════════════════════════════════════════════════
#  RESULTS
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.get("analyzed"):
    active_skills  = st.session_state.get("extracted_skills", [])
    active_exp     = st.session_state.get("user_experience", 0.0)
    active_intern  = st.session_state.get("internship_years", 0.0)
    active_edu     = st.session_state.get("user_education", "Not Specified")

    if not active_skills:
        st.error("Please provide at least one skill to calculate job compatibility.")
    else:
        st.markdown("### 🏆 Top 4 Role Compatibility Matches")
        if active_intern > 0:
            st.caption(
                f"📊 Scoring basis: **{active_exp} yrs** professional + **{active_intern} yrs** internship (counted at 40 %) | Education: {active_edu}"
            )
        else:
            st.caption(
                f"📊 Scoring basis: **{active_exp} yrs** experience | Education: {active_edu}"
            )

        ranked_roles = rank_top_roles(
            user_skills=active_skills,
            user_experience=active_exp,
            user_education=active_edu,
            internship_years=active_intern,
            top_n=4,
        )

        for idx, role in enumerate(ranked_roles):
            score = role["compatibility_score"]
            badge_cls = "score-high" if score >= 75 else ("score-mid" if score >= 50 else "score-low")

            st.markdown(f"""
            <div class="match-card">
                <div class="match-card-header">
                    <div>
                        <span style="font-size:0.8rem;color:#64748b;font-weight:600;">RANK #{idx+1} • {role['category'].upper()}</span>
                        <div class="match-role-title">{role['title']}</div>
                    </div>
                    <span class="score-badge {badge_cls}">{score}% Match</span>
                </div>
                <div style="font-size:0.9rem;color:#475569;margin-bottom:0.75rem;">
                    {role['description']}
                </div>
                <div style="font-size:0.8rem;color:#64748b;">
                    💰 Typical salary (India): <strong>₹{role.get('typical_salary_lpa','—')} LPA</strong>
                    &nbsp;|&nbsp; Min. experience: <strong>{role['min_experience']} yr(s)</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(score / 100.0)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.caption("✅ Matched Skills:")
                if role["matched_skills"]:
                    tags = " ".join(
                        f"<span class='skill-tag skill-tag-matched'>{s}</span>"
                        for s in role["matched_skills"]
                    )
                else:
                    tags = "<span style='font-size:0.8rem;color:#94a3b8;'>None</span>"
                st.markdown(f"<div class='tag-container'>{tags}</div>", unsafe_allow_html=True)
            with col_m2:
                st.caption("💡 Recommended Skills to Learn:")
                if role["missing_skills"]:
                    tags = " ".join(
                        f"<span class='skill-tag skill-tag-missing'>{s}</span>"
                        for s in role["missing_skills"]
                    )
                else:
                    tags = "<span style='font-size:0.8rem;color:#15803d;'>All core skills covered!</span>"
                st.markdown(f"<div class='tag-container'>{tags}</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom:1.5rem;'></div>", unsafe_allow_html=True)

        # ── Job Openings ─────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### 💼 Curated Live Job Openings")
        st.caption("Aggregated opportunities aligned with your top matched role profile.")

        c_filter1, c_filter2 = st.columns([2, 1])
        with c_filter1:
            selected_role = st.selectbox(
                "Filter openings by ranked role:",
                options=[r["title"] for r in ranked_roles],
                index=0,
            )
        with c_filter2:
            work_type = st.selectbox("Work Arrangement:", ["All", "Remote", "Hybrid", "On-site"])

        jobs = fetch_jobs_for_role(selected_role, work_type_filter=work_type, limit=5)

        if jobs:
            for job in jobs:
                st.markdown(f"""
                <div class="job-listing-card">
                    <div>
                        <div style="font-size:1.05rem;font-weight:600;color:#0f172a;">{job.get('job_title')}</div>
                        <div class="job-meta-row">
                            <span>🏢 {job.get('company')}</span>
                            <span>📍 {job.get('location')}</span>
                            <span>💼 {job.get('work_type')}</span>
                            <span>💰 {job.get('salary_range')}</span>
                        </div>
                        <div style="font-size:0.85rem;color:#475569;margin-top:0.5rem;">
                            <strong>Skills:</strong> {job.get('skills_required')}
                        </div>
                    </div>
                    <div>
                        <a href="{job.get('apply_url','#')}" target="_blank" class="apply-button-link">Apply Now ↗</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"No specific openings found for '{selected_role}' with '{work_type}' arrangement.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Skill-to-Job Matching Platform • India-aware NLP • Deployable on Streamlit Cloud")
