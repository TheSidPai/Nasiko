import styles from "./HomePage.module.css";

const FEATURES = [
  { icon: "⚡", title: "Full-Cycle Recruitment",    desc: "Screen resumes, generate tailored interview questions, draft offer or rejection emails, and benchmark salaries — all in one place." },
  { icon: "🔍", title: "Internal Talent Match",     desc: "Before posting externally, discover if the right person already works for you. Reduce hiring costs and boost retention." },
  { icon: "📋", title: "Policy FAQ",                desc: "Instant, accurate answers to any HR policy question — leave, WFH, appraisals, benefits — grounded in your policy doc." },
  { icon: "🔥", title: "Burnout Risk Detection",    desc: "Proactively identify at-risk employees using work activity signals and get actionable intervention recommendations." },
  { icon: "🚪", title: "Attrition Risk Prediction", desc: "AI-powered flight-risk scoring for every employee. Know who is likely to resign before they hand in their notice." },
  { icon: "🗓",  title: "Onboarding Planner",       desc: "Generate day-by-day onboarding plans with 30/60/90-day milestones tailored to any role and department." },
  { icon: "📊", title: "Exit Interview Analysis",   desc: "Extract resignation root causes, sentiment, and team-wide risk flags from exit interview transcripts automatically." },
  { icon: "➕", title: "Employee Database",         desc: "Add new employees, check leave balances, and keep your people database up to date — all via natural language." },
];

export default function HomePage({ setPage }) {
  return (
    <div className={styles.page}>
      {/* Hero */}
      <div className={styles.hero}>
        <div className={styles.glow} />

        <div className={styles.badge}>✦ AI-POWERED HR AUTOMATION</div>

        <h1 className={styles.heading}>
          HR that works<br />
          <span className={styles.headingGradient}>while you think</span>
        </h1>

        <p className={styles.subtitle}>
          TalentFlow automates your most repetitive HR workflows — from hiring
          to retention — so your team can focus on people, not paperwork.
        </p>

        <div className={styles.actions}>
          <button className={styles.btnPrimary} onClick={() => setPage("Chat")}>
            Try the Agent →
          </button>
          <button className={styles.btnSecondary} onClick={() => setPage("Dashboard")}>
            View Dashboard
          </button>
        </div>
      </div>

      {/* Features */}
      <div className={styles.features}>
        <div className={styles.grid}>
          {FEATURES.map((f) => (
            <div key={f.title} className={styles.card}>
              <div className={styles.cardIcon}>{f.icon}</div>
              <div className={styles.cardTitle}>{f.title}</div>
              <div className={styles.cardDesc}>{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
