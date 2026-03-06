import { useState } from "react";
import { searchInternalTalent } from "../../services/api";
import styles from "./InternalSearchPage.module.css";

export default function InternalSearchPage() {
  const [query, setQuery]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [results, setResults]   = useState(null);  // null = not searched yet
  const [aiSummary, setAiSummary] = useState("");
  const [errMsg, setErrMsg]     = useState("");

  async function handleSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setResults(null);
    setAiSummary("");
    setErrMsg("");

    try {
      const data = await searchInternalTalent(query.trim());
      setResults(data.matches || []);
      setAiSummary(data.ai_summary || "");
    } catch (err) {
      setErrMsg("Could not search internal talent: " + err.message);
    }
    setLoading(false);
  }

  const SCORE_COLOR = (s) =>
    s >= 70 ? "#4ff78c" : s >= 45 ? "#f7c94f" : "#f74f4f";

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>🔍 Internal Talent Search</h1>
        <p className={styles.sub}>
          Before posting an external job opening, check if someone in your company already has
          the skills. Search your employee database by role or skill set.
        </p>
      </div>

      <form className={styles.searchBar} onSubmit={handleSearch}>
        <input
          className={styles.searchInput}
          type="text"
          placeholder="e.g. Senior ML Engineer, React developer with 3+ years, Data Analyst…"
          value={query}
          onChange={e => setQuery(e.target.value)}
        />
        <button className={styles.searchBtn} type="submit" disabled={loading || !query.trim()}>
          {loading ? "Searching…" : "Search →"}
        </button>
      </form>

      {errMsg && <div className={styles.err}>{errMsg}</div>}

      {/* Loading */}
      {loading && (
        <div className={styles.loadingWrap}>
          <div className={styles.spinner} />
          <p className={styles.loadingText}>Analysing your employee database…</p>
        </div>
      )}

      {/* No results */}
      {!loading && results !== null && results.length === 0 && (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>🔎</div>
          <p className={styles.emptyText}>No strong internal matches found for this role.</p>
          <p className={styles.emptySub}>Consider posting an external job opening.</p>
        </div>
      )}

      {/* AI summary */}
      {!loading && aiSummary && (
        <div className={styles.aiSummaryBox}>
          <div className={styles.aiSummaryLabel}>AI Recommendation</div>
          <p className={styles.aiSummaryText}>{aiSummary}</p>
        </div>
      )}

      {/* Results */}
      {!loading && results && results.length > 0 && (
        <>
          <div className={styles.resultsHeader}>
            Found <strong>{results.length}</strong> potential internal match{results.length > 1 ? "es" : ""} for "{query}"
          </div>
          <div className={styles.resultsList}>
            {results.map((emp, i) => (
              <div key={emp.id || i} className={styles.empCard}>
                <div className={styles.empLeft}>
                  <div className={styles.empRank}>#{i + 1}</div>
                  <div>
                    <div className={styles.empName}>{emp.name}</div>
                    <div className={styles.empRole}>{emp.role}</div>
                    {emp.match_reason && (
                      <div className={styles.empReason}>{emp.match_reason}</div>
                    )}
                  </div>
                </div>
                <div className={styles.empRight}>
                  {emp.fit_score !== undefined && (
                    <div
                      className={styles.fitBadge}
                      style={{ color: SCORE_COLOR(emp.fit_score), borderColor: SCORE_COLOR(emp.fit_score) }}
                    >
                      {emp.fit_score}% fit
                    </div>
                  )}
                  <div
                    className={styles.availBadge}
                    style={emp.available
                      ? { color: "#4ff78c", borderColor: "#4ff78c" }
                      : { color: "#f7c94f", borderColor: "#f7c94f" }}
                  >
                    {emp.available ? "Available" : "Currently busy"}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Empty initial state */}
      {!loading && results === null && (
        <div className={styles.hint}>
          <div className={styles.hintGrid}>
            {[
              { icon: "🤖", text: "AI ranks employees by skill match" },
              { icon: "📊", text: "See fit scores for each person" },
              { icon: "💡", text: "Decide before creating an external job post" },
              { icon: "⚡", text: "Results from your live employee database" },
            ].map((h, i) => (
              <div key={i} className={styles.hintCard}>
                <span className={styles.hintIcon}>{h.icon}</span>
                <span className={styles.hintText}>{h.text}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
