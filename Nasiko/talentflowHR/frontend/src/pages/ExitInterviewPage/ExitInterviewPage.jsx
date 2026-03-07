import { useState } from "react";
import { sendToAgent } from "../../services/api";
import styles from "./ExitInterviewPage.module.css";

const EXAMPLE_TRANSCRIPT = `Interviewer: Why have you decided to leave?
Employee: Honestly, I felt my growth had stalled. I've been in the same role for over two years and despite performing well in reviews, there was no promotion conversation.

Interviewer: How was your relationship with your manager?
Employee: It was okay, but I felt like my manager was too hands-off. I needed more mentorship and feedback and rarely got it.

Interviewer: Would you recommend the company to others?
Employee: Maybe. The team is great and the culture is collaborative. But career growth transparency needs work.`;

export default function ExitInterviewPage() {
  const [transcript,    setTranscript]    = useState("");
  const [employeeRole,  setEmployeeRole]  = useState("");
  const [loading,       setLoading]       = useState(false);
  const [result,        setResult]        = useState("");
  const [error,         setError]         = useState("");

  async function handleAnalyze(e) {
    e.preventDefault();
    if (!transcript.trim()) return;
    setLoading(true);
    setResult("");
    setError("");

    const roleClause = employeeRole.trim() ? `\nEmployee Role: ${employeeRole.trim()}\n` : "";
    const prompt = `Analyze this exit interview transcript and give me a structured report with sentiment, primary resignation reasons, team risk flags, and recommended HR actions.${roleClause}\n\nEXIT INTERVIEW TRANSCRIPT:\n${transcript.trim()}`;

    try {
      const reply = await sendToAgent(prompt);
      setResult(reply);
    } catch (err) {
      setError("Could not reach the agent: " + err.message);
    }
    setLoading(false);
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>🚪 Exit Interview Analyzer</h1>
        <p className={styles.sub}>
          Paste an exit interview transcript and let AI surface the real resignation
          reasons, flag systemic risks, and give you concrete retention actions for
          the rest of the team.
        </p>
      </div>

      <form className={styles.form} onSubmit={handleAnalyze}>
        <div className={styles.fieldGroup}>
          <label className={styles.label}>
            Employee Role
            <span className={styles.optional}> (optional)</span>
          </label>
          <input
            className={styles.input}
            type="text"
            placeholder="e.g. Senior Backend Engineer, Product Manager…"
            value={employeeRole}
            onChange={e => setEmployeeRole(e.target.value)}
          />
        </div>

        <div className={styles.fieldGroup}>
          <label className={styles.label}>Exit Interview Transcript *</label>
          <textarea
            className={styles.textarea}
            rows={14}
            placeholder="Paste the full exit interview notes or conversation here…"
            value={transcript}
            onChange={e => setTranscript(e.target.value)}
            required
          />
          {!transcript && (
            <button
              type="button"
              className={styles.exampleBtn}
              onClick={() => setTranscript(EXAMPLE_TRANSCRIPT)}
            >
              📋 Load example transcript
            </button>
          )}
        </div>

        <button
          className={styles.analyzeBtn}
          type="submit"
          disabled={loading || !transcript.trim()}
        >
          {loading ? "Analysing…" : "Analyse Exit Interview →"}
        </button>
      </form>

      {error && <div className={styles.err}>{error}</div>}

      {loading && (
        <div className={styles.loadingWrap}>
          <div className={styles.spinner} />
          <p className={styles.loadingText}>Extracting insights from the interview…</p>
        </div>
      )}

      {!loading && result && (
        <div className={styles.resultBox}>
          <div className={styles.resultLabel}>EXIT INTERVIEW ANALYSIS</div>
          <div className={styles.resultText}>{result}</div>
        </div>
      )}
    </div>
  );
}
