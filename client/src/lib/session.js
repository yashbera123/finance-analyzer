/** localStorage key for persisted analysis session id */
export const SESSION_STORAGE_KEY = "session_id";

export function getStoredSessionId() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(SESSION_STORAGE_KEY);
}

export function setStoredSessionId(id) {
  localStorage.setItem(SESSION_STORAGE_KEY, id);
}

export function clearStoredSessionId() {
  localStorage.removeItem(SESSION_STORAGE_KEY);
}
