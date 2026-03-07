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
            "Subject: [Compelling subject line]\n\n"
            "Body:\n"
            "If OFFER: Open with genuine congratulations, briefly mention what impressed us, "
            "outline next steps (background check, documentation, start date), include a warm welcome.\n"
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
            "INTERNAL TALENT ASSESSMENT\n"
            "Identify the top 1-3 internal candidates. For each:\n"
            "Name & Current Role:\n"
            "Match Score: X/10\n"
            "Why They're a Strong Fit: (2-3 concrete reasons based on skills and experience)\n"
            "Skills to Develop: (1-2 gaps to close)\n"
            "Recommended Action: Immediate Transfer / Upskill and Transfer in 3 months / Not a fit\n\n"
            "If no strong internal match (score < 5), clearly state: "
            "'No strong internal match found - recommend external hiring' and explain why.\n"
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
                "TEAM BURNOUT RISK OVERVIEW\n"
                "Rank all employees using weighted signals:\n"
                "- Overtime hours (35%): more than 30 hrs = High risk\n"
                "- Days since last leave (35%): more than 60 days = High risk\n"
                "- Open tickets (20%): more than 12 = High risk\n"
                "- Months since appraisal (10%): more than 12 = High risk\n\n"
                "Label each: Low / Medium / High / Critical\n"
                "For the top 3 highest-risk employees, provide:\n"
                "Immediate Actions (this week): specific interventions\n"
                "30-Day Plan: sustained support measures\n"
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
            "BURNOUT RISK ASSESSMENT\n"
            "Risk Level: Low / Medium / High / Critical\n"
            "Risk Score: X/100\n"
            "Primary Risk Factors: (2-3 specific data points)\n\n"
            "RECOMMENDED INTERVENTIONS\n"
            "Immediate (this week):\n"
            "- [Action 1]\n"
            "- [Action 2]\n"
            "Short-term (30 days):\n"
            "- [Action]\n"
            "Manager Talking Points: (2 sentences for 1:1)\n"
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


# ---------------------------------------------------------------------------
# TOOL 8 — Check Application Status (candidate self-service)
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
# TOOL 9 — Improve CV
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
# TOOL 10 — Send Email to Candidate (actually sends via Gmail)
# ---------------------------------------------------------------------------

@tool
def send_email_to_candidate(
    candidate_name: str,
    to_email: str,
    email_type: str,
    role_title: str,
) -> str:
    """
    Send a real email to a candidate via Gmail SMTP.
    Use this when HR wants to actually send an offer or rejection email to a candidate.
    email_type must be either 'offer' or 'rejection'.

    Args:
        candidate_name: Full name of the candidate.
        to_email: Candidate's email address.
        email_type: Either 'offer' or 'rejection'.
        role_title: The role the candidate applied for.
    """
    try:
        from email_service import send_email, build_offer_email, build_rejection_email
        if email_type.lower() == "offer":
            subject, html_body = build_offer_email(candidate_name, role_title)
        else:
            subject, html_body = build_rejection_email(candidate_name, role_title)
        result = send_email(to_email=to_email, subject=subject, html_body=html_body)
        if result.get("success"):
            return json.dumps({
                "status": "success",
                "message": f"Email successfully sent to {candidate_name} at {to_email}.",
                "type": email_type,
            })
        else:
            return json.dumps({
                "status": "failed",
                "message": result.get("error", "Unknown error sending email."),
            })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------
# TOOL 11 — Get My Meetings (Google Calendar)
# ---------------------------------------------------------------------------

@tool
def get_my_meetings(date_query: str) -> str:
    """
    Get scheduled interviews or meetings from Google Calendar for today or tomorrow.
    Use this when HR asks what meetings or interviews they have scheduled.

    Args:
        date_query: 'today', 'tomorrow', or a date like '2026-03-10'.
    """
    try:
        from datetime import datetime, timedelta
        from calendar_service import CREDENTIALS_PATH, CALENDAR_ID

        today = datetime.now().date()
        target_date = today + timedelta(days=1) if "tomorrow" in date_query.lower() else today

        if CREDENTIALS_PATH and os.path.exists(CREDENTIALS_PATH):
            try:
                from googleapiclient.discovery import build as gbuild
                from google.oauth2 import service_account
                creds = service_account.Credentials.from_service_account_file(
                    CREDENTIALS_PATH,
                    scopes=["https://www.googleapis.com/auth/calendar.readonly"]
                )
                service = gbuild("calendar", "v3", credentials=creds)
                time_min = f"{target_date}T00:00:00Z"
                time_max = f"{target_date}T23:59:59Z"
                events_result = service.events().list(
                    calendarId=CALENDAR_ID,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime"
                ).execute()
                events = events_result.get("items", [])
                if not events:
                    return json.dumps({"status": "success", "message": f"No meetings found for {date_query}."})
                meetings = [
                    {
                        "title": e.get("summary", "Untitled"),
                        "time": e["start"].get("dateTime", e["start"].get("date", "")),
                        "attendees": [a["email"] for a in e.get("attendees", [])],
                        "location": e.get("location", "Not specified"),
                    }
                    for e in events
                ]
                return json.dumps({
                    "status": "success",
                    "date": str(target_date),
                    "meetings": meetings,
                    "instruction": (
                        f"List all meetings for {date_query} clearly in plain text.\n"
                        "For each: Time, With (attendees), Location."
                    )
                })
            except Exception as api_err:
                logger.warning(f"Calendar API error: {api_err}")

        return json.dumps({
            "status": "no_credentials",
            "message": (
                f"Google Calendar API credentials are not configured. "
                f"To check your meetings for {date_query}, please open Google Calendar directly. "
                f"To enable this feature, add GOOGLE_CALENDAR_CREDENTIALS_JSON to your environment."
            )
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------
# TOOL 12 — Add Employee to Database
# ---------------------------------------------------------------------------

@tool
def add_employee_to_database(
    name: str,
    role: str,
    department: str,
    skills: str,
    years_exp: int,
    email: str = "",
) -> str:
    """
    Add a new employee to the MongoDB employees collection.
    Use this when HR wants to add a new person to the internal employee database.

    Args:
        name: Full name of the employee.
        role: Job title or role (e.g. Backend Engineer).
        department: Department name (e.g. Engineering, HR, Analytics).
        skills: Comma-separated list of skills (e.g. 'Python, React, SQL').
        years_exp: Number of years of total experience.
        email: Employee work email address (optional).
    """
    try:
        from database import get_sync_db
        db = get_sync_db()
        count = db.employees.count_documents({})
        new_id = f"E{str(count + 1).zfill(3)}"
        skills_list = [s.strip() for s in skills.split(",") if s.strip()]
        record = {
            "id": new_id,
            "name": name,
            "role": role,
            "department": department,
            "skills": skills_list,
            "years_exp": years_exp,
            "email": email,
            "overtime_hrs_last_month": 0,
            "days_since_last_leave": 0,
            "open_tickets": 0,
            "last_appraisal_months_ago": 0,
            "tenure_years": 0,
            "added_at": datetime.utcnow().isoformat(),
        }
        db.employees.insert_one(record)
        logger.info(f"Added employee {name} with ID {new_id}")
        return json.dumps({
            "status": "success",
            "message": f"Employee '{name}' has been added to the database with ID {new_id}.",
            "employee_id": new_id,
            "role": role,
            "department": department,
        })
    except Exception as e:
        logger.warning(f"Failed to add employee: {e}")
        return json.dumps({
            "status": "error",
            "message": f"Could not add employee to database: {str(e)}",
        })
