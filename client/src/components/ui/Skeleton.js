"use client";

/* ═══════════════════════════════════════════════════════════════════
   Loading skeletons — shimmer placeholders for async content
   ═══════════════════════════════════════════════════════════════════ */

function Bone({ className = "" }) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-[var(--color-surface-2)] ${className}`}
    />
  );
}

/**
 * Skeleton for the 4 summary cards.
 */
export function SummaryCardsSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="glass-card flex items-start gap-4 p-5">
          <Bone className="h-12 w-12 shrink-0 rounded-xl" />
          <div className="flex-1 space-y-2">
            <Bone className="h-3 w-20" />
            <Bone className="h-7 w-28" />
            <Bone className="h-3 w-24" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for a chart card.
 */
export function ChartSkeleton() {
  return (
    <div className="glass-card p-6">
      <Bone className="mb-4 h-4 w-36" />
      <Bone className="h-56 w-full rounded-xl" />
    </div>
  );
}

/**
 * Skeleton for the insights panel.
 */
export function InsightsSkeleton() {
  return (
    <div className="space-y-4">
      <div className="glass-card p-6 space-y-4">
        <Bone className="h-4 w-32" />
        <div className="flex gap-3">
          <Bone className="h-7 w-24 rounded-full" />
          <Bone className="h-7 w-28 rounded-full" />
        </div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="space-y-1">
              <div className="flex justify-between">
                <Bone className="h-3 w-16" />
                <Bone className="h-3 w-8" />
              </div>
              <Bone className="h-1.5 w-full rounded-full" />
            </div>
          ))}
        </div>
      </div>
      <div className="glass-card p-6 space-y-3">
        <Bone className="h-4 w-36" />
        {[...Array(3)].map((_, i) => (
          <Bone key={i} className="h-20 w-full rounded-xl" />
        ))}
      </div>
    </div>
  );
}

/**
 * Skeleton for the recent transactions list.
 */
export function TransactionsSkeleton() {
  return (
    <div className="glass-card p-6 space-y-2">
      <Bone className="mb-4 h-4 w-40" />
      {[...Array(6)].map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3">
          <Bone className="h-10 w-10 shrink-0 rounded-xl" />
          <div className="flex-1 space-y-1.5">
            <Bone className="h-4 w-32" />
            <Bone className="h-3 w-24" />
          </div>
          <Bone className="h-4 w-16" />
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for the transactions table.
 */
export function TableSkeleton() {
  return (
    <div className="glass-card overflow-hidden">
      {/* Header */}
      <div className="flex gap-4 border-b border-[var(--color-border)] p-4">
        {[80, 200, 100, 60, 80, 80].map((w, i) => (
          <Bone key={i} className="h-3" style={{ width: w }} />
        ))}
      </div>
      {/* Rows */}
      {[...Array(8)].map((_, i) => (
        <div key={i} className="flex items-center gap-4 border-b border-[var(--color-border)]/50 p-4">
          <Bone className="h-4 w-20" />
          <Bone className="h-4 w-44" />
          <Bone className="h-6 w-24 rounded-full" />
          <Bone className="h-5 w-14 rounded" />
          <Bone className="h-4 w-16" />
          <div className="flex items-center gap-2">
            <Bone className="h-1.5 w-16 rounded-full" />
            <Bone className="h-3 w-8" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Full page loading state.
 */
export function PageSkeleton() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div className="relative h-12 w-12">
          <div className="absolute inset-0 animate-ping rounded-full bg-[var(--color-primary)]/20" />
          <div className="relative h-12 w-12 animate-spin rounded-full border-4 border-[var(--color-surface-3)] border-t-[var(--color-primary)]" />
        </div>
        <Bone className="h-4 w-32" />
      </div>
    </div>
  );
}
