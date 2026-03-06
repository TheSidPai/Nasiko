import { useRef, useState } from "react";
import { uploadPDF, storeCandidate } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { sendToAgent } from "../../services/api";
import styles from "./ApplyPage.module.css";

function parseResult(text) {
  const scoreMatch = text.match(/Fit\s*Score[:\s#*]+(\d+)/i);
  const fitScore = scoreMatch ? parseInt(scoreMatch[1]) : null;
  const recMatch = text.match(/\b(Proceed|Hold|Reject)\b/i);
  const recommendation = recMatch
    ? recMatch[1].charAt(0).toUpperCase() + recMatch[1].slice(1).toLowerCase()
    : fitScore !== null
      ? fitScore >= 70 ? "Proceed" : fitScore >= 45 ? "Hold" : "Reject"
      : "Hold";
  const summary = text.replace(/[#*`]/g, "").slice(0, 400);
  return { fitScore, recommendation, summary };
}

export default function ApplyPage() {
  const { auth } = useAuth();
  const [roleApplied, setRoleApplied]     = useState("");
  const [pdfFileName, setPdfFileName]     = useState("");
  const [resumeText, setResumeText]       = useState("");
  const [pdfUploading, setPdfUploading]   = useState(false);
  const [submitting, setSubmitting]       = useState(false);
  const [stage, setStage]                 = useState("form"); // 'form' | 'processing' | 'done' | 'error'
  const [errMsg, setErrMsg]               = useState("");
  const [fitScore, setFitScore]           = useState(null);
  const fileInputRef = useRef(null);

  async function handlePdfUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setPdfUploading(true);
    setPdfFileName(file.name);
    try {
      const text = await uploadPDF(file);
      setResumeText(text);
    } catch (err) {
      alert("Could not extract PDF: " + err.message);
      setPdfFileName("");
    }
    setPdfUploading(false);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!resumeText) { setErrMsg("Please upload your CV before submitting."); return; }
    if (!roleApplied.trim()) { setErrMsg("Please specify the role you're applying for."); return; }
    setErrMsg("");
    setSubmitting(true);
    setStage("processing");

    try {
      // 1. AI screens the resume
      const prompt = `Screen this resume for the following job role and provide a structured report with a Fit Score out of 100 and a recommendation (Proceed / Hold / Reject).

ROLE APPLIED FOR: ${roleApplied}

RESUME:
${resumeText}`;

      const aiReport = await sendToAgent(prompt);
      const parsed   = parseResult(aiReport);
      setFitScore(parsed.fitScore);

      // 2. Save to DB with status "pending" — HR will review it
      await storeCandidate({
        name:           auth.name,
        email:          auth.email,
        role_applied:   roleApplied.trim(),
        fit_score:      parsed.fitScore ?? 50,
        recommendation: parsed.recommendation,
        resume_summary: parsed.summary,
        status:         "pending",        // HR must approve / reject
        applicant_type: "self_applied",   // submitted by candidate themselves
      });

      setStage("done");
    } catch (err) {
      setErrMsg("Something went wrong: " + err.message);
      setStage("form");
    }
    setSubmitting(false);
  }

  // ── Done screen ────────────────────────────────────────────────────────────
  if (stage === "done") {
    return (
      <div className={styles.page}>
        <div className={styles.doneCard}>
          <div className={styles.doneIcon}>🎉</div>
          <h2 className={styles.doneTitle}>Application Submitted!</h2>
          <p className={styles.doneSub}>
            Your CV has been analysed and your application for <strong>{roleApplied}</strong> has been
            sent to the HR team for review.
          </p>
          {fitScore !== null && (
            <div className={styles.scoreHint}>
              Your profile matched the role at <strong>{fitScore}%</strong>.
            </div>
          )}
          <p className={styles.doneNote}>
            📧 You will receive an email at <strong>{auth.email}</strong> once the HR team has reviewed
            your application. This usually takes 2–3 business days.
          </p>
          <button
            className={styles.applyAgainBtn}
            onClick={() => {
              setStage("form");
              setRoleApplied("");
              setPdfFileName("");
              setResumeText("");
              setFitScore(null);
            }}
          >
            Apply for Another Role
          </button>
        </div>
      </div>
    );
  }

  // ── Processing screen ──────────────────────────────────────────────────────
  if (stage === "processing") {
    return (
      <div className={styles.page}>
        <div className={styles.processingCard}>
          <div className={styles.spinner} />
          <h3 className={styles.processingTitle}>Analysing your CV…</h3>
          <p className={styles.processingSub}>Our AI is reviewing your resume. This takes a few seconds.</p>
        </div>
      </div>
    );
  }

  // ── Main form ──────────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Apply for a Position</h1>
        <p className={styles.sub}>
          Upload your CV and tell us which role you're applying for. Our AI will analyse your fit
          instantly — you'll hear back via email once the HR team reviews your application.
        </p>
      </div>

      <form className={styles.form} onSubmit={handleSubmit}>
        {/* Role input */}
        <div className={styles.field}>
          <label className={styles.label}>Role You're Applying For <span className={styles.req}>*</span></label>
          <input
            className={styles.input}
            type="text"
            placeholder="e.g. Senior Software Engineer, Data Analyst, Product Manager…"
            value={roleApplied}
            onChange={e => setRoleApplied(e.target.value)}
          />
        </div>

        {/* CV upload */}
        <div className={styles.field}>
          <label className={styles.label}>Upload Your CV (PDF) <span className={styles.req}>*</span></label>
          <div
            className={`${styles.dropZone} ${pdfFileName ? styles.dropZoneLoaded : ""}`}
            onClick={() => fileInputRef.current?.click()}
          >
            {pdfUploading ? (
              <span className={styles.dzText}>Extracting text…</span>
            ) : pdfFileName ? (
              <>
                <span className={styles.dzIcon}>✅</span>
                <span className={styles.dzFile}>{pdfFileName}</span>
                <span className={styles.dzChange}>Click to change</span>
              </>
            ) : (
              <>
                <span className={styles.dzIcon}>📄</span>
                <span className={styles.dzText}>Click to upload your PDF CV</span>
                <span className={styles.dzHint}>Only PDF files are supported</span>
              </>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              style={{ display: "none" }}
              onChange={handlePdfUpload}
            />
          </div>
        </div>

        {/* Applying as */}
        <div className={styles.applyingAs}>
          Applying as: <strong>{auth?.name}</strong> ({auth?.email})
        </div>

        {errMsg && <div className={styles.err}>{errMsg}</div>}

        <button
          className={styles.submitBtn}
          type="submit"
          disabled={submitting || pdfUploading || !resumeText}
        >
          {submitting ? "Submitting…" : "Submit Application →"}
        </button>
      </form>
    </div>
  );
}
