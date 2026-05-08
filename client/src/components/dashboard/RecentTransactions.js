"use client";

/**
 * Recent transactions list for the dashboard.
 */
export default function RecentTransactions({ transactions = [] }) {
  if (!transactions.length) return null;

  return (
    <div className="glass-card p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
          Recent Transactions
        </h3>
        <a
          href="/transactions"
          className="text-xs text-[var(--color-primary)] transition-colors hover:text-[var(--color-primary-light)]"
        >
          View All →
        </a>
      </div>

      <div className="space-y-2">
        {transactions.map((txn, i) => (
          <div
            key={i}
            className="flex items-center gap-3 rounded-xl p-3 transition-colors hover:bg-[var(--color-surface-2)]"
          >
            {/* Icon */}
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--color-surface-2)] text-lg">
              {txn.icon || "📋"}
            </span>

            {/* Info */}
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-[var(--color-text)]">
                {txn.description}
              </p>
              <p className="text-xs text-[var(--color-text-muted)]">
                {txn.date || "—"} • {txn.category}
              </p>
            </div>

            {/* Amount */}
            <span
              className={`shrink-0 text-sm font-semibold ${
                txn.type === "credit"
                  ? "text-[var(--color-success)]"
                  : "text-[var(--color-text)]"
              }`}
            >
              {txn.type === "credit" ? "+" : "−"}₹
              {txn.amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
