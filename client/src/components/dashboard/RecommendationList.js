"use client";

/**
 * Recommendation cards — grouped by priority with visual hierarchy.
 */
export default function RecommendationList({ recommendations = [], totalSavings = 0 }) {
  if (!recommendations.length) return null;

  const priorityConfig = {
    high:   { border: "border-red-500/20",    bg: "bg-red-500/5",    dot: "bg-red-400",    label: "High Priority" },
    medium: { border: "border-yellow-500/20", bg: "bg-yellow-500/5", dot: "bg-yellow-400", label: "Medium" },
    low:    { border: "border-emerald-500/20",bg: "bg-emerald-500/5",dot: "bg-emerald-400",label: "Good Habit" },
  };

  return (
    <div className="space-y-4">
      {/* Savings banner */}
      {totalSavings > 0 && (
        <div
          className="rounded-2xl p-5 text-center"
          style={{ background: "var(--gradient-primary)" }}
        >
          <p className="text-sm font-medium text-white/80">Total Potential Monthly Savings</p>
          <p className="mt-1 text-3xl font-bold text-white">
            ₹{totalSavings.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
        {recommendations.map((rec, i) => {
          const config = priorityConfig[rec.priority] || priorityConfig.medium;
          return (
            <div
              key={i}
              className={`glass-card border ${config.border} overflow-hidden transition-all duration-300 hover:scale-[1.01]`}
            >
              <div className="flex items-start gap-4 p-5">
                {/* Icon */}
                <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${config.bg} text-2xl`}>
                  {rec.icon}
                </div>

                {/* Content */}
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-[var(--color-text)]">{rec.title}</h4>
                    <span className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium ${config.bg}`}>
                      <span className={`h-1.5 w-1.5 rounded-full ${config.dot}`} />
                      {config.label}
                    </span>
                  </div>
                  <p className="mt-1.5 text-sm leading-relaxed text-[var(--color-text-secondary)]">
                    {rec.description}
                  </p>
                  {rec.potential_savings > 0 && (
                    <div className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-emerald-500/10 px-3 py-1.5">
                      <span className="text-sm">💰</span>
                      <span className="text-xs font-semibold text-emerald-400">
                        Save ~₹{rec.potential_savings.toLocaleString("en-IN", { minimumFractionDigits: 2 })}/month
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
