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


# ---------------------------------------------------------------------------
# TOOL 13 — Check Leave Balance
# ---------------------------------------------------------------------------

@tool
def check_leave_balance(employee_identifier: str) -> str:
    """
    Check the leave balance and entitlement for an employee.
    Use this when an employee asks how many leaves they have left.

    Args:
        employee_identifier: Employee name or ID.
    """
    employees = _get_employees_from_db()
    employee = None
    for e in employees:
        if employee_identifier.lower() in e["name"].lower() or employee_identifier.upper() == e.get("id", ""):
            employee = e
            break

    if not employee:
        return json.dumps({
            "status": "not_found",
            "message": f"Employee '{employee_identifier}' not found in the database."
        })

    joining_month = None
    added_at = employee.get("added_at", "")
    if added_at:
        try:
            joining_month = datetime.fromisoformat(added_at).month
        except Exception:
            joining_month = None

    annual_entitlement = 18
    sick_entitlement = 10
    if joining_month and joining_month > 10:
        annual_entitlement = 3

    days_since_leave = employee.get("days_since_last_leave", 0)
    tenure_years = employee.get("tenure_years", 1)

    return json.dumps({
        "tool": "check_leave_balance",
        "employee": {
            "name": employee["name"],
            "role": employee.get("role", ""),
            "tenure_years": tenure_years,
            "days_since_last_leave": days_since_leave,
        },
        "policy_entitlement": {
            "annual_leave_days": annual_entitlement,
            "sick_leave_days": sick_entitlement,
            "carry_forward_max": 5,
            "maternity_leave_weeks": 26,
            "paternity_leave_days": 5,
        },
        "instruction": (
            f"You are an HR assistant giving {employee['name']} their leave entitlement summary.\n"
            "Present this clearly in plain text with no markdown:\n"
            "LEAVE BALANCE SUMMARY\n"
            "Annual Leave: X days entitlement per year\n"
            "Sick Leave: X days entitlement per year\n"
            "Carry Forward: Up to 5 unused annual leave days\n"
            f"Note: Last leave was {days_since_leave} days ago. "
            "Remind them to apply via the HRMS portal at least 3 working days in advance. "
            "Note that actual days taken this year would need to be tracked in HRMS for a precise remaining balance."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 14 — Generate Onboarding Plan
# ---------------------------------------------------------------------------

@tool
def generate_onboarding_plan(role: str, start_date: str, department: str = "") -> str:
    """
    Generate a personalized day-by-day onboarding plan for a new hire.
    Use this when HR needs to create an onboarding schedule for a new employee.

    Args:
        role: The job title of the new hire (e.g. ML Engineer, Frontend Developer).
        start_date: The joining date (e.g. March 15, 2026).
        department: The department they are joining (optional).
    """
    return json.dumps({
        "tool": "generate_onboarding_plan",
        "role": role,
        "start_date": start_date,
        "department": department,
        "instruction": (
            f"You are an expert HR onboarding specialist. Create a detailed onboarding plan for a new {role} "
            f"joining on {start_date}{' in the ' + department + ' department' if department else ''}.\n\n"
            "ONBOARDING PLAN\n\n"
            "DAY 1 - Welcome and Orientation\n"
            "- List 4-5 specific activities (IT setup, team intro, policy walkthrough, etc.)\n\n"
            "DAY 2-3 - Role Immersion\n"
            "- List role-specific activities tailored to the job title\n\n"
            "WEEK 1 END - First Check-in\n"
            "- Manager 1:1 agenda, key questions to ask\n\n"
            "WEEK 2-4 - Ramp Up\n"
            "- First project/task recommendations, key stakeholders to meet\n\n"
            "30-DAY MILESTONE\n"
            "- What success looks like at 30 days\n\n"
            "60-DAY MILESTONE\n"
            "- Expected independence and contributions\n\n"
            "90-DAY MILESTONE\n"
            "- Full productivity benchmark and first performance check-in\n\n"
            "Keep it specific to the role. Plain text only, no markdown."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 15 — Predict Attrition Risk
# ---------------------------------------------------------------------------

@tool
def predict_attrition_risk(employee_identifier: str) -> str:
    """
    Predict attrition (resignation) risk for an employee based on their profile data.
    Use this when HR wants to proactively identify flight-risk employees.

    Args:
        employee_identifier: Employee name or ID (e.g. 'Priya Sharma' or 'E001'), or 'all' for full team.
    """
    employees = _get_employees_from_db()

    if employee_identifier.lower() == "all":
        targets = employees
    else:
        targets = [
            e for e in employees
            if employee_identifier.lower() in e["name"].lower() or employee_identifier.upper() == e.get("id", "")
        ]
        if not targets:
            return json.dumps({"status": "not_found", "message": f"Employee '{employee_identifier}' not found."})

    profiles = json.dumps([
        {
            "name": e["name"],
            "role": e.get("role", ""),
            "tenure_years": e.get("tenure_years", 0),
            "overtime_hrs_last_month": e.get("overtime_hrs_last_month", 0),
            "days_since_last_leave": e.get("days_since_last_leave", 0),
            "last_appraisal_months_ago": e.get("last_appraisal_months_ago", 0),
            "open_tickets": e.get("open_tickets", 0),
        }
        for e in targets
    ], indent=2)

    return json.dumps({
        "tool": "predict_attrition_risk",
        "profiles": profiles,
        "instruction": (
            "You are an HR data analyst specializing in attrition prediction.\n"
            "For each employee, analyze their signals and return:\n\n"
            "ATTRITION RISK REPORT\n\n"
            "For each person:\n"
            "Name and Role:\n"
            "Attrition Risk: Low / Medium / High / Critical\n"
            "Risk Score: X/100\n"
            "Key Risk Signals: (2-3 data-backed reasons)\n"
            "Retention Strategy: (2-3 specific, actionable steps HR should take immediately)\n\n"
            "Use these scoring guidelines:\n"
            "- Tenure under 1 year or over 8 years = elevated risk\n"
            "- Overtime over 40hrs/month = high stress signal\n"
            "- No leave in over 90 days = disengagement signal\n"
            "- No appraisal in over 12 months = recognition gap\n"
            "End with a team attrition risk summary if multiple employees shown.\n"
            "Plain text only, no markdown."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 16 — Benchmark Salary
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


# ---------------------------------------------------------------------------
# TOOL 17 — Analyze Exit Interview
# ---------------------------------------------------------------------------

@tool
def analyze_exit_interview(transcript: str, employee_role: str = "") -> str:
    """
    Analyze an exit interview transcript to surface reasons for resignation,
    sentiment, and team-level risk flags.
    Use this when HR wants to extract insights from an employee's exit interview.

    Args:
        transcript: The full text of the exit interview conversation or notes.
        employee_role: The role of the departing employee (optional, for context).
    """
    return json.dumps({
        "tool": "analyze_exit_interview",
        "transcript": transcript,
        "employee_role": employee_role,
        "instruction": (
            "You are an HR analytics specialist analyzing an exit interview to extract actionable insights.\n\n"
            "EXIT INTERVIEW ANALYSIS\n\n"
            "OVERALL SENTIMENT: Positive / Neutral / Negative / Mixed\n\n"
            "PRIMARY RESIGNATION REASONS\n"
            "Categorize into: Compensation / Career Growth / Management / Work-Life Balance / "
            "Culture / Role Clarity / External Opportunity / Personal Reasons\n"
            "For each identified reason, give a 1-sentence quote or paraphrase from the transcript.\n\n"
            "TEAM AND MANAGEMENT RISK FLAGS\n"
            "- Flag any signals that suggest systemic issues (not just personal)\n"
            "- Example: If manager style is mentioned negatively, flag team retention risk\n\n"
            "SENTIMENT BREAKDOWN\n"
            "- Feelings about team: Positive / Negative\n"
            "- Feelings about role: Positive / Negative\n"
            "- Feelings about company: Positive / Negative\n"
            "- Would recommend company: Yes / No / Maybe\n\n"
            "RECOMMENDED HR ACTIONS\n"
            "1. Immediate action (this week)\n"
            "2. Policy or process change to address root cause\n"
            "3. Team follow-up steps\n\n"
            "Plain text only, no markdown."
        )
    })


# ---------------------------------------------------------------------------
# TOOL 18 — Advise Offer Negotiation
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
# TOOL 19 — Get Hiring Pipeline Summary
# ---------------------------------------------------------------------------

@tool
def get_pipeline_summary(role_filter: str = "") -> str:
    """
    Get a summary of the hiring pipeline showing all candidates grouped by stage.
    Use this when HR asks for an overview of the current hiring pipeline,
    optionally filtered by role.

    Args:
        role_filter: Filter by a specific role name (optional). Leave empty for all roles.
    """
    try:
        from database import get_sync_db
        db = get_sync_db()
        query = {}
        if role_filter:
            query["role_applied"] = {"$regex": role_filter, "$options": "i"}
        candidates = list(db.candidates.find(query, {"_id": 0}))

        if not candidates:
            msg = f"No candidates found{' for ' + role_filter if role_filter else ''} in the pipeline."
            return json.dumps({"status": "empty", "message": msg})

        from collections import defaultdict
        by_role = defaultdict(lambda: {"Proceed": [], "Hold": [], "Reject": [], "pending": [], "approved": [], "rejected": []})
        for c in candidates:
            role = c.get("role_applied", "Unknown")
            rec = c.get("recommendation", "Hold")
            status = c.get("status", "pending")
            entry = {"name": c.get("name", "?"), "fit_score": c.get("fit_score", 0), "status": status, "email_sent": c.get("email_sent", False)}
            by_role[role][rec].append(entry)

        summary = {}
        for role, buckets in by_role.items():
            summary[role] = {
                "total": sum(len(v) for v in buckets.values()),
                "proceed": len(buckets["Proceed"]),
                "hold": len(buckets["Hold"]),
                "reject": len(buckets["Reject"]),
                "approved": len(buckets["approved"]),
                "rejected": len(buckets["rejected"]),
                "pending_review": len(buckets["pending"]),
                "candidates": buckets["Proceed"] + buckets["Hold"],
            }

        return json.dumps({
            "tool": "get_pipeline_summary",
            "pipeline": summary,
            "total_candidates": len(candidates),
            "instruction": (
                "You are an HR analyst presenting the hiring pipeline to a recruiter.\n"
                "Present clearly in plain text:\n\n"
                "HIRING PIPELINE SUMMARY\n\n"
                "For each role show:\n"
                "Role name: X total candidates\n"
                "- Proceed: X | Hold: X | Reject: X\n"
                "- Approved: X | Pending Review: X\n"
                "- Top candidates (name and fit score) from Proceed bucket\n\n"
                "End with a one-line overall pipeline health comment.\n"
                "Plain text only, no markdown."
            )
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
