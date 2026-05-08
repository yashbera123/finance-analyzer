"""
PDF Report Generator
====================
Generates a professional financial analysis PDF report using ReportLab.
"""

import io
from datetime import datetime
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak,
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart


# ── Color palette ──────────────────────────────────────────────────
PRIMARY     = colors.HexColor("#6366f1")
ACCENT      = colors.HexColor("#06b6d4")
SUCCESS     = colors.HexColor("#10b981")
WARNING     = colors.HexColor("#f59e0b")
DANGER      = colors.HexColor("#ef4444")
DARK_BG     = colors.HexColor("#0f0f16")
SURFACE     = colors.HexColor("#1a1a24")
BORDER      = colors.HexColor("#2a2a3a")
TEXT_PRIMARY = colors.HexColor("#ededf5")
TEXT_MUTED   = colors.HexColor("#9d9db8")
WHITE        = colors.white
BLACK        = colors.black

CHART_COLORS = [
    colors.HexColor("#6366f1"),
    colors.HexColor("#06b6d4"),
    colors.HexColor("#10b981"),
    colors.HexColor("#f59e0b"),
    colors.HexColor("#ef4444"),
    colors.HexColor("#8b5cf6"),
    colors.HexColor("#ec4899"),
    colors.HexColor("#14b8a6"),
    colors.HexColor("#f97316"),
    colors.HexColor("#64748b"),
]


# ── Custom styles ──────────────────────────────────────────────────
def _build_styles():
    base = getSampleStyleSheet()
    styles = {}
    styles["Title"] = ParagraphStyle(
        "Title", parent=base["Title"],
        fontSize=28, leading=34, textColor=PRIMARY,
        spaceAfter=6,
    )
    styles["Subtitle"] = ParagraphStyle(
        "Subtitle", parent=base["Normal"],
        fontSize=11, leading=14, textColor=TEXT_MUTED,
        spaceAfter=20,
    )
    styles["SectionHead"] = ParagraphStyle(
        "SectionHead", parent=base["Heading2"],
        fontSize=16, leading=20, textColor=PRIMARY,
        spaceBefore=16, spaceAfter=10,
    )
    styles["Body"] = ParagraphStyle(
        "Body", parent=base["Normal"],
        fontSize=10, leading=14, textColor=BLACK,
    )
    styles["BodySmall"] = ParagraphStyle(
        "BodySmall", parent=base["Normal"],
        fontSize=9, leading=12, textColor=colors.HexColor("#555555"),
    )
    styles["MetricValue"] = ParagraphStyle(
        "MetricValue", parent=base["Normal"],
        fontSize=22, leading=26, textColor=PRIMARY,
        alignment=1,
    )
    styles["MetricLabel"] = ParagraphStyle(
        "MetricLabel", parent=base["Normal"],
        fontSize=9, leading=12, textColor=colors.HexColor("#777777"),
        alignment=1,
    )
    return styles


def _hr():
    return HRFlowable(
        width="100%", thickness=0.5,
        color=colors.HexColor("#e0e0e0"),
        spaceAfter=10, spaceBefore=6,
    )


# ── Charts ─────────────────────────────────────────────────────────
def _category_pie(breakdown):
    """Pie chart for spending by category."""
    if not breakdown:
        return Spacer(1, 0)

    sorted_cats = sorted(breakdown, key=lambda c: c.total, reverse=True)[:8]
    drawing = Drawing(280, 200)

    pie = Pie()
    pie.x = 40
    pie.y = 20
    pie.width = 150
    pie.height = 150
    pie.data = [c.total for c in sorted_cats]
    pie.labels = [c.label for c in sorted_cats]
    pie.sideLabels = True
    pie.slices.strokeWidth = 0.5
    pie.slices.strokeColor = WHITE

    for i, _ in enumerate(sorted_cats):
        pie.slices[i].fillColor = CHART_COLORS[i % len(CHART_COLORS)]
        pie.slices[i].fontColor = colors.HexColor("#333333")
        pie.slices[i].fontSize = 8

    drawing.add(pie)
    return drawing


def _monthly_bar(months):
    """Bar chart for monthly spending vs income."""
    if not months:
        return Spacer(1, 0)

    drawing = Drawing(450, 180)

    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 30
    chart.width = 370
    chart.height = 130

    chart.data = [
        [m.total_income for m in months],
        [m.total_spending for m in months],
    ]
    chart.categoryAxis.categoryNames = [m.month for m in months]
    chart.categoryAxis.labels.fontSize = 8
    chart.categoryAxis.labels.fillColor = colors.HexColor("#555555")

    chart.valueAxis.valueMin = 0
    chart.valueAxis.labels.fontSize = 8
    chart.valueAxis.labels.fillColor = colors.HexColor("#555555")

    chart.bars[0].fillColor = SUCCESS
    chart.bars[1].fillColor = DANGER
    chart.bars.strokeWidth = 0
    chart.barSpacing = 2
    chart.groupSpacing = 10

    # Legend
    drawing.add(chart)
    for i, (label, color) in enumerate([("Income", SUCCESS), ("Spending", DANGER)]):
        x_pos = 50 + i * 80
        drawing.add(Rect(x_pos, 170, 10, 10, fillColor=color, strokeWidth=0))
        drawing.add(String(x_pos + 14, 171, label, fontSize=8, fillColor=colors.HexColor("#555555")))

    return drawing


# ── Main generator ─────────────────────────────────────────────────
def generate_report(dashboard_data: Dict[str, Any], insights_data: Dict[str, Any]) -> bytes:
    """
    Generate a complete PDF report and return as bytes.
    """
    buffer = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=25 * mm, rightMargin=25 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
        title="Finance Analyzer Report",
        author="AI Finance Engine",
    )

    elements = []

    # ═══════════════════════════════════════════════════════════════
    # TITLE PAGE
    # ═══════════════════════════════════════════════════════════════
    elements.append(Spacer(1, 60))
    elements.append(Paragraph("Finance Analyzer", styles["Title"]))
    elements.append(Paragraph(
        f"AI-Powered Financial Analysis Report  •  {datetime.now().strftime('%B %d, %Y')}",
        styles["Subtitle"],
    ))
    elements.append(_hr())

    # ═══════════════════════════════════════════════════════════════
    # SUMMARY CARDS
    # ═══════════════════════════════════════════════════════════════
    cards = dashboard_data.get("summary_cards", [])
    if cards:
        card_data = []
        for c in cards:
            card_data.append([
                Paragraph(f"{c['icon']} {c['label']}", styles["BodySmall"]),
                Paragraph(str(c["value"]), styles["MetricValue"]),
                Paragraph(str(c.get("subtitle", "")), styles["MetricLabel"]),
            ])

        card_table = Table(
            [card_data[i] for i in range(len(card_data))],
            colWidths=[doc.width / len(card_data)] * len(card_data) if len(card_data) > 1 else [doc.width],
        )

        # Transpose: each card as a column
        rows = list(zip(*card_data)) if len(card_data) > 1 else [card_data]
        card_table = Table(
            rows,
            colWidths=[doc.width / len(cards)] * len(cards),
        )
        card_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
        ]))
        elements.append(card_table)
        elements.append(Spacer(1, 16))

    # ═══════════════════════════════════════════════════════════════
    # MONTHLY TRENDS CHART
    # ═══════════════════════════════════════════════════════════════
    trends_data = dashboard_data.get("_analysis_trends")
    if trends_data and hasattr(trends_data, "months"):
        elements.append(Paragraph("📊 Monthly Trends", styles["SectionHead"]))
        elements.append(_monthly_bar(trends_data.months))
        elements.append(Spacer(1, 8))

        # Trends table
        trend_rows = [["Month", "Income", "Spending", "Net", "Txns"]]
        for m in trends_data.months:
            trend_rows.append([
                m.month,
                f"₹{m.total_income:,.2f}",
                f"₹{m.total_spending:,.2f}",
                f"₹{m.net:,.2f}",
                str(m.transaction_count),
            ])

        trend_table = Table(trend_rows, colWidths=[80, 90, 90, 90, 50])
        trend_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#f5f5f5")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(trend_table)
        elements.append(Spacer(1, 16))

    # ═══════════════════════════════════════════════════════════════
    # CATEGORY BREAKDOWN
    # ═══════════════════════════════════════════════════════════════
    categories_data = dashboard_data.get("_analysis_categories")
    if categories_data and hasattr(categories_data, "breakdown"):
        elements.append(Paragraph("📂 Spending by Category", styles["SectionHead"]))
        elements.append(_category_pie(categories_data.breakdown))
        elements.append(Spacer(1, 8))

        cat_rows = [["Category", "Total", "Count", "Avg", "% of Spend"]]
        total_spend = sum(c.total for c in categories_data.breakdown if c.total > 0)
        for c in sorted(categories_data.breakdown, key=lambda x: x.total, reverse=True):
            if c.total <= 0:
                continue
            pct = (c.total / total_spend * 100) if total_spend > 0 else 0
            cat_rows.append([
                c.label,
                f"₹{c.total:,.2f}",
                str(c.count),
                f"₹{c.avg_per_transaction:,.2f}",
                f"{pct:.1f}%",
            ])

        cat_table = Table(cat_rows, colWidths=[110, 80, 50, 80, 70])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#f5f5f5")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(cat_table)

    elements.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════
    # FINANCIAL PROFILE
    # ═══════════════════════════════════════════════════════════════
    profile = insights_data.get("profile", {})
    if profile:
        elements.append(Paragraph("🧠 Financial Profile", styles["SectionHead"]))

        personality = (profile.get("personality") or "unknown").replace("_", " ").title()
        risk = (profile.get("risk_level") or "unknown").title()
        desc = profile.get("personality_description") or ""

        elements.append(Paragraph(
            f"<b>Personality:</b> {personality}  &nbsp;|&nbsp;  <b>Risk Level:</b> {risk}",
            styles["Body"],
        ))
        if desc:
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(desc, styles["BodySmall"]))
        elements.append(Spacer(1, 10))

        # Scores
        scores = profile.get("scores", {})
        if scores:
            score_rows = [["Metric", "Score"]]
            for key, label in [
                ("overall", "Overall Health"),
                ("savings", "Savings Discipline"),
                ("spending_control", "Spending Control"),
                ("consistency", "Consistency"),
                ("diversification", "Diversification"),
            ]:
                val = scores.get(key, 0)
                score_rows.append([label, f"{val}/100"])

            score_table = Table(score_rows, colWidths=[200, 80])
            score_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#f0fdf4")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(score_table)
            elements.append(Spacer(1, 12))

        # Strengths & Weaknesses
        strengths = profile.get("strengths", [])
        weaknesses = profile.get("weaknesses", [])

        if strengths:
            elements.append(Paragraph("💪 <b>Strengths</b>", styles["Body"]))
            for s in strengths:
                elements.append(Paragraph(f"  ✓  {s}", styles["BodySmall"]))
            elements.append(Spacer(1, 6))

        if weaknesses:
            elements.append(Paragraph("⚠️ <b>Areas to Improve</b>", styles["Body"]))
            for w in weaknesses:
                elements.append(Paragraph(f"  !  {w}", styles["BodySmall"]))
            elements.append(Spacer(1, 12))

    # ═══════════════════════════════════════════════════════════════
    # RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════════
    recs = insights_data.get("recommendations", [])
    if recs:
        elements.append(Paragraph("💡 Recommendations", styles["SectionHead"]))

        total_savings = insights_data.get("total_potential_savings", 0)
        if total_savings > 0:
            elements.append(Paragraph(
                f"<b>Total Potential Monthly Savings: ₹{total_savings:,.2f}</b>",
                ParagraphStyle("savings", parent=styles["Body"], textColor=SUCCESS, fontSize=12),
            ))
            elements.append(Spacer(1, 8))

        rec_rows = [["Priority", "Recommendation", "Potential Savings"]]
        for r in recs:
            icon = r.get("icon", "💡")
            title = r.get("title", "")
            desc = r.get("description", "")
            priority = (r.get("priority", "medium")).title()
            savings = r.get("potential_savings")
            savings_str = f"₹{savings:,.2f}/mo" if savings else "—"

            rec_rows.append([
                priority,
                f"{icon} {title}\n{desc}",
                savings_str,
            ])

        rec_table = Table(rec_rows, colWidths=[60, 300, 90])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#f5f5ff")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(rec_table)
        elements.append(Spacer(1, 12))

    # ═══════════════════════════════════════════════════════════════
    # ANOMALIES
    # ═══════════════════════════════════════════════════════════════
    anomalies = dashboard_data.get("top_anomalies", [])
    if anomalies:
        elements.append(Paragraph("🚨 Anomaly Alerts", styles["SectionHead"]))

        anom_rows = [["Date", "Description", "Amount", "Reason"]]
        for a in anomalies:
            anom_rows.append([
                str(a.get("date", a.get("transaction_date", "—"))),
                str(a.get("description", "—")),
                f"₹{a.get('amount', 0):,.2f}",
                str(a.get("reason", "—")),
            ])

        anom_table = Table(anom_rows, colWidths=[70, 140, 70, 170])
        anom_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DANGER),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e0e0e0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#fef2f2")]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(anom_table)

    # ═══════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════
    elements.append(Spacer(1, 30))
    elements.append(_hr())
    elements.append(Paragraph(
        f"Generated by Finance Analyzer  •  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ParagraphStyle("footer", parent=styles["BodySmall"], alignment=1, textColor=TEXT_MUTED),
    ))

    # Build
    doc.build(elements)
    return buffer.getvalue()
