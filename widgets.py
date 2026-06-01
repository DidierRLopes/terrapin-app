"""Widget manifest for the Muni Bond OpenBB app."""

from __future__ import annotations

import copy
from typing import Any

DEFAULT_CUSIP = "74445MAB5"
ALL_STATES = "ALL"

# ---------------------------------------------------------------------------
# Shared option catalogs
# ---------------------------------------------------------------------------

US_STATE_CODES = [
    "ALL",
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

ISSUER_SECTORS = [
    ("Education", "education"),
    ("Healthcare", "healthcare"),
    ("Housing", "housing"),
    ("Industrial", "industrial"),
    ("Local", "local"),
    ("State", "state"),
    ("Tobacco", "tobacco"),
    ("Transportation", "transportation"),
    ("Utilities", "utilities"),
]

USE_SECTORS = [
    ("Development", "development"),
    ("Education", "education"),
    ("Government", "government"),
    ("Healthcare", "healthcare"),
    ("Housing", "housing"),
    ("Miscellaneous", "miscellaneous"),
    ("Recreation", "recreation"),
    ("Transportation", "transportation"),
    ("Utility", "utility"),
]

INTEREST_TYPES = [
    ("Fixed Rate", "fixed rate"),
    ("Variable Rate", "variable rate"),
    ("CAB", "cab"),
    ("CAB-to-Fixed", "cab-to-fixed"),
    ("Step Rate", "step rate"),
    ("Term Rate", "term rate"),
    ("Zero / Discount", "zero rate / discount rate"),
]

SOURCES_OF_REPAYMENT = [
    ("Revenue", "Revenue"),
    ("General Obligation", "General Obligation"),
    ("Double Barrel", "Double Barrel"),
]

RANK_BY_OPTIONS = [
    ("Trade Volume", "trade_volume"),
    ("Trade Count", "trade_count"),
    ("Traded CUSIPs", "traded_cusip_count"),
    ("New Issuance Par", "new_issuance_par_value"),
    ("New CUSIPs", "new_cusip_count"),
]

PERIOD_OPTIONS = [
    ("All", "all"),
    ("Day", "day"),
    ("Week", "week"),
    ("Month", "month"),
    ("Quarter", "quarter"),
    ("Year", "year"),
]

GROUP_BY_OPTIONS = [
    ("None", "none"),
    ("Basic: State", "state"),
    ("Basic: Source of Repayment", "source_of_repayment"),
    ("Basic: Rating Group", "rating_group"),
    ("Basic: Interest Type", "interest_type"),
    ("Basic: Seniority", "seniority"),
    ("Basic: Capital Purpose", "capital_purpose"),
    ("Use of Funds: Use Sectors", "use_sectors"),
    ("Use of Funds: Use Categories", "use_categories"),
    ("Use of Funds: Uses of Proceeds", "uses_of_proceeds"),
    ("Flags: Federally Taxable", "is_federally_taxable"),
    ("Flags: AMT", "is_amt"),
    ("Flags: Bank Qualified", "is_bank_qualified"),
    ("Flags: Insured", "is_insured"),
    ("Flags: Green", "is_green"),
    ("Flags: Social", "is_social"),
    ("Flags: Sustainable", "is_sustainable"),
    ("Flags: PAC", "is_pac"),
]

TRADE_METRIC_OPTIONS = [
    ("Trade Volume", "trade_volume"),
    ("Trade Count", "trade_count"),
    ("Customer Bought Count", "customer_bought_count"),
    ("Customer Sold Count", "customer_sold_count"),
    ("Inter-Dealer Count", "inter_dealer_count"),
]

ISSUANCE_METRIC_OPTIONS = [
    ("New Issuance Par Value", "new_issuance_par_value"),
    ("New CUSIP Count", "new_cusip_count"),
    ("Issuer Count", "issuer_count"),
]

OUTSTANDING_METRIC_OPTIONS = [
    ("Outstanding Par Value", "outstanding_par_value"),
    ("CUSIP Count", "cusip_count"),
    ("Entity Count", "entity_count"),
]
SHARED_STATS_PARAM_NAMES = {
    "states",
    "sources_of_repayment",
    "sectors",
    "use_categories",
    "uses_of_proceeds",
    "rating_group",
    "interest_types",
    "seniority",
    "capital_purpose",
    "is_federally_taxable",
    "is_amt",
    "is_bank_qualified",
    "is_insured",
    "is_green",
    "is_social",
    "is_sustainable",
    "is_pac",
}

RATING_GROUP_OPTIONS = [
    ("Investment Grade", "investment_grade"),
    ("High Yield", "high_yield"),
]

SENIORITY_OPTIONS = [
    ("Senior", "senior"),
    ("First Lien", "first_lien"),
    ("Second Lien", "second_lien"),
    ("Subordinate", "subordinate"),
    ("Junior", "junior"),
]

CAPITAL_PURPOSE_OPTIONS = [
    ("New Money", "new money"),
    ("Refunding", "refunding"),
    ("Mixed", "mixed"),
]

USE_CATEGORY_OPTIONS = [
    ("General Purpose", "general purpose"),
    ("Essential Services", "essential services"),
    ("Higher Education", "higher education"),
    ("Primary and Secondary Education", "primary and secondary education"),
    ("Pre-School", "pre-school"),
    ("Airport", "airport"),
    ("Port", "port"),
    ("Public Transit", "public transit"),
    ("Roads", "roads"),
    ("Bridges", "bridges"),
    ("Parking", "parking"),
    ("Economic Development", "economic development"),
    ("Industrial Development", "industrial development"),
    ("Recreational", "recreational"),
    ("Culture", "culture"),
    ("Health System", "health system"),
    ("Hospitals", "hospitals"),
    ("Senior Living", "senior living"),
    ("Single Family Housing", "single family housing"),
    ("Multi-Family Housing", "multi-family housing"),
    ("Military Housing", "military housing"),
    ("Public Housing", "public housing"),
    ("Power", "power"),
    ("Water and Sewer", "water and sewer"),
    ("Waste Removal", "waste removal"),
    ("Gas", "gas"),
    ("Electrical", "electrical"),
    ("Communication", "communication"),
    ("Gas Prepay", "gas prepay"),
    ("Student Loan", "student loan"),
    ("Miscellaneous", "miscellaneous"),
]

USES_OF_PROCEEDS_OPTIONS = [
    ("Tribal", "tribal"),
    ("Police", "police"),
    ("Fire", "fire"),
    ("Courts", "courts"),
    ("Correctional Facilities", "correctional facilities"),
    ("Public College", "public college"),
    ("Private College", "private college"),
    ("Community College", "community college"),
    ("Student Housing", "student housing"),
    ("Charter School", "charter school"),
    ("Standalone Public School", "standalone public school"),
    ("Public School District", "public school district"),
    ("Pre-School and Daycare", "pre-school and daycare"),
    ("Airport", "airport"),
    ("Combined Port Authority", "combined port authority"),
    ("Standalone Port", "standalone port"),
    ("Trains", "trains"),
    ("Buses", "buses"),
    ("Ferries", "ferries"),
    ("State Toll Roads", "state toll roads"),
    ("Regional Toll Roads", "regional toll roads"),
    ("Non-Toll Roads", "non-toll roads"),
    ("State Toll Bridges", "state toll bridges"),
    ("Regional Toll Bridges", "regional toll bridges"),
    ("Non-Toll Bridges", "non-toll bridges"),
    ("Parking Facilities", "parking facilities"),
    ("Hospitality", "hospitality"),
    ("Office Buildings", "office buildings"),
    ("Public Buildings", "public buildings"),
    ("Shopping Centres", "shopping centres"),
    ("Development District", "development district"),
    ("Industrial Development", "industrial development"),
    ("Pollution Control", "pollution control"),
    ("Stadium", "stadium"),
    ("Parks", "parks"),
    ("Library", "library"),
    ("Museum", "museum"),
    ("Community Centre", "community centre"),
    ("Health System", "health system"),
    ("Critical Access Hospital", "critical access hospital"),
    ("Standalone Hospital", "standalone hospital"),
    ("Specialty Hospital", "specialty hospital"),
    ("Assisted Living", "assisted living"),
    ("Independent Living", "independent living"),
    ("Continuing Care Retirement Community", "continuing care retirement community"),
    ("Nursing Home", "nursing home"),
    ("State HFA Single Family Housing", "state hfa single family housing"),
    ("Local HFA Single Family Housing", "local hfa single family housing"),
    ("Local Standalone Single Family Housing", "local standalone single family housing"),
    ("State HFA Multi-Family Housing", "state hfa multi-family housing"),
    ("Local HFA Multi-Family Housing", "local hfa multi-family housing"),
    ("Local Standalone Multi-Family Housing", "local standalone multi-family housing"),
    ("Military Housing", "military housing"),
    ("Public Housing", "public housing"),
    ("Nuclear Power", "nuclear power"),
    ("Coal Power", "coal power"),
    ("Gas Power", "gas power"),
    ("Wind Power", "wind power"),
    ("Solar Power", "solar power"),
    ("Alternative Source Power", "alternative source power"),
    ("Water", "water"),
    ("Sewer", "sewer"),
    ("Storm Water", "storm water"),
    ("Flood Control", "flood control"),
    ("Irrigation", "irrigation"),
    ("Waste Removal", "waste removal"),
    ("Gas Infrastructure", "gas infrastructure"),
    ("Electrical Infrastructure", "electrical infrastructure"),
    ("Telephone", "telephone"),
    ("Broadband", "broadband"),
    ("Gas Prepay", "gas prepay"),
    ("Student Loan", "student loan"),
    ("Miscellaneous", "miscellaneous"),
]


# ---------------------------------------------------------------------------
# Param builders
# ---------------------------------------------------------------------------

def _options(pairs: list[tuple[str, str]]) -> list[dict[str, str]]:
    return [{"label": label, "value": value} for label, value in pairs]


def _state_options() -> list[dict[str, str]]:
    return [
        {"label": "All States" if code == ALL_STATES else code, "value": code}
        for code in US_STATE_CODES
    ]


def _param(
    param_name: str,
    *,
    type: str = "text",
    label: str,
    description: str = "",
    value: str | None = "",
    options: list[dict[str, str]] | None = None,
    multi_select: bool = False,
    **extra: Any,
) -> dict[str, Any]:
    p: dict[str, Any] = {
        "paramName": param_name,
        "type": type,
        "label": label,
        "description": description,
        "value": value,
    }
    if options is not None:
        p["options"] = options
    if multi_select:
        p["multiSelect"] = True
    p.update(extra)
    return p


def cusip_param(value: str = DEFAULT_CUSIP) -> dict[str, Any]:
    return _param(
        "cusip",
        label="CUSIP",
        description="9-character US CUSIP",
        value=value,
    )


def states_param(
    *,
    value: str = ALL_STATES,
    description: str = "Filter by state, or All States for nationwide",
    multi_select: bool = True,
) -> dict[str, Any]:
    return _param(
        "states",
        label="States",
        description=description,
        value=value,
        options=_state_options(),
        multi_select=multi_select,
    )


def sources_of_repayment_param(*, value: str = "") -> dict[str, Any]:
    return _param(
        "sources_of_repayment",
        label="Source of Repayment",
        description="How the bond is repaid",
        value=value,
        options=_options(SOURCES_OF_REPAYMENT),
        multi_select=True,
    )


def issuer_sectors_param(*, value: str = "") -> dict[str, Any]:
    return _param(
        "sectors",
        label="Sectors",
        description="Bond issuer sectors",
        value=value,
        options=_options(ISSUER_SECTORS),
        multi_select=True,
    )


def use_sectors_param(*, value: str = "") -> dict[str, Any]:
    return _param(
        "sectors",
        label="Use Sectors",
        description="Top-level use of funds sector",
        value=value,
        options=_options(USE_SECTORS),
        multi_select=True,
    )


def interest_types_param(*, value: str = "") -> dict[str, Any]:
    return _param(
        "interest_types",
        label="Interest Types",
        description="Types of interest",
        value=value,
        options=_options(INTEREST_TYPES),
        multi_select=True,
    )


def date_range_params(
    *,
    start: str = "$currentDate-3m",
    end: str = "$currentDate",
    start_label: str = "Start Date",
    end_label: str = "End Date",
    start_description: str = "Period start",
    end_description: str = "Period end",
) -> list[dict[str, Any]]:
    return [
        _param("start_date", type="date", label=start_label, description=start_description, value=start),
        _param("end_date", type="date", label=end_label, description=end_description, value=end),
    ]


def stats_non_boolean_filter_params(*, states: str = ALL_STATES) -> list[dict[str, Any]]:
    return [
        states_param(value=states, multi_select=True),
        sources_of_repayment_param(),
        use_sectors_param(),
        _param(
            "use_categories",
            label="Use Categories",
            description="Filter by use categories",
            options=_options(USE_CATEGORY_OPTIONS),
            multi_select=True,
        ),
        _param(
            "uses_of_proceeds",
            label="Uses of Proceeds",
            description="Filter by uses of proceeds",
            options=_options(USES_OF_PROCEEDS_OPTIONS),
            multi_select=True,
        ),
        _param(
            "rating_group",
            label="Rating Group",
            description="Single rating group filter",
            options=_options(RATING_GROUP_OPTIONS),
        ),
        _param(
            "seniority",
            label="Seniority",
            description="Filter by seniority",
            options=_options(SENIORITY_OPTIONS),
            multi_select=True,
        ),
        _param(
            "capital_purpose",
            label="Capital Purpose",
            description="Filter by capital purpose",
            options=_options(CAPITAL_PURPOSE_OPTIONS),
            multi_select=True,
        ),
    ]


def stats_compact_filter_params(*, states: str = ALL_STATES) -> list[dict[str, Any]]:
    """Keep only the most intuitive, high-signal stats filters."""
    return [
        states_param(value=states, multi_select=True),
        sources_of_repayment_param(),
        use_sectors_param(),
    ]


def _boolean_filter_options(default_label: str, param_name: str) -> list[dict[str, str]]:
    pretty_name = param_name.removeprefix("is_")
    return [
        {"label": default_label, "value": ""},
        {"label": param_name, "value": "true"},
        {"label": f"is not {pretty_name}", "value": "false"},
    ]


def stats_yes_no_filter_params() -> list[dict[str, Any]]:
    return [
        _param(
            "is_federally_taxable",
            label="Federally Taxable",
            description="Optional boolean filter",
            value="",
            options=_boolean_filter_options("Federally Taxable", "is_federally_taxable"),
        ),
        _param(
            "is_amt",
            label="AMT",
            description="Optional boolean filter",
            value="",
            options=_boolean_filter_options("AMT", "is_amt"),
        ),
        _param(
            "is_bank_qualified",
            label="Bank Qualified",
            description="Optional boolean filter",
            value="",
            options=_boolean_filter_options("Bank Qualified", "is_bank_qualified"),
        ),
        _param(
            "is_insured",
            label="Insured",
            description="Optional boolean filter",
            value="",
            options=_boolean_filter_options("Insured", "is_insured"),
        ),
        _param(
            "is_green",
            label="Green",
            description="Optional boolean filter",
            value="",
            options=_boolean_filter_options("Green", "is_green"),
        ),
        _param(
            "is_social",
            label="Social",
            description="Optional boolean filter",
            value="",
            options=_boolean_filter_options("Social", "is_social"),
        ),
        _param(
            "is_sustainable",
            label="Sustainable",
            description="Optional boolean filter",
            value="",
            options=_boolean_filter_options("Sustainable", "is_sustainable"),
        ),
        _param(
            "is_pac",
            label="PAC",
            description="Optional boolean filter",
            value="",
            options=_boolean_filter_options("PAC", "is_pac"),
        ),
    ]


def stats_filter_params(*, states: str = ALL_STATES) -> list[dict[str, Any]]:
    return [
        *stats_non_boolean_filter_params(states=states),
        *stats_yes_no_filter_params(),
    ]


def stats_metrics_param(*, options: list[tuple[str, str]], value: str) -> dict[str, Any]:
    return _param(
        "metrics",
        label="Metrics",
        description="Choose one metric to display",
        value=value,
        options=_options(options),
    )


def stats_period_param(*, value: str = "all") -> dict[str, Any]:
    return _param(
        "period",
        label="Period",
        description="Aggregation period for time series stats",
        value=value,
        options=_options(PERIOD_OPTIONS),
    )


def stats_group_by_param(*, value: str = "none") -> dict[str, Any]:
    return _param(
        "group_by",
        label="Group By",
        description="Optional dimension for grouped stats",
        value=value,
        options=_options(GROUP_BY_OPTIONS),
    )


def chart_title_param(*, value: str = "", show: bool = True) -> dict[str, Any]:
    return _param(
        "title",
        label="Title",
        description="Optional chart title annotation",
        value=value,
        show=show,
    )


def hide_shared_stats_params(params: list[Any]) -> list[Any]:
    hidden = copy.deepcopy(params)

    def walk(node: Any):
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if isinstance(node, dict) and node.get("paramName") in SHARED_STATS_PARAM_NAMES:
            node["show"] = False

    walk(hidden)
    return hidden


def stats_core_params(
    *,
    metric_options: list[tuple[str, str]],
    metric_value: str,
    include_period: bool = False,
) -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = [
        stats_metrics_param(options=metric_options, value=metric_value),
        stats_group_by_param(),
    ]
    if include_period:
        params.append(stats_period_param(value="month"))
    return params


def document_selector_param() -> dict[str, Any]:
    return _param(
        "file_id",
        type="endpoint",
        label="Documents",
        show=False,
        multiSelect=True,
        roles=["fileSelector"],
        optionsEndpoint="/muni/documents/options",
        optionsParams={"cusip": "$cusip"},
    )


def table_col(field: str, header: str, **extra: Any) -> dict[str, Any]:
    return {"field": field, "headerName": header, **extra}


def stats_kv_table() -> dict[str, Any]:
    return {
        "table": {
            "columnsDefs": [
                table_col("metric", "Metric", cellDataType="text", flex=2),
                table_col("value", "Value", cellDataType="text", flex=2),
            ],
        },
    }


def cusip_click_col() -> dict[str, Any]:
    return table_col(
        "cusip",
        "CUSIP",
        cellDataType="text",
        pinned="left",
        width=110,
        renderFn="cellOnClick",
        renderFnParams={
            "actionType": "groupBy",
            "groupBy": {"paramName": "cusip", "valueField": "cusip"},
        },
    )


# ---------------------------------------------------------------------------
# Widget definitions
# ---------------------------------------------------------------------------

WIDGETS: dict[str, dict[str, Any]] = {
    "muni_reference": {
        "name": "Muni Bond Reference Data",
        "description": "Full reference data for a US municipal bond, organised by section.",
        "type": "markdown",
        "endpoint": "/muni/reference",
        "gridData": {"w": 10, "h": 28},
        "params": [cusip_param()],
    },

    "muni_pricing_chart": {
        "name": "Muni Bond Pricing History",
        "description": "Trade prices over time for a US municipal bond, coloured by trade type.",
        "type": "chart",
        "endpoint": "/muni/pricing_chart",
        "gridData": {"w": 20, "h": 16},
        "runButton": True,
        "params": [
            cusip_param(),
            *date_range_params(
                start="$currentDate-1y",
                start_description="Defaults to 1 year ago",
                end_description="Defaults to today",
            ),
        ],
    },

    "muni_document_viewer": {
        "name": "Bond Documents",
        "description": "Official statements and disclosure documents viewer. Select a document from the dropdown to open it.",
        "type": "multi_file_viewer",
        "endpoint": "/muni/document/view",
        "gridData": {"w": 30, "h": 24},
        "params": [cusip_param(), document_selector_param()],
    },

    "muni_cashflows": {
        "name": "Muni Bond Cashflows",
        "description": "Cashflow schedules to maturity and to next call for a US municipal bond.",
        "type": "markdown",
        "endpoint": "/muni/cashflows",
        "gridData": {"w": 20, "h": 14},
        "params": [cusip_param()],
    },

    "muni_bond_search": {
        "name": "Bond Explorer",
        "description": "Search and filter US municipal bonds. Click a CUSIP to load the bond in Security Details.",
        "type": "table",
        "endpoint": "/muni/search",
        "gridData": {"w": 40, "h": 22},
        "params": [
            [
                _param("issuer_name", label="Issuer Name", description="Filter by issuer name (partial match)"),
                states_param(),
                issuer_sectors_param(),
                interest_types_param(),
                sources_of_repayment_param(),
            ],
            [
                _param("coupon_min", label="Coupon Min (%)", description="Minimum coupon rate"),
                _param("coupon_max", label="Coupon Max (%)", description="Maximum coupon rate"),
                _param("maturity_date_min", type="date", label="Maturity From", description="Minimum maturity date"),
                _param("maturity_date_max", type="date", label="Maturity To", description="Maximum maturity date", value=None),
                _param("last_traded_since", type="date", label="Last Traded Since", description="Only include bonds traded since this date", value=None),
                _param("limit", label="Result Limit", description="Maximum number of results (default 100)", value="100"),
            ],
        ],
        "data": {
            "table": {
                "columnsDefs": [
                    cusip_click_col(),
                    table_col("ticker", "Ticker", cellDataType="text", flex=2),
                    table_col("issuer_name", "Issuer", cellDataType="text", flex=3),
                    table_col("state", "State", cellDataType="text", width=70),
                    table_col("coupon", "Coupon", cellDataType="text", width=90),
                    table_col("interest_type", "Type", cellDataType="text", width=110),
                    table_col("maturity_date", "Maturity", cellDataType="dateString", width=110),
                    table_col("callable", "Callable", cellDataType="text", width=80),
                    table_col("rating", "Rating", cellDataType="text", width=130),
                    table_col("has_os", "Official Stmt", cellDataType="text", width=100),
                ],
            },
        },
    },

    "muni_stats_filters": {
        "name": "Filters",
        "description": "Shared filters for the Market Activity widgets.",
        "type": "markdown",
        "endpoint": "/muni/stats/filters_summary",
        "gridData": {"w": 40, "h": 8},
        "runButton": True,
        "params": [
            [
                states_param(),
                sources_of_repayment_param(),
                use_sectors_param(),
                interest_types_param(),
                _param(
                    "use_categories",
                    label="Use Categories",
                    description="Filter by use categories",
                    options=_options(USE_CATEGORY_OPTIONS),
                    multi_select=True,
                ),
                _param(
                    "uses_of_proceeds",
                    label="Uses of Proceeds",
                    description="Filter by uses of proceeds",
                    options=_options(USES_OF_PROCEEDS_OPTIONS),
                    multi_select=True,
                ),
                _param(
                    "rating_group",
                    label="Rating Group",
                    description="Single rating group filter",
                    options=_options(RATING_GROUP_OPTIONS),
                ),
                _param(
                    "seniority",
                    label="Seniority",
                    description="Filter by seniority",
                    options=_options(SENIORITY_OPTIONS),
                    multi_select=True,
                ),
                _param(
                    "capital_purpose",
                    label="Capital Purpose",
                    description="Filter by capital purpose",
                    options=_options(CAPITAL_PURPOSE_OPTIONS),
                    multi_select=True,
                ),
            ],
            [
                *stats_yes_no_filter_params(),
            ]
        ],
    },

    "muni_stats_outstanding": {
        "name": "Outstanding Universe",
        "description": "Cross-sectional outstanding par value, CUSIP count, and issuer count for the filtered universe.",
        "type": "table",
        "endpoint": "/muni/stats/outstanding",
        "gridData": {"w": 13, "h": 12},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                stats_group_by_param(value="use_sectors"),
                stats_metrics_param(
                    options=OUTSTANDING_METRIC_OPTIONS,
                    value="outstanding_par_value",
                ),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
        "data": {
            "table": {
                "columnsDefs": [
                    table_col("group_key", "Group", cellDataType="text", width=180),
                    table_col("outstanding_par_value", "Outstanding Par Value", cellDataType="number", width=180),
                    table_col("cusip_count", "CUSIP Count", cellDataType="number", width=120),
                    table_col("entity_count", "Entity Count", cellDataType="number", width=120),
                ],
            },
        },
    },

    "muni_stats_issuance": {
        "name": "Issuance",
        "description": "Time series issuance stats over the selected date range and filters.",
        "type": "chart",
        "endpoint": "/muni/stats/issuance_chart",
        "gridData": {"w": 13, "h": 12},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                stats_group_by_param(),
                stats_metrics_param(
                    options=ISSUANCE_METRIC_OPTIONS,
                    value="new_issuance_par_value",
                ),
                stats_period_param(value="month"),
                *date_range_params(start="2025-01-01"),
                chart_title_param(),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
    },

    "muni_stats_trade_activity": {
        "name": "Trade Activity",
        "description": "Time series secondary-market trade stats for the selected date range and filters.",
        "type": "chart",
        "endpoint": "/muni/stats/trade_activity_chart",
        "gridData": {"w": 14, "h": 12},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                stats_group_by_param(),
                stats_metrics_param(
                    options=TRADE_METRIC_OPTIONS,
                    value="trade_volume",
                ),
                stats_period_param(value="month"),
                *date_range_params(start="2025-01-01"),
                chart_title_param(),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
    },

    "muni_stats_outstanding_seniority": {
        "name": "Outstanding Universe: Seniority",
        "description": "Outstanding universe breakdown grouped by seniority.",
        "type": "table",
        "endpoint": "/muni/stats/outstanding",
        "gridData": {"w": 20, "h": 16},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                stats_group_by_param(value="seniority"),
                stats_metrics_param(
                    options=OUTSTANDING_METRIC_OPTIONS,
                    value="outstanding_par_value",
                ),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
        "data": {
            "table": {
                "columnsDefs": [
                    table_col("group_key", "Group", cellDataType="text", width=180),
                    table_col("outstanding_par_value", "Outstanding Par Value", cellDataType="number", width=180),
                    table_col("cusip_count", "CUSIP Count", cellDataType="number", width=120),
                    table_col("entity_count", "Entity Count", cellDataType="number", width=120),
                ],
            },
        },
    },

    "muni_stats_trade_volume_monthly": {
        "name": "Trade Activity: Volume Trend",
        "description": "Trade volume trend for the selected period.",
        "type": "chart",
        "endpoint": "/muni/stats/trade_activity_chart",
        "gridData": {"w": 20, "h": 16},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                stats_group_by_param(value="none"),
                stats_metrics_param(
                    options=TRADE_METRIC_OPTIONS,
                    value="trade_volume",
                ),
                stats_period_param(value="month"),
                *date_range_params(start="2025-01-01"),
                chart_title_param(),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
    },

    "muni_stats_trade_customer_bought_monthly": {
        "name": "Trade Activity: Customer Bought by Month",
        "description": "Monthly customer-bought trade count trend.",
        "type": "chart",
        "endpoint": "/muni/stats/trade_activity_chart",
        "gridData": {"w": 20, "h": 16},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                stats_group_by_param(value="none"),
                stats_metrics_param(
                    options=TRADE_METRIC_OPTIONS,
                    value="customer_bought_count",
                ),
                stats_period_param(value="month"),
                *date_range_params(start="2025-01-01"),
                chart_title_param(value="Customer Bought by Month"),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
    },

    "muni_stats_issuance_interest_type": {
        "name": "Issuance: Interest Type",
        "description": "Monthly issuance split by interest type.",
        "type": "chart",
        "endpoint": "/muni/stats/issuance_chart",
        "gridData": {"w": 20, "h": 16},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                stats_group_by_param(value="interest_type"),
                stats_metrics_param(
                    options=ISSUANCE_METRIC_OPTIONS,
                    value="new_issuance_par_value",
                ),
                stats_period_param(value="month"),
                *date_range_params(start="2025-01-01"),
                chart_title_param(value="Issuance by Interest Type"),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
    },

    "muni_stats_issuance_sector": {
        "name": "Issuance: Sector",
        "description": "Monthly issuance split by sector.",
        "type": "chart",
        "endpoint": "/muni/stats/issuance_chart",
        "gridData": {"w": 20, "h": 16},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                stats_group_by_param(value="use_sectors"),
                stats_metrics_param(
                    options=ISSUANCE_METRIC_OPTIONS,
                    value="new_issuance_par_value",
                ),
                stats_period_param(value="month"),
                *date_range_params(start="2025-01-01"),
                chart_title_param(value="Issuance by Sector"),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
    },

    "muni_stats_top_issuers": {
        "name": "Top Issuers",
        "description": "Issuers ranked by trade volume, trade count, new issuance, or traded CUSIP count.",
        "type": "table",
        "endpoint": "/muni/stats/top_issuers",
        "gridData": {"w": 40, "h": 18},
        "runButton": True,
        "params": hide_shared_stats_params([
            *date_range_params(start="2025-01-01"),
            _param(
                "rank_by",
                label="Rank By",
                description="Metric used to rank issuers",
                value="trade_volume",
                options=_options(RANK_BY_OPTIONS),
            ),
            _param("limit", label="Limit", description="Maximum number of issuers", value="25"),
            *stats_filter_params(),
        ]),
        "data": {
            "table": {
                "columnsDefs": [
                    table_col("rank", "#", cellDataType="text", width=50, pinned="left"),
                    table_col("issuer_name", "Issuer", cellDataType="text", flex=3),
                    table_col("trade_volume", "Trade Volume", cellDataType="text", width=130),
                    table_col("trade_count", "Trades", cellDataType="text", width=90),
                    table_col("traded_cusip_count", "Traded CUSIPs", cellDataType="text", width=120),
                    table_col("new_issuance_par_value", "New Issuance", cellDataType="text", width=130),
                    table_col("new_cusip_count", "New CUSIPs", cellDataType="text", width=100),
                    table_col("last_trade_date", "Last Trade", cellDataType="dateString", width=110),
                ],
            },
        },
    },

    "muni_stats_top_issuers_chart": {
        "name": "Top Issuers Chart",
        "description": "Bar chart of top issuers by selected metric.",
        "type": "chart",
        "endpoint": "/muni/stats/top_issuers_chart",
        "gridData": {"w": 20, "h": 18},
        "runButton": True,
        "params": hide_shared_stats_params([
            [
                *date_range_params(start="2025-01-01"),
                _param(
                    "rank_by",
                    label="Rank By",
                    description="Metric used to rank issuers",
                    value="trade_volume",
                    options=_options(RANK_BY_OPTIONS),
                ),
                _param("limit", label="Limit", description="Maximum number of issuers", value="25"),
                chart_title_param(),
            ],
            [*stats_non_boolean_filter_params()],
            [*stats_yes_no_filter_params()],
        ]),
    },
}
