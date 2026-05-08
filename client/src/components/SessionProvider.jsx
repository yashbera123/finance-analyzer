"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { fetchSession } from "@/lib/api";
import {
  clearStoredSessionId,
  getStoredSessionId,
  setStoredSessionId,
} from "@/lib/session";

const SessionContext = createContext(null);

function readInitialSessionId() {
  return getStoredSessionId() ?? null;
}

function SessionProvider({ children }) {
  const router = useRouter();
  const [sessionId, setSessionIdState] = useState(readInitialSessionId);
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(() =>
    Boolean(readInitialSessionId())
  );
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!sessionId) return;

    let cancelled = false;

    fetchSession(sessionId)
      .then((payload) => {
        if (!cancelled) {
          setData(payload);
          setError(null);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setData(null);
          setError(err.message);

          if (err.status === 404) {
            clearStoredSessionId();
            setSessionIdState(null);
            router.replace("/");
          }
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [sessionId, router]);

  const setSession = useCallback((id) => {
    setStoredSessionId(id);
    setData(null);
    setError(null);
    setIsLoading(true);
    setSessionIdState(id);
  }, []);

  const clearSession = useCallback(() => {
    clearStoredSessionId();
    setSessionIdState(null);
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  const value = useMemo(
    () => ({
      sessionId,
      data,
      isLoading,
      error,
      setSession,
      clearSession,
    }),
    [sessionId, data, isLoading, error, setSession, clearSession]
  );

  return (
    <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
  );
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) {
    throw new Error("useSession must be used within SessionProvider");
  }
  return ctx;
}

export default SessionProvider;
