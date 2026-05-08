"use client";

import { formatDate, formatCurrency } from "@/lib/utils";

const CATEGORY_ICONS = {
  food_dining: "🍕",
  groceries: "🛒",
  transport: "🚗",
  shopping: "🛍️",
  subscriptions: "📱",
  bills_utilities: "💡",
  rent_housing: "🏠",
  health_fitness: "💪",
  entertainment: "🎬",
  travel: "✈️",
  education: "📚",
  income: "💰",
  transfer: "🔄",
  atm_cash: "🏧",
  insurance: "🛡️",
  investments: "📈",
  personal_care: "💇",
  gifts_donations: "🎁",
  fees_charges: "🏦",
  other: "📋",
};

function SortIcon({ active, order }) {
  if (!active) {
    return (
      <span className="ml-1 text-[var(--color-text-muted)] opacity-0 transition-opacity group-hover:opacity-50">
        ↕
      </span>
    );
  }

  return (
    <span className="ml-1 text-[var(--color-primary)]">
      {order === "asc" ? "↑" : "↓"}
    </span>
  );
}

/**
 * Transaction data table.
 *
 * @param {{ transactions: Array, sortBy: string, order: string, onSort: (col: string) => void }} props
 */
export default function TransactionTable({ transactions, sortBy, order, onSort }) {
  if (!transactions.length) {
    return (
      <div className="glass-card flex min-h-[200px] items-center justify-center p-8">
        <p className="text-sm text-[var(--color-text-muted)]">No transactions found</p>
      </div>
    );
  }

  const headerClass =
    "group cursor-pointer select-none px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-text-secondary)]";

  return (
    <div className="glass-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[var(--color-border)]">
              <th className={headerClass} onClick={() => onSort("date")}>
                Date <SortIcon active={sortBy === "date"} order={order} />
              </th>
              <th className={`${headerClass} min-w-[200px]`}>Description</th>
              <th className={headerClass}>Category</th>
              <th className={headerClass}>Type</th>
              <th className={headerClass} onClick={() => onSort("amount")}>
                Amount <SortIcon active={sortBy === "amount"} order={order} />
              </th>
              <th className={headerClass}>Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-border)]/50">
            {transactions.map((txn, i) => (
              <tr
                key={i}
                className="transition-colors hover:bg-[var(--color-surface-2)]/50"
              >
                {/* Date */}
                <td className="whitespace-nowrap px-4 py-3 text-sm text-[var(--color-text-secondary)]">
                  {formatDate(txn.transaction_date || txn.date)}
                </td>

                {/* Description */}
                <td className="px-4 py-3">
                  <p className="max-w-[250px] truncate text-sm font-medium text-[var(--color-text)]">
                    {txn.description || "—"}
                  </p>
                </td>

                {/* Category */}
                <td className="px-4 py-3">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-[var(--color-surface-2)] px-2.5 py-1 text-xs text-[var(--color-text-secondary)]">
                    <span>{CATEGORY_ICONS[txn.category] || "📋"}</span>
                    {txn.category_label}
                  </span>
                </td>

                {/* Type */}
                <td className="px-4 py-3">
                  <span
                    className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${
                      txn.transaction_type === "credit"
                        ? "bg-emerald-500/10 text-emerald-400"
                        : "bg-red-500/10 text-red-400"
                    }`}
                  >
                    {txn.transaction_type}
                  </span>
                </td>

                {/* Amount */}
                <td className="whitespace-nowrap px-4 py-3 text-right">
                  <span
                    className={`text-sm font-semibold ${
                      txn.transaction_type === "credit"
                        ? "text-[var(--color-success)]"
                        : "text-[var(--color-text)]"
                    }`}
                  >
                    {txn.transaction_type === "credit" ? "+" : "−"}
                    {formatCurrency(txn.amount)}
                  </span>
                </td>

                {/* Confidence */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 w-16 overflow-hidden rounded-full bg-[var(--color-surface-3)]">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${(txn.categorization_confidence || 0) * 100}%`,
                          backgroundColor:
                            (txn.categorization_confidence || 0) > 0.7
                              ? "var(--color-success)"
                              : (txn.categorization_confidence || 0) > 0.4
                              ? "var(--color-warning)"
                              : "var(--color-danger)",
                        }}
                      />
                    </div>
                    <span className="text-xs text-[var(--color-text-muted)]">
                      {((txn.categorization_confidence || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
