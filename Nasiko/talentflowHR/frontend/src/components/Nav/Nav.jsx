import { NAV_ITEMS } from "../../constants";
import styles from "./Nav.module.css";

export default function Nav({ page, setPage }) {
  return (
    <nav className={styles.nav}>
      <div className={styles.logo}>TalentFlow</div>
      <div className={styles.links}>
        {NAV_ITEMS.map((name) => (
          <button
            key={name}
            className={`${styles.link} ${page === name ? styles.linkActive : ""}`}
            onClick={() => setPage(name)}
          >
            {name}
          </button>
        ))}
      </div>
    </nav>
  );
}
