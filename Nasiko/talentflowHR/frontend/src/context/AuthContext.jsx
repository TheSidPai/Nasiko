/**
 * AuthContext — stores the current user role and identity across the app.
 * role: 'candidate' | 'hr' | null
 */
import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    try {
      const saved = sessionStorage.getItem("tf_auth");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  function login(role, userInfo) {
    const payload = { role, ...userInfo };
    setAuth(payload);
    sessionStorage.setItem("tf_auth", JSON.stringify(payload));
  }

  function logout() {
    setAuth(null);
    sessionStorage.removeItem("tf_auth");
    sessionStorage.removeItem("talentflow_session_id");
  }

  return (
    <AuthContext.Provider value={{ auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
