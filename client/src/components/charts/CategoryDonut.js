"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 shadow-lg">
      <p className="text-sm font-medium text-[var(--color-text)]">{d.name}</p>
      <p className="text-xs text-[var(--color-text-secondary)]">
        ${d.value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
      </p>
    </div>
  );
};

/**
 * Donut chart showing spending by category.
 *
 * @param {{ data: Array<{ label: string, value: number, color: string }> }} props
 */
export default function CategoryDonut({ data = [] }) {
  if (!data.length) return null;

  // Take top 6, group rest as "Other"
  const sorted = [...data].sort((a, b) => b.value - a.value);
  const top = sorted.slice(0, 6);
  const restValue = sorted.slice(6).reduce((sum, d) => sum + d.value, 0);
  const chartData = restValue > 0
    ? [...top, { label: "Other", value: restValue, color: "#6b7280" }]
    : top;

  const total = chartData.reduce((s, d) => s + d.value, 0);

  return (
    <div className="glass-card p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
        Spending by Category
      </h3>

      <div className="flex flex-col items-center gap-6 lg:flex-row">
        {/* Chart */}
        <div className="h-56 w-56 shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="label"
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={3}
                strokeWidth={0}
              >
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="flex flex-1 flex-wrap gap-x-6 gap-y-2">
          {chartData.map((entry, i) => {
            const pct = total > 0 ? ((entry.value / total) * 100).toFixed(1) : 0;
            return (
              <div key={i} className="flex items-center gap-2">
                <span
                  className="h-3 w-3 shrink-0 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-xs text-[var(--color-text-secondary)]">
                  {entry.label}
                  <span className="ml-1 text-[var(--color-text-muted)]">{pct}%</span>
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
