"use client";

/**
 * 4 summary metric cards across the top of the dashboard.
 */
export default function SummaryCards({ cards = [] }) {
  if (!cards.length) return null;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, i) => (
        <div
          key={i}
          className="glass-card group flex items-start gap-4 p-5 transition-all duration-300"
        >
          {/* Icon */}
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[var(--color-surface-2)] text-2xl transition-transform duration-300 group-hover:scale-110">
            {card.icon}
          </div>

          {/* Content */}
          <div className="min-w-0">
            <p className="text-xs font-medium uppercase tracking-wider text-[var(--color-text-muted)]">
              {card.label}
            </p>
            <p className="mt-1 text-2xl font-bold tracking-tight text-[var(--color-text)]">
              {card.value}
            </p>
            <div className="mt-1 flex items-center gap-1.5">
              {card.trend && (
                <span
                  className={`text-xs font-medium ${
                    card.trend === "up" ? "text-[var(--color-success)]" : "text-[var(--color-danger)]"
                  }`}
                >
                  {card.trend === "up" ? "↑" : "↓"}
                </span>
              )}
              <span className="truncate text-xs text-[var(--color-text-muted)]">
                {card.subtitle}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
