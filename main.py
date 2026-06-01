import json
import os
from datetime import date, timedelta
from html import escape
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

from formatters import fmt, fmt_coupon, fmt_enum, fmt_par, cashflows_markdown, ref_markdown
from widgets import ALL_STATES, WIDGETS

load_dotenv()

TERRAPIN_API_KEY = os.getenv("TERRAPIN_API_KEY", "")
TERRAPIN_BASE_URL = "https://terrapinfinance.com"

app = FastAPI(title="Muni Bond App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pro.openbb.co",
        "https://pro.openbb.dev",
        "http://localhost:1420",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APPS_FILE = Path(__file__).parent / "apps.json"

_NO_CACHE_HEADERS = {"Cache-Control": "no-store, no-cache, must-revalidate", "Pragma": "no-cache"}

TRADE_TYPE_META = {
    "customer_bought": {"label": "Customer Bought", "color": "#2196F3"},
    "customer_sold":   {"label": "Customer Sold",   "color": "#F44336"},
    "inter_dealer":    {"label": "Inter-Dealer",    "color": "#9C27B0"},
}

MUNI_STATS_PERIODS = {"all", "day", "week", "month", "quarter", "year"}
MUNI_STATS_GROUP_BYS = {
    "none",
    "state",
    "source_of_repayment",
    "rating_group",
    "interest_type",
    "seniority",
    "capital_purpose",
    "use_sectors",
    "use_categories",
    "uses_of_proceeds",
    "is_federally_taxable",
    "is_amt",
    "is_bank_qualified",
    "is_insured",
    "is_green",
    "is_social",
    "is_sustainable",
    "is_pac",
}
OUTSTANDING_METRIC_KEYS = ["outstanding_par_value", "cusip_count", "entity_count"]
ISSUANCE_METRIC_KEYS = ["new_issuance_par_value", "new_cusip_count", "issuer_count"]
TRADE_ACTIVITY_METRIC_KEYS = [
    "trade_volume",
    "trade_count",
    "customer_bought_count",
    "customer_sold_count",
    "inter_dealer_count",
]
TRADE_ACTIVITY_METRIC_LABELS = {
    "trade_volume": "Trade Volume",
    "trade_count": "Trade Count",
    "customer_bought_count": "Customer Bought Count",
    "customer_sold_count": "Customer Sold Count",
    "inter_dealer_count": "Inter-Dealer Count",
}
ISSUANCE_METRIC_LABELS = {
    "new_issuance_par_value": "New Issuance Par Value",
    "new_cusip_count": "New CUSIP Count",
    "issuer_count": "Issuer Count",
}
TOP_ISSUERS_RANK_BY_KEYS = {
    "trade_volume",
    "trade_count",
    "traded_cusip_count",
    "new_issuance_par_value",
    "new_cusip_count",
}
TOP_ISSUERS_RANK_BY_LABELS = {
    "trade_volume": "Trade Volume",
    "trade_count": "Trade Count",
    "traded_cusip_count": "Traded CUSIPs",
    "new_issuance_par_value": "New Issuance Par Value",
    "new_cusip_count": "New CUSIP Count",
}
OUTSTANDING_METRIC_LABELS = {
    "outstanding_par_value": "Outstanding Par Value",
    "cusip_count": "CUSIP Count",
    "entity_count": "Entity Count",
}
OUTPUT_MODES = {"raw", "chart"}
PERIOD_TITLE_LABELS = {
    "all": "All Periods",
    "day": "Day",
    "week": "Week",
    "month": "Month",
    "quarter": "Quarter",
    "year": "Year",
}


# ---------------------------------------------------------------------------
# Terrapin API helpers
# ---------------------------------------------------------------------------

def terrapin_headers() -> dict:
    return {
        "Authorization": f"Bearer {TERRAPIN_API_KEY}",
        "Content-Type": "application/json",
    }


def cusip_to_isin(cusip: str) -> str:
    cusip = cusip.strip().upper()
    with httpx.Client(timeout=15) as client:
        resp = client.post(
            f"{TERRAPIN_BASE_URL}/api/v1/convert_to_isin",
            headers=terrapin_headers(),
            json={"identifiers": [cusip]},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    isin = resp.json()["data"][0]["isin"]
    if isin is None:
        raise HTTPException(status_code=422, detail=f"'{cusip}' is not a valid CUSIP.")
    return isin


def _csv(v: Optional[str]) -> list:
    return [x.strip() for x in v.split(",") if x.strip()] if v else []


def _build_muni_stats_filters(
    states: Optional[str] = None,
    sources_of_repayment: Optional[str] = None,
    sectors: Optional[str] = None,
    interest_types: Optional[str] = None,
    use_categories: Optional[str] = None,
    uses_of_proceeds: Optional[str] = None,
    rating_group: Optional[str] = None,
    seniority: Optional[str] = None,
    capital_purpose: Optional[str] = None,
    is_federally_taxable: Optional[bool] = None,
    is_amt: Optional[bool] = None,
    is_bank_qualified: Optional[bool] = None,
    is_insured: Optional[bool] = None,
    is_green: Optional[bool] = None,
    is_social: Optional[bool] = None,
    is_sustainable: Optional[bool] = None,
    is_pac: Optional[bool] = None,
) -> dict:
    body: dict = {}
    if sl := [s for s in _csv(states) if s.upper() != ALL_STATES]:
        body["states"] = sl
    if sr := _csv(sources_of_repayment):
        body["sources_of_repayment"] = sr
    if sc := _csv(sectors):
        body["use_sectors"] = sc
    if it := _csv(interest_types):
        body["interest_types"] = it
    if uc := _csv(use_categories):
        body["use_categories"] = uc
    if uop := _csv(uses_of_proceeds):
        body["uses_of_proceeds"] = uop
    if rating_group:
        body["rating_group"] = rating_group
    if sn := _csv(seniority):
        body["seniority"] = sn
    if cp := _csv(capital_purpose):
        body["capital_purpose"] = cp
    if is_federally_taxable is not None:
        body["is_federally_taxable"] = is_federally_taxable
    if is_amt is not None:
        body["is_amt"] = is_amt
    if is_bank_qualified is not None:
        body["is_bank_qualified"] = is_bank_qualified
    if is_insured is not None:
        body["is_insured"] = is_insured
    if is_green is not None:
        body["is_green"] = is_green
    if is_social is not None:
        body["is_social"] = is_social
    if is_sustainable is not None:
        body["is_sustainable"] = is_sustainable
    if is_pac is not None:
        body["is_pac"] = is_pac
    return body


def _stats_filters_query(
    states: Optional[str] = Query(None),
    sources_of_repayment: Optional[str] = Query(None),
    sectors: Optional[str] = Query(None),
    interest_types: Optional[str] = Query(None),
    use_categories: Optional[str] = Query(None),
    uses_of_proceeds: Optional[str] = Query(None),
    rating_group: Optional[str] = Query(None),
    seniority: Optional[str] = Query(None),
    capital_purpose: Optional[str] = Query(None),
    is_federally_taxable: Optional[bool] = Query(None),
    is_amt: Optional[bool] = Query(None),
    is_bank_qualified: Optional[bool] = Query(None),
    is_insured: Optional[bool] = Query(None),
    is_green: Optional[bool] = Query(None),
    is_social: Optional[bool] = Query(None),
    is_sustainable: Optional[bool] = Query(None),
    is_pac: Optional[bool] = Query(None),
) -> dict:
    return {
        "states": states,
        "sources_of_repayment": sources_of_repayment,
        "sectors": sectors,
        "interest_types": interest_types,
        "use_categories": use_categories,
        "uses_of_proceeds": uses_of_proceeds,
        "rating_group": rating_group,
        "seniority": seniority,
        "capital_purpose": capital_purpose,
        "is_federally_taxable": is_federally_taxable,
        "is_amt": is_amt,
        "is_bank_qualified": is_bank_qualified,
        "is_insured": is_insured,
        "is_green": is_green,
        "is_social": is_social,
        "is_sustainable": is_sustainable,
        "is_pac": is_pac,
    }


def _post_muni_stats_rows(endpoint: str, body: dict) -> list[dict]:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{TERRAPIN_BASE_URL}/api/v1/{endpoint}",
            headers=terrapin_headers(),
            json=body,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    data = resp.json().get("data", [])
    if not data:
        raise HTTPException(status_code=404, detail="No statistics found for the selected filters.")
    return data


def _validated_period(period: Optional[str]) -> str:
    p = (period or "all").strip().lower()
    if p not in MUNI_STATS_PERIODS:
        raise HTTPException(status_code=422, detail=f"Invalid period '{period}'.")
    return p


def _metric_period_title(metric_label: str, period: str) -> str:
    period_label = PERIOD_TITLE_LABELS.get(period, period.title())
    return f"{metric_label} by {period_label}"


def _validated_group_by(group_by: Optional[str]) -> str:
    g = (group_by or "none").strip().lower()
    if g not in MUNI_STATS_GROUP_BYS:
        raise HTTPException(status_code=422, detail=f"Invalid group_by '{group_by}'.")
    return g


def _group_by_for_api(group_by: str) -> str:
    return group_by


def _validated_rank_by(rank_by: Optional[str]) -> str:
    r = (rank_by or "trade_volume").strip().lower()
    if r not in TOP_ISSUERS_RANK_BY_KEYS:
        raise HTTPException(status_code=422, detail=f"Invalid rank_by '{rank_by}'.")
    return r


def _validated_output_mode(output: Optional[str]) -> str:
    o = (output or "raw").strip().lower()
    if o not in OUTPUT_MODES:
        raise HTTPException(status_code=422, detail=f"Invalid output '{output}'. Use 'raw' or 'chart'.")
    return o


def _selected_metric_keys(metrics: Optional[str], allowed_keys: list[str]) -> list[str]:
    selected = _csv(metrics)
    if not selected:
        return allowed_keys

    allowed_set = set(allowed_keys)
    invalid = [m for m in selected if m not in allowed_set]
    if invalid:
        raise HTTPException(status_code=422, detail=f"Invalid metrics: {', '.join(invalid)}.")

    deduped = []
    seen = set()
    for m in selected:
        if m not in seen:
            deduped.append(m)
            seen.add(m)
    if len(deduped) > 1:
        raise HTTPException(status_code=422, detail="Please select only one metric.")
    return deduped


def _categorical_bar_chart(
    rows: list[dict],
    *,
    metric_key: str,
    metric_label: str,
    group_by: str,
    theme: str = "dark",
    title: Optional[str] = None,
) -> dict:
    if not rows:
        return {"data": [], "layout": {}}

    x_axis = []
    y_vals = []
    for r in rows:
        if group_by != "none":
            x_val = str(r.get("group_key") if r.get("group_key") is not None else "undefined")
        else:
            x_val = "all"
        x_axis.append(x_val)
        y_vals.append(float(r.get(metric_key) or 0))

    is_dark = theme.strip().lower() == "dark"
    bg_color = "#151518" if is_dark else "#FFFFFF"
    grid_color = "#2A2A2A" if is_dark else "#E5E7EB"
    text_color = "#CCCCCC" if is_dark else "#1F2937"
    title_color = "#FFFFFF" if is_dark else "#000000"

    annotations = []
    if title and title.strip():
        annotations.append(
            {
                "text": f"<b>{title.strip()}</b>",
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": 1.1,
                "xanchor": "left",
                "yanchor": "bottom",
                "showarrow": False,
                "font": {"color": title_color, "size": 25},
                "yshift": 8,
            }
        )

    return {
        "data": [
            {
                "type": "bar",
                "name": metric_label,
                "x": x_axis,
                "y": y_vals,
                "hovertemplate": "<b>%{x}</b><br>" + metric_label + ": %{y:,.2f}<extra></extra>",
            }
        ],
        "layout": {
            "plot_bgcolor": bg_color,
            "paper_bgcolor": bg_color,
            "font": {"color": text_color},
            "xaxis": {
                "title": {"text": ""},
                "gridcolor": grid_color,
                "linecolor": grid_color,
                "tickfont": {"color": text_color},
            },
            "yaxis": {
                "title": {"text": metric_label},
                "gridcolor": grid_color,
                "linecolor": grid_color,
                "tickfont": {"color": text_color},
            },
            "hovermode": "x unified",
            "annotations": annotations,
        },
    }


def _stacked_bar_chart(
    rows: list[dict],
    *,
    metric_key: str,
    metric_label: str,
    period: str,
    group_by: str,
    theme: str = "dark",
    title: Optional[str] = None,
) -> dict:
    if not rows:
        return {"data": [], "layout": {}}

    x_axis: list[str] = []
    grouped: dict[str, dict[str, float]] = {}
    for r in rows:
        x = str(r.get("period") or "all")
        if x not in x_axis:
            x_axis.append(x)
        group = str(r.get("group_key")) if group_by != "none" and r.get("group_key") is not None else "undefined"
        grouped.setdefault(group, {})
        grouped[group][x] = float(r.get(metric_key) or 0)

    traces = []
    for group, values in grouped.items():
        traces.append(
            {
                "type": "bar",
                "name": group,
                "x": x_axis,
                "y": [values.get(x, 0) for x in x_axis],
                "hovertemplate": "<b>%{x}</b><br>" + metric_label + ": %{y:,.2f}<extra>" + group + "</extra>",
            }
        )

    is_dark = theme.strip().lower() == "dark"
    bg_color = "#151518" if is_dark else "#FFFFFF"
    grid_color = "#2A2A2A" if is_dark else "#E5E7EB"
    text_color = "#CCCCCC" if is_dark else "#1F2937"
    title_color = "#FFFFFF" if is_dark else "#000000"

    annotations = []
    if title and title.strip():
        annotations.append(
            {
                "text": f"<b>{title.strip()}</b>",
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": 1.1,
                "xanchor": "left",
                "yanchor": "bottom",
                "showarrow": False,
                "font": {"color": title_color, "size": 25},
                "yshift": 8,
            }
        )

    return {
        "data": traces,
        "layout": {
            "barmode": "stack",
            "plot_bgcolor": bg_color,
            "paper_bgcolor": bg_color,
            "font": {"color": text_color},
            "xaxis": {
                "title": {"text": ""},
                "gridcolor": grid_color,
                "linecolor": grid_color,
                "tickfont": {"color": text_color},
            },
            "yaxis": {
                "title": {"text": metric_label},
                "gridcolor": grid_color,
                "linecolor": grid_color,
                "tickfont": {"color": text_color},
            },
            "legend": {"orientation": "h", "y": -0.2, "font": {"color": text_color}},
            "hovermode": "x unified",
            "annotations": annotations,
        },
    }


# ---------------------------------------------------------------------------
# Manifest endpoints
# ---------------------------------------------------------------------------

@app.get("/widgets.json")
def get_widgets():
    return JSONResponse(content=WIDGETS, headers=_NO_CACHE_HEADERS)


@app.get("/apps.json")
def get_apps():
    with open(APPS_FILE, encoding="utf-8") as f:
        return JSONResponse(content=json.load(f), headers=_NO_CACHE_HEADERS)


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------

@app.get("/muni/reference")
def muni_reference(cusip: str = Query(..., description="9-character CUSIP")):
    isin = cusip_to_isin(cusip)

    with httpx.Client(timeout=15) as client:
        resp = client.post(
            f"{TERRAPIN_BASE_URL}/api/v1/muni_reference",
            headers=terrapin_headers(),
            json={"isins": [isin]},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json().get("data", [])
    if not data:
        raise HTTPException(status_code=404, detail="No reference data found.")

    return PlainTextResponse(ref_markdown(data[0], cusip))


# ---------------------------------------------------------------------------
# Pricing history chart
# ---------------------------------------------------------------------------

@app.get("/muni/pricing_chart")
def muni_pricing_chart(
    cusip: str = Query(..., description="9-character CUSIP"),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    raw: bool = Query(False),
    theme: str = Query("dark", description="OpenBB workspace theme (dark/light)"),
):
    today = date.today()
    if not end_date:
        end_date = today.isoformat()
    if not start_date:
        start_date = (today - timedelta(days=365)).isoformat()

    isin = cusip_to_isin(cusip)

    with httpx.Client(timeout=20) as client:
        resp = client.post(
            f"{TERRAPIN_BASE_URL}/api/v1/muni_pricing_history",
            headers=terrapin_headers(),
            json={"isin": isin, "start_date": start_date, "end_date": end_date},
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    trades = resp.json().get("data", [])

    if raw:
        return trades

    if not trades:
        return {"data": [], "layout": {}}

    trades = sorted(trades, key=lambda t: t["trade_datetime"])

    buckets: dict[str, dict] = {}
    for t in trades:
        tt = t.get("trade_type", "unknown")
        meta = TRADE_TYPE_META.get(tt, {"label": tt.replace("_", " ").title(), "color": "#78909C"})
        if tt not in buckets:
            buckets[tt] = {"x": [], "y": [], "customdata": [], "label": meta["label"], "color": meta["color"]}
        ytm = t.get("ytm_semi_annual")
        amt = t.get("amount")
        buckets[tt]["x"].append(t["trade_datetime"])
        buckets[tt]["y"].append(t["price"])
        buckets[tt]["customdata"].append([
            f"{ytm:.4f}%" if ytm is not None else "n/a",
            f"{int(amt):,}" if amt is not None else "n/a",
        ])

    traces = [
        {
            "type": "scatter",
            "mode": "markers",
            "name": b["label"],
            "x": b["x"],
            "y": b["y"],
            "customdata": b["customdata"],
            "marker": {"size": 8, "color": b["color"], "opacity": 0.85},
            "hovertemplate": (
                "<b>%{x|%Y-%m-%d %H:%M}</b><br>"
                "Price: %{y:.3f}<br>"
                "MSRB Yield: %{customdata[0]}<br>"
                "Volume: %{customdata[1]}"
                "<extra>" + b["label"] + "</extra>"
            ),
        }
        for b in buckets.values()
    ]

    is_dark = theme.strip().lower() == "dark"
    bg_color = "#151518" if is_dark else "#FFFFFF"
    grid_color = "#2A2A2A" if is_dark else "#E5E7EB"
    text_color = "#CCCCCC" if is_dark else "#1F2937"
    title_color = "#FFFFFF" if is_dark else "#000000"

    return {
        "data": traces,
        "layout": {
            "plot_bgcolor": bg_color,
            "paper_bgcolor": bg_color,
            "font": {"color": text_color},
            "xaxis": {"title": {"text": "Trade Date"}, "gridcolor": grid_color, "linecolor": grid_color, "tickfont": {"color": text_color}},
            "yaxis": {"title": {"text": "Price"}, "gridcolor": grid_color, "linecolor": grid_color, "tickfont": {"color": text_color}},
            "legend": {"orientation": "h", "y": -0.15, "font": {"color": text_color}},
            "hovermode": "closest",
        },
    }


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

@app.get("/muni/documents/options")
def muni_documents_options(cusip: str = Query(..., description="9-character CUSIP")):
    """Returns [{label, value}] for the multi_file_viewer file selector."""
    isin = cusip_to_isin(cusip)
    rows = []
    with httpx.Client(timeout=15) as client:
        for doc_type in ("official_statement", "disclosure_document"):
            resp = client.post(
                f"{TERRAPIN_BASE_URL}/api/v1/muni_documents",
                headers=terrapin_headers(),
                json={"isin": isin, "document_type": doc_type},
            )
            if resp.status_code == 200:
                rows.extend(resp.json().get("data", []))
    rows.sort(key=lambda d: d.get("publish_date") or "", reverse=True)
    return [
        {"label": d["document_name"], "value": d["file_id"], "_date": d.get("publish_date") or ""}
        for d in rows if d.get("file_id")
    ]


# ---------------------------------------------------------------------------
# Cashflows
# ---------------------------------------------------------------------------

@app.get("/muni/cashflows")
def muni_cashflows(cusip: str = Query(..., description="9-character CUSIP")):
    isin = cusip_to_isin(cusip)

    with httpx.Client(timeout=15) as client:
        cf_resp = client.post(
            f"{TERRAPIN_BASE_URL}/api/v1/muni_cashflows",
            headers=terrapin_headers(),
            json={"isins": [isin]},
        )

    if cf_resp.status_code != 200:
        raise HTTPException(status_code=cf_resp.status_code, detail=cf_resp.text)

    cf_data = cf_resp.json().get("data", [])
    if not cf_data:
        return PlainTextResponse("No cashflow data available.")

    cashflows = sorted(cf_data[0]["cashflows"], key=lambda c: (c["date"], c["type"]))
    return PlainTextResponse(cashflows_markdown(cashflows))


# ---------------------------------------------------------------------------
# Bond search
# ---------------------------------------------------------------------------

@app.get("/muni/search")
def muni_search(
    issuer_name: Optional[str] = Query(None),
    states: Optional[str] = Query(None),
    sectors: Optional[str] = Query(None),
    coupon_min: Optional[float] = Query(None),
    coupon_max: Optional[float] = Query(None),
    maturity_date_min: Optional[str] = Query(None),
    maturity_date_max: Optional[str] = Query(None),
    interest_types: Optional[str] = Query(None),
    sources_of_repayment: Optional[str] = Query(None),
    is_insured: Optional[bool] = Query(None),
    include_callable: Optional[bool] = Query(None),
    last_traded_since: Optional[str] = Query(None),
    limit: int = Query(100),
):
    body: dict = {"limit": limit, "sort": ["-issue_date"]}
    if issuer_name:                                body["issuer_name"] = issuer_name
    if sl := [s for s in _csv(states) if s.upper() != ALL_STATES]: body["states"] = sl
    if sc := _csv(sectors):                         body["sectors"] = sc
    if coupon_min is not None:                     body["coupon_min"] = coupon_min
    if coupon_max is not None:                     body["coupon_max"] = coupon_max
    if maturity_date_min:                          body["maturity_date_min"] = maturity_date_min
    if maturity_date_max:                          body["maturity_date_max"] = maturity_date_max
    if it := _csv(interest_types):                  body["interest_types"] = it
    if sr := _csv(sources_of_repayment):            body["sources_of_repayment"] = sr
    if is_insured is not None:                     body["is_insured"] = is_insured
    if include_callable is not None:               body["include_callable"] = include_callable
    if last_traded_since:                          body["last_traded_since"] = last_traded_since

    with httpx.Client(timeout=20) as client:
        resp = client.post(
            f"{TERRAPIN_BASE_URL}/api/v1/muni_search",
            headers=terrapin_headers(),
            json=body,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return [
        {
            "cusip":           b["isin"][2:11],
            "ticker":          b.get("ticker") or "—",
            "issuer_name":     b.get("issuer_name") or "—",
            "state":           b.get("state") or "—",
            "coupon":          fmt_coupon(b.get("interest_rate")),
            "interest_type":   fmt_enum(b.get("interest_type")),
            "maturity_date":   b.get("maturity_date") or "—",
            "callable":        "Yes" if b.get("is_callable") else "No",
            "rating":          fmt_enum(b.get("rating_group")),
        }
        for b in resp.json().get("data", [])
    ]


# ---------------------------------------------------------------------------
# Market statistics
# ---------------------------------------------------------------------------

@app.get("/muni/stats/filters_summary")
def muni_stats_filters_summary(
    filters: dict = Depends(_stats_filters_query),
):
    states = filters["states"]
    sources_of_repayment = filters["sources_of_repayment"]
    sectors = filters["sectors"]
    use_categories = filters["use_categories"]
    uses_of_proceeds = filters["uses_of_proceeds"]
    rating_group = filters["rating_group"]
    interest_types = filters["interest_types"]
    seniority = filters["seniority"]
    capital_purpose = filters["capital_purpose"]
    is_federally_taxable = filters["is_federally_taxable"]
    is_amt = filters["is_amt"]
    is_bank_qualified = filters["is_bank_qualified"]
    is_insured = filters["is_insured"]
    is_green = filters["is_green"]
    is_social = filters["is_social"]
    is_sustainable = filters["is_sustainable"]
    is_pac = filters["is_pac"]

    states_value = ", ".join([s for s in _csv(states) if s.upper() != ALL_STATES]) if states else "All States"
    sources_value = ", ".join(_csv(sources_of_repayment)) if sources_of_repayment else "All"
    sectors_value = ", ".join(_csv(sectors)) if sectors else "All"
    categories_value = ", ".join(_csv(use_categories)) if use_categories else "All"
    proceeds_value = ", ".join(_csv(uses_of_proceeds)) if uses_of_proceeds else "All"
    interest_value = ", ".join(_csv(interest_types)) if interest_types else "All"
    seniority_value = ", ".join(_csv(seniority)) if seniority else "All"
    capital_value = ", ".join(_csv(capital_purpose)) if capital_purpose else "All"
    rating_value = rating_group or "All"
    yn = lambda v: "Yes" if v is True else "No"
    non_boolean_cells = [
        ("States", states_value),
        ("Source of Repayment", sources_value),
        ("Use Sectors", sectors_value),
        ("Use Categories", categories_value),
        ("Uses of Proceeds", proceeds_value),
        ("Rating Group", rating_value),
        ("Interest Types", interest_value),
        ("Seniority", seniority_value),
        ("Capital Purpose", capital_value),
    ]
    boolean_cells = []
    for label, value in [
        ("Federally Taxable", is_federally_taxable),
        ("AMT", is_amt),
        ("Bank Qualified", is_bank_qualified),
        ("Insured", is_insured),
        ("Green", is_green),
        ("Social", is_social),
        ("Sustainable", is_sustainable),
        ("PAC", is_pac),
    ]:
        if value is not None:
            boolean_cells.append((label, yn(value)))
    if not boolean_cells:
        boolean_cells = [("Boolean Filters", "None")]

    def _row(items: list[tuple[str, str]]) -> str:
        return "<tr>" + "".join(
            (
                "<td style='text-align:left; vertical-align:top; padding:6px 10px; border-bottom:1px solid rgba(120,140,170,0.25);'>"
                f"<strong>{escape(label)}:</strong> {escape(value)}"
                "</td>"
            )
            if label
            else "<td style='padding:6px 10px;'></td>"
            for label, value in items
        ) + "</tr>"

    markdown = "\n".join(
        [
            "### Active Shared Filters",
            "",
            "<table style='width:100%; border-collapse:collapse; text-align:left;'>",
            "<tbody>",
            _row(non_boolean_cells),
            _row(boolean_cells),
            "</tbody>",
            "</table>",
            "",
            "These filters are shared across the Market Activity widgets below.",
        ]
    )
    return PlainTextResponse(markdown)


@app.get("/muni/stats/outstanding")
def muni_stats_outstanding(
    metrics: Optional[str] = Query(None, description="Single metric key"),
    output: str = Query("raw", description="Response mode: raw rows or chart"),
    group_by: str = Query("none"),
    filters: dict = Depends(_stats_filters_query),
    theme: str = Query("dark", description="OpenBB workspace theme (dark/light)"),
    title: Optional[str] = Query(None, description="Optional chart title annotation"),
):
    output = _validated_output_mode(output)
    group_by = _validated_group_by(group_by)
    api_group_by = _group_by_for_api(group_by)
    metric_key = _selected_metric_keys(metrics, OUTSTANDING_METRIC_KEYS)[0]
    body = _build_muni_stats_filters(**filters)
    body["group_by"] = api_group_by

    rows = _post_muni_stats_rows("muni_stats_outstanding", body)
    raw_rows = [
        {
            **({"group_key": r.get("group_key")} if group_by != "none" and r.get("group_key") is not None else {}),
            metric_key: r.get(metric_key),
        }
        for r in rows
    ]
    if output == "chart":
        return _categorical_bar_chart(
            raw_rows,
            metric_key=metric_key,
            metric_label=OUTSTANDING_METRIC_LABELS[metric_key],
            group_by=group_by,
            theme=theme,
            title=title,
        )
    return raw_rows


@app.get("/muni/stats/issuance")
def muni_stats_issuance(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    metrics: Optional[str] = Query(None, description="Single metric key"),
    output: str = Query("raw", description="Response mode: raw rows or chart"),
    period: str = Query("month"),
    group_by: str = Query("none"),
    filters: dict = Depends(_stats_filters_query),
    theme: str = Query("dark", description="OpenBB workspace theme (dark/light)"),
    title: Optional[str] = Query(None, description="Optional chart title annotation"),
):
    output = _validated_output_mode(output)
    period = _validated_period(period)
    group_by = _validated_group_by(group_by)
    api_group_by = _group_by_for_api(group_by)
    metric_key = _selected_metric_keys(metrics, ISSUANCE_METRIC_KEYS)[0]
    body = _build_muni_stats_filters(**filters)
    body["start_date"] = start_date
    body["end_date"] = end_date
    body["period"] = period
    body["group_by"] = api_group_by

    rows = _post_muni_stats_rows("muni_stats_issuance", body)
    raw_rows = [
        {
            **({"period": r.get("period")} if period != "all" and r.get("period") is not None else {}),
            **({"group_key": r.get("group_key")} if period != "all" and group_by != "none" and r.get("group_key") is not None else {}),
            metric_key: r.get(metric_key),
        }
        for r in rows
    ]
    if output == "chart":
        dynamic_title = _metric_period_title(ISSUANCE_METRIC_LABELS[metric_key], period)
        resolved_title = title.strip() if title and title.strip() else dynamic_title
        return _stacked_bar_chart(
            rows,
            metric_key=metric_key,
            metric_label=ISSUANCE_METRIC_LABELS[metric_key],
            period=period,
            group_by=group_by,
            theme=theme,
            title=resolved_title,
        )
    return raw_rows


@app.get("/muni/stats/trade_activity")
def muni_stats_trade_activity(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    metrics: Optional[str] = Query(None, description="Single metric key"),
    output: str = Query("raw", description="Response mode: raw rows or chart"),
    period: str = Query("month"),
    group_by: str = Query("none"),
    filters: dict = Depends(_stats_filters_query),
    theme: str = Query("dark", description="OpenBB workspace theme (dark/light)"),
    title: Optional[str] = Query(None, description="Optional chart title annotation"),
):
    output = _validated_output_mode(output)
    period = _validated_period(period)
    group_by = _validated_group_by(group_by)
    api_group_by = _group_by_for_api(group_by)
    metric_key = _selected_metric_keys(metrics, TRADE_ACTIVITY_METRIC_KEYS)[0]
    body = _build_muni_stats_filters(**filters)
    body["start_date"] = start_date
    body["end_date"] = end_date
    body["period"] = period
    body["group_by"] = api_group_by

    rows = _post_muni_stats_rows("muni_stats_trade_activity", body)
    raw_rows = [
        {
            **({"period": r.get("period")} if period != "all" and r.get("period") is not None else {}),
            **({"group_key": r.get("group_key")} if period != "all" and group_by != "none" and r.get("group_key") is not None else {}),
            metric_key: r.get(metric_key),
        }
        for r in rows
    ]
    if output == "chart":
        dynamic_title = _metric_period_title(TRADE_ACTIVITY_METRIC_LABELS[metric_key], period)
        resolved_title = title.strip() if title and title.strip() else dynamic_title
        return _stacked_bar_chart(
            rows,
            metric_key=metric_key,
            metric_label=TRADE_ACTIVITY_METRIC_LABELS[metric_key],
            period=period,
            group_by=group_by,
            theme=theme,
            title=resolved_title,
        )
    return raw_rows


@app.get("/muni/stats/issuance_chart")
def muni_stats_issuance_chart(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    metrics: Optional[str] = Query(None, description="Single metric key"),
    period: str = Query("month"),
    group_by: str = Query("none"),
    filters: dict = Depends(_stats_filters_query),
    title: Optional[str] = Query(None, description="Optional chart title annotation"),
    theme: str = Query("dark", description="OpenBB workspace theme (dark/light)"),
):
    period = _validated_period(period)
    group_by = _validated_group_by(group_by)
    api_group_by = _group_by_for_api(group_by)
    metric_key = _selected_metric_keys(metrics, ISSUANCE_METRIC_KEYS)[0]

    body = _build_muni_stats_filters(**filters)
    body.update({"start_date": start_date, "end_date": end_date, "period": period, "group_by": api_group_by})
    rows = _post_muni_stats_rows("muni_stats_issuance", body)
    dynamic_title = _metric_period_title(ISSUANCE_METRIC_LABELS[metric_key], period)
    resolved_title = title.strip() if title and title.strip() else dynamic_title
    return _stacked_bar_chart(
        rows,
        metric_key=metric_key,
        metric_label=ISSUANCE_METRIC_LABELS[metric_key],
        period=period,
        group_by=group_by,
        theme=theme,
        title=resolved_title,
    )


@app.get("/muni/stats/trade_activity_chart")
def muni_stats_trade_activity_chart(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    metrics: Optional[str] = Query(None, description="Single metric key"),
    period: str = Query("month"),
    group_by: str = Query("none"),
    filters: dict = Depends(_stats_filters_query),
    title: Optional[str] = Query(None, description="Optional chart title annotation"),
    theme: str = Query("dark", description="OpenBB workspace theme (dark/light)"),
):
    period = _validated_period(period)
    group_by = _validated_group_by(group_by)
    api_group_by = _group_by_for_api(group_by)
    metric_key = _selected_metric_keys(metrics, TRADE_ACTIVITY_METRIC_KEYS)[0]

    body = _build_muni_stats_filters(**filters)
    body.update({"start_date": start_date, "end_date": end_date, "period": period, "group_by": api_group_by})
    rows = _post_muni_stats_rows("muni_stats_trade_activity", body)
    dynamic_title = _metric_period_title(TRADE_ACTIVITY_METRIC_LABELS[metric_key], period)
    resolved_title = title.strip() if title and title.strip() else dynamic_title
    return _stacked_bar_chart(
        rows,
        metric_key=metric_key,
        metric_label=TRADE_ACTIVITY_METRIC_LABELS[metric_key],
        period=period,
        group_by=group_by,
        theme=theme,
        title=resolved_title,
    )


@app.get("/muni/stats/top_issuers")
def muni_stats_top_issuers(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    rank_by: str = Query("trade_volume"),
    limit: int = Query(25),
    filters: dict = Depends(_stats_filters_query),
):
    rank_by = _validated_rank_by(rank_by)
    body = _build_muni_stats_filters(**filters)
    body.update({"start_date": start_date, "end_date": end_date, "rank_by": rank_by, "limit": limit})

    rows = _post_top_issuers_rows(body)
    return [
        {
            "rank":                   i + 1,
            "issuer_name":            r.get("issuer_name") or "—",
            "trade_volume":           fmt_par(r.get("trade_volume")),
            "trade_count":            fmt(r.get("trade_count")),
            "traded_cusip_count":     fmt(r.get("traded_cusip_count")),
            "new_issuance_par_value": fmt_par(r.get("new_issuance_par_value")),
            "new_cusip_count":        fmt(r.get("new_cusip_count")),
            "last_trade_date":        r.get("last_trade_date") or "—",
        }
        for i, r in enumerate(rows)
    ]


def _post_top_issuers_rows(body: dict) -> list[dict]:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{TERRAPIN_BASE_URL}/api/v1/muni_stats_top_issuers",
            headers=terrapin_headers(),
            json=body
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    rows = resp.json().get("data", [])
    if not rows:
        raise HTTPException(status_code=404, detail="No top issuers found for the selected filters.")
    return rows


@app.get("/muni/stats/top_issuers_chart")
def muni_stats_top_issuers_chart(
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD"),
    rank_by: str = Query("trade_volume"),
    limit: int = Query(25),
    filters: dict = Depends(_stats_filters_query),
    title: Optional[str] = Query(None, description="Optional chart title annotation"),
    theme: str = Query("dark", description="OpenBB workspace theme (dark/light)"),
):
    rank_by = _validated_rank_by(rank_by)
    body = _build_muni_stats_filters(**filters)
    body.update({"start_date": start_date, "end_date": end_date, "rank_by": rank_by, "limit": limit})

    rows = _post_top_issuers_rows(body)
    x_axis = [r.get("issuer_name") or "—" for r in rows]
    y_axis = [float(r.get(rank_by) or 0) for r in rows]

    is_dark = theme.strip().lower() == "dark"
    bg_color = "#151518" if is_dark else "#FFFFFF"
    grid_color = "#2A2A2A" if is_dark else "#E5E7EB"
    text_color = "#CCCCCC" if is_dark else "#1F2937"
    title_color = "#FFFFFF" if is_dark else "#000000"

    dynamic_title = f"Top Issuers by {TOP_ISSUERS_RANK_BY_LABELS[rank_by]}"
    resolved_title = title.strip() if title and title.strip() else dynamic_title

    annotations = []
    if resolved_title:
        annotations.append(
            {
                "text": f"<b>{resolved_title}</b>",
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": 1,
                "xanchor": "left",
                "yanchor": "bottom",
                "showarrow": False,
                "font": {"color": title_color, "size": 20},
                "yshift": 8,
            }
        )

    return {
        "data": [
            {
                "type": "bar",
                "orientation": "h",
                "x": y_axis,
                "y": x_axis,
                "hovertemplate": "<b>%{y}</b><br>" + TOP_ISSUERS_RANK_BY_LABELS[rank_by] + ": %{x:,.2f}<extra></extra>",
            }
        ],
        "layout": {
            "plot_bgcolor": bg_color,
            "paper_bgcolor": bg_color,
            "font": {"color": text_color},
            "xaxis": {
                "title": {"text": ""},
                "gridcolor": grid_color,
                "linecolor": grid_color,
                "tickfont": {"color": text_color},
            },
            "yaxis": {
                "title": {"text": ""},
                "gridcolor": grid_color,
                "linecolor": grid_color,
                "tickfont": {"color": text_color},
                "automargin": True,
            },
            "hovermode": "closest",
            "annotations": annotations,
            "margin": {"l": 190},
        },
    }


# ---------------------------------------------------------------------------
# Document viewer
# ---------------------------------------------------------------------------

@app.post("/muni/document/view")
def muni_document_view(file_id: list = Body(..., embed=True)):
    """POST endpoint for the multi_file_viewer widget.
    Accepts {"file_id": ["..."]} and returns a list of base64-encoded PDFs.
    """
    import base64
    results = []
    with httpx.Client(timeout=60) as client:
        for fid in file_id:
            try:
                resp = client.post(
                    f"{TERRAPIN_BASE_URL}/api/v1/download_document",
                    headers=terrapin_headers(),
                    json={"file_id": fid},
                )
                resp.raise_for_status()
                encoded = base64.b64encode(resp.content).decode("utf-8")
                results.append({
                    "content": encoded,
                    "data_format": {"data_type": "pdf", "filename": fid},
                })
            except Exception as exc:
                results.append({
                    "error_type": "download_error",
                    "content": f"Failed to download {fid}: {exc}",
                })
    return JSONResponse(content=results)
