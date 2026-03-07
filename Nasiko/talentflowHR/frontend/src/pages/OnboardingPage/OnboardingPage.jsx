import { useState } from "react";
import { sendToAgent } from "../../services/api";
import styles from "./OnboardingPage.module.css";

const ROLE_EXAMPLES = [
  "Backend Engineer",
  "Product Manager",
  "Data Scientist",
  "Frontend Developer",
  "DevOps Engineer",
  "HR Business Partner",
];

export default function OnboardingPage() {
  const [role,       setRole]       = useState("");
  const [startDate,  setStartDate]  = useState("");
  const [department, setDepartment] = useState("");
  const [loading,    setLoading]    = useState(false);
  const [result,     setResult]     = useState("");
  const [error,      setError]      = useState("");

  async function handleGenerate(e) {
    e.preventDefault();
    if (!role.trim() || !startDate) return;
    setLoading(true);
    setResult("");
    setError("");

    const deptClause = department.trim() ? ` in the ${department.trim()} department` : "";
    const prompt = `Generate a detailed day-by-day onboarding plan for a new ${role.trim()} joining on ${startDate}${deptClause}. Include Day 1, Days 2-3, Week 1 check-in, Week 2-4 ramp-up, and 30/60/90-day milestones.`;

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
        <h1 className={styles.title}>🗓 Onboarding Planner</h1>
        <p className={styles.sub}>
          Generate a personalised day-by-day onboarding plan for a new hire — covering
          Day 1 orientation, role immersion, and 30/60/90-day milestones.
        </p>
      </div>

      <form className={styles.form} onSubmit={handleGenerate}>
        <div className={styles.fieldGroup}>
          <label className={styles.label}>Role / Job Title *</label>
          <input
            className={styles.input}
            type="text"
            placeholder="e.g. Senior ML Engineer, Product Manager…"
            value={role}
            onChange={e => setRole(e.target.value)}
            required
          />
          <div className={styles.examples}>
            {ROLE_EXAMPLES.map(r => (
              <button
                key={r}
                type="button"
                className={styles.pill}
                onClick={() => setRole(r)}
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        <div className={styles.row}>
          <div className={styles.fieldGroup}>
            <label className={styles.label}>Joining Date *</label>
            <input
              className={styles.input}
              type="date"
              value={startDate}
              onChange={e => setStartDate(e.target.value)}
              required
            />
          </div>
          <div className={styles.fieldGroup}>
            <label className={styles.label}>Department <span className={styles.optional}>(optional)</span></label>
            <input
              className={styles.input}
              type="text"
              placeholder="e.g. Engineering, HR, Analytics…"
              value={department}
              onChange={e => setDepartment(e.target.value)}
            />
          </div>
        </div>

        <button
          className={styles.generateBtn}
          type="submit"
          disabled={loading || !role.trim() || !startDate}
        >
          {loading ? "Generating plan…" : "Generate Onboarding Plan →"}
        </button>
      </form>

      {error && <div className={styles.err}>{error}</div>}

      {loading && (
        <div className={styles.loadingWrap}>
          <div className={styles.spinner} />
          <p className={styles.loadingText}>Building a personalised plan…</p>
        </div>
      )}

      {!loading && result && (
        <div className={styles.resultBox}>
          <div className={styles.resultLabel}>ONBOARDING PLAN</div>
          <div className={styles.resultText}>{result}</div>
        </div>
      )}
    </div>
  );
}
