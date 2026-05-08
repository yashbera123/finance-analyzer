"use client";

import { useSession } from "@/components/SessionProvider";

/**
 * Dashboard view data from persisted session (`summary`).
 *
 * @returns {{ data, isLoading, error, fileId, sessionReady }}
 */
export function useDashboard() {
  const { sessionId, data, isLoading, error } = useSession();

  const sessionReady = sessionId !== undefined;
  const summary = data?.summary ?? null;
  const fileId = summary?.file_id ?? null;

  return {
    data: summary,
    isLoading: sessionReady && isLoading,
    error,
    fileId,
    sessionReady,
    hasSession: Boolean(sessionId),
  };
}
