"""
HR Agent Tools — TalentFlow Candidate Agent
Tools:
  1. screen_resume            — Score a resume against a JD
  2. generate_interview_qs    — Tailored interview questions
  3. answer_policy_question   — Policy FAQ from embedded policy text
  4. check_application_status — Candidate self-service status check
  5. improve_cv               — CV improvement suggestions
  6. advise_offer_negotiation — Salary negotiation strategy
  7. benchmark_salary         — Market salary benchmarking
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
            "FIT SCORE: X/100\n"
            "CANDIDATE SUMMARY: (3 sentences)\n"
            "MATCHED SKILLS: (list top 5 with proficiency level)\n"
            "SKILL GAPS: (list top 3 with severity: Critical/Minor)\n"
            "EXPERIENCE ASSESSMENT: (years required vs years candidate has)\n"
            "RECOMMENDATION: PROCEED / HOLD / REJECT\n"
            "REASON: (one clear sentence)\n"
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
            "ROUND 1 - TECHNICAL VALIDATION (3 questions)\n"
            "- 2 questions validating strongest claimed skills with realistic scenarios\n"
            "- 1 deep-dive on a technology gap from the JD\n\n"
            "ROUND 2 - BEHAVIOURAL (2 questions)\n"
            "- STAR-format questions relevant to the role's key responsibilities\n\n"
            "ROUND 3 - PROBLEM SOLVING (2 questions)\n"
            "- Situational / case-study questions for this specific role type\n\n"
            "CULTURE FIT (1 question)\n"
            "- Assess collaboration style and growth mindset\n\n"
            "For each question, add: (Difficulty: Easy/Medium/Hard) and (What to listen for)"
        )
    })


# ---------------------------------------------------------------------------
# TOOL 3 — Policy FAQ
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
            "Answer: [Clear, direct answer in 2-3 sentences]\n"
            "Policy Reference: [Exact section name]\n"
            "Key Details:\n"
            "- [Bullet 1]\n"
            "- [Bullet 2]\n"
            "Important Note: [Any exceptions, conditions, or next steps]\n\n"
            "If not covered: 'This topic is not in the current policy. "
            "Please contact HR at hr@talentflow.com or raise a ticket in HRMS.'"
        )
    })


# ---------------------------------------------------------------------------
# TOOL 4 — Check Application Status (candidate self-service)
# ---------------------------------------------------------------------------

@tool
def check_application_status(email: str) -> str:
    """
    Check the application status of a candidate using their email address.
    Use this when a candidate asks about the status of their job application.

    Args:
        email: The candidate's email address.
    """
    try:
        from database import get_sync_db
        db = get_sync_db()
        record = db.candidates.find_one({"email": email}, {"_id": 0})
        if not record:
            return json.dumps({
                "status": "not_found",
                "message": f"No application found for {email}. Please check your email address or contact HR directly."
            })
        return json.dumps({
            "tool": "check_application_status",
            "application": record,
            "instruction": (
                "You are a helpful HR assistant giving a candidate their application update.\n"
                "Report clearly in plain text with no markdown:\n"
                "Application Status: [status]\n"
                "Role Applied For: [role]\n"
                "Fit Score: [score]/100\n"
                "Recommendation: [recommendation]\n"
                "Email Sent: [yes/no]\n"
                "Applied On: [date]\n"
                "Use warm, encouraging language. If status is pending, say HR is reviewing and will be in touch soon."
            )
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------
# TOOL 5 — Improve CV
# ---------------------------------------------------------------------------

@tool
def improve_cv(resume_text: str) -> str:
    """
    Analyze a candidate's resume and provide specific, actionable improvement suggestions.
    Use this when a candidate asks how to improve their CV or resume.

    Args:
        resume_text: The full text content of the candidate's resume.
    """
    return json.dumps({
        "tool": "improve_cv",
        "resume_text": resume_text,
        "instruction": (
            "You are a professional CV coach. Review this resume and give specific, actionable improvements.\n\n"
            "CV IMPROVEMENT REPORT\n\n"
            "OVERALL IMPRESSION\n"
            "One sentence on the CV's current strength.\n\n"
            "CRITICAL FIXES (must change)\n"
            "List 3-5 specific issues. Be concrete, not generic. Example: Your bullet points say what you did, "
            "not what you achieved. Change: Managed a team -> Led a team of 5 engineers, delivering 3 product "
            "releases on time and 15% under budget.\n\n"
            "MISSING SECTIONS\n"
            "List any sections absent but important for this candidate's profile.\n\n"
            "STRONG POINTS\n"
            "List 2-3 things already done well. Be genuine and specific.\n\n"
            "QUICK WINS (fix in under 10 minutes)\n"
            "List 3 small things they can add or fix immediately.\n\n"
            "Be specific, direct, and encouraging. Reference their actual content."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 6 — Advise Offer Negotiation
# ---------------------------------------------------------------------------

@tool
def advise_offer_negotiation(
    current_offer: str,
    desired_salary: str,
    role: str,
    years_experience: int,
    competing_offer: str = "",
) -> str:
    """
    Provide a negotiation strategy and script for a candidate negotiating a job offer.
    Use this when a candidate wants advice on how to negotiate their salary.

    Args:
        current_offer: The offer received (e.g. '10 LPA', '$90k').
        desired_salary: What the candidate wants (e.g. '13 LPA', '$110k').
        role: The job title being offered.
        years_experience: Candidate's years of experience.
        competing_offer: A competing offer if any (optional).
    """
    return json.dumps({
        "tool": "advise_offer_negotiation",
        "current_offer": current_offer,
        "desired_salary": desired_salary,
        "role": role,
        "years_experience": years_experience,
        "competing_offer": competing_offer,
        "instruction": (
            f"You are a career coach helping a {role} with {years_experience} years of experience "
            f"negotiate their salary from {current_offer} to {desired_salary}."
            f"{' They have a competing offer of: ' + competing_offer if competing_offer else ''}\n\n"
            "OFFER NEGOTIATION ADVICE\n\n"
            "SITUATION ASSESSMENT\n"
            f"- Current offer: {current_offer}\n"
            f"- Target: {desired_salary}\n"
            f"- Gap: (calculate the difference)\n"
            "- Is this ask reasonable? (Yes/No with 1-sentence reason based on market knowledge)\n\n"
            "NEGOTIATION STRATEGY\n"
            "- Approach: (Collaborative / Firm / Flexible)\n"
            "- Your strongest leverage points: (list 2-3)\n"
            "- What to lead with in the conversation\n\n"
            "WORD-FOR-WORD SCRIPT\n"
            "Opening line: (exact words to say when starting the negotiation)\n"
            "If they push back: (exact words to hold your position)\n"
            "Closing: (how to land the conversation positively)\n\n"
            "FALLBACK OPTIONS\n"
            "If they cannot meet the salary, suggest 2-3 alternatives to negotiate "
            "(signing bonus, extra leave, remote work, faster review cycle, etc.)\n\n"
            "Be direct, realistic, and encouraging. Plain text only."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 7 — Benchmark Salary
# ---------------------------------------------------------------------------

@tool
def benchmark_salary(role: str, years_experience: int, location: str = "India", current_salary: str = "") -> str:
    """
    Benchmark a salary against current market rates for a given role and experience level.
    Use this when HR asks if a salary is competitive, or when a candidate wants to know market rates.

    Args:
        role: Job title (e.g. React Developer, Data Scientist, Product Manager).
        years_experience: Years of relevant experience.
        location: City or country for market context (default: India).
        current_salary: The salary being evaluated (optional, e.g. '14LPA' or '$120k').
    """
    return json.dumps({
        "tool": "benchmark_salary",
        "role": role,
        "years_experience": years_experience,
        "location": location,
        "current_salary": current_salary,
        "instruction": (
            f"You are a compensation specialist with deep knowledge of {location} tech salary benchmarks.\n"
            f"Evaluate the market rate for a {role} with {years_experience} years of experience in {location}.\n"
            f"{'The salary being evaluated is: ' + current_salary + chr(10) if current_salary else ''}"
            "\nSALARY BENCHMARK REPORT\n\n"
            f"Role: {role}\n"
            f"Experience: {years_experience} years\n"
            f"Market: {location}\n\n"
            "Market Range:\n"
            "- Entry band (P25): X\n"
            "- Median (P50): X\n"
            "- Senior band (P75): X\n"
            "- Top of market (P90): X\n\n"
            f"{'Verdict on ' + current_salary + ': Below market / Competitive / Above market' + chr(10) if current_salary else ''}"
            "Key Factors Affecting This Range: (skills in demand, location premium, company size)\n\n"
            "Recommendation: What the company should offer to attract and retain this profile.\n"
            "Plain text only, no markdown. Use LPA for India, USD/year for US."
        )
    })
