import json
import os
from datetime import date
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse

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

WIDGETS_FILE = Path(__file__).parent / "widgets.json"
APPS_FILE = Path(__file__).parent / "apps.json"

TRADE_TYPE_META = {
    "customer_bought": {"label": "Customer Bought", "color": "#2196F3"},
    "customer_sold":   {"label": "Customer Sold",   "color": "#F44336"},
    "inter_dealer":    {"label": "Inter-Dealer",    "color": "#9C27B0"},
}


# ---------------------------------------------------------------------------
# Helpers
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


def _fmt(v) -> str:
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


def _fmt_enum(v) -> str:
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


def _fmt_list(v) -> str:
    """Format a list of proper names (no case-mangling)."""
    if not v:
        return "—"
    return ", ".join(str(x) for x in v)


def _kv(field: str, value) -> dict:
    """Key-value row for table widgets."""
    if isinstance(value, list):
        value = _fmt_list(value) if value else "—"
    elif value is None:
        value = "—"
    elif isinstance(value, bool):
        value = "Yes" if value else "No"
    return {"field": field, "value": value}


# ---------------------------------------------------------------------------
# Manifest endpoints
# ---------------------------------------------------------------------------

@app.get("/widgets.json")
def get_widgets():
    with open(WIDGETS_FILE, encoding="utf-8") as f:
        return JSONResponse(content=json.load(f))


@app.get("/apps.json")
def get_apps():
    with open(APPS_FILE, encoding="utf-8") as f:
        return JSONResponse(content=json.load(f))


# ---------------------------------------------------------------------------
# Reference data  (markdown widget)
# ---------------------------------------------------------------------------

def _ref_markdown(b: dict, cusip: str) -> str:
    rows: list[str] = []

    def section(title: str):
        rows.append(f"\n## {title}")
        rows.append("| Field | Value |")
        rows.append("|:---|:---|")

    def row(label: str, value: str):
        rows.append(f"| {label} | {value} |")

    coupon = b.get("interest_rate")
    coupon_str = f"{_fmt(coupon)}%" if coupon is not None else "—"

    section("Security Details")
    row("ISIN",              _fmt(b.get("isin")))
    row("CUSIP",             cusip.upper())
    row("FIGI",              _fmt(b.get("figi")))
    row("Ticker",            _fmt(b.get("ticker")))
    row("Sector",            _fmt_enum(b.get("sector")))
    row("Repayment",         _fmt_enum(b.get("source_of_repayment")))
    row("Uses of Proceeds",  _fmt_enum(b.get("use_categories")))
    row("Capital Purpose",   _fmt_enum(b.get("capital_purpose")))
    row("Obligor",           _fmt(b.get("obligor")))

    section("Key Dates")
    row("Maturity Date",  _fmt(b.get("maturity_date")))
    row("Award Date",     _fmt(b.get("award_date")))
    row("Closing Date",   _fmt(b.get("closing_date")))
    row("Dated Date",     _fmt(b.get("dated_date")))

    section("Features")
    row("Callable",     _fmt(b.get("is_callable")))
    row("Sinking Fund", _fmt(b.get("has_mandatory_redemption")))
    row("Insured",      _fmt(b.get("is_insured")))

    section("Interest Details")
    row("Interest Type",        _fmt_enum(b.get("interest_type")))
    row("Coupon Rate",          coupon_str)
    row("Coupons per Year",     _fmt(b.get("coupon_frequency")))
    row("Interest Accrual Date",_fmt(b.get("interest_accrual_date")))
    row("First Coupon Date",    _fmt(b.get("first_interest_payment_date")))
    row("Next Coupon Date",     _fmt(b.get("next_coupon_date")))
    row("Previous Coupon Date", _fmt(b.get("previous_coupon_date")))
    row("Day Count Convention", _fmt(b.get("interest_accrual_convention")))

    section("Amounts")
    row("Issued Amount",      _fmt(b.get("issued_amount")))
    row("Outstanding Amount", _fmt(b.get("outstanding_amount")))
    row("Series Amount",      _fmt(b.get("series_issued_amount")))
    row("Min Denomination",   _fmt(b.get("minimum_denomination")))
    row("Integral Multiple",  _fmt(b.get("integral_multiple")))

    section("Classifications")
    row("Green Bond",      _fmt(b.get("is_green")))
    row("Social Bond",     _fmt(b.get("is_social")))
    row("Sustainable Bond",_fmt(b.get("is_sustainable")))

    section("Tax Status")
    row("State Taxable",     _fmt(b.get("is_state_taxable")))
    row("Federally Taxable", _fmt(b.get("is_federally_taxable")))
    row("AMT",               _fmt(b.get("is_amt")))
    row("Bank Qualified",    _fmt(b.get("is_bank_qualified")))

    section("Counterparties")
    row("Insurers",           _fmt_list(b.get("insurers") or []))
    row("Underwriters",       _fmt_list(b.get("underwriters") or []))
    row("Advisors",           _fmt_list(b.get("advisors") or []))
    row("Bond Counsel",       _fmt_list(b.get("bond_counsel") or []))
    row("Disclosure Counsel", _fmt_list(b.get("disclosure_counsel") or []))
    row("Trustees",           _fmt_list(b.get("trustees") or []))

    section("Credit Enhancement")
    row("Credit Enhanced",    _fmt(b.get("is_credit_enhanced")))
    row("State Enhanced",     _fmt(b.get("is_state_enhanced")))
    row("Guarantee",          _fmt_enum(b.get("guarantee")))
    row("Enhancement Types",  _fmt_enum(b.get("credit_enhancement_type")))

    return "\n".join(rows)


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

    return PlainTextResponse(_ref_markdown(data[0], cusip))


# ---------------------------------------------------------------------------
# Pricing history chart
# ---------------------------------------------------------------------------

@app.get("/muni/pricing_chart")
def muni_pricing_chart(
    cusip: str = Query(..., description="9-character CUSIP"),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    raw: bool = Query(False),
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

    _DARK = "#151515"
    _GRID = "#2a2a2a"
    _TEXT = "#cccccc"

    return {
        "data": traces,
        "layout": {
            "plot_bgcolor":  _DARK,
            "paper_bgcolor": _DARK,
            "font":   {"color": _TEXT},
            "xaxis":  {"title": {"text": "Trade Date"}, "gridcolor": _GRID, "linecolor": _GRID, "tickfont": {"color": _TEXT}},
            "yaxis":  {"title": {"text": "Price"},      "gridcolor": _GRID, "linecolor": _GRID, "tickfont": {"color": _TEXT}},
            "legend": {"orientation": "h", "y": -0.15, "font": {"color": _TEXT}},
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

    def _amt(v: float) -> str:
        return str(int(v)) if v == int(v) else f"{v:.2f}"

    lines = ["| Date | Amount | Type |", "|:---|---:|:---|"]
    for c in cashflows:
        lines.append(f"| {c['date']} | {_amt(c['amount'])} | {c['type'].title()} |")

    return PlainTextResponse("## Cashflows to Maturity\n\n" + "\n".join(lines))


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
    def csv(v: Optional[str]) -> list:
        return [x.strip() for x in v.split(",") if x.strip()] if v else []

    body: dict = {"limit": limit, "sort": ["-issue_date"]}
    if issuer_name:                                body["issuer_name"] = issuer_name
    if sl := csv(states):                          body["states"] = sl
    if sc := csv(sectors):                         body["sectors"] = sc
    if coupon_min is not None:                     body["coupon_min"] = coupon_min
    if coupon_max is not None:                     body["coupon_max"] = coupon_max
    if maturity_date_min:                          body["maturity_date_min"] = maturity_date_min
    if maturity_date_max:                          body["maturity_date_max"] = maturity_date_max
    if it := csv(interest_types):                  body["interest_types"] = it
    if sr := csv(sources_of_repayment):            body["sources_of_repayment"] = sr
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

    def _coupon(v) -> str:
        if isinstance(v, (int, float)):
            return f"{v}%"
        if isinstance(v, dict):
            bm = v.get("benchmark", "")
            sp = v.get("spread_in_bps")
            return f"{sp}bps / {bm}" if sp else bm
        return "—"

    return [
        {
            "cusip":           b["isin"][2:11],
            "ticker":          b.get("ticker") or "—",
            "issuer_name":     b.get("issuer_name") or "—",
            "state":           b.get("state") or "—",
            "coupon":          _coupon(b.get("interest_rate")),
            "interest_type":   _fmt_enum(b.get("interest_type")),
            "maturity_date":   b.get("maturity_date") or "—",
            "callable":        "Yes" if b.get("is_callable") else "No",
            "rating":          _fmt_enum(b.get("rating_group")),
            "has_os":          "✓" if b.get("has_official_statement") else "—",
        }
        for b in resp.json().get("data", [])
    ]


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
