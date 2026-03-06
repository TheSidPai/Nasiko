/**
 * Backend communication — all calls to the TalentFlow agent and REST API live here.
 */
import { AGENT_URL } from "../constants";

/**
 * A single session ID for the lifetime of this browser tab.
 */
function getSessionId() {
  const KEY = "talentflow_session_id";
  let id = sessionStorage.getItem(KEY);
  if (!id) {
    id = `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
    sessionStorage.setItem(KEY, id);
  }
  return id;
}

/**
 * Send a plain-text message to the TalentFlow agent and return its reply.
 */
export async function sendToAgent(text) {
  const res = await fetch(AGENT_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: Date.now().toString(),
      method: "message/send",
      params: {
        session_id: getSessionId(),
        message: { role: "user", parts: [{ kind: "text", text }] },
      },
    }),
  });

  if (!res.ok) {
    const errorBody = await res.text();
    throw new Error(`Agent responded with ${res.status}: ${errorBody}`);
  }

  const data = await res.json();
  return (
    data?.result?.artifacts?.[0]?.parts?.[0]?.text ?? "No response from agent."
  );
}

/**
 * Upload a PDF file to the backend for text extraction.
 * @param {File} file  The PDF file object.
 * @returns {Promise<string>} The extracted text.
 */
export async function uploadPDF(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${AGENT_URL}upload-pdf`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`PDF upload failed: ${err}`);
  }

  const data = await res.json();
  return data.text;
}

/**
 * Save a screened candidate to MongoDB.
 */
export async function storeCandidate(candidate) {
  const res = await fetch(`${AGENT_URL}candidates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(candidate),
  });
  if (!res.ok) throw new Error(`Failed to store candidate: ${res.status}`);
  return res.json();
}

/**
 * Fetch all candidates from MongoDB.
 * @param {string} [recommendation]  Optional filter: 'Proceed' | 'Hold' | 'Reject'
 * @param {string} [status]          Optional status filter: 'pending' | 'approved' | 'rejected'
 */
export async function getCandidates(recommendation, status) {
  const params = new URLSearchParams();
  if (recommendation) params.set("recommendation", recommendation);
  if (status) params.set("status", status);
  const qs  = params.toString();
  const url = qs ? `${AGENT_URL}candidates?${qs}` : `${AGENT_URL}candidates`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch candidates: ${res.status}`);
  const data = await res.json();
  return data.candidates;
}

/**
 * Fetch all employees from MongoDB (for burnout dashboard).
 */
export async function getEmployees() {
  const res = await fetch(`${AGENT_URL}employees`);
  if (!res.ok) throw new Error(`Failed to fetch employees: ${res.status}`);
  const data = await res.json();
  return data.employees;
}

/**
 * Delete a candidate by ID.
 */
export async function deleteCandidate(id) {
  const res = await fetch(`${AGENT_URL}candidates/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Failed to delete candidate: ${res.status}`);
  return res.json();
}

/**
 * Track that an email was sent to a candidate.
 */
export async function trackEmail(candidateId, emailType, emailBody) {
  const res = await fetch(`${AGENT_URL}email/track`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_id: candidateId,
      email_type: emailType,
      email_body: emailBody,
    }),
  });
  if (!res.ok) throw new Error(`Failed to track email: ${res.status}`);
  return res.json();
}

/**
 * Send a real email to a candidate via Gmail SMTP.
 * @param {Object} opts
 * @param {string} opts.candidateId
 * @param {string} opts.toEmail
 * @param {string} opts.emailType   - "offer" | "rejection" | "custom"
 * @param {string} [opts.subject]
 * @param {string} [opts.body]
 * @param {string} [opts.candidateName]
 * @param {string} [opts.role]
 */
export async function sendCandidateEmail({ candidateId, toEmail, emailType, subject = "", body = "", candidateName = "", role = "" }) {
  const res = await fetch(`${AGENT_URL}email/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_id: candidateId,
      to_email: toEmail,
      email_type: emailType,
      subject,
      body,
      candidate_name: candidateName,
      role,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `Email send failed: ${res.status}`);
  }
  return res.json();
}

/**
 * Schedule an interview on Google Calendar.
 * @param {Object} opts
 * @param {string} opts.candidateName
 * @param {string} opts.role
 * @param {string} [opts.candidateEmail]
 * @param {string} [opts.interviewerEmail]
 * @param {string} [opts.interviewDatetime]  ISO string e.g. "2025-02-15T14:00:00"
 * @param {number} [opts.durationMinutes]
 * @param {string} [opts.notes]
 */
export async function scheduleInterview({ candidateName, role, candidateEmail = "", interviewerEmail = "", interviewDatetime = "", durationMinutes = 60, notes = "" }) {
  const res = await fetch(`${AGENT_URL}calendar/schedule`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      candidate_name: candidateName,
      role,
      candidate_email: candidateEmail,
      interviewer_email: interviewerEmail,
      interview_datetime: interviewDatetime,
      duration_minutes: durationMinutes,
      notes,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `Scheduling failed: ${res.status}`);
  }
  return res.json();
}

/**
 * HR: approve or reject a self-applied candidate, optionally sending them an email.
 * @param {string} candidateId  MongoDB _id
 * @param {string} status  'approved' | 'rejected'
 * @param {boolean} [sendEmail=true]
 */
export async function updateCandidateStatus(candidateId, status, sendEmail = true) {
  const res = await fetch(`${AGENT_URL}candidates/${candidateId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, send_email: sendEmail }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `Status update failed: ${res.status}`);
  }
  return res.json();
}

/**
 * HR: search internal employees for a role/skill match.
 * @param {string} query  Natural language role description
 */
export async function searchInternalTalent(query) {
  const res = await fetch(`${AGENT_URL}internal-search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `Internal search failed: ${res.status}`);
  }
  return res.json();
}
