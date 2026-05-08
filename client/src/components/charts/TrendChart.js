"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 shadow-lg">
      <p className="mb-1 text-xs font-medium text-[var(--color-text-muted)]">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-sm" style={{ color: p.color }}>
          {p.name}: ${p.value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
        </p>
      ))}
    </div>
  );
};

/**
 * Area chart showing monthly spending vs income trends.
 *
 * @param {{ data: Array<{ month: string, spending: number, income: number, net: number }> }} props
 */
export default function TrendChart({ data = [] }) {
  if (!data.length) return null;

  // Format month labels (2024-01 → Jan '24)
  const formatted = data.map((d) => {
    const [y, m] = d.month.split("-");
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return {
      ...d,
      label: `${monthNames[parseInt(m, 10) - 1]} '${y.slice(2)}`,
    };
  });

  return (
    <div className="glass-card p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-[var(--color-text-muted)]">
        Monthly Trends
      </h3>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={formatted} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="gradIncome" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gradSpending" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />

            <XAxis
              dataKey="label"
              tick={{ fill: "var(--color-text-muted)", fontSize: 12 }}
              axisLine={{ stroke: "var(--color-border)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "var(--color-text-muted)", fontSize: 12 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `₹${(v / 1000).toFixed(1)}k`}
            />

            <Tooltip content={<CustomTooltip />} />

            <Legend
              verticalAlign="top"
              align="right"
              iconType="circle"
              iconSize={8}
              wrapperStyle={{ fontSize: 12, color: "var(--color-text-secondary)" }}
            />

            <Area
              type="monotone"
              dataKey="income"
              name="Income"
              stroke="#10b981"
              strokeWidth={2}
              fill="url(#gradIncome)"
            />
            <Area
              type="monotone"
              dataKey="spending"
              name="Spending"
              stroke="#ef4444"
              strokeWidth={2}
              fill="url(#gradSpending)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
