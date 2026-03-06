import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import styles from "./LoginPage.module.css";

const HR_ACCESS_CODE = "tf2026";

export default function LoginPage() {
  const { login } = useAuth();
  const [view, setView] = useState("choose"); // 'choose' | 'candidate' | 'hr'

  // Candidate fields
  const [candName, setCandName]   = useState("");
  const [candEmail, setCandEmail] = useState("");
  const [candErr, setCandErr]     = useState("");

  // HR fields
  const [hrCode, setHrCode]   = useState("");
  const [hrName, setHrName]   = useState("");
  const [hrErr, setHrErr]     = useState("");

  function submitCandidate(e) {
    e.preventDefault();
    const name  = candName.trim();
    const email = candEmail.trim();
    if (!name)  { setCandErr("Please enter your full name."); return; }
    if (!email || !email.includes("@")) { setCandErr("Please enter a valid email address."); return; }
    login("candidate", { name, email });
  }

  function submitHR(e) {
    e.preventDefault();
    const name = hrName.trim();
    if (!name) { setHrErr("Please enter your name."); return; }
    if (hrCode.trim() !== HR_ACCESS_CODE) {
      setHrErr("Invalid HR access code. Please contact your IT administrator.");
      return;
    }
    login("hr", { name, email: "" });
  }

  if (view === "candidate") {
    return (
      <div className={styles.page}>
        <div className={styles.formCard}>
          <button className={styles.backBtn} onClick={() => setView("choose")}>← Back</button>
          <div className={styles.formIcon}>🧑‍💼</div>
          <h2 className={styles.formTitle}>Job Applicant Login</h2>
          <p className={styles.formSub}>Enter your details to submit your application and track its status.</p>
          <form onSubmit={submitCandidate} className={styles.form}>
            <label className={styles.label}>Full Name</label>
            <input
              className={styles.input}
              type="text"
              placeholder="e.g. Priya Sharma"
              value={candName}
              onChange={e => { setCandName(e.target.value); setCandErr(""); }}
            />
            <label className={styles.label}>Email Address</label>
            <input
              className={styles.input}
              type="email"
              placeholder="e.g. priya@example.com"
              value={candEmail}
              onChange={e => { setCandEmail(e.target.value); setCandErr(""); }}
            />
            {candErr && <div className={styles.err}>{candErr}</div>}
            <button className={styles.submitBtn} type="submit">Continue →</button>
          </form>
        </div>
      </div>
    );
  }

  if (view === "hr") {
    return (
      <div className={styles.page}>
        <div className={styles.formCard}>
          <button className={styles.backBtn} onClick={() => setView("choose")}>← Back</button>
          <div className={styles.formIcon}>🏢</div>
          <h2 className={styles.formTitle}>HR / Management Login</h2>
          <p className={styles.formSub}>Enter your name and the HR access code provided by your IT team.</p>
          <form onSubmit={submitHR} className={styles.form}>
            <label className={styles.label}>Your Name</label>
            <input
              className={styles.input}
              type="text"
              placeholder="e.g. Rahul Verma"
              value={hrName}
              onChange={e => { setHrName(e.target.value); setHrErr(""); }}
            />
            <label className={styles.label}>HR Access Code</label>
            <input
              className={styles.input}
              type="password"
              placeholder="Enter access code"
              value={hrCode}
              onChange={e => { setHrCode(e.target.value); setHrErr(""); }}
            />
            <div className={styles.codeHint}>Contact your IT administrator for the access code.</div>
            {hrErr && <div className={styles.err}>{hrErr}</div>}
            <button className={styles.submitBtn} type="submit">Access HR Portal →</button>
          </form>
        </div>
      </div>
    );
  }

  // Default: role chooser
  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <div className={styles.heroLogo}>TalentFlow</div>
        <h1 className={styles.heroTitle}>AI-Powered Talent Platform</h1>
        <p className={styles.heroSub}>
          Smarter hiring, happier teams. Built for both job seekers and HR managers.
        </p>
      </div>

      <div className={styles.cards}>
        {/* Candidate card */}
        <div className={styles.roleCard} onClick={() => setView("candidate")}>
          <div className={styles.roleIcon}>🧑‍💼</div>
          <h3 className={styles.roleTitle}>I'm Applying for a Job</h3>
          <ul className={styles.roleFeatures}>
            <li>Upload your CV — AI analyzes it instantly</li>
            <li>Get your fit score for the role</li>
            <li>Receive offer or rejection email automatically</li>
            <li>Ask our AI any questions about the process</li>
          </ul>
          <button className={styles.roleBtn}>Get Started →</button>
        </div>

        {/* HR card */}
        <div className={`${styles.roleCard} ${styles.roleCardHR}`} onClick={() => setView("hr")}>
          <div className={styles.roleIcon}>🏢</div>
          <h3 className={styles.roleTitle}>I'm from HR / Management</h3>
          <ul className={styles.roleFeatures}>
            <li>Review & decision on pending applications</li>
            <li>Monitor employee burnout & stress levels</li>
            <li>Search internal talent before hiring externally</li>
            <li>Screen resumes & generate interview questions</li>
          </ul>
          <button className={`${styles.roleBtn} ${styles.roleBtnHR}`}>HR Portal →</button>
        </div>
      </div>
    </div>
  );
}
