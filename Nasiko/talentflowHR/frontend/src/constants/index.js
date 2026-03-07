/**
 * Application constants — data, config, and labels used across pages.
 */

export const AGENT_URL = process.env.REACT_APP_AGENT_URL || "https://nasiko-production.up.railway.app/";

/** Nav items shown to HR / management users */
export const NAV_HR = [
  { key: "Dashboard",      label: "Dashboard"         },
  { key: "Screen",         label: "Screen Resume"      },
  { key: "InternalSearch", label: "Internal Search"    },
  { key: "Onboarding",     label: "Onboarding Planner" },
  { key: "ExitInterview",  label: "Exit Interview"     },
  { key: "HRChat",         label: "AI Assistant"       },
];

/** Nav items shown to job applicants */
export const NAV_CANDIDATE = [
  { key: "Apply", label: "Apply"         },
  { key: "Chat",  label: "Ask AI"        },
];

/** @deprecated — kept for safety, use NAV_HR or NAV_CANDIDATE instead */
export const NAV_ITEMS = ["Dashboard", "Screen", "InternalSearch", "HRChat"];

/** Suggested quick prompts for HR users */
export const SUGGESTED_PROMPTS = [
  "Check burnout risk for Meena Iyer and suggest what action I should take",
  "Predict attrition risk for the full team — who is most likely to resign?",
  "We need a Senior ML Engineer — find the best internal match first",
  "Generate interview questions for a Full Stack Developer candidate",
  "Check Priya Sharma's leave balance",
  "What is our WFH policy and notice period?",
  "Benchmark salary for a Product Manager with 5 years of experience in Bangalore",
  "What meetings do I have scheduled for today?",
];

/** Suggested quick prompts for job applicant (candidate) users */
export const CANDIDATE_PROMPTS = [
  "What skills do I need to become a Data Analyst?",
  "How can I improve my CV for a software engineering role?",
  "What are the most common interview questions for a Product Manager?",
  "What should I expect in a technical interview?",
  "What is a good fresher salary range for an ML Engineer in India?",
  "I received an offer of 10 LPA for a React Developer role — how do I negotiate it up?",
];

// BURNOUT_DATA is now loaded live from MongoDB via /employees endpoint
// Kept here only as a fallback shape reference — not used directly
export const BURNOUT_DATA = [];

export const RISK_CONFIG = {
  Critical: { color: "#ff4444", bg: "rgba(255,68,68,0.12)",  bar: "#ff4444" },
  High:     { color: "#ff8800", bg: "rgba(255,136,0,0.12)",  bar: "#ff8800" },
  Medium:   { color: "#f0c000", bg: "rgba(240,192,0,0.12)",  bar: "#f0c000" },
  Low:      { color: "#00c48c", bg: "rgba(0,196,140,0.12)",  bar: "#00c48c" },
};

export const RISK_ORDER = ["Critical", "High", "Medium", "Low"];

export const RESUME_MODES = [
  { id: "screen",    label: "Screen Resume"       },
  { id: "questions", label: "Interview Questions"  },
  { id: "email",     label: "Draft Email"          },
];
