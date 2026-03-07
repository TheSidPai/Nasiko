import { useRef, useState } from "react";
import { sendToAgent, uploadPDF, storeCandidate, sendCandidateEmail } from "../../services/api";
import { RESUME_MODES } from "../../constants";
import styles from "./ResumePage.module.css";

const FIT_THRESHOLD_PROCEED = 70;  // >= 70 â†’ Proceed
const FIT_THRESHOLD_HOLD    = 45;  // 45â€“69 â†’ Hold, < 45 â†’ Reject

function parseResult(text) {
  const scoreMatch = text.match(/Fit\s*Score[:\s#*]+(\d+)/i);
  const fitScore = scoreMatch ? parseInt(scoreMatch[1]) : null;
  const recMatch = text.match(/\b(Proceed|Hold|Reject)\b/i);
  const recommendation = recMatch
    ? recMatch[1].charAt(0).toUpperCase() + recMatch[1].slice(1).toLowerCase().replace("proceed","Proceed").replace("hold","Hold").replace("reject","Reject")
    : fitScore !== null
      ? fitScore >= FIT_THRESHOLD_PROCEED ? "Proceed" : fitScore >= FIT_THRESHOLD_HOLD ? "Hold" : "Reject"
      : "Hold";
  const summary = text.replace(/[#*`]/g, "").slice(0, 300);
  return { fitScore, recommendation, summary };
}

const REC_STYLE = {
  Proceed: { color: "#4ff78c", bg: "rgba(79,247,140,0.12)", label: "âœ… PROCEED" },
  Hold:    { color: "#f7c94f", bg: "rgba(247,201,79,0.12)",  label: "â¸ HOLD"    },
  Reject:  { color: "#f74f4f", bg: "rgba(247,79,79,0.12)",   label: "âŒ REJECT"  },
};

export default function ResumePage() {
  const [resume, setResume] = useState("");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("screen");
  const [pdfUploading, setPdfUploading] = useState(false);
  const [pdfFileName, setPdfFileName] = useState("");

  // Action panel state (shown after screening)
  const [parsed, setParsed]             = useState(null);   // { fitScore, recommendation, summary }
  const [candName, setCandName]         = useState("");
  const [candEmail, setCandEmail]       = useState("");
  const [actionStatus, setActionStatus] = useState("");     // '' | 'saving' | 'done' | 'error'
  const [actionMsg, setActionMsg]       = useState("");
  const [savedId, setSavedId]           = useState(null);

  const fileInputRef = useRef(null);

  async function handlePdfUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setPdfUploading(true);
    setPdfFileName(file.name);
    try {
      const text = await uploadPDF(file);
      setResume(text);
    } catch (err) {
      alert("Could not extract PDF: " + err.message);
      setPdfFileName("");
    }
    setPdfUploading(false);
  }

  async function run() {
    if (!resume.trim() || !jd.trim()) return;
    setLoading(true);
    setResult("");
    setParsed(null);
    setActionStatus("");
    setActionMsg("");
    setSavedId(null);

    const prompts = {
      screen:    `Screen this resume against the job description and provide a full structured report.\n\nRESUME:\n${resume}\n\nJOB DESCRIPTION:\n${jd}`,
      questions: `Generate tailored interview questions for this candidate.\n\nRESUME:\n${resume}\n\nJOB DESCRIPTION:\n${jd}`,
      email:     `Draft a professional offer email for the candidate based on this resume and JD.\n\nRESUME:\n${resume}\n\nJOB DESCRIPTION:\n${jd}`,
    };

    try {
      const reply = await sendToAgent(prompts[mode]);
      setResult(reply);
      if (mode === "screen") {
        const p = parseResult(reply);
        setParsed(p);
        // Auto-save to DB immediately
        await autoSave(p);
      }
    } catch {
      setResult("âš ï¸ Could not reach the agent. Make sure the backend is running on port 5000.");
    }
    setLoading(false);
  }

  async function autoSave(p) {
    try {
      const res = await storeCandidate({
        name: candName || "Pending Name",
        role_applied: jd.slice(0, 80),
        fit_score: p.fitScore ?? 50,
        recommendation: p.recommendation,
        resume_summary: p.summary,
        email: candEmail || "",
      });
      setSavedId(res?.id || null);
    } catch {
      // silent â€” HR can still act via the action panel
    }
  }

  async function handleAction(sendEmail) {
    if (!parsed) return;
    setActionStatus("saving");

    const name  = candName.trim()  || "Candidate";
    const email = candEmail.trim();
    const role  = jd.slice(0, 80);

    try {
      // Save/update candidate with real name + email
      const saveRes = await storeCandidate({
        name,
        role_applied: role,
        fit_score: parsed.fitScore ?? 50,
        recommendation: parsed.recommendation,
        resume_summary: parsed.summary,
        email,
      });
      const id = saveRes?.id || savedId || "";

      if (sendEmail && email) {
        const emailType = parsed.recommendation === "Proceed" ? "offer" : "rejection";
        const emailRes = await sendCandidateEmail({
          candidateId: id,
          toEmail: email,
          emailType,
          candidateName: name,
          role,
        });
        if (emailRes.success) {
          setActionMsg(`âœ… Saved to database & ${emailType} email sent to ${email}`);
        } else {
          setActionMsg(`âœ… Saved to database. âš ï¸ Email failed: ${emailRes.error}`);
        }
      } else {
        setActionMsg(`âœ… Saved to database${sendEmail && !email ? " (no email â€” recipient address missing)" : ""}`);
      }
      setActionStatus("done");
    } catch (e) {
      setActionStatus("error");
      setActionMsg("âš ï¸ Failed: " + e.message);
    }
  }

  const activeLabel = RESUME_MODES.find((m) => m.id === mode)?.label ?? "";
  const canRun = resume.trim() && jd.trim() && !loading;

  return (
    <div className={styles.page}>
      <h2 className={styles.heading}>Resume Analyzer</h2>
      <p className={styles.subtitle}>
        Upload a candidate's CV â€” AI screens it, scores it, and you confirm with one click to save &amp; email.
      </p>

      {/* Mode tabs */}
      <div className={styles.tabs}>
        {RESUME_MODES.map((m) => (
          <button
            key={m.id}
            className={`${styles.tab} ${mode === m.id ? styles.tabActive : ""}`}
            onClick={() => setMode(m.id)}
          >
            {m.label}
          </button>
        ))}
      </div>

      {/* PDF Upload */}
      <div className={styles.pdfRow}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          style={{ display: "none" }}
          onChange={handlePdfUpload}
        />
        <button
          className={styles.pdfBtn}
          onClick={() => fileInputRef.current?.click()}
          disabled={pdfUploading}
        >
          {pdfUploading ? "Extracting..." : "ðŸ“„ Upload Candidate CV (PDF)"}
        </button>
        {pdfFileName && (
          <span className={styles.pdfName}>
            {pdfUploading ? `Reading ${pdfFileName}â€¦` : `âœ… ${pdfFileName}`}
          </span>
        )}
      </div>

      {/* Text areas */}
      <div className={styles.grid}>
        {[
          { label: "CANDIDATE RESUME",  value: resume, setter: setResume, ph: "Paste candidate resume here â€” or upload a PDF above..." },
          { label: "JOB DESCRIPTION",   value: jd,     setter: setJd,     ph: "Paste job description here..." },
        ].map(({ label, value, setter, ph }) => (
          <div key={label}>
            <div className={styles.label}>{label}</div>
            <textarea
              className={styles.textarea}
              value={value}
              onChange={(e) => setter(e.target.value)}
              placeholder={ph}
              rows={12}
            />
          </div>
        ))}
      </div>

      <button className={styles.runBtn} onClick={run} disabled={!canRun}>
        {loading ? "Analyzing..." : `${activeLabel} â†’`}
      </button>

      {result && (
        <div className={styles.result}>
          <div className={styles.resultLabel}>AGENT RESPONSE</div>
          <div className={styles.resultBody}>{result}</div>

          {/* â”€â”€ Smart Action Panel (screening mode only) â”€â”€ */}
          {mode === "screen" && parsed && actionStatus !== "done" && (
            <div className={styles.actionPanel}>
              {/* Score + recommendation */}
              <div className={styles.actionHeader}>
                <div className={styles.scoreBox}>
                  <span className={styles.scoreNum} style={{ color: REC_STYLE[parsed.recommendation]?.color }}>
                    {parsed.fitScore !== null ? `${parsed.fitScore}/100` : "â€”"}
                  </span>
                  <span className={styles.scoreLabel}>Fit Score</span>
                </div>
                <div
                  className={styles.recBadge}
                  style={{
                    color: REC_STYLE[parsed.recommendation]?.color,
                    background: REC_STYLE[parsed.recommendation]?.bg,
                  }}
                >
                  {REC_STYLE[parsed.recommendation]?.label}
                </div>
              </div>

              <p className={styles.actionHint}>
                {parsed.recommendation === "Proceed"
                  ? "Candidate meets the bar. Fill in details below and confirm to save & send offer email."
                  : parsed.recommendation === "Reject"
                  ? "Candidate does not meet the bar. Save and optionally send a polite rejection."
                  : "Candidate is borderline. Save for review and optionally notify them."}
              </p>

              {/* Candidate details */}
              <div className={styles.actionFields}>
                <input
                  className={styles.actionInput}
                  type="text"
                  placeholder="Candidate full name *"
                  value={candName}
                  onChange={e => setCandName(e.target.value)}
                />
                <input
                  className={styles.actionInput}
                  type="email"
                  placeholder="Candidate email address (for sending email)"
                  value={candEmail}
                  onChange={e => setCandEmail(e.target.value)}
                />
              </div>

              {/* Action buttons */}
              <div className={styles.actionBtns}>
                <button
                  className={styles.actionBtnPrimary}
                  style={{
                    background: parsed.recommendation === "Proceed"
                      ? "linear-gradient(135deg,#4ff78c,#00c9a7)"
                      : "linear-gradient(135deg,#f74f4f,#c0392b)",
                  }}
                  onClick={() => handleAction(true)}
                  disabled={actionStatus === "saving" || !candName.trim()}
                >
                  {actionStatus === "saving"
                    ? "Processingâ€¦"
                    : parsed.recommendation === "Proceed"
                    ? "ðŸ’¾ Save & Send Offer Email"
                    : "ðŸ’¾ Save & Send Rejection Email"}
                </button>
                <button
                  className={styles.actionBtnSecondary}
                  onClick={() => handleAction(false)}
                  disabled={actionStatus === "saving" || !candName.trim()}
                >
                  {actionStatus === "saving" ? "â€¦" : "ðŸ“ Save Only (No Email)"}
                </button>
              </div>

              {!candName.trim() && (
                <p className={styles.actionWarning}>* Enter candidate name to continue</p>
              )}
            </div>
          )}

          {actionStatus === "done" && (
            <div className={styles.actionDone}>
              {actionMsg}
            </div>
          )}
          {actionStatus === "error" && (
            <div className={styles.actionDone} style={{ color: "#f74f4f" }}>
              {actionMsg}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
