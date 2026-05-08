"use client";

import { Suspense } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useInsights } from "@/hooks/useInsights";
import { useSession } from "@/components/SessionProvider";
import { FadeIn, StaggerContainer, StaggerItem } from "@/components/ui/Motion";
import { InsightsSkeleton } from "@/components/ui/Skeleton";
import ProfileCard from "@/components/dashboard/ProfileCard";
import RecommendationList from "@/components/dashboard/RecommendationList";
import AnomalyAlerts from "@/components/dashboard/AnomalyAlerts";

function InsightsContent() {
  const {
    data: insights,
    dashboardAnomalies: anomalies,
    isLoading,
    error,
    sessionReady,
    hasSession,
  } = useInsights();

  if (!sessionReady) {
    return (
      <div className="space-y-6">
        <div className="glass-card p-8"><div className="shimmer h-32 w-full rounded-xl" /></div>
        <InsightsSkeleton />
      </div>
    );
  }

  if (!hasSession) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="glass-card max-w-md p-10 text-center">
          <span className="text-5xl">🧠</span>
          <h2 className="mt-4 text-xl font-semibold">No analysis session</h2>
          <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
            Upload a bank statement to see your financial insights.
          </p>
          <Link
            href="/"
            className="mt-6 inline-block rounded-xl px-6 py-2.5 text-sm font-semibold text-white transition-all hover:scale-105"
            style={{ background: "var(--gradient-primary)" }}
          >
            Upload File
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="glass-card p-8"><div className="shimmer h-32 w-full rounded-xl" /></div>
        <InsightsSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="glass-card max-w-md p-10 text-center">
          <span className="text-5xl">⚠️</span>
          <h2 className="mt-4 text-xl font-semibold text-[var(--color-danger)]">Failed to load</h2>
          <p className="mt-2 text-sm text-[var(--color-text-secondary)]">{error}</p>
        </div>
      </div>
    );
  }

  if (!insights) return null;

  const profile = insights.profile;
  const recs = insights.recommendations || [];

  return (
    <StaggerContainer stagger={0.12} className="space-y-8">
      <StaggerItem>
        <ProfileCard profile={profile} />
      </StaggerItem>

      <StaggerItem>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-5">
          <section className="lg:col-span-3">
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-[var(--color-text)]">
              <span>💡</span> Recommendations
            </h2>
            <RecommendationList
              recommendations={recs}
              totalSavings={insights.total_potential_savings || 0}
            />
          </section>
          <section className="lg:col-span-2">
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-[var(--color-text)]">
              <span>🚨</span> Anomaly Alerts
              {anomalies.length > 0 && (
                <span className="rounded-full bg-red-500/15 px-2 py-0.5 text-xs font-medium text-red-400 pulse-danger">
                  {anomalies.length}
                </span>
              )}
            </h2>
            <AnomalyAlerts anomalies={anomalies} />
          </section>
        </div>
      </StaggerItem>
    </StaggerContainer>
  );
}

export default function InsightsPage() {
  const router = useRouter();
  const { clearSession } = useSession();

  const handleNewUpload = () => {
    clearSession();
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-grid px-4 py-8 sm:px-6 lg:px-8">
      <FadeIn className="mx-auto mb-8 max-w-7xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              <span className="text-gradient">Financial Insights</span>
            </h1>
            <p className="mt-1 text-sm text-[var(--color-text-muted)]">
              Your behavior profile, recommendations, and alerts
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/dashboard"
              className="rounded-lg border border-[var(--color-border)] px-4 py-2 text-sm text-[var(--color-text-secondary)] transition-all hover:border-[var(--color-border-light)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-2)]"
            >
              ← Dashboard
            </Link>
            <button
              type="button"
              onClick={handleNewUpload}
              className="rounded-lg border border-[var(--color-border)] px-4 py-2 text-sm text-[var(--color-text-secondary)] transition-all hover:border-[var(--color-border-light)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-2)]"
            >
              Upload New File
            </button>
          </div>
        </div>
      </FadeIn>

      <div className="mx-auto max-w-7xl">
        <Suspense
          fallback={
            <div className="flex min-h-[60vh] items-center justify-center">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" />
            </div>
          }
        >
          <InsightsContent />
        </Suspense>
      </div>
    </div>
  );
}
