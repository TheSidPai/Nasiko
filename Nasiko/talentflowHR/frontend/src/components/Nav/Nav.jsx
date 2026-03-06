import { NAV_HR, NAV_CANDIDATE } from "../../constants";
import { useAuth } from "../../context/AuthContext";
import styles from "./Nav.module.css";

export default function Nav({ page, setPage }) {
  const { auth, logout } = useAuth();
  const items = auth?.role === "hr" ? NAV_HR : auth?.role === "candidate" ? NAV_CANDIDATE : [];

  return (
    <nav className={styles.nav}>
      <div className={styles.logo}>TalentFlow</div>
      <div className={styles.links}>
        {items.map(({ key, label }) => (
          <button
            key={key}
            className={`${styles.link} ${page === key ? styles.linkActive : ""}`}
            onClick={() => setPage(key)}
          >
            {label}
          </button>
        ))}
        {auth && (
          <button className={styles.logoutBtn} onClick={logout}>
            Sign Out
          </button>
        )}
      </div>
    </nav>
  );
}
