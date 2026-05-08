"use client";

const CATEGORIES = [
  { value: "", label: "All Categories" },
  { value: "food_dining", label: "🍕 Food & Dining" },
  { value: "groceries", label: "🛒 Groceries" },
  { value: "transport", label: "🚗 Transport" },
  { value: "shopping", label: "🛍️ Shopping" },
  { value: "subscriptions", label: "📱 Subscriptions" },
  { value: "bills_utilities", label: "💡 Bills & Utilities" },
  { value: "rent_housing", label: "🏠 Rent & Housing" },
  { value: "health_fitness", label: "💪 Health & Fitness" },
  { value: "entertainment", label: "🎬 Entertainment" },
  { value: "travel", label: "✈️ Travel" },
  { value: "education", label: "📚 Education" },
  { value: "income", label: "💰 Income" },
  { value: "transfer", label: "🔄 Transfer" },
  { value: "other", label: "📋 Other" },
];

const TYPES = [
  { value: "", label: "All Types" },
  { value: "debit", label: "Debit" },
  { value: "credit", label: "Credit" },
];

/**
 * Filter toolbar — search, category, type, and date range.
 */
export default function FilterBar({
  search,
  onSearchChange,
  category,
  onCategoryChange,
  txnType,
  onTypeChange,
  dateFrom,
  dateTo,
  onDateFromChange,
  onDateToChange,
  total,
  filtered,
}) {
  const selectClass =
    "rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-sm text-[var(--color-text)] outline-none transition-colors focus:border-[var(--color-primary)] hover:border-[var(--color-border-light)]";

  return (
    <div className="glass-card space-y-4 p-4">
      {/* Search */}
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-muted)]"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search transactions..."
          className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] py-2.5 pl-10 pr-4 text-sm text-[var(--color-text)] outline-none transition-colors placeholder:text-[var(--color-text-muted)] focus:border-[var(--color-primary)]"
        />
      </div>

      {/* Filters row */}
      <div className="flex flex-wrap items-center gap-3">
        <select value={category} onChange={(e) => onCategoryChange(e.target.value)} className={selectClass}>
          {CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>{c.label}</option>
          ))}
        </select>

        <select value={txnType} onChange={(e) => onTypeChange(e.target.value)} className={selectClass}>
          {TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>

        <input
          type="date"
          value={dateFrom}
          onChange={(e) => onDateFromChange(e.target.value)}
          className={selectClass}
          placeholder="From"
        />
        <input
          type="date"
          value={dateTo}
          onChange={(e) => onDateToChange(e.target.value)}
          className={selectClass}
          placeholder="To"
        />

        {/* Results count */}
        <span className="ml-auto text-xs text-[var(--color-text-muted)]">
          {filtered === total
            ? `${total} transactions`
            : `${filtered} of ${total} transactions`}
        </span>
      </div>
    </div>
  );
}
