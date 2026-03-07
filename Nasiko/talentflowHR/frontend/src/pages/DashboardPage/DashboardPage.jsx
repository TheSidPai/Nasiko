import { useEffect, useState } from "react";
import { sendToAgent, getCandidates, deleteCandidate, getEmployees, sendCandidateEmail, scheduleInterview, updateCandidateStatus } from "../../services/api";
import { RISK_CONFIG, RISK_ORDER } from "../../constants";
import styles from "./DashboardPage.module.css";

/** Compute risk level from raw employee metrics */
function computeRisk(emp) {
  const score =
    (emp.overtime_hrs_last_month / 60) * 35 +
    (emp.days_since_last_leave / 150) * 35 +
    (emp.open_tickets / 25) * 20 +
    (emp.last_appraisal_months_ago / 20) * 10;
  const s = Math.min(100, Math.round(score));
  if (s >= 75) return "Critical";
  if (s >= 50) return "High";
  if (s >= 28) return "Medium";
  return "Low";
}

/** Map MongoDB employee shape â†’ dashboard display shape */
function toDisplayEmp(e) {
  return {
    id: e.id,
    name: e.name,
    role: e.role,
    overtime: e.overtime_hrs_last_month ?? 0,
    daysSinceLeave: e.days_since_last_leave ?? 0,
    tickets: e.open_tickets ?? 0,
    appraisalMonths: e.last_appraisal_months_ago ?? 0,
    risk: computeRisk(e),
  };
}

function scoreOf(emp) {
  return Math.min(
    100,
    Math.round(
      (emp.overtime / 60) * 35 +
      (emp.daysSinceLeave / 150) * 35 +
      (emp.tickets / 25) * 20 +
      (emp.appraisalMonths / 20) * 10
    )
  );
}

const REC_COLORS = {
  Proceed: { color: "#4ff78c", bg: "rgba(79,247,140,0.1)" },
  Hold:    { color: "#f7c94f", bg: "rgba(247,201,79,0.1)" },
  Reject:  { color: "#f74f4f", bg: "rgba(247,79,79,0.1)" },
};

// ── EmailModal ────────────────────────────────────────────────────────────────

function EmailModal({ candidate, onClose, onSent }) {
  const [type, setType] = useState(candidate.recommendation === "Proceed" ? "offer" : "rejection");
  const [email, setEmail] = useState(candidate.email || "");
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);

  async function handleSend() {
    if (!email) { alert("Please enter a recipient email."); return; }
    setSending(true);
    setResult(null);
    try {
      const res = await sendCandidateEmail({
        candidateId: candidate._id,
        toEmail: email,
        emailType: type,
        candidateName: candidate.name,
        role: candidate.role_applied,
      });
      setResult(res);
      if (res.success) onSent(candidate._id);
    } catch (e) {
      setResult({ success: false, error: e.message });
    }
    setSending(false);
  }

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <span>📧 Send Email — {candidate.name}</span>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>
        <div className={styles.modalBody}>
          <label className={styles.modalLabel}>Email Type</label>
          <div className={styles.emailTypeRow}>
            {["offer", "rejection"].map(t => (
              <button
                key={t}
                className={`${styles.typeBtn} ${type === t ? styles.typeBtnActive : ""}`}
                style={type === t
                  ? { borderColor: t === "offer" ? "#4ff78c" : "#f74f4f", color: t === "offer" ? "#4ff78c" : "#f74f4f" }
                  : {}}
                onClick={() => setType(t)}
              >
                {t === "offer" ? "🎉 Offer" : "📭 Rejection"}
              </button>
            ))}
          </div>
          <label className={styles.modalLabel}>Recipient Email</label>
          <input
            className={styles.modalInput}
            type="email"
            placeholder="candidate@example.com"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />
          <div className={styles.templatePreview}>
            {type === "offer"
              ? `A congratulations email will be sent to ${candidate.name} for the ${candidate.role_applied} position.`
              : `A polite rejection email will be sent to ${candidate.name} for the ${candidate.role_applied} position.`}
          </div>
          {result && (
            <div className={styles.resultBanner} style={{ color: result.success ? "#4ff78c" : "#f74f4f" }}>
              {result.success ? `✅ ${result.message}` : `❌ ${result.error}`}
            </div>
          )}
          <button className={styles.sendBtn} onClick={handleSend} disabled={sending}>
            {sending ? "Sending..." : "📤 Send Email"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── CalendarModal ─────────────────────────────────────────────────────────────

function CalendarModal({ candidate, onClose }) {
  const tomorrow = new Date(Date.now() + 86400000);
  tomorrow.setHours(10, 0, 0, 0);
  const defaultDt = tomorrow.toISOString().slice(0, 16);

  const [interviewerEmail, setInterviewerEmail] = useState("");
  const [datetime, setDatetime] = useState(defaultDt);
  const [duration, setDuration] = useState(60);
  const [notes, setNotes] = useState("");
  const [scheduling, setScheduling] = useState(false);
  const [result, setResult] = useState(null);

  async function handleSchedule() {
    setScheduling(true);
    setResult(null);
    try {
      const res = await scheduleInterview({
        candidateName: candidate.name,
        role: candidate.role_applied,
        candidateEmail: candidate.email || "",
        interviewerEmail,
        interviewDatetime: datetime ? `${datetime}:00` : "",
        durationMinutes: duration,
        notes,
      });
      setResult(res);
    } catch (e) {
      setResult({ success: false, error: e.message });
    }
    setScheduling(false);
  }

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <span>📅 Schedule Interview — {candidate.name}</span>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>
        <div className={styles.modalBody}>
          <label className={styles.modalLabel}>Interview Date &amp; Time</label>
          <input
            className={styles.modalInput}
            type="datetime-local"
            value={datetime}
            onChange={e => setDatetime(e.target.value)}
          />
          <label className={styles.modalLabel}>Duration (minutes)</label>
          <select
            className={styles.modalInput}
            value={duration}
            onChange={e => setDuration(Number(e.target.value))}
          >
            {[30, 45, 60, 90, 120].map(d => (
              <option key={d} value={d}>{d} min</option>
            ))}
          </select>
          <label className={styles.modalLabel}>Interviewer Email (optional)</label>
          <input
            className={styles.modalInput}
            type="email"
            placeholder="interviewer@company.com"
            value={interviewerEmail}
            onChange={e => setInterviewerEmail(e.target.value)}
          />
          <label className={styles.modalLabel}>Notes (optional)</label>
          <textarea
            className={styles.modalInput}
            rows={3}
            placeholder="Topics to cover, preparation guidelines..."
            value={notes}
            onChange={e => setNotes(e.target.value)}
          />
          {result && (
            <div className={styles.resultBanner} style={{ color: result.success ? "#4ff78c" : "#f74f4f" }}>
              {result.success ? (
                <>
                  ✅ {result.message}
                  {result.calendar_url && (
                    <a href={result.calendar_url} target="_blank" rel="noreferrer" className={styles.calLink}>
                      &nbsp;📆 Open in Google Calendar
                    </a>
                  )}
                </>
              ) : `❌ ${result.error}`}
            </div>
          )}
          <button className={styles.sendBtn} onClick={handleSchedule} disabled={scheduling}>
            {scheduling ? "Scheduling..." : "📅 Schedule Interview"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [view, setView] = useState("burnout");

  // â”€â”€ Burnout state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const [employees, setEmployees] = useState([]);
  const [empLoading, setEmpLoading] = useState(true);
  const [empError, setEmpError]   = useState("");
  const [selected, setSelected]   = useState(null);
  const [aiInsight, setAiInsight] = useState("");
  const [loadingInsight, setLoadingInsight] = useState(false);

  // â”€â”€ Candidates state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  const [candidates, setCandidates] = useState([]);
  const [cFilter, setCFilter]       = useState("all");
  const [cLoading, setCLoading]     = useState(false);
  const [cError, setCError]         = useState("");

  // ── Modal state ────────────────────────────────────────────
  const [emailModal, setEmailModal] = useState(null);
  const [calModal, setCalModal]     = useState(null);
  // ── Attrition state ──────────────────────────────────────
  const [attritionText,    setAttritionText]    = useState("");
  const [attritionLoading, setAttritionLoading] = useState(false);

  // ── Meetings state ───────────────────────────────────────
  const [meetingsText,    setMeetingsText]    = useState("");
  const [meetingsLoading, setMeetingsLoading] = useState(false);
  const [meetingsDay,     setMeetingsDay]     = useState("");

  // ── Add Employee modal ───────────────────────────────────
  const [addEmpModal, setAddEmpModal] = useState(false);
  // Load employees from MongoDB on mount
  useEffect(() => {
    async function load() {
      setEmpLoading(true);
      setEmpError("");
      try {
        const data = await getEmployees();
        setEmployees(data.map(toDisplayEmp).sort(
          (a, b) => RISK_ORDER.indexOf(a.risk) - RISK_ORDER.indexOf(b.risk)
        ));
      } catch {
        setEmpError("Could not load employees from database. Is the backend running?");
      }
      setEmpLoading(false);
    }
    load();
  }, []);

  const counts = Object.fromEntries(
    RISK_ORDER.map((r) => [r, employees.filter((e) => e.risk === r).length])
  );

  async function getInsight(emp) {
    setSelected(emp);
    setAiInsight("");
    setLoadingInsight(true);
    try {
      const reply = await sendToAgent(
        `Flag burnout risk for ${emp.name} and suggest specific interventions.`
      );
      setAiInsight(reply);
    } catch {
      setAiInsight("âš ï¸ Could not reach the agent.");
    }
    setLoadingInsight(false);
  }

  async function loadCandidates(filter) {
    setCLoading(true);
    setCError("");
    try {
      // "pending" is a status filter, others are recommendation filters
      const rec    = (filter === "all" || filter === "pending") ? undefined : filter;
      const status = filter === "pending" ? "pending" : undefined;
      const data   = await getCandidates(rec, status);
      setCandidates(data);
    } catch {
      setCError("Could not load candidates. Is the backend running?");
    }
    setCLoading(false);
  }

  async function loadAttrition() {
    setAttritionText("");
    setAttritionLoading(true);
    try {
      const reply = await sendToAgent(
        "Predict attrition risk for all employees. Give me a full team report with risk scores, key signals, and concrete retention strategies for each person."
      );
      setAttritionText(reply);
    } catch {
      setAttritionText("⚠️ Could not load attrition data. Is the backend running on port 5000?");
    }
    setAttritionLoading(false);
  }

  async function loadMeetings(day) {
    setMeetingsDay(day);
    setMeetingsText("");
    setMeetingsLoading(true);
    try {
      const reply = await sendToAgent(`What meetings or interviews do I have scheduled for ${day}?`);
      setMeetingsText(reply);
    } catch {
      setMeetingsText("⚠️ Could not load meetings. Is the backend running on port 5000?");
    }
    setMeetingsLoading(false);
  }

  useEffect(() => {
    if (view === "candidates") loadCandidates(cFilter);
    if (view === "attrition")  loadAttrition();
  }, [view, cFilter]);

  async function handleDelete(id) {
    if (!window.confirm("Delete this candidate?")) return;
    try {
      await deleteCandidate(id);
      setCandidates((prev) => prev.filter((c) => c._id !== id));
    } catch {
      alert("Could not delete candidate.");
    }
  }

  function markEmailSent(candidateId) {
    setCandidates((prev) =>
      prev.map((c) => c._id === candidateId ? { ...c, email_sent: true } : c)
    );
  }

  // Approve or reject a self-applied candidate (sends email automatically)
  async function handleDecision(candidateId, decision) {
    const label = decision === "approved" ? "Approve" : "Reject";
    if (!window.confirm(`${label} this candidate and send them an email?`)) return;
    try {
      await updateCandidateStatus(candidateId, decision, true);
      setCandidates((prev) =>
        prev.map((c) => c._id === candidateId ? { ...c, status: decision, email_sent: true } : c)
      );
    } catch (e) {
      alert("Could not update status: " + e.message);
    }
  }

  return (
    <div className={styles.page}>
      {emailModal && (
        <EmailModal
          candidate={emailModal}
          onClose={() => setEmailModal(null)}
          onSent={(id) => { markEmailSent(id); }}
        />
      )}
      {calModal && (
        <CalendarModal
          candidate={calModal}
          onClose={() => setCalModal(null)}
        />
      )}
      {addEmpModal && (
        <AddEmployeeModal onClose={() => setAddEmpModal(false)} />
      )}
      <div className={styles.dashHeadRow}>
        <div>
          <h2 className={styles.heading}>HR Dashboard</h2>
          <p className={styles.subtitle}>
            Live burnout &amp; attrition risk · candidate pipeline · meetings — all AI-powered.
          </p>
        </div>
        <button className={styles.addEmpBtn} onClick={() => setAddEmpModal(true)}>
          ➕ Add Employee
        </button>
      </div>

      {/* View toggle */}
      <div className={styles.viewTabs}>
        <button
          className={`${styles.viewTab} ${view === "burnout" ? styles.viewTabActive : ""}`}
          onClick={() => setView("burnout")}
        >
          ðŸ”¥ Burnout Risk
        </button>
        <button
          className={`${styles.viewTab} ${view === "candidates" ? styles.viewTabActive : ""}`}
          onClick={() => setView("candidates")}
        >
          ðŸ‘¥ Candidates Pipeline
        </button>        <button
          className={`${styles.viewTab} ${view === "attrition" ? styles.viewTabActive : ""}`}
          onClick={() => setView("attrition")}
        >
          🚪 Attrition Risk
        </button>
        <button
          className={`${styles.viewTab} ${view === "meetings" ? styles.viewTabActive : ""}`}
          onClick={() => setView("meetings")}
        >
          📅 My Meetings
        </button>      </div>

      {/* â”€â”€ BURNOUT VIEW â”€â”€ */}
      {view === "burnout" && (
        <>
          {empLoading && <div className={styles.cEmpty}>Loading employees from database...</div>}
          {empError   && <div className={styles.cEmpty} style={{ color: "#f74f4f" }}>{empError}</div>}

          {!empLoading && !empError && (
            <>
              <div className={styles.summary}>
                {RISK_ORDER.map((r) => (
                  <div
                    key={r}
                    className={styles.summaryCard}
                    style={{ borderColor: `${RISK_CONFIG[r].color}33` }}
                  >
                    <div className={styles.summaryCount} style={{ color: RISK_CONFIG[r].color }}>
                      {counts[r] ?? 0}
                    </div>
                    <div className={styles.summaryLabel}>{r} Risk</div>
                  </div>
                ))}
              </div>

              <div className={`${styles.body} ${selected ? styles.bodyWithPanel : ""}`}>
                <div className={styles.list}>
                  {employees.map((emp) => {
                    const cfg = RISK_CONFIG[emp.risk];
                    const score = scoreOf(emp);
                    const active = selected?.id === emp.id;
                    return (
                      <div
                        key={emp.id}
                        className={styles.empCard}
                        style={{
                          background: active ? cfg.bg : undefined,
                          borderColor: active ? `${cfg.color}66` : undefined,
                        }}
                        onClick={() => getInsight(emp)}
                      >
                        <div
                          className={styles.avatar}
                          style={{ background: cfg.bg, border: `2px solid ${cfg.color}`, color: cfg.color }}
                        >
                          {emp.name.split(" ").map((n) => n[0]).join("")}
                        </div>
                        <div className={styles.empInfo}>
                          <div className={styles.empHeader}>
                            <span className={styles.empName}>{emp.name}</span>
                            <span className={styles.empBadge} style={{ color: cfg.color, background: cfg.bg }}>
                              {emp.risk}
                            </span>
                          </div>
                          <div className={styles.empRole}>{emp.role}</div>
                          <div className={styles.barTrack}>
                            <div className={styles.barFill} style={{ width: `${score}%`, background: cfg.bar }} />
                          </div>
                        </div>
                        <div className={styles.empScore} style={{ color: cfg.color }}>{score}</div>
                      </div>
                    );
                  })}
                </div>

                {selected && (
                  <div className={styles.panel} style={{ borderColor: `${RISK_CONFIG[selected.risk].color}44` }}>
                    <div className={styles.panelHeader}>
                      <div>
                        <div className={styles.panelName}>{selected.name}</div>
                        <div className={styles.panelRole}>{selected.role}</div>
                      </div>
                      <button className={styles.closeBtn} onClick={() => setSelected(null)}>âœ•</button>
                    </div>
                    <div className={styles.stats}>
                      {[
                        ["Overtime hrs", selected.overtime],
                        ["Days since leave", selected.daysSinceLeave],
                        ["Open tickets", selected.tickets],
                        ["Months since appraisal", selected.appraisalMonths],
                      ].map(([label, val]) => (
                        <div key={label} className={styles.stat}>
                          <div className={styles.statValue} style={{ color: RISK_CONFIG[selected.risk].color }}>{val}</div>
                          <div className={styles.statLabel}>{label}</div>
                        </div>
                      ))}
                    </div>
                    <div className={styles.aiLabel}>AI ASSESSMENT</div>
                    {loadingInsight ? (
                      <div className={styles.aiLoading}>Analyzing with TalentFlow...</div>
                    ) : aiInsight ? (
                      <div className={styles.aiContent}>{aiInsight}</div>
                    ) : (
                      <div className={styles.aiLoading}>Loading AI assessment...</div>
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </>
      )}

      {/* â”€â”€ CANDIDATES VIEW â”€â”€ */}
      {view === "candidates" && (
        <div>
          <div className={styles.cFilterBar}>
            {["all", "pending", "Proceed", "Hold", "Reject"].map((f) => (
              <button
                key={f}
                className={`${styles.cFilterBtn} ${cFilter === f ? styles.cFilterActive : ""}`}
                onClick={() => setCFilter(f)}
              >
                {f === "all" ? "All" : f === "pending" ? "🕐 Pending Review" : f}
              </button>
            ))}
            <button className={styles.cRefreshBtn} onClick={() => loadCandidates(cFilter)}>â†» Refresh</button>
          </div>

          {cLoading && <div className={styles.cEmpty}>Loading candidates...</div>}
          {cError   && <div className={styles.cEmpty} style={{ color: "#f74f4f" }}>{cError}</div>}

          {!cLoading && !cError && candidates.length === 0 && (
            <div className={styles.cEmpty}>
              No candidates yet. Screen a resume on the Resume Analyzer page and click "Save to Database".
            </div>
          )}

          {!cLoading && candidates.length > 0 && (
            <div className={styles.cGrid}>
              {candidates.map((c) => {
                const cfg = REC_COLORS[c.recommendation] ?? REC_COLORS.Hold;
                return (
                  <div key={c._id} className={styles.cCard}>
                    <div className={styles.cCardHeader}>
                      <div className={styles.cName}>{c.name}</div>
                      <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                        {c.applicant_type === "self_applied" && (
                          <span className={styles.cBadge} style={{ color: "#a78bfa", background: "rgba(167,139,250,0.1)", fontSize: "11px" }}>
                            Self-applied
                          </span>
                        )}
                        {c.status === "pending" && (
                          <span className={styles.cBadge} style={{ color: "#f7c94f", background: "rgba(247,201,79,0.1)", fontSize: "11px" }}>
                            ⏳ Pending
                          </span>
                        )}
                        {c.status === "approved" && (
                          <span className={styles.cBadge} style={{ color: "#4ff78c", background: "rgba(79,247,140,0.08)", fontSize: "11px" }}>
                            ✅ Approved
                          </span>
                        )}
                        {c.status === "rejected" && (
                          <span className={styles.cBadge} style={{ color: "#f74f4f", background: "rgba(247,79,79,0.08)", fontSize: "11px" }}>
                            ❌ Rejected
                          </span>
                        )}
                        <span className={styles.cBadge} style={{ color: cfg.color, background: cfg.bg }}>
                          {c.recommendation}
                        </span>
                      </div>
                    </div>
                    <div className={styles.cRole}>{c.role_applied}</div>
                    <div className={styles.cScoreRow}>
                      <span className={styles.cScoreLabel}>Fit Score</span>
                      <span className={styles.cScore} style={{ color: cfg.color }}>{c.fit_score}/100</span>
                    </div>
                    <div className={styles.cSummary}>{c.resume_summary}</div>
                    <div className={styles.cMeta}>
                      {c.email && <span>✉ {c.email}</span>}
                      <span>{c.email_sent ? "📧 Email sent" : "📭 No email sent"}</span>
                      <span style={{ color: "var(--muted)", fontSize: "0.75rem" }}>
                        {new Date(c.submitted_at).toLocaleDateString()}
                      </span>
                    </div>
                    {/* ── Action buttons ── */}
                    <div className={styles.cActions}>
                      {/* HR Decision — for self-applied candidates pending review */}
                      {c.applicant_type === "self_applied" && c.status === "pending" && (
                        <>
                          <button
                            className={styles.cActionBtn}
                            style={{ borderColor: "#4ff78c", color: "#4ff78c" }}
                            onClick={() => handleDecision(c._id, "approved")}
                          >
                            ✅ Approve
                          </button>
                          <button
                            className={styles.cActionBtn}
                            style={{ borderColor: "#f74f4f", color: "#f74f4f" }}
                            onClick={() => handleDecision(c._id, "rejected")}
                          >
                            ❌ Reject
                          </button>
                        </>
                      )}
                      {/* Standard actions */}
                      <button
                        className={styles.cActionBtn}
                        style={{ borderColor: "#6c63ff", color: "#6c63ff" }}
                        onClick={() => setEmailModal(c)}
                        title="Send offer or rejection email"
                      >
                        📧 Send Email
                      </button>
                      <button
                        className={styles.cActionBtn}
                        style={{ borderColor: "#4ecdc4", color: "#4ecdc4" }}
                        onClick={() => setCalModal(c)}
                        title="Schedule interview on Google Calendar"
                      >
                        📅 Schedule
                      </button>
                      <button className={styles.cDelete} onClick={() => handleDelete(c._id)}>🗑</button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* ── ATTRITION RISK VIEW ── */}
      {view === "attrition" && (
        <div>
          <div className={styles.attrHeader}>
            <p className={styles.attrSubtitle}>
              AI flight-risk prediction based on tenure, workload, appraisal patterns and leave engagement signals.
            </p>
            <button className={styles.cRefreshBtn} onClick={loadAttrition}>↻ Refresh</button>
          </div>
          {attritionLoading && <div className={styles.cEmpty}>Analysing attrition signals for all employees…</div>}
          {!attritionLoading && attritionText && (
            <div className={styles.attrResult}>{attritionText}</div>
          )}
          {!attritionLoading && !attritionText && (
            <div className={styles.cEmpty}>Loading attrition risk analysis…</div>
          )}
        </div>
      )}

      {/* ── MEETINGS VIEW ── */}
      {view === "meetings" && (
        <div>
          <p className={styles.subtitle} style={{ marginBottom: "1.25rem" }}>
            Fetch today or tomorrow’s scheduled interviews and meetings from Google Calendar.
          </p>
          <div className={styles.meetBtns}>
            <button
              className={`${styles.viewTab} ${meetingsDay === "today" ? styles.viewTabActive : ""}`}
              onClick={() => loadMeetings("today")}
            >
              📅 Today
            </button>
            <button
              className={`${styles.viewTab} ${meetingsDay === "tomorrow" ? styles.viewTabActive : ""}`}
              onClick={() => loadMeetings("tomorrow")}
            >
              📆 Tomorrow
            </button>
          </div>
          {meetingsLoading && <div className={styles.cEmpty}>Fetching meetings…</div>}
          {!meetingsLoading && meetingsText && (
            <div className={styles.attrResult}>{meetingsText}</div>
          )}
          {!meetingsLoading && !meetingsText && !meetingsDay && (
            <div className={styles.cEmpty}>Select Today or Tomorrow to see your schedule.</div>
          )}
        </div>
      )}
    </div>
  );
}
