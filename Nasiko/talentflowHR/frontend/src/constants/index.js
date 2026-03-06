/**
 * Application constants — data, config, and labels used across pages.
 */

export const AGENT_URL = "http://localhost:5000/";

export const NAV_ITEMS = ["Home", "Chat", "Resume", "Dashboard"];

export const SUGGESTED_PROMPTS = [
  "How many days of annual leave do I get?",
  "Check burnout risk for Meena Iyer",
  "We have an open ML Engineer role — check internally first",
  "What is the WFH policy?",
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
