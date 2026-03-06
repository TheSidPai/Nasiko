"""
HR Agent Tools — TalentFlow
Tools:
  1. screen_resume          — Score a resume against a JD
  2. generate_interview_qs  — Tailored interview questions
  3. draft_email            — Offer or rejection email
  4. match_internal_talent  — Check existing employees before posting externally (MongoDB)
  5. answer_policy_question — Policy FAQ from embedded policy text
  6. flag_burnout_risk      — Burnout risk assessment (MongoDB)
  7. store_candidate        — Save a screened candidate to MongoDB
"""

import json
import logging
from datetime import datetime
from langchain_core.tools import tool

logger = logging.getLogger("talentflow.tools")

# ---------------------------------------------------------------------------
# HR Policy Text (embedded)
# ---------------------------------------------------------------------------

HR_POLICY_TEXT = """
COMPANY HR POLICY DOCUMENT — TalentFlow Corp

LEAVE POLICY:
- Annual Leave: Every employee is entitled to 18 days of paid annual leave per year.
- Sick Leave: 10 days of paid sick leave per year. A medical certificate is required for absences exceeding 3 consecutive days.
- Carry Forward: A maximum of 5 unused annual leave days may be carried forward to the next calendar year. Remaining unused days lapse.
- Mid-Year Joiners: Leave is prorated based on the month of joining. Employees joining after October 1 are entitled to 3 days for the remainder of that year.
- Maternity Leave: 26 weeks of paid maternity leave for the first two children.
- Paternity Leave: 5 days of paid paternity leave within 3 months of the child's birth.
- Leave Application: All leave must be applied for at least 3 working days in advance (except sick leave) via the HRMS portal.

WORK FROM HOME (WFH) POLICY:
- Employees may work from home up to 2 days per week, subject to manager approval.
- WFH is not permitted during the first 90 days of employment (probation period).
- Employees must be reachable and responsive during core hours: 10am–4pm.

PERFORMANCE APPRAISAL:
- Appraisals are conducted bi-annually: April and October.
- Employees are rated on a 5-point scale across 4 dimensions: Delivery, Collaboration, Growth, and Leadership.
- Promotions are linked to two consecutive above-average appraisal cycles.

COMPENSATION & BENEFITS:
- Salary revisions are effective from April 1 each year.
- Employees are eligible for performance bonuses of up to 15% of annual CTC based on appraisal scores.
- Health insurance covers employee, spouse, and up to 2 dependent children.

ANTI-HARASSMENT POLICY:
- The company has zero tolerance for workplace harassment of any kind.
- Complaints can be raised to the Internal Complaints Committee (ICC) confidentially.
- All complaints will be investigated within 30 working days.

RESIGNATION & NOTICE PERIOD:
- The standard notice period is 60 days for all employees.
- Notice period buyout is available at the discretion of the reporting manager and HR.
- Employees serving notice are not eligible for new project assignments.

DRESS CODE:
- Business casual is the standard dress code on weekdays.
- Formal attire is required for client meetings and external events.
- Smart casual is permitted on Fridays.
- Clothing with offensive graphics or language is strictly prohibited.

WORKING HOURS:
- Standard working hours are 9:00 AM to 6:00 PM, Monday to Friday.
- Flexible start times between 8:00 AM and 10:00 AM are permitted with manager approval.
- Overtime beyond 10 hours per day must be pre-approved by the department head.

CODE OF CONDUCT:
- Employees must maintain confidentiality of company and client information at all times.
- Use of company resources for personal commercial activities is prohibited.
- Employees must declare any conflict of interest to their manager and HR immediately.
- Social media posts that could damage the company's reputation are prohibited.
"""


# ---------------------------------------------------------------------------
# Helper — fetch employees from MongoDB with fallback to seed data
# ---------------------------------------------------------------------------

def _get_employees_from_db():
    """Fetch employee profiles from MongoDB. Falls back to seed data if DB unavailable."""
    try:
        from database import get_sync_db, SEED_EMPLOYEES
        db = get_sync_db()
        employees = list(db.employees.find({}, {"_id": 0}))
        return employees if employees else SEED_EMPLOYEES
    except Exception as e:
        logger.warning(f"MongoDB unavailable, using seed data: {e}")
        from database import SEED_EMPLOYEES
        return SEED_EMPLOYEES


# ---------------------------------------------------------------------------
# TOOL 1 — Resume Screener
# ---------------------------------------------------------------------------

@tool
def screen_resume(resume_text: str, job_description: str) -> str:
    """
    Screen a candidate's resume against a job description.
    Returns a fit score (0-100), matched skills, missing skills, and a hiring recommendation.

    Args:
        resume_text: The full text content of the candidate's resume.
        job_description: The full text of the job description for the open role.
    """
    return json.dumps({
        "tool": "screen_resume",
        "resume_text": resume_text,
        "job_description": job_description,
        "instruction": (
            "You are a senior technical recruiter. Analyze the resume against the job description thoroughly. "
            "Return a STRUCTURED report with:\n"
            "## Fit Score: X/100\n"
            "## Candidate Summary (3 sentences)\n"
            "## Matched Skills (list top 5 with proficiency level)\n"
            "## Skill Gaps (list top 3 with severity: Critical/Minor)\n"
            "## Experience Assessment (years required vs years candidate has)\n"
            "## Recommendation: PROCEED / HOLD / REJECT\n"
            "## One-Line Reason for Recommendation\n"
            "Be specific, data-driven, and professional. Reference exact skills and technologies from both documents."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 2 — Interview Question Generator
# ---------------------------------------------------------------------------

@tool
def generate_interview_questions(resume_text: str, job_description: str) -> str:
    """
    Generate tailored interview questions for a candidate based on their resume and the job description.
    Focuses on the candidate's skill gaps and areas needing validation.

    Args:
        resume_text: The full text content of the candidate's resume.
        job_description: The full text of the job description for the open role.
    """
    return json.dumps({
        "tool": "generate_interview_questions",
        "resume_text": resume_text,
        "job_description": job_description,
        "instruction": (
            "You are a senior technical interviewer. Generate 8 tailored interview questions:\n\n"
            "**Round 1 — Technical Validation (3 questions)**\n"
            "- 2 questions validating strongest claimed skills with realistic scenarios\n"
            "- 1 deep-dive on a technology gap from the JD\n\n"
            "**Round 2 — Behavioural (2 questions)**\n"
            "- STAR-format questions relevant to the role's key responsibilities\n\n"
            "**Round 3 — Problem Solving (2 questions)**\n"
            "- Situational / case-study questions for this specific role type\n\n"
            "**Culture Fit (1 question)**\n"
            "- Assess collaboration style and growth mindset\n\n"
            "For each question, add: [Difficulty: Easy/Medium/Hard] and [What to listen for]"
        )
    })


# ---------------------------------------------------------------------------
# TOOL 3 — Email Drafter (Offer or Rejection)
# ---------------------------------------------------------------------------

@tool
def draft_email(candidate_name: str, role_title: str, decision: str, extra_details: str = "") -> str:
    """
    Draft a professional offer or rejection email for a candidate.

    Args:
        candidate_name: Full name of the candidate.
        role_title: The title of the role they applied for.
        decision: Either 'offer' or 'rejection'.
        extra_details: Optional extra info, e.g. salary for offer, or specific feedback for rejection.
    """
    return json.dumps({
        "tool": "draft_email",
        "candidate_name": candidate_name,
        "role_title": role_title,
        "decision": decision,
        "extra_details": extra_details,
        "instruction": (
            f"Draft a warm, professional {decision} email to {candidate_name} for the {role_title} role.\n"
            "Format:\n"
            "**Subject:** [Compelling subject line]\n\n"
            "**Body:**\n"
            "If OFFER: Open with genuine congratulations, briefly mention what impressed us, "
            "outline next steps (background check → documentation → start date), include a warm welcome.\n"
            "If REJECTION: Open warmly, thank them sincerely, mention one genuine positive, "
            "encourage future applications, offer to keep their profile on file. Never mention specific rejection reasons.\n"
            f"Additional context: {extra_details}.\n"
            "Tone: human, warm, brand-positive. Length: 150-200 words."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 4 — Internal Talent Matcher (MongoDB)
# ---------------------------------------------------------------------------

@tool
def match_internal_talent(job_description: str) -> str:
    """
    Before posting a job externally, search existing employees for internal candidates who match the role.
    Returns a ranked list of internal matches with match reasoning.

    Args:
        job_description: The full text of the job description for the open role.
    """
    employees = _get_employees_from_db()
    profiles_summary = json.dumps([
        {
            "id": e["id"],
            "name": e["name"],
            "role": e["role"],
            "skills": e["skills"],
            "years_exp": e["years_exp"],
            "department": e["department"]
        }
        for e in employees
    ], indent=2)

    return json.dumps({
        "tool": "match_internal_talent",
        "job_description": job_description,
        "employee_profiles": profiles_summary,
        "instruction": (
            "You are an internal mobility specialist. Compare the job description against all employee profiles.\n\n"
            "## Internal Talent Assessment\n"
            "Identify the top 1-3 internal candidates. For each:\n"
            "**Name & Current Role:**\n"
            "**Match Score:** X/10\n"
            "**Why They're a Strong Fit:** (2-3 concrete reasons based on skills + experience)\n"
            "**Skills to Develop:** (1-2 gaps to close)\n"
            "**Recommended Action:** Immediate Transfer / Upskill & Transfer in 3 months / Not a fit\n\n"
            "If no strong internal match (score < 5), clearly state: "
            "'No strong internal match found — recommend external hiring' and explain why.\n"
            "End with a cost-benefit note on internal vs external hiring."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 5 — Policy FAQ
# ---------------------------------------------------------------------------

@tool
def answer_policy_question(question: str) -> str:
    """
    Answer an employee's HR policy question using the company's official policy document.
    Covers leave, WFH, appraisals, compensation, harassment, resignation, dress code, and conduct.

    Args:
        question: The employee's policy question in natural language.
    """
    return json.dumps({
        "tool": "answer_policy_question",
        "question": question,
        "policy_document": HR_POLICY_TEXT,
        "instruction": (
            "You are a knowledgeable HR Business Partner. Answer using ONLY the policy document.\n"
            "Format:\n"
            "**Answer:** [Clear, direct answer in 2-3 sentences]\n"
            "**Policy Reference:** [Exact section name]\n"
            "**Key Details:**\n"
            "- [Bullet 1]\n"
            "- [Bullet 2]\n"
            "**Important Note:** [Any exceptions, conditions, or next steps]\n\n"
            "If not covered: 'This topic isn't in the current policy. "
            "Please contact HR at hr@talentflow.com or raise a ticket in HRMS.'"
        )
    })


# ---------------------------------------------------------------------------
# TOOL 6 — Burnout Risk Flagging (MongoDB)
# ---------------------------------------------------------------------------

@tool
def flag_burnout_risk(employee_identifier: str) -> str:
    """
    Assess burnout risk for an employee based on their work activity data.
    Returns a risk level (Low/Medium/High/Critical) and suggested HR interventions.

    Args:
        employee_identifier: The employee's name or ID (e.g. 'E001' or 'Priya Sharma').
    """
    employees = _get_employees_from_db()

    burnout_data = [
        {
            "id": e["id"],
            "name": e["name"],
            "role": e.get("role", ""),
            "overtime_hrs_last_month": e.get("overtime_hrs_last_month", 0),
            "days_since_last_leave": e.get("days_since_last_leave", 0),
            "open_tickets": e.get("open_tickets", 0),
            "last_appraisal_months_ago": e.get("last_appraisal_months_ago", 0),
            "tenure_years": e.get("tenure_years", 0),
        }
        for e in employees
    ]

    employee = None
    for e in burnout_data:
        if employee_identifier.lower() in e["name"].lower() or employee_identifier.upper() == e["id"]:
            employee = e
            break

    if not employee:
        return json.dumps({
            "tool": "flag_burnout_risk",
            "note": f"Employee '{employee_identifier}' not found. Showing full team burnout overview.",
            "all_employees": burnout_data,
            "instruction": (
                "You are an HR wellness specialist. Analyze the full team's burnout risk.\n\n"
                "## Team Burnout Risk Overview\n"
                "Rank all employees using weighted signals:\n"
                "- Overtime hours (35%): >30 hrs = High risk\n"
                "- Days since last leave (35%): >60 days = High risk\n"
                "- Open tickets (20%): >12 = High risk\n"
                "- Months since appraisal (10%): >12 = High risk\n\n"
                "Label each: Low / Medium / High / Critical\n"
                "For the top 3 highest-risk employees, provide:\n"
                "**Immediate Actions (this week):** specific interventions\n"
                "**30-Day Plan:** sustained support measures\n"
                "End with a team-level wellness summary."
            )
        })

    return json.dumps({
        "tool": "flag_burnout_risk",
        "employee": employee,
        "instruction": (
            f"You are an HR wellness specialist assessing {employee['name']} ({employee['role']}).\n"
            f"Data: {employee['overtime_hrs_last_month']} overtime hrs/month, "
            f"{employee['days_since_last_leave']} days since leave, "
            f"{employee['open_tickets']} open tickets, "
            f"last appraisal {employee['last_appraisal_months_ago']} months ago, "
            f"{employee['tenure_years']} years tenure.\n\n"
            "## Burnout Risk Assessment\n"
            "**Risk Level:** Low / Medium / High / Critical\n"
            "**Risk Score:** X/100\n"
            "**Primary Risk Factors:** (2-3 specific data points)\n\n"
            "## Recommended Interventions\n"
            "**Immediate (this week):**\n"
            "- [Action 1]\n"
            "- [Action 2]\n"
            "**Short-term (30 days):**\n"
            "- [Action]\n"
            "**Manager Talking Points:** (2 sentences for 1:1)\n"
            "Be empathetic, specific, and actionable."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 7 — Store Candidate to Database
# ---------------------------------------------------------------------------

@tool
def store_candidate(
    candidate_name: str,
    role_applied: str,
    fit_score: int,
    recommendation: str,
    resume_summary: str,
    email: str = ""
) -> str:
    """
    Save a screened candidate's details to the MongoDB candidates collection.
    Call this AFTER screening a resume to persist the candidate record.

    Args:
        candidate_name: Full name of the candidate.
        role_applied: The role title they applied for.
        fit_score: Numeric fit score from 0-100.
        recommendation: One of 'Proceed', 'Hold', or 'Reject'.
        resume_summary: 2-3 sentence summary of the candidate.
        email: Candidate's email address if available.
    """
    try:
        from database import get_sync_db
        db = get_sync_db()
        record = {
            "name": candidate_name,
            "role_applied": role_applied,
            "fit_score": fit_score,
            "recommendation": recommendation,
            "resume_summary": resume_summary,
            "email": email,
            "submitted_at": datetime.utcnow().isoformat(),
            "email_sent": False,
        }
        result = db.candidates.insert_one(record)
        logger.info(f"Stored candidate {candidate_name} with id {result.inserted_id}")
        return json.dumps({
            "status": "success",
            "message": f"Candidate '{candidate_name}' saved to database successfully.",
            "candidate_id": str(result.inserted_id),
        })
    except Exception as e:
        logger.warning(f"Failed to store candidate: {e}")
        return json.dumps({
            "status": "warning",
            "message": f"Could not save to database (MongoDB may be offline): {str(e)}",
        })

