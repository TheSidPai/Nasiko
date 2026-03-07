import logging
import uuid
import click
import uvicorn
import io
from datetime import datetime
from typing import List, Optional, Any, Dict, Union, Literal

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import Agent
from models import JsonRpcRequest, JsonRpcResponse, Message, Task, TaskStatus, Artifact, ArtifactPart
from database import get_async_db, seed_database, serialize_doc
from email_service import send_email, build_offer_email, build_rejection_email
from calendar_service import schedule_interview

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent-template")

app = FastAPI(title="TalentFlow HR Agent", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = Agent()


# ---------------------------------------------------------------------------
# Startup — seed MongoDB
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    await seed_database()
    logger.info("TalentFlow HR Agent v2.0 started")


# ---------------------------------------------------------------------------
# Pydantic models for REST endpoints
# ---------------------------------------------------------------------------

class CandidateIn(BaseModel):
    name: str
    role_applied: str
    fit_score: int
    recommendation: str  # Proceed / Hold / Reject
    resume_summary: str
    email: str = ""
    status: str = "pending"          # pending | approved | rejected
    applicant_type: str = "hr_uploaded"  # hr_uploaded | self_applied

class CandidateStatusUpdate(BaseModel):
    status: str          # approved | rejected
    send_email: bool = True
    email_body: str = ""  # optional override

class InternalSearchRequest(BaseModel):
    query: str           # free-text role / skill description

class EmailTrackRequest(BaseModel):
    candidate_id: str
    email_type: str  # offer / rejection
    email_body: str

class EmailSendRequest(BaseModel):
    candidate_id: str
    to_email: str
    email_type: str  # offer | rejection | custom
    subject: str = ""
    body: str = ""        # If provided, overrides the auto-generated template
    candidate_name: str = ""
    role: str = ""

class CalendarScheduleRequest(BaseModel):
    candidate_name: str
    role: str
    candidate_email: str = ""
    interviewer_email: str = ""
    interview_datetime: str = ""   # ISO format: "2025-02-15T14:00:00"
    duration_minutes: int = 60
    notes: str = ""

@app.post("/")
async def handle_rpc(request: JsonRpcRequest):
    """Handle JSON-RPC requests."""
    
    if request.method == "message/send":
        try:
            # 1. Parse Input
            # request.params is now a JsonRpcParams model
            user_message = request.params.message
            session_id = request.params.session_id
            
            # Extract text
            input_text = ""
            for part in user_message.parts:
                if part.kind == "text" and part.text:
                    input_text += part.text
            
            logger.info(f"Received message: {input_text[:50]}... (Session: {session_id})")
            
            # 2. Invoke Agent Logic
            # Use session_id as thread_id so each chat session has its own memory.
            # Fall back to a stable default if the client sends no session_id.
            thread_id = session_id if session_id else "default"
            response_text = agent.process_message(input_text, thread_id)
            
            # 3. Construct Response
            task_id = str(uuid.uuid4())
            context_id = session_id if session_id else str(uuid.uuid4())
            
            artifact = Artifact(
                parts=[ArtifactPart(text=response_text)]
            )
            
            task = Task(
                id=task_id,
                status=TaskStatus(
                    state="completed",
                    timestamp=datetime.now().isoformat()
                ),
                artifacts=[artifact],
                contextId=context_id
            )
            
            return JsonRpcResponse(
                id=request.id,
                result=task
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    else:
        raise HTTPException(status_code=404, detail=f"Method {request.method} not found")


# ---------------------------------------------------------------------------
# PDF Upload — extract text from uploaded PDF
# ---------------------------------------------------------------------------

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF resume and extract its text content."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        import pdfplumber
        contents = await file.read()
        text_pages = []
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_pages.append(page_text)
        extracted_text = "\n\n".join(text_pages)
        if not extracted_text.strip():
            raise HTTPException(status_code=422, detail="Could not extract text from PDF. The file may be image-based.")
        return {"text": extracted_text, "pages": len(pdf.pages) if hasattr(pdf, 'pages') else len(text_pages)}
    except ImportError:
        raise HTTPException(status_code=500, detail="pdfplumber not installed. Run: pip install pdfplumber")
    except Exception as e:
        logger.error(f"PDF extraction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")


# ---------------------------------------------------------------------------
# Candidates — store and retrieve screened candidates
# ---------------------------------------------------------------------------

@app.post("/candidates", status_code=201)
async def create_candidate(candidate: CandidateIn):
    """Save a screened candidate to MongoDB."""
    db = get_async_db()
    record = candidate.dict()
    record["submitted_at"] = datetime.utcnow().isoformat()
    record["email_sent"] = False
    result = await db.candidates.insert_one(record)
    return {"id": str(result.inserted_id), "message": "Candidate saved successfully."}


@app.get("/candidates")
async def list_candidates(recommendation: Optional[str] = None, status: Optional[str] = None):
    """List all candidates, optionally filtered by recommendation (Proceed/Hold/Reject) and/or status (pending/approved/rejected)."""
    db = get_async_db()
    query = {}
    if recommendation:
        query["recommendation"] = recommendation
    if status:
        query["status"] = status
    cursor = db.candidates.find(query).sort("submitted_at", -1).limit(100)
    candidates = [serialize_doc(doc) async for doc in cursor]
    return {"candidates": candidates, "total": len(candidates)}


@app.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: str):
    """Delete a candidate record."""
    from bson import ObjectId
    db = get_async_db()
    result = await db.candidates.delete_one({"_id": ObjectId(candidate_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return {"message": "Candidate deleted."}


@app.patch("/candidates/{candidate_id}/status")
async def update_candidate_status(candidate_id: str, req: CandidateStatusUpdate):
    """HR approves or rejects a self-applied candidate, optionally sending an email."""
    from bson import ObjectId
    db = get_async_db()

    # Fetch candidate to get name, email, role
    doc = await db.candidates.find_one({"_id": ObjectId(candidate_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Candidate not found.")

    await db.candidates.update_one(
        {"_id": ObjectId(candidate_id)},
        {"$set": {"status": req.status, "reviewed_at": datetime.utcnow().isoformat()}}
    )

    email_result = None
    if req.send_email and doc.get("email"):
        try:
            name = doc.get("name", "Candidate")
            role = doc.get("role_applied", "the position")
            if req.email_body:
                html_body = f"<p>{req.email_body}</p>"
                subject = "Update on your application"
            elif req.status == "approved":
                html_body = build_offer_email(name, role)
                subject = f"Congratulations! Offer for {role}"
            else:
                html_body = build_rejection_email(name, role)
                subject = f"Your application for {role}"
            success = send_email(doc["email"], subject, html_body)
            email_result = {"sent": success, "to": doc["email"]}
            if success:
                await db.candidates.update_one(
                    {"_id": ObjectId(candidate_id)},
                    {"$set": {"email_sent": True}}
                )
        except Exception as e:
            email_result = {"sent": False, "error": str(e)}

    return {"message": f"Candidate status updated to '{req.status}'.", "email": email_result}


@app.post("/internal-search")
async def internal_talent_search(req: InternalSearchRequest):
    """Search existing employees for internal talent matching a role/skill description."""
    db = get_async_db()
    employees = [serialize_doc(e) async for e in db.employees.find({}).limit(200)]

    if not employees:
        return {"matches": [], "ai_summary": "No employees found in the database."}

    # Build a compact profile list for the LLM
    profiles = "\n".join(
        f"- ID:{e.get('id','?')}, Name:{e.get('name','?')}, Role:{e.get('role','?')}"
        for e in employees
    )

    prompt = (
        f"You are an HR AI. A manager is looking for someone internally who fits this description:\n"
        f"\"{req.query}\"\n\n"
        f"Here are the current employees:\n{profiles}\n\n"
        f"Return a JSON object with two fields:\n"
        f"1. \"matches\": array of the top matches (max 5), each with: id, name, role, fit_score (0-100), match_reason, available (true/false)\n"
        f"2. \"ai_summary\": 1-2 sentences summarising your recommendation (e.g. whether to hire externally or use internal resources)\n"
        f"Respond ONLY with valid JSON, no markdown fences."
    )

    try:
        import json, re
        # Use the global agent instance (already running), fire a one-shot search prompt
        raw = agent.process_message(prompt, thread_id="internal_search_oneshot")

        # Strip any accidental markdown fences
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
        parsed = json.loads(cleaned)

        matches = parsed.get("matches", [])
        ai_summary = parsed.get("ai_summary", "")

        # Enrich with burnout risk so HR can see availability
        emp_map = {e.get("id"): e for e in employees}
        for m in matches:
            emp = emp_map.get(m.get("id"))
            if emp:
                from bson import ObjectId
                # compute a simple risk proxy — high overtime means "busy"
                overtime = emp.get("overtime_hrs_last_month", 0)
                m.setdefault("available", overtime < 50)

        return {"matches": matches, "ai_summary": ai_summary}
    except Exception as e:
        logger.error(f"Internal search error: {e}")
        return {"matches": [], "ai_summary": f"Search failed: {str(e)}"}



@app.post("/email/track")
async def track_email(req: EmailTrackRequest):
    """Record that an email was sent to a candidate."""
    from bson import ObjectId
    db = get_async_db()
    record = {
        "candidate_id": req.candidate_id,
        "email_type": req.email_type,
        "email_body": req.email_body,
        "sent_at": datetime.utcnow().isoformat(),
    }
    await db.emails.insert_one(record)
    # Mark candidate as email_sent
    try:
        await db.candidates.update_one(
            {"_id": ObjectId(req.candidate_id)},
            {"$set": {"email_sent": True}}
        )
    except Exception:
        pass
    return {"message": "Email tracked successfully."}


@app.post("/email/send")
async def send_candidate_email(req: EmailSendRequest):
    """
    Send a real email to a candidate via Gmail SMTP.
    Automatically builds offer/rejection HTML templates if body is not provided.
    Also marks the candidate as email_sent in MongoDB.
    """
    from bson import ObjectId

    name = req.candidate_name or "Candidate"
    role = req.role or "the position"

    # Determine subject + HTML body
    if req.body:
        subject = req.subject or f"Update regarding your application – {role}"
        html_body = req.body.replace("\n", "<br>")
    elif req.email_type == "offer":
        subject, html_body = build_offer_email(name, role)
    elif req.email_type == "rejection":
        subject, html_body = build_rejection_email(name, role)
    else:
        subject = req.subject or f"Update regarding your application – {role}"
        html_body = req.body or f"<p>Dear {name},</p><p>Thank you for your application.</p>"

    result = send_email(to_email=req.to_email, subject=subject, html_body=html_body)

    if result["success"]:
        # Mark candidate as email_sent + log to emails collection
        db = get_async_db()
        log_record = {
            "candidate_id": req.candidate_id,
            "email_type": req.email_type,
            "to_email": req.to_email,
            "subject": subject,
            "sent_at": datetime.utcnow().isoformat(),
        }
        await db.emails.insert_one(log_record)
        if req.candidate_id:
            try:
                await db.candidates.update_one(
                    {"_id": ObjectId(req.candidate_id)},
                    {"$set": {"email_sent": True, "email_type": req.email_type}}
                )
            except Exception:
                pass

    return result


# ---------------------------------------------------------------------------
# Google Calendar — schedule interviews
# ---------------------------------------------------------------------------

@app.post("/calendar/schedule")
async def create_calendar_event(req: CalendarScheduleRequest):
    """
    Schedule an interview on Google Calendar.
    - If GOOGLE_CALENDAR_CREDENTIALS_JSON is set → creates a real calendar event.
    - Otherwise → returns a pre-filled Google Calendar quick-add URL.
    """
    result = schedule_interview(
        candidate_name=req.candidate_name,
        role=req.role,
        candidate_email=req.candidate_email,
        interviewer_email=req.interviewer_email,
        interview_datetime_iso=req.interview_datetime,
        duration_minutes=req.duration_minutes,
        notes=req.notes,
    )
    return result


# ---------------------------------------------------------------------------
# Employees (read-only for frontend dashboard)
# ---------------------------------------------------------------------------

@app.get("/employees")
async def list_employees():
    """List all employees from MongoDB."""
    db = get_async_db()
    cursor = db.employees.find({}, {"_id": 0})
    employees = [doc async for doc in cursor]
    return {"employees": employees}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": "TalentFlow HR Agent", "version": "2.0.0"}


if __name__ == "__main__":
    @click.command()
    @click.option('--host', 'host', default='0.0.0.0')
    @click.option('--port', 'port', default=5000)
    def main(host: str, port: int):
        uvicorn.run(app, host=host, port=port)

    main()
