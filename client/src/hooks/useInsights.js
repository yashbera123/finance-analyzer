"use client";

import { useSession } from "@/components/SessionProvider";

/**
 * Insights (profile) + anomaly list from session payload.
 */
export function useInsights() {
  const { sessionId, data, isLoading, error } = useSession();

  const sessionReady = sessionId !== undefined;
  const insights = data?.insights ?? null;
  const anomalies = data?.summary?.top_anomalies ?? [];

  return {
    data: insights,
    dashboardAnomalies: anomalies,
    isLoading: sessionReady && isLoading,
    error,
    sessionReady,
    hasSession: Boolean(sessionId),
  };
}
