"use client";

import { useState, useCallback, Suspense } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { downloadReport } from "@/lib/api";
import { useSession } from "@/components/SessionProvider";
import { useDashboard } from "@/hooks/useDashboard";
import { FadeIn, StaggerContainer, StaggerItem } from "@/components/ui/Motion";
import {
  SummaryCardsSkeleton,
  ChartSkeleton,
  InsightsSkeleton,
  TransactionsSkeleton,
} from "@/components/ui/Skeleton";
import SummaryCards from "@/components/dashboard/SummaryCards";
import CategoryDonut from "@/components/charts/CategoryDonut";
import TrendChart from "@/components/charts/TrendChart";
import InsightsPanel from "@/components/dashboard/InsightsPanel";
import RecentTransactions from "@/components/dashboard/RecentTransactions";

function DashboardContent() {
  const { data, isLoading, error, fileId, sessionReady, hasSession } = useDashboard();

  if (!sessionReady) {
    return (
      <div className="space-y-6">
        <SummaryCardsSkeleton />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      </div>
    );
  }

  if (!hasSession) {
    return (
      <FadeIn className="flex min-h-[60vh] items-center justify-center">
        <div className="glass-card max-w-md p-10 text-center">
          <span className="text-5xl">📊</span>
          <h2 className="mt-4 text-xl font-semibold">No analysis session</h2>
          <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
            Upload a bank statement to see your dashboard.
          </p>
          <Link
            href="/"
            className="mt-6 inline-block rounded-xl px-6 py-2.5 text-sm font-semibold text-white transition-all hover:scale-105"
            style={{ background: "var(--gradient-primary)" }}
          >
            Upload File
          </Link>
        </div>
      </FadeIn>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <SummaryCardsSkeleton />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <InsightsSkeleton />
          </div>
          <TransactionsSkeleton />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <FadeIn className="flex min-h-[60vh] items-center justify-center">
        <div className="glass-card max-w-md p-10 text-center">
          <span className="text-5xl">⚠️</span>
          <h2 className="mt-4 text-xl font-semibold text-[var(--color-danger)]">Failed to load</h2>
          <p className="mt-2 text-sm text-[var(--color-text-secondary)]">{error}</p>
          <Link
            href="/"
            className="mt-6 inline-block rounded-xl px-6 py-2.5 text-sm font-semibold text-white transition-all hover:scale-105"
            style={{ background: "var(--gradient-primary)" }}
          >
            Try Again
          </Link>
        </div>
      </FadeIn>
    );
  }

  if (!data) return null;

  return (
    <StaggerContainer stagger={0.1} className="space-y-6">
      <StaggerItem>
        <SummaryCards cards={data.summary_cards} />
      </StaggerItem>

      <StaggerItem>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <TrendChart data={data.monthly_trends} />
          <CategoryDonut data={data.category_breakdown} />
        </div>
      </StaggerItem>

      <StaggerItem>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <InsightsPanel
              profile={data.profile_summary}
              recommendations={data.recommendations}
            />
          </div>
          <div>
            <RecentTransactions transactions={data.recent_transactions} />
          </div>
        </div>
      </StaggerItem>
    </StaggerContainer>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const { clearSession } = useSession();
  const { fileId } = useDashboard();
  const [downloading, setDownloading] = useState(false);

  const handleDownload = useCallback(async () => {
    if (!fileId) return;
    setDownloading(true);
    try {
      await downloadReport(fileId);
    } catch (err) {
      console.error("Report download failed:", err);
    } finally {
      setDownloading(false);
    }
  }, [fileId]);

  const handleNewUpload = useCallback(() => {
    clearSession();
    router.push("/");
  }, [clearSession, router]);

  return (
    <div className="min-h-screen bg-grid px-4 py-8 sm:px-6 lg:px-8">
      <FadeIn className="mx-auto mb-8 max-w-7xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              <span className="text-gradient">Dashboard</span>
            </h1>
            <p className="mt-1 text-sm text-[var(--color-text-muted)]">
              Your financial behavior at a glance
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={handleDownload}
              disabled={downloading || !fileId}
              className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-all hover:scale-[1.03] active:scale-[0.97] disabled:opacity-60 disabled:cursor-not-allowed"
              style={{ background: "var(--gradient-primary)" }}
            >
              {downloading ? (
                <>
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Generating...
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download PDF
                </>
              )}
            </button>
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
            <div className="space-y-6">
              <SummaryCardsSkeleton />
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <ChartSkeleton />
                <ChartSkeleton />
              </div>
            </div>
          }
        >
          <DashboardContent />
        </Suspense>
      </div>
    </div>
  );
}
