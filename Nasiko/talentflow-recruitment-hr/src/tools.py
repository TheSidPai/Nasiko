"""
HR Agent Tools — TalentFlow Recruitment HR Agent
Tools:
  1. screen_resume            — Score a resume against a JD
  2. generate_interview_qs    — Tailored interview questions
  3. draft_email              — Offer or rejection email drafter
  4. send_email_to_candidate  — Actually send offer/rejection via Gmail
  5. store_candidate          — Save screened candidate to MongoDB
  6. check_application_status — Lookup candidate application status
  7. get_pipeline_summary     — Hiring pipeline overview by role
  8. get_my_meetings          — Check today/tomorrow's calendar
  9. benchmark_salary         — Market salary benchmarking
 10. answer_policy_question   — Policy FAQ from embedded policy text
"""

import json
import logging
import os
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
# TOOL 4 — Send Email to Candidate (actually sends via Gmail)
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
# TOOL 5 — Store Candidate to Database
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
# TOOL 6 — Check Application Status
# ---------------------------------------------------------------------------

@tool
def check_application_status(email: str) -> str:
    """
    Check the application status of a candidate using their email address.
    Use this when a recruiter looks up the status of a specific candidate's application.

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
                "message": f"No application found for {email}. Please check the email address."
            })
        return json.dumps({
            "tool": "check_application_status",
            "application": record,
            "instruction": (
                "You are an HR recruiter reviewing a candidate's application record.\n"
                "Report clearly in plain text with no markdown:\n"
                "Candidate Name: [name]\n"
                "Application Status: [status]\n"
                "Role Applied For: [role]\n"
                "Fit Score: [score]/100\n"
                "Recommendation: [recommendation]\n"
                "Email Sent: [yes/no]\n"
                "Applied On: [date]\n"
            )
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


# ---------------------------------------------------------------------------
# TOOL 7 — Get Hiring Pipeline Summary
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


# ---------------------------------------------------------------------------
# TOOL 8 — Get My Meetings (Google Calendar)
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
# TOOL 9 — Benchmark Salary
# ---------------------------------------------------------------------------

@tool
def benchmark_salary(role: str, years_experience: int, location: str = "India", current_salary: str = "") -> str:
    """
    Benchmark a salary against current market rates for a given role and experience level.
    Use this when HR asks if a salary offer is competitive or needs adjusting.

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
# TOOL 10 — Policy FAQ
# ---------------------------------------------------------------------------

@tool
def answer_policy_question(question: str) -> str:
    """
    Answer an HR policy question using the company's official policy document.
    Covers leave, WFH, appraisals, compensation, harassment, resignation, dress code, and conduct.

    Args:
        question: The policy question in natural language.
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
