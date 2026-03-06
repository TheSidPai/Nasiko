import { useRef, useState } from "react";
import { sendToAgent, uploadPDF, storeCandidate } from "../../services/api";
import { RESUME_MODES } from "../../constants";
import styles from "./ResumePage.module.css";

export default function ResumePage() {
  const [resume, setResume] = useState("");
  const [jd, setJd] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("screen");
  const [pdfUploading, setPdfUploading] = useState(false);
  const [pdfFileName, setPdfFileName] = useState("");
  const [saveStatus, setSaveStatus] = useState(""); // '', 'saving', 'saved', 'error'
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
    setSaveStatus("");

    const prompts = {
      screen: `Screen this resume against the job description and provide a full structured report.\n\nRESUME:\n${resume}\n\nJOB DESCRIPTION:\n${jd}`,
      questions: `Generate tailored interview questions for this candidate.\n\nRESUME:\n${resume}\n\nJOB DESCRIPTION:\n${jd}`,
      email: `Draft a professional offer email for the candidate based on this resume and JD.\n\nRESUME:\n${resume}\n\nJOB DESCRIPTION:\n${jd}`,
    };

    try {
      const reply = await sendToAgent(prompts[mode]);
      setResult(reply);
    } catch {
      setResult("⚠️ Could not reach the agent. Make sure the backend is running on port 5000.");
    }
    setLoading(false);
  }

  async function saveCandidate() {
    if (!result) return;
    setSaveStatus("saving");
    // Extract a basic fit_score from the result text
    const scoreMatch = result.match(/Fit Score[:\s]+(\d+)/i);
    const fitScore = scoreMatch ? parseInt(scoreMatch[1]) : 50;
    const recMatch = result.match(/\b(Proceed|Hold|Reject)\b/i);
    const recommendation = recMatch ? recMatch[1] : "Hold";
    // Use first 300 chars of result as summary
    const summary = result.replace(/[#*`]/g, "").slice(0, 300);

    try {
      await storeCandidate({
        name: "Candidate (from Resume Page)",
        role_applied: jd.slice(0, 60) + "...",
        fit_score: fitScore,
        recommendation,
        resume_summary: summary,
        email: "",
      });
      setSaveStatus("saved");
    } catch {
      setSaveStatus("error");
    }
  }

  const activeLabel = RESUME_MODES.find((m) => m.id === mode)?.label ?? "";
  const canRun = resume.trim() && jd.trim() && !loading;

  return (
    <div className={styles.page}>
      <h2 className={styles.heading}>Resume Analyzer</h2>
      <p className={styles.subtitle}>
        Upload a PDF or paste text — screen resumes, generate interview questions, or draft emails.
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
          {pdfUploading ? "Extracting..." : "📄 Upload Resume PDF"}
        </button>
        {pdfFileName && (
          <span className={styles.pdfName}>
            {pdfUploading ? `Reading ${pdfFileName}…` : `✅ ${pdfFileName}`}
          </span>
        )}
      </div>

      {/* Text areas */}
      <div className={styles.grid}>
        {[
          { label: "RESUME",          value: resume, setter: setResume, ph: "Paste candidate resume here — or upload a PDF above..." },
          { label: "JOB DESCRIPTION", value: jd,     setter: setJd,     ph: "Paste job description here..." },
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
        {loading ? "Analyzing..." : `${activeLabel} →`}
      </button>

      {result && (
        <div className={styles.result}>
          <div className={styles.resultLabel}>AGENT RESPONSE</div>
          <div className={styles.resultBody}>{result}</div>

          {mode === "screen" && (
            <div className={styles.saveRow}>
              <button
                className={styles.saveBtn}
                onClick={saveCandidate}
                disabled={saveStatus === "saving" || saveStatus === "saved"}
              >
                {saveStatus === "saving" && "Saving…"}
                {saveStatus === "saved" && "✅ Saved to Database"}
                {saveStatus === "error" && "⚠️ Save Failed"}
                {saveStatus === "" && "💾 Save Candidate to Database"}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
