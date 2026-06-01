"""Display formatters for muni bond API responses."""

from __future__ import annotations

from html import escape
from typing import Any


def fmt(v: Any) -> str:
    """Format a scalar value for display."""
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, float) and v == int(v):
        return f"{int(v):,}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def fmt_enum(v: Any) -> str:
    """Format an enum or list of enums: underscores → spaces, title-case."""
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, list):
        if not v:
            return "—"
        return ", ".join(str(x).replace("_", " ").title() for x in v)
    return str(v).replace("_", " ").title()


def fmt_list(v: list) -> str:
    """Format a list of proper names (no case-mangling)."""
    if not v:
        return "—"
    return ", ".join(str(x) for x in v)


def fmt_par(v: Any) -> str:
    """Format a dollar par value for display."""
    if v is None:
        return "—"
    n = float(v)
    if abs(n) >= 1_000_000_000:
        return f"${n / 1_000_000_000:,.2f}B"
    if abs(n) >= 1_000_000:
        return f"${n / 1_000_000:,.2f}M"
    return f"${n:,.0f}"


def fmt_coupon(v: Any) -> str:
    """Format a coupon rate or benchmark spread for search results."""
    if isinstance(v, (int, float)):
        return f"{v}%"
    if isinstance(v, dict):
        bm = v.get("benchmark", "")
        sp = v.get("spread_in_bps")
        return f"{sp}bps / {bm}" if sp else bm
    return "—"


def fmt_amount(v: float) -> str:
    """Format a cashflow amount."""
    return str(int(v)) if v == int(v) else f"{v:.2f}"


def stats_rows(rows: list[tuple[str, str]]) -> list[dict[str, str]]:
    """Build metric/value rows for stats table widgets."""
    return [{"metric": label, "value": value} for label, value in rows]


def ref_markdown(b: dict, cusip: str) -> str:
    """Render full reference data as a markdown table."""
    rows: list[str] = []
    open_table = False

    def section(title: str):
        nonlocal open_table
        if open_table:
            rows.append("</tbody></table>")
        rows.append(f"\n## {title}")
        rows.append("<table style='width:100%; border-collapse:collapse; text-align:left;'>")
        rows.append("<thead><tr><th style='text-align:left; padding:6px 4px; width:40%;'>Field</th><th style='text-align:left; padding:6px 4px;'>Value</th></tr></thead>")
        rows.append("<tbody>")
        open_table = True

    def row(label: str, value: str):
        rows.append(
            "<tr>"
            f"<td style='text-align:left; padding:6px 4px; vertical-align:top; width:40%;'>{escape(label)}</td>"
            f"<td style='text-align:left; padding:6px 4px; vertical-align:top;'>{escape(value)}</td>"
            "</tr>"
        )

    coupon = b.get("interest_rate")
    coupon_str = f"{fmt(coupon)}%" if coupon is not None else "—"

    section("Security Details")
    row("ISIN",              fmt(b.get("isin")))
    row("CUSIP",             cusip.upper())
    row("FIGI",              fmt(b.get("figi")))
    row("Ticker",            fmt(b.get("ticker")))
    row("Sector",            fmt_enum(b.get("sector")))
    row("Repayment",         fmt_enum(b.get("source_of_repayment")))
    row("Uses of Proceeds",  fmt_enum(b.get("use_categories")))
    row("Capital Purpose",   fmt_enum(b.get("capital_purpose")))
    row("Obligor",           fmt(b.get("obligor")))

    section("Key Dates")
    row("Maturity Date",  fmt(b.get("maturity_date")))
    row("Award Date",     fmt(b.get("award_date")))
    row("Closing Date",   fmt(b.get("closing_date")))
    row("Dated Date",     fmt(b.get("dated_date")))

    section("Features")
    row("Callable",     fmt(b.get("is_callable")))
    row("Sinking Fund", fmt(b.get("has_mandatory_redemption")))
    row("Insured",      fmt(b.get("is_insured")))

    section("Interest Details")
    row("Interest Type",         fmt_enum(b.get("interest_type")))
    row("Coupon Rate",           coupon_str)
    row("Coupons per Year",      fmt(b.get("coupon_frequency")))
    row("Interest Accrual Date", fmt(b.get("interest_accrual_date")))
    row("First Coupon Date",     fmt(b.get("first_interest_payment_date")))
    row("Next Coupon Date",      fmt(b.get("next_coupon_date")))
    row("Previous Coupon Date",  fmt(b.get("previous_coupon_date")))
    row("Day Count Convention",  fmt(b.get("interest_accrual_convention")))

    section("Amounts")
    row("Issued Amount",     fmt(b.get("issued_amount")))
    row("Outstanding Amount", fmt(b.get("outstanding_amount")))
    row("Series Amount",     fmt(b.get("series_issued_amount")))
    row("Min Denomination",  fmt(b.get("minimum_denomination")))
    row("Integral Multiple", fmt(b.get("integral_multiple")))

    section("Classifications")
    row("Green Bond",       fmt(b.get("is_green")))
    row("Social Bond",      fmt(b.get("is_social")))
    row("Sustainable Bond", fmt(b.get("is_sustainable")))

    section("Tax Status")
    row("State Taxable",     fmt(b.get("is_state_taxable")))
    row("Federally Taxable", fmt(b.get("is_federally_taxable")))
    row("AMT",               fmt(b.get("is_amt")))
    row("Bank Qualified",    fmt(b.get("is_bank_qualified")))

    section("Counterparties")
    row("Insurers",           fmt_list(b.get("insurers") or []))
    row("Underwriters",       fmt_list(b.get("underwriters") or []))
    row("Advisors",           fmt_list(b.get("advisors") or []))
    row("Bond Counsel",       fmt_list(b.get("bond_counsel") or []))
    row("Disclosure Counsel", fmt_list(b.get("disclosure_counsel") or []))
    row("Trustees",           fmt_list(b.get("trustees") or []))

    section("Credit Enhancement")
    row("Credit Enhanced",   fmt(b.get("is_credit_enhanced")))
    row("State Enhanced",    fmt(b.get("is_state_enhanced")))
    row("Guarantee",         fmt_enum(b.get("guarantee")))
    row("Enhancement Types", fmt_enum(b.get("credit_enhancement_type")))

    if open_table:
        rows.append("</tbody></table>")

    return "<div style='text-align:left;'>\n" + "\n".join(rows) + "\n</div>"


def cashflows_markdown(cashflows: list[dict]) -> str:
    """Render cashflow schedule as a markdown table."""
    lines = ["| Date | Amount | Type |", "|:---|---:|:---|"]
    for c in cashflows:
        lines.append(f"| {c['date']} | {fmt_amount(c['amount'])} | {c['type'].title()} |")
    body = "## Cashflows to Maturity\n\n" + "\n".join(lines)
    return "<div style='text-align:left;'>\n" + body + "\n</div>"
