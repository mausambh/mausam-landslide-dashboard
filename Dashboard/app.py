import textwrap

import html
from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
import numpy as np
import streamlit as st
import plotly.express as px
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Nepal Highway Landslide Research",
    page_icon="🏔️",
    layout="wide"
)


ROOT = Path(__file__).resolve().parent.parent

@st.cache_data
def load_csv(relative):
    return pd.read_csv(ROOT / relative)

@st.cache_data
def load_geojson(relative):
    return gpd.read_file(ROOT / relative).to_crs("EPSG:4326")

@st.cache_data
def load_manifest():
    with open(
        ROOT / "Results/two_highway_final_research_manifest.json",
        encoding="utf-8"
    ) as f:
        return json.load(f)

manifest = load_manifest()

# Dashboard appearance and navigation.
if "dashboard_theme" not in st.session_state:
    st.session_state.dashboard_theme = "dark"

theme = st.session_state.dashboard_theme

colors = (
    {
        "background": "#0b1220",
        "surface": "#131f31",
        "border": "#2b3a50",
        "text": "#f1f5f9",
        "muted": "#9fb0c6",
        "accent": "#60a5fa",
    }
    if theme == "dark"
    else {
        "background": "#f7f9fc",
        "surface": "#ffffff",
        "border": "#dce4ef",
        "text": "#17243a",
        "muted": "#53657e",
        "accent": "#2563eb",
    }
)

# Unified dashboard appearance and compact sticky header.
st.markdown(
    f"""
    <style>

    /* MOBILE_THEME_SINGLE_BUTTON_FIX_V1 */
    @media (max-width: 600px) {{
        .st-key-dashboard_theme_toggle
        .stButton > div > button:not(
            .stTooltipHoverTarget button
        ) {{
            display: none !important;
        }}
    }}

/* MOBILE_THEME_WRAPPER_FIX_V1 */
@media (max-width: 600px) {{
    .st-key-dashboard_theme_toggle
    [data-testid="stButton"] > div {{
        display: block !important;
        visibility: visible !important;
    }}

    .st-key-dashboard_theme_toggle button {{
        display: flex !important;
        visibility: visible !important;
        min-width: 44px !important;
        min-height: 44px !important;
    }}
}}


/* DASHBOARD_RESPONSIVE_V1 */

/* Tablet */
@media (max-width: 900px) {{
    .block-container {{
        padding-left: 1.25rem !important;
        padding-right: 1.25rem !important;
    }}

    [data-testid="stPlotlyChart"],
    [data-testid="stVegaLiteChart"] {{
        max-width: 100%;
    }}
}}

/* Mobile */
@media (max-width: 600px) {{
    .block-container {{
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        padding-top: 1rem !important;
    }}

    h1 {{
        font-size: 1.65rem !important;
        line-height: 1.25 !important;
    }}

    h2 {{
        font-size: 1.35rem !important;
        line-height: 1.3 !important;
    }}

    h3 {{
        font-size: 1.12rem !important;
    }}

    [data-testid="stMetric"] {{
        min-width: 0;
    }}

    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    [data-testid="stPlotlyChart"],
    iframe {{
        max-width: 100%;
    }}
}}

    .stApp {{
        background: {colors['background']};
        color: {colors['text']};
    }}

    /* One spacing rule instead of three competing rules. */
    .stMainBlockContainer,
    .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 2rem;
        max-width: 1550px;
    }}

    /* Hide Streamlit's built-in header and menu. */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stMainMenu"],
    #MainMenu,
    [data-testid="stSidebar"] {{
        display: none !important;
    }}

    /* Make the OUTER Streamlit layout element sticky.
       The inner keyed container alone cannot stick reliably. */
    [data-testid="stVerticalBlock"]
    > [data-testid="stElementContainer"]:has(
        .st-key-research_sticky_header
    ),
    [data-testid="stVerticalBlock"]
    > [data-testid="stLayoutWrapper"]:has(
        .st-key-research_sticky_header
    ) {{
        position: sticky !important;
        top: 0 !important;
        z-index: 1000 !important;
        align-self: stretch !important;
        background: {colors['background']} !important;
    }}

    .st-key-research_sticky_header {{
        background: {colors['background']} !important;
        border-bottom: 1px solid {colors['border']} !important;
        padding: 0.4rem 0.8rem !important;
        border-radius: 0 !important;
    }}

    /* Theme-aware header text. */
    .st-key-research_sticky_header h3 {{
        color: {colors['text']} !important;
    }}

    .st-key-research_sticky_header
    [data-testid="stCaptionContainer"] {{
        color: {colors['muted']} !important;
    }}

    /* MOBILE_THEME_BUTTON_VISIBILITY_V1 */
    @media (max-width: 600px) {{
        .st-key-dashboard_theme_toggle {{
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            min-width: 44px !important;
        }}

        .st-key-dashboard_theme_toggle button {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            min-width: 44px !important;
            min-height: 44px !important;
            align-items: center !important;
            justify-content: center !important;
        }}
    }}

    /* Visible sun/moon button. */
    .st-key-dashboard_theme_toggle button {{
        background: {colors['surface']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 10px;
        min-height: 2.5rem;
    }}

    /* Navigation text and backgrounds. */
    .st-key-research_sticky_header
    [data-testid="stSegmentedControl"] button {{
        background: {colors['surface']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}

    .st-key-research_sticky_header
    [data-testid="stSegmentedControl"] button * {{
        color: {colors['text']} !important;
    }}



    /* UNIFIED_HOVER_FIX_V4 */

    /* Streamlit segmented-control navigation */
    .stApp button[role="radio"] {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}

    .stApp button[role="radio"] *,
    .stApp button[role="radio"]:hover * {{
        color: {colors['text']} !important;
    }}

    .stApp button[role="radio"]:hover {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
        border-color: {colors['accent']} !important;
    }}

    .stApp button[role="radio"][aria-checked="true"] {{
        border-color: {colors['accent']} !important;
    }}

    /* Streamlit highway radio selector */
    .stApp [data-testid="stRadio"] label,
    .stApp [data-testid="stRadio"] label:hover,
    .stApp [data-testid="stRadio"] label:focus-within {{
        color: {colors['text']} !important;
        background-color: transparent !important;
    }}

    .stApp [data-testid="stRadio"] label p,
    .stApp [data-testid="stRadio"] label:hover p,
    .stApp [data-testid="stRadio"] label span,
    .stApp [data-testid="stRadio"] label:hover span {{
        color: {colors['text']} !important;
    }}

    .stApp [data-testid="stRadio"] label:hover
    [data-baseweb="radio"] {{
        outline: 1px solid {colors['accent']} !important;
        outline-offset: 3px;
        border-radius: 50%;
    }}


    /* HIGHWAY_RADIO_BLUE_HOVER_FINAL_V1
       Selected = native red; hovered = blue; inactive = gray.
       Targets the actual Streamlit 1.66 radio circle. */

    .stApp label[data-testid="stRadioOption"]:hover {{
        background: transparent !important;
        outline: none !important;
    }}

    .stApp label[data-testid="stRadioOption"]
    :is(input[type="radio"]) {{
        accent-color: #ff4b4b;
    }}

    .stApp label[data-testid="stRadioOption"]:not(:has(input:checked)):hover
    > div:first-of-type > div:first-child {{
        background-color: {colors['accent']} !important;
        border-color: {colors['accent']} !important;
        border-radius: 50% !important;
        position: relative !important;
    }}

    .stApp label[data-testid="stRadioOption"]:not(:has(input:checked)):hover
    > div:first-of-type > div:first-child::after {{
        content: "" !important;
        display: block !important;
        position: absolute !important;
        width: 7px !important;
        height: 7px !important;
        background-color: #ffffff !important;
        border-radius: 50% !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }}


    /* METRIC_SELECTBOX_THEME_CONTRAST_V1 */

    /* Metric labels and numerical values */
    .stApp [data-testid="stMetric"] {{
        color: {colors['text']} !important;
    }}

    .stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stMetricLabel"] *,
    .stApp [data-testid="stMetricValue"],
    .stApp [data-testid="stMetricValue"] *,
    .stApp [data-testid="stMetricDelta"],
    .stApp [data-testid="stMetricDelta"] * {{
        color: {colors['text']} !important;
    }}

    /* Selectbox labels, including simulated road blockage */
    .stApp [data-testid="stSelectbox"] label,
    .stApp [data-testid="stSelectbox"] label *,
    .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stWidgetLabel"] * {{
        color: {colors['text']} !important;
    }}

    /* Selectbox field and selected option */
    .stApp [data-testid="stSelectbox"]
    [data-baseweb="select"] > div {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}

    .stApp [data-testid="stSelectbox"]
    [data-baseweb="select"] span,
    .stApp [data-testid="stSelectbox"]
    [data-baseweb="select"] input,
    .stApp [data-testid="stSelectbox"]
    [data-baseweb="select"] svg {{
        color: {colors['text']} !important;
        fill: {colors['text']} !important;
    }}

    /* Dropdown menu when expanded */
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="popover"] [role="option"] {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
    }}

    [data-baseweb="popover"] [role="option"]:hover {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
    }}




    /* REACT_ARIA_DROPDOWN_THEME_FINAL_V2
       Tested React Aria selectbox styling. */

    /* Field and combobox */
    .stApp [data-testid="stSelectbox"]
    div:has(> input[role="combobox"]) {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}

    .stApp [data-testid="stSelectbox"]
    input[role="combobox"] {{
        color: {colors['text']} !important;
        -webkit-text-fill-color: {colors['text']} !important;
    }}

    /* Dropdown arrow */
    .stApp [data-testid="stSelectbox"]
    .react-aria-ComboBox button,
    .stApp [data-testid="stSelectbox"]
    .react-aria-ComboBox button svg {{
        color: {colors['text']} !important;
    }}

    /* Actual dropdown panel and options.
       Keep selectors consistent with the successful Chrome test. */
    [data-testid="stSelectbox"] [role="listbox"],
    [data-testid="stSelectbox"] [role="option"],
    [data-testid="stSelectbox"] [data-rac],
    [data-testid="stPopoverBody"],
    [data-testid="stSelectboxVirtualDropdown"],
    [data-testid="stSelectboxVirtualDropdown"] *,
    [data-testid="stSelectboxVirtualDropdown"] [data-rac] {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
    }}

    /* Subtle hover on the individual option */
    [data-testid="stSelectbox"] [data-rac][data-focused] > div,
    [data-testid="stSelectbox"] [data-rac][data-hovered] > div,
    [data-testid="stSelectbox"] [data-rac]:hover > div,
    [data-testid="stSelectboxVirtualDropdown"] [data-focused] > div,
    [data-testid="stSelectboxVirtualDropdown"] [data-hovered] > div {{
        background-color: {colors['background']} !important;
        color: {colors['text']} !important;
        border-radius: 6px !important;
    }}

    /* EXPANDER_THEME_CONTRAST_FIX_V1 */
    /* Match expander header, text, and icon to selected dashboard theme. */
    .stApp [data-testid="stExpander"] details > summary {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border: 1px solid {colors['border']} !important;
        border-radius: 8px !important;
    }}

    .stApp [data-testid="stExpander"] details > summary *,
    .stApp [data-testid="stExpander"] details > summary p,
    .stApp [data-testid="stExpander"] details > summary svg {{
        color: {colors['text']} !important;
        stroke: {colors['text']} !important;
    }}

    .stApp [data-testid="stExpander"] details > summary:hover {{
        background-color: {colors['background']} !important;
    }}

    /* TABLE_DIVIDER_THEME_FIX_V1 */

    /* Streamlit dataframe/table container */
    .stApp [data-testid="stDataFrame"],
    .stApp [data-testid="stDataFrame"] > div,
    .stApp [data-testid="stTable"],
    .stApp [data-testid="stTable"] table {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}

    /* Native HTML tables */
    .stApp [data-testid="stTable"] th,
    .stApp [data-testid="stTable"] td,
    .stApp table th,
    .stApp table td {{
        background-color: {colors['surface']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}

    /* Dataframe labels and controls */
    .stApp [data-testid="stDataFrame"] label,
    .stApp [data-testid="stDataFrame"] button {{
        color: {colors['text']} !important;
    }}

    /* Horizontal dividers, including footer separators */
    .stApp hr,
    .stApp [data-testid="stDivider"] {{
        border-color: {colors['border']} !important;
        opacity: 1 !important;
    }}

    .stApp [data-testid="stDivider"] hr {{
        border-color: {colors['border']} !important;
        opacity: 1 !important;
    }}

    /* Keep other page headings readable. */
    .stApp h1, .stApp h2, .stApp h3 {{
        color: {colors['text']};
    }}

    .stApp [data-testid="stRadio"] label p {{
        color: {colors['text']} !important;
    }}

    .stApp [data-baseweb="select"] > div {{
        background: {colors['surface']} !important;
        color: {colors['text']} !important;
        border-color: {colors['border']} !important;
    }}

    /* LIGHT_MODE_WARNING_CONTRAST_V2 */
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"],
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] * {{
        color: {"#17243a" if theme == "light" else colors['text']} !important;
        -webkit-text-fill-color: {"#17243a" if theme == "light" else colors['text']} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container(key="research_sticky_header"):
    title_col, mode_col = st.columns(
        [9, 1],
        vertical_alignment="center",
    )

    with title_col:
        st.markdown("### 🏔️ Nepal Highway Landslide Research")
        st.caption(
            "2018 Random Forest susceptibility | "
            "Hypothetical closures | Validated alternative routes"
        )

    with mode_col:
        if st.button(
            "☀️" if theme == "dark" else "🌙",
            help=(
                "Switch to Light Mode"
                if theme == "dark"
                else "Switch to Dark Mode"
            ),
            key="dashboard_theme_toggle",
            use_container_width=True,
        ):
            st.session_state.dashboard_theme = (
                "light" if theme == "dark" else "dark"
            )
            st.rerun()

    pages = [
        "Landslide Route Explorer",
        "Research Overview",
        "Arniko Highway",
        "Pasang Lhamu Highway",
        "Machine Learning",
        "Methodology & Limitations",
    ]

    page = st.segmented_control(
        "Dashboard navigation",
        options=pages,
        default=pages[0],
        selection_mode="single",
        label_visibility="collapsed",
        key="dashboard_top_navigation_v2",
    )

    if page is None:
        page = pages[0]


def highway_susceptibility_map(corridor_name):
    """Map only saved 2018 RF-scored sections of one highway."""

    roads = load_geojson(
        "Data/two_highway_rf_road_sections_rebuilt_2018.geojson"
    )

    highway = roads.loc[
        roads["corridor"] == corridor_name
    ].copy()

    if highway.empty:
        st.error("No saved RF-scored sections for this highway.")
        return

    highway = highway.to_crs("EPSG:4326")

    bounds = highway.total_bounds

    center = [
        (bounds[1] + bounds[3]) / 2,
        (bounds[0] + bounds[2]) / 2
    ]

    m = folium.Map(
        location=center,
        zoom_start=10,
        tiles="OpenStreetMap",
        control_scale=True
    )

    def susceptibility_color(score):
        if pd.isna(score):
            return "#808080"
        if score < 0.20:
            return "#2E7D32"
        if score < 0.40:
            return "#F9A825"
        if score < 0.60:
            return "#EF6C00"
        return "#C62828"

    for _, section in highway.iterrows():
        score = section["rf_score"]
        color = susceptibility_color(score)

        folium.GeoJson(
            section.geometry.__geo_interface__,
            style_function=lambda feature, c=color: {
                "color": c,
                "weight": 7,
                "opacity": 0.95
            },
            tooltip=(
                f"2018 RF susceptibility score: {float(score):.3f}"
                if pd.notna(score)
                else "RF score unavailable"
            )
        ).add_to(m)

    m.fit_bounds(
        [
            [bounds[1], bounds[0]],
            [bounds[3], bounds[2]]
        ],
        padding=(25, 25)
    )

    legend = """
    <div style="
        position:fixed;
        bottom:25px;
        left:25px;
        z-index:9999;
        background:white;
        padding:12px 15px;
        border:1px solid #bbb;
        border-radius:8px;
        font-size:12px;
        color:#222;
        box-shadow:0 2px 8px #0002;
    ">
        <b>2018 Landslide Susceptibility</b><br>
        <span style="color:#2E7D32;">&#9632;</span> Below 0.20<br>
        <span style="color:#F9A825;">&#9632;</span> 0.20–0.40<br>
        <span style="color:#EF6C00;">&#9632;</span> 0.40–0.60<br>
        <span style="color:#C62828;">&#9632;</span> 0.60 and above<br>
        <small>Relative RF scores, not probabilities</small>
    </div>
    """

    m.get_root().html.add_child(folium.Element(legend))

    st_folium(
        m,
        width="stretch",
        height=540,
        returned_objects=[]
    )

    st.caption(
        f"Displaying {len(highway)} saved RF-scored road sections. "
        "Scores are retrospective 2018 estimates, not real-time "
        "landslide predictions. Unmapped sections are not assessed here."
    )



def render_highway_research(highway):
    """Consistent research presentation for both highways."""

    if highway == "arniko":
        results = load_csv(
            "Results/arniko_final_12_route_research_table.csv"
        )
        overlap = load_csv(
            "Results/arniko_12_alternatives_overlap.csv"
        )

        scenario_cols = ["component", "closure_position_pct"]

        arniko_status = load_csv(
            "Dashboard/arniko_local_bypass_status.csv"
        )

        scenarios = load_csv(
            "Routes/arniko_highway_wide_closure_scenarios.csv"
        )

        options = [
            (int(r.component), int(r.closure_position_pct))
            for r in scenarios.sort_values(
                scenario_cols
            ).itertuples()
        ]

        location_names = dict(zip(
            arniko_status["scenario_id"],
            arniko_status["display_name"]
        ))

        def label(option):
            scenario_id = f"ARNIKO_C{option[0]}_{option[1]}"
            return location_names.get(
                scenario_id, "Saved Arniko closure location"
            )

        def select_results(option):
            return results.loc[
                (results["component"] == option[0])
                & (results["closure_position_pct"] == option[1])
            ].sort_values("alternative_rank")

        def select_overlap(option):
            return overlap.loc[
                (overlap["component"] == option[0])
                & (overlap["closure_position_pct"] == option[1])
            ]

        distance_col = "distance_km"
        exposure_col = "matched_rf_score"
        coverage_col = "coverage_pct"
        extra_col = "additional_distance_km"
        extra_pct_col = "additional_distance_pct"
        valid_col = "route_valid"

        # The saved final table contains alternatives only.
        # Full 12-scenario outcomes are read from the closure-scenario file.
        closure_scenarios = load_csv(
            "Routes/arniko_highway_wide_closure_scenarios.csv"
        )

        def arniko_scenario_label(row):
            return (
                f"Component {int(row['component'])} — "
                f"closure at {int(row['closure_position_pct'])}%"
            )

        # Public research summary matches the approved explorer.
        # Original 12-scenario research data remains unchanged.
        public_ids = [
            "ARNIKO_C0_40",  # Dolalghat
            "ARNIKO_C0_80",  # Itafu
            "ARNIKO_C1_20",  # Dandakateri
            "ARNIKO_C1_40",  # Gati
            "ARNIKO_C1_60",  # Panthali
            "ARNIKO_C1_80",  # Larcha
        ]
        summary = arniko_status.loc[
            arniko_status["scenario_id"].isin(public_ids)
        ].copy()
        assert len(summary) == 6
        summary["Scenario"] = summary["display_name"]
        summary["Road"] = "NH34"
        summary["Original distance (km)"] = float("nan")
        summary["Alternative distance (km)"] = (
            summary["shortest_local_bypass_km"]
        )
        summary["Extra distance (km)"] = float("nan")
        summary["Distance increase (%)"] = float("nan")

        status_labels = {
            "VALIDATED_GRAPH_DERIVED_BYPASS":
                "Local bypass identified",
            "NO_BYPASS_FOUND_WITHIN_TESTED_LIMITS":
                "No qualifying bypass under tested constraints",
            "NO_QUALIFYING_BYPASS_UNDER_TESTED_CONSTRAINTS":
                "No qualifying bypass under tested constraints",
            "NOT_ASSESSED_REVISED_METHODOLOGY":
                "Local bypass assessment pending",
        }

        summary["Result"] = (
            summary["assessment_status"].map(status_labels)
        )
        summary.loc[
            summary["scenario_id"] == "ARNIKO_C0_80", "Result"
        ] = "3 local alternatives identified"
        summary.loc[
            summary["scenario_id"] == "ARNIKO_C1_40", "Result"
        ] = "Provisional local bypass candidate"

        total_scenarios = len(summary)

        # Count both validated and provisional candidate scenarios.
        candidate_statuses = [
            "VALIDATED_GRAPH_DERIVED_BYPASS",
            "PROVISIONAL_GRAPH_DERIVED_BYPASS",
        ]
        detours = int(
            summary["assessment_status"]
            .isin(candidate_statuses)
            .sum()
        )

        # Keep provisional candidates visible without counting them
        # as validated alternatives in the research-status CSV.
        provisional_count = int(
            (
                summary["assessment_status"]
                == "PROVISIONAL_GRAPH_DERIVED_BYPASS"
            ).sum()
        )
        total_alternatives = int(
            summary["validated_alternative_count"]
            .fillna(0).sum()
            + provisional_count
        )

        limitations = (
            "Arniko alternatives are distance-ranked, graph-valid "
            "candidates within the modeled corridor. They are not "
            "risk-optimized or field-verified. Some geometries repeat "
            "between scenarios, and RF coverage varies."
        )

    else:
        scenarios = load_csv(
            "Results/pasang_final_17_scenario_research_table.csv"
        )
        results = load_csv(
            "Results/pasang_final_33_alternatives.csv"
        )
        overlap = load_csv(
            "Results/pasang_final_33_alternatives_overlap.csv"
        )

        options = sorted(scenarios["scenario_id"].dropna().unique())

        # Public labels come from saved, manually reviewed locality
        # references. Scenario IDs remain unchanged internally.
        location_catalogue = load_csv(
            "Dashboard/scenario_location_catalogue.csv"
        )
        pasang_location_names = dict(zip(
            location_catalogue["scenario_id"].astype(str),
            location_catalogue["location_label"].astype(str),
        ))

        def label(option):
            return pasang_location_names.get(
                str(option),
                "Saved Pasang Lhamu closure location",
            )

        def select_results(option):
            return results.loc[
                results["scenario_id"] == option
            ].sort_values("alternative_rank")

        def select_overlap(option):
            return overlap.loc[
                overlap["scenario_id"] == option
            ]

        distance_col = "distance_km"
        exposure_col = "length_weighted_rf_score_2018"
        coverage_col = "rf_coverage_pct"
        extra_col = "extra_vs_shortest_km"
        extra_pct_col = "extra_vs_shortest_pct"
        valid_col = "graph_valid"

        summary = scenarios.copy()
        summary["Scenario"] = summary["scenario_id"]
        summary["Road"] = summary["designation"]
        summary["Original distance (km)"] = summary["baseline_km"]
        summary["Alternative distance (km)"] = summary["alternative_km"]
        summary["Extra distance (km)"] = summary["additional_km"]
        summary["Distance increase (%)"] = summary["additional_pct"]
        summary["Result"] = summary["status"].map({
            "DETOUR_FOUND": "Detour found",
            "NO_ROUTE_IN_GRAPH": "No route in modeled graph",
            "NO_MEANINGFUL_CHANGE": "No meaningful route change",
        }).fillna("Other research outcome")

        total_scenarios = len(scenarios)
        detours = int(
            (scenarios["status"] == "DETOUR_FOUND").sum()
        )
        total_alternatives = len(results)

        limitations = (
            "Pasang Lhamu alternatives avoid their modeled blocked "
            "edges but are not field-verified. The routing graph is "
            "undirected, and some scenarios have no route in the "
            "modeled graph. These results do not establish real-world "
            "road safety or drivability."
        )

    # --------------------------------------------
    # Shared layout for both highway pages
    # --------------------------------------------

    st.subheader("Research Summary")

    a, b, c = st.columns(3)
    a.metric("Closure scenarios", total_scenarios)

    if highway == "arniko":
        b.metric("Scenarios with bypass candidates", detours)
        c.metric("Candidate route results", total_alternatives)
        st.caption(
            "Five route results are recorded as validated graph-derived "
            "candidates; Gati is provisional. Candidate counts do not "
            "represent distinct physical corridors or field-verified roads."
        )
    else:
        b.metric("Detours found", detours)
        c.metric("Alternative routes", total_alternatives)

    # Public demonstration overview, separate from full research results.
    st.subheader("Public Scenario Overview")

    location_catalogue = load_csv(
        "Dashboard/scenario_location_catalogue.csv"
    )

    if highway == "arniko":
        public_ids = [
            "ARNIKO_C0_40",
            "ARNIKO_C0_80",
            "ARNIKO_C1_20",
            "ARNIKO_C1_40",
            "ARNIKO_C1_60",
            "ARNIKO_C1_80",
        ]

        public_data = load_csv(
            "Dashboard/arniko_local_bypass_status.csv"
        )

        public_data = public_data.set_index(
            "scenario_id"
        ).loc[public_ids].reset_index()

        status_labels = {
            "VALIDATED_GRAPH_DERIVED_BYPASS":
                "Possible alternative route",
            "PROVISIONAL_GRAPH_DERIVED_BYPASS":
                "Possible route — needs further checking",
            "NO_BYPASS_FOUND_WITHIN_TESTED_LIMITS":
                "No suitable alternative found in this test",
            "NO_QUALIFYING_BYPASS_UNDER_TESTED_CONSTRAINTS":
                "No suitable alternative found in this test",
        }

        public_data["Outcome"] = (
            public_data["assessment_status"]
            .map(status_labels)
            .fillna("See research assessment")
        )

        public_data["Local bypass (km)"] = (
            pd.to_numeric(
                public_data["shortest_local_bypass_km"],
                errors="coerce"
            ).round(2)
        )

        public_data["Evidence"] = public_data[
            "assessment_status"
        ].map({
            "VALIDATED_GRAPH_DERIVED_BYPASS":
                "Route connects in the map data; not checked on the ground",
            "PROVISIONAL_GRAPH_DERIVED_BYPASS":
                "Needs further checking; avoidance of the closure was not confirmed",
            "NO_BYPASS_FOUND_WITHIN_TESTED_LIMITS":
                "No suitable alternative found within the tested limits",
            "NO_QUALIFYING_BYPASS_UNDER_TESTED_CONSTRAINTS":
                "No suitable alternative found under the tested conditions",
        })

        public_data["Highway"] = "Arniko"

    else:
        public_ids = [
            "JUNCTION_1",
            "NH42_S1_25",
            "NH42_S1_75",
            "NH42_S0_50",
            "NH18_S1_50",
            "NH18_S1_75",
        ]

        public_data = load_csv(
            "Results/pasang_final_17_scenario_research_table.csv"
        )

        public_data = public_data.set_index(
            "scenario_id"
        ).loc[public_ids].reset_index()

        public_data["Outcome"] = public_data["status"].map({
            "DETOUR_FOUND": "Alternative route found in the map data",
            "NO_ROUTE_IN_GRAPH": "No alternative found in the map data",
            "NO_MEANINGFUL_CHANGE": "No meaningful change to the route",
        }).fillna("See research assessment")

        public_data["Local bypass (km)"] = pd.to_numeric(
            public_data["alternative_km"],
            errors="coerce"
        ).round(2)

        # Pipal Taar has two saved mapped dashboard alternatives.
        # Display both in the public overview without changing the
        # original research results or the six-location summary.
        pipal_overview_routes = load_geojson(
            "Routes/dashboard_junction1_complete_bypasses.geojson"
        ).sort_values("alternative_rank")

        assert len(pipal_overview_routes) == 2
        assert (
            pipal_overview_routes["alternative_rank"].astype(int).tolist()
            == [1, 2]
        )

        pipal_overview_distances = "; ".join(
            f"Alternative {int(row.alternative_rank)}: "
            f"{float(row.distance_km):.2f} km"
            for row in pipal_overview_routes.itertuples()
        )

        pipal_overview_mask = (
            public_data["scenario_id"] == "JUNCTION_1"
        )
        assert pipal_overview_mask.sum() == 1

        public_data.loc[
            pipal_overview_mask, "Local bypass (km)"
        ] = pipal_overview_distances

        public_data.loc[
            pipal_overview_mask, "Outcome"
        ] = "2 mapped alternative routes in the map data"

        # NH42 public summary correction:
        # Use validated local bypasses for display only.
        # Original fixed-endpoint research CSV remains unchanged.
        nh42_local = load_geojson(
            "Routes/pasang_nh42_validated_local_bypasses.geojson"
        )

        nh42_counts = nh42_local.groupby("scenario_id").size()
        nh42_shortest = (
            nh42_local.sort_values("alternative_km")
            .drop_duplicates("scenario_id")
            .set_index("scenario_id")["alternative_km"]
        )

        for sid in ("NH42_S1_25", "NH42_S1_75"):
            assert sid in nh42_shortest.index
            assert (public_data["scenario_id"] == sid).sum() == 1

            public_data.loc[
                public_data["scenario_id"] == sid,
                "Local bypass (km)"
            ] = round(float(nh42_shortest.loc[sid]), 2)

            count = int(nh42_counts.loc[sid])
            public_data.loc[
                public_data["scenario_id"] == sid,
                "Outcome"
            ] = (
                f"{count} possible alternative routes in the map data"
                if count > 1
                else "1 possible alternative route in the map data"
            )

        public_data["Evidence"] = (
            "Based on map data; not checked on the ground"
        )

        for sid in ("NH42_S1_25", "NH42_S1_75"):
            public_data.loc[
                public_data["scenario_id"] == sid,
                "Evidence"
            ] = (
                "Avoidance of the closure and road connections "
                "checked in map data; not checked on the ground"
            )

        public_data.loc[
            public_data["scenario_id"] == "JUNCTION_1",
            "Evidence"
        ] = (
            "Both routes are graph-derived; road access, "
            "passability and safety are not field-verified"
        )

        public_data["Highway"] = "Pasang Lhamu"

    location_lookup = location_catalogue[
        ["highway", "scenario_id", "location_label"]
    ].drop_duplicates(subset=["highway", "scenario_id"])

    public_data = public_data.merge(
        location_lookup,
        left_on=["Highway", "scenario_id"],
        right_on=["highway", "scenario_id"],
        how="left",
        validate="one_to_one"
    )

    assert len(public_data) == 6
    assert public_data["location_label"].notna().all()

    # Public-facing labels only; retain scenario IDs in research data.
    public_display = public_data.rename(columns={
        "location_label": "Location",
        "Outcome": "Result",
        "Local bypass (km)": "Alternative route distance (km)",
        "Evidence": "What this result means",
    })[
        [
            "Location",
            "Result",
            "Alternative route distance (km)",
            "What this result means",
        ]
    ]

    # Six-row public summary: readable, wrapping, theme-aware HTML.
    # Research data and internal scenario identifiers remain unchanged.
    from html import escape as escape_html

    public_table_bg = "#ffffff" if theme == "light" else "#131f31"
    public_table_fg = "#17243a" if theme == "light" else "#f1f5f9"
    public_table_border = "#dce4ef" if theme == "light" else "#2b3a50"
    public_header_bg = "#edf2f8" if theme == "light" else "#1c2b41"

    public_table = public_display.copy()
    distance_column = "Alternative route distance (km)"
    public_table[distance_column] = public_table[distance_column].apply(
        lambda value: (
            value
            if isinstance(value, str)
            else f"{float(value):.2f}"
            if pd.notna(value)
            else "—"
        )
    )

    public_headers = "".join(
        "<th scope='col'>" + escape_html(str(column)) + "</th>"
        for column in public_table.columns
    )

    public_rows = "".join(
        "<tr>" + "".join(
            "<td>" + escape_html(str(value)) + "</td>"
            for value in row
        ) + "</tr>"
        for row in public_table.itertuples(index=False, name=None)
    )

    st.markdown(
        f"""
        <style>
        .public-scenario-table {{
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
            background: {public_table_bg};
            color: {public_table_fg};
            font-size: 0.88rem;
        }}
        .public-scenario-table th,
        .public-scenario-table td {{
            padding: 0.75rem;
            text-align: left;
            vertical-align: top;
            border: 1px solid {public_table_border};
            overflow-wrap: anywhere;
            white-space: normal;
            color: {public_table_fg} !important;
        }}
        .public-scenario-table th {{
            background: {public_header_bg} !important;
            font-weight: 600;
        }}
        .public-scenario-table td {{
            background: {public_table_bg} !important;
        }}
        @media (max-width: 600px) {{
            .public-scenario-table {{
                font-size: 0.76rem;
            }}
            .public-scenario-table th,
            .public-scenario-table td {{
                padding: 0.45rem;
            }}
        }}
        </style>
        <div style="overflow-x:auto; width:100%;">
          <table class="public-scenario-table">
            <thead><tr>{public_headers}</tr></thead>
            <tbody>{public_rows}</tbody>
          </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Six selected public demonstrations. Distances are "
        "scenario-specific modeled alternatives, not necessarily "
        "complete journeys. A missing distance does not establish "
        "that no real-world bypass exists."
    )

    with st.expander(
        "Detailed route scenarios and research results",
        expanded=False
    ):
        st.subheader("Select a Closure Scenario")

        # Public demonstrations use six selected scenarios per highway.
        if highway == "arniko":
            public_options = [
                (0, 40),  # Dolalghat
                (0, 80),  # Itafu
                (1, 20),  # Dandakateri
                (1, 40),  # Gati
                (1, 60),  # Panthali
                (1, 80),  # Larcha
            ]
        else:
            public_options = [
                "JUNCTION_1",
                "NH42_S1_25",
                "NH42_S1_75",
                "NH42_S0_50",
                "NH18_S1_50",
                "NH18_S1_75",
            ]

        assert all(option in options for option in public_options), (
            "Public scenario missing from research options"
        )

        selected = st.selectbox(
            "Hypothetical road closure",
            public_options,
            format_func=label,
            key=f"{highway}_unified_scenario"
        )

        st.subheader("Local Road Section and Bypass Comparison")
        st.caption(
            "Distances compare the original road section with an "
            "alternative between the same local entry and exit points. "
            "These are not complete highway journeys."
        )

        local_records = []

        if highway == "arniko":
            original = load_csv(
                "Dashboard/arniko_local_original_segments.csv"
            ).set_index("scenario_id")

            local_files = {
                "ARNIKO_C0_40": "dashboard_dolalghat_local_bypass.geojson",
                "ARNIKO_C0_80": "dashboard_itafu_local_bypass.geojson",
                "ARNIKO_C1_20": "dashboard_dandakateri_local_bypass.geojson",
                "ARNIKO_C1_40": "dashboard_arniko_c1_40_local_bypass.geojson",
            }

            selected_id = f"ARNIKO_C{selected[0]}_{selected[1]}"
            if selected_id in local_files and selected_id in original.index:
                local_routes = gpd.read_file(
                    ROOT / "Routes" / local_files[selected_id]
                ).sort_values("alternative_rank")
                baseline = float(
                    original.loc[selected_id, "original_nh34_segment_km"]
                )
                for _, route in local_routes.iterrows():
                    alternative = float(route["distance_km"])
                    local_records.append({
                        "Alternative": int(route["alternative_rank"]),
                        "Original local section (km)": round(baseline, 2),
                        "Local bypass (km)": round(alternative, 2),
                        "Additional distance (km)": round(
                            alternative - baseline, 2
                        ),
                        "Distance increase (%)": round(
                            (alternative / baseline - 1) * 100, 1
                        ),
                        "Evidence status": (
                            "Provisional — additional verification needed"
                            if selected_id == "ARNIKO_C1_40"
                            else "Graph-derived; not field verified"
                        ),
                    })

        else:
            local_routes = gpd.read_file(
                ROOT / "Routes/pasang_nh42_validated_local_bypasses.geojson"
            )
            local_routes = local_routes.loc[
                local_routes["scenario_id"] == selected
            ].sort_values("alternative_rank")

            for _, route in local_routes.iterrows():
                local_records.append({
                    "Alternative": int(route["alternative_rank"]),
                    "Original local section (km)": round(
                        float(route["baseline_km"]), 2
                    ),
                    "Local bypass (km)": round(
                        float(route["alternative_km"]), 2
                    ),
                    "Additional distance (km)": round(
                        float(route["additional_km"]), 2
                    ),
                    "Distance increase (%)": round(
                        float(route["additional_pct"]), 1
                    ),
                    "Evidence status": "Graph-validated; not field verified",
                })

        if highway == "pasang" and selected == "JUNCTION_1":
            junction_routes = gpd.read_file(
                ROOT / "Routes/dashboard_junction1_complete_bypasses.geojson"
            )
            junction_routes = junction_routes.loc[
                junction_routes["scenario_id"] == selected
            ].sort_values("alternative_rank")

            # Reconstructed original-road estimates for each route's
            # own endpoints. A 329.952 m network gap is approximated
            # by a straight connection; estimates are provisional.
            pipal_baselines = {
                1: 3.637845,
                2: 2.363346,
            }
            pipal_sensitivity = {
                1: "9.54–19.48%",
                2: "117.55–147.92%",
            }

            junction_display = pd.DataFrame([
                {
                    "Alternative": int(route["alternative_rank"]),
                    "Original road, provisional (km)": round(
                        pipal_baselines[int(route["alternative_rank"])], 3
                    ),
                    "Mapped bypass (km)": round(
                        float(route["distance_km"]), 3
                    ),
                    "Additional distance, provisional (km)": round(
                        float(route["distance_km"])
                        - pipal_baselines[int(route["alternative_rank"])], 3
                    ),
                    "Increase, provisional (%)": round(
                        100 * (
                            float(route["distance_km"])
                            - pipal_baselines[int(route["alternative_rank"])]
                        ) / pipal_baselines[int(route["alternative_rank"])],
                        2
                    ),
                    "Sensitivity range (increase)": pipal_sensitivity[
                        int(route["alternative_rank"])
                    ],
                }
                for _, route in junction_routes.iterrows()
            ])

            # Two-row research comparison: styled to match the
            # desktop dashboard's dark navy theme.
            # Data and calculations remain unchanged.
            pipal_headers = "".join(
                f"<th>{column}</th>"
                for column in junction_display.columns
            )
            pipal_rows = "".join(
                "<tr>" + "".join(
                    f"<td>{value}</td>"
                    for value in row
                ) + "</tr>"
                for row in junction_display.itertuples(
                    index=False, name=None
                )
            )

            st.markdown(
                """
                <style>
                .pipal-comparison-wrap {
                    width: 100%;
                    overflow-x: auto;
                    margin: 0.75rem 0 1rem;
                    border: 1px solid #30435d;
                    border-radius: 9px;
                    background: #111e31;
                }
                .pipal-comparison-table {
                    width: 100%;
                    border-collapse: collapse;
                    color: #f1f5f9;
                    font-size: 0.88rem;
                    font-variant-numeric: tabular-nums;
                }
                .pipal-comparison-table th {
                    background: #1c304a;
                    color: #e2e8f0;
                    font-weight: 600;
                    text-align: left;
                    padding: 13px 11px;
                    border-bottom: 1px solid #40516a;
                    white-space: normal;
                }
                .pipal-comparison-table td {
                    padding: 13px 11px;
                    border-bottom: 1px solid #293c55;
                    color: #f1f5f9;
                    text-align: right;
                    white-space: nowrap;
                }
                .pipal-comparison-table td:first-child {
                    text-align: left;
                    font-weight: 600;
                }
                .pipal-comparison-table tbody tr:nth-child(even) {
                    background: #182941;
                }
                .pipal-comparison-table tbody tr:last-child td {
                    border-bottom: none;
                }
                </style>
                <div class="pipal-comparison-wrap">
                    <table class="pipal-comparison-table">
                        <thead><tr>"""
                + pipal_headers
                + """</tr></thead>
                        <tbody>"""
                + pipal_rows
                + """</tbody>
                    </table>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.warning(
                "PROVISIONAL MODEL ESTIMATES — not verified original-road "
                "measurements. The reconstructed network has a missing "
                "329.952 m highway section, approximated by a straight "
                "connection. Sensitivity ranges test hypothetical gap "
                "lengths from 1.0× to 2.0× that distance; they are not "
                "statistical confidence intervals. Each alternative has "
                "a different starting point and is compared against its "
                "own reconstructed original-road baseline."
            )
            st.caption(
                "These graph-derived alternatives are not field-verified. "
                "Road access, driving suitability, passability, and safety "
                "remain unconfirmed."
            )
        elif local_records:
            st.dataframe(
                pd.DataFrame(local_records),
                width="stretch",
                hide_index=True,
            )
            st.caption(
                "Graph-derived alternatives are not verified for "
                "real-world road access, driving suitability, or safety."
            )
        else:
            st.info(
                "A comparable local entry-to-exit bypass measurement "
                "is not available for this selected closure. "
                "This does not mean that no real-world alternative exists."
            )

        st.info(limitations)




def public_closure_label(highway, selected):
    """Return a geographic reference label for a saved scenario."""
    catalogue = load_csv(
        "Dashboard/scenario_location_catalogue.csv"
    )

    if highway.startswith("Arniko"):
        scenario_id = (
            f"ARNIKO_C{int(selected[0])}_{int(selected[1])}"
        )
    else:
        scenario_id = str(selected)

        # Match southern routing IDs to catalogue IDs.
        southern_map = {
            "NH18_SOUTH_25": "NH18_SOUTH_1",
            "NH18_SOUTH_50": "NH18_SOUTH_2",
            "NH18_SOUTH_75": "NH18_SOUTH_3",
        }
        scenario_id = southern_map.get(
            scenario_id, scenario_id
        )

    match = catalogue.loc[
        catalogue["scenario_id"].astype(str) == scenario_id
    ]

    if match.empty:
        return "Saved simulated closure — location not named"

    return (
        str(match.iloc[0]["location_label"])
        + " — simulated closure"
    )


def get_saved_closure_reference(highway, selected):
    """Return a saved scenario reference coordinate, if available.

    This is a map reference, not necessarily the exact
    blocked road edge or an observed landslide location.
    """
    if highway.startswith("Arniko"):
        locations = load_geojson(
            "Routes/arniko_highway_wide_closure_locations.geojson"
        )
        match = locations.loc[
            (locations["component"] == selected[0])
            & (locations["position_pct"] == selected[1])
        ]
        if match.empty:
            return None

        point = match.geometry.iloc[0]
        return (float(point.y), float(point.x))

    if selected.startswith(("NH18_S", "NH42_S")):
        # Exclude southern NH18 IDs, which do not have
        # saved precise blockage locations.
        if selected.startswith("NH18_SOUTH"):
            return None

        parts = selected.split("_")
        if len(parts) != 3:
            return None

        designation = parts[0]
        section_id = int(parts[1][1:])
        position = int(parts[2])

        locations = load_geojson(
            "Routes/pasang_northern_nh18_nh42_locations_corrected.geojson"
        )

        match = locations.loc[
            (locations["designation"] == designation)
            & (locations["section_id"] == section_id)
            & (locations["closure_position_pct"] == position)
        ]

        if match.empty:
            return None

        # Representative point of the saved closure geometry.
        geom = match.geometry.iloc[0]
        point = geom.representative_point()
        return (float(point.y), float(point.x))

    if selected.startswith("JUNCTION_"):
        junction_id = int(selected.split("_")[1])

        locations = load_geojson(
            "Routes/pasang_nh18_nh42_junction_footprints.geojson"
        )

        match = locations.loc[
            locations["junction_id"] == junction_id
        ]

        if match.empty:
            return None

        point = match.geometry.iloc[0].representative_point()
        return (float(point.y), float(point.x))

    return None


def route_map(gdf, selected=None, closure_point=None, closure_label=None, highway_name=None, scenario_id=None):
    if selected is not None:
        gdf = gdf[selected].copy()

    if gdf.empty:
        st.info("No route geometry available.")
        return

    bounds = gdf.total_bounds
    center = gdf.geometry.union_all().centroid

    m = folium.Map(
        location=[center.y, center.x],
        zoom_start=10,
        tiles="OpenStreetMap",
        control_scale=True
    )

    def risk_color(score):
        if pd.isna(score):
            return "#808080"
        score = float(score)
        if score < 0.20:
            return "#2E7D32"
        if score < 0.40:
            return "#F9A825"
        if score < 0.60:
            return "#EF6C00"
        return "#C62828"

    # ----------------------------------------------
    # Full 5 km model-estimated susceptibility grid
    # ----------------------------------------------

    grid = load_geojson(
        "Dashboard/rf_susceptibility_grid_2018.geojson"
    )

    pad = 0.035

    grid = grid.cx[
        bounds[0] - pad : bounds[2] + pad,
        bounds[1] - pad : bounds[3] + pad
    ].copy()

    grid_layer = folium.FeatureGroup(
        name="2018 RF susceptibility grid (5 km)",
        show=False
    )

    for _, cell in grid.iterrows():
        score = float(cell["rf_score_2018"])
        color = risk_color(score)

        folium.GeoJson(
            cell.geometry.__geo_interface__,
            style_function=lambda feature, c=color: {
                "fillColor": c,
                "color": "#555555",
                "weight": 0.6,
                "fillOpacity": 0.30,
                "opacity": 0.35
            },
            tooltip=(
                f"Grid {cell['grid_id']} | "
                f"2018 RF score: {score:.3f}"
            )
        ).add_to(grid_layer)

    grid_layer.add_to(m)

    # ----------------------------------------------
    # RF-scored highway sections
    # ----------------------------------------------

    sections = load_geojson(
        "Data/two_highway_rf_road_sections_rebuilt_2018.geojson"
    )

    sections = sections.cx[
        bounds[0] - pad : bounds[2] + pad,
        bounds[1] - pad : bounds[3] + pad
    ].copy()

    highway_layer = folium.FeatureGroup(
        name="RF-scored highway sections",
        show=False
    )

    for _, section in sections.iterrows():
        if section.geometry is None or section.geometry.is_empty:
            continue

        score = section["rf_score"]
        color = risk_color(score)

        folium.GeoJson(
            section.geometry.__geo_interface__,
            style_function=lambda feature, c=color: {
                "color": c,
                "weight": 5,
                "opacity": 0.85
            },
            tooltip=(
                f"Highway RF score: {float(score):.3f}"
                if pd.notna(score)
                else "RF score unavailable"
            )
        ).add_to(highway_layer)

    highway_layer.add_to(m)

    # ----------------------------------------------
    # Validated alternative routes
    # ----------------------------------------------

    route_colors = ["#1565C0", "#8E24AA", "#00ACC1"]

    # Preserve original route ranks for corrected local bypasses.
    # Other scenarios retain their existing sequential display ranks.
    is_local_arniko = (
        highway_name == "Arniko"
        and scenario_id in ("ARNIKO_C0_40", "ARNIKO_C0_80")
    )

    preserve_route_ranks = (
        is_local_arniko
        or (
            highway_name == "Pasang Lhamu"
            and scenario_id in ("NH42_S1_25", "NH42_S1_75")
        )
    )

    original_ranks = sorted(
        int(r) for r in gdf["alternative_rank"].dropna().unique()
    )

    display_ranks = (
        {rank: rank for rank in original_ranks}
        if preserve_route_ranks
        else {
            original_rank: display_rank
            for display_rank, original_rank in enumerate(
                original_ranks, start=1
            )
        }
    )

    for _, row in gdf.iterrows():
        rank = display_ranks[int(row["alternative_rank"])]
        color = route_colors[(rank - 1) % 3]

        layer = folium.FeatureGroup(
            name=f"Alternative {rank}",
            show=True
        )

        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda feature, c=color: {
                "color": c,
                "weight": 3.5,
                "opacity": 0.95
            },
            tooltip=(
                f"Alternative {rank} | "
                f"{float(row['distance_km']):.2f} km"
            )
        ).add_to(layer)

        layer.add_to(m)

        # NH42_LOCAL_ENDPOINT_MARKERS_V1
        # These are modeled route endpoints, not field-verified access points.
        if (
            highway_name == "Pasang Lhamu"
            and scenario_id in ("NH42_S1_25", "NH42_S1_75")
        ):
            geometry = row.geometry

            if (
                geometry is not None
                and not geometry.is_empty
                and geometry.geom_type == "LineString"
            ):
                endpoint_specs = [
                    (
                        geometry.coords[0],
                        "Modeled NH42 highway departure",
                        "#16a34a",
                    ),
                    (
                        geometry.coords[-1],
                        "Modeled NH42 highway reconnection",
                        "#f59e0b",
                    ),
                ]

                for (lon, lat), label, marker_color in endpoint_specs:
                    popup_text = (
                        f"<b>{label}</b><br>"
                        f"Alternative {rank}<br>"
                        f"Coordinates: {lat:.6f}, {lon:.6f}<br>"
                        "Geometric connection to mapped NH42; "
                        "Road access and drivability not field-verified."
                    )

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=7,
                        color="white",
                        weight=2,
                        fill=True,
                        fill_color=marker_color,
                        fill_opacity=1,
                        tooltip=label,
                        popup=folium.Popup(
                            popup_text,
                            max_width=320,
                        ),
                    ).add_to(layer)

    m.fit_bounds([
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]]
    ])

    # Show only alternatives present in the selected route geometry.
    available_ranks = sorted(display_ranks.values())

    legend_items = "".join(
        (
            f'<span style="color:{route_colors[(rank - 1) % 3]};">'
            '&#9644;</span> '
            f'Alternative {rank}<br>'
        )
        for rank in available_ranks
    )

    closure_legend = (
        '<b>Simulated Road Closure</b><br>'
        '<span style="color:#dc2626;">&#9679;</span> '
        'Closure reference location<br>'
        '<hr style="margin:7px 0;">'
        if closure_point is not None
        else ""
    )

    legend = f"""
    <div style="
        position:fixed;
        bottom:30px;
        left:30px;
        z-index:9999;
        background:white;
        padding:12px 15px;
        border:1px solid #bbb;
        border-radius:8px;
        font-size:12px;
        color:#222;
        box-shadow:0 2px 8px #0002;
    ">
        {closure_legend}
        <b>Alternative Routes</b><br>
        {legend_items}
        <small>Distance-ranked, not safety-ranked</small>
    </div>
    """

    m.get_root().html.add_child(
        folium.Element(legend)
    )


    # Display saved simulated closure geometry where available.
    # This is modeled road disruption, not an observed landslide.
    if highway_name == "Pasang Lhamu" and scenario_id is not None:
        closure_geometry = None

        if str(scenario_id).startswith(("NH18_S", "NH42_S")):
            if not str(scenario_id).startswith("NH18_SOUTH"):
                parts = str(scenario_id).split("_")

                if len(parts) == 3:
                    designation = parts[0]
                    section_id = int(parts[1][1:])
                    position = int(parts[2])

                    footprints = load_geojson(
                        "Routes/pasang_northern_nh18_nh42_locations_corrected.geojson"
                    )

                    matching = footprints.loc[
                        (footprints["designation"] == designation)
                        & (footprints["section_id"] == section_id)
                        & (footprints["closure_position_pct"] == position)
                    ]

                    if not matching.empty:
                        closure_geometry = matching.geometry.iloc[0]

        elif str(scenario_id).startswith("JUNCTION_"):
            junction_id = int(str(scenario_id).split("_")[1])

            footprints = load_geojson(
                "Routes/pasang_nh18_nh42_junction_footprints.geojson"
            )

            matching = footprints.loc[
                footprints["junction_id"] == junction_id
            ]

            if not matching.empty:
                closure_geometry = matching.geometry.iloc[0]

        if closure_geometry is not None:
            # Retain the simulated footprint as an optional map layer.
            # The standard red reference marker remains the default.
            footprint_layer = folium.FeatureGroup(
                name="Simulated closure footprint",
                show=False
            )
            folium.GeoJson(
                closure_geometry.__geo_interface__,
                style_function=lambda feature: {
                    "color": "#dc2626",
                    "weight": 3,
                    "opacity": 0.85,
                    "fillColor": "#dc2626",
                    "fillOpacity": 0.10,
                },
                tooltip="Saved simulated closure footprint (not an observed landslide)",
            ).add_to(footprint_layer)
            footprint_layer.add_to(m)


    if highway_name == "Arniko" and scenario_id in (
        "ARNIKO_C0_40", "ARNIKO_C0_80",
        "ARNIKO_C1_20", "ARNIKO_C1_40"
    ):
        route_info = gdf.iloc[0]
        start_lon, start_lat = list(route_info.geometry.coords)[0]
        end_lon, end_lat = list(route_info.geometry.coords)[-1]

        junction_markers = [
            (
                f"Entry: {route_info['entry_name']}",
                start_lat, start_lon, "#16a34a"
            ),
            (
                f"Exit: {route_info['exit_name']}",
                end_lat, end_lon, "#f97316"
            ),
        ]
        for label, lat, lon, color in junction_markers:
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                color="#ffffff",
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=1.0,
                tooltip=label,
                popup=folium.Popup(
                    f"<b>{label}</b>"
                    f"<br>Latitude: {lat:.6f}"
                    f"<br>Longitude: {lon:.6f}"
                    "<br>Descriptive junction label, not an official name"
                    "<br>Graph-derived route; not field-verified",
                    max_width=340,
                ),
            ).add_to(m)

    if closure_point is not None:
        lat, lon = closure_point

        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=9,
            color="#ffffff",
            weight=3,
            fill=True,
            fill_color="#dc2626",
            fill_opacity=1.0,
            tooltip=(
                closure_label
                or "Saved simulated-closure reference location"
            ),
            popup=folium.Popup(
                (
                    f"<b>{closure_label or 'Simulated closure'}</b>"
                    "<br>Saved geographic reference point"
                    "<br>Not necessarily the exact blocked road edge"
                    "<br>Not an observed landslide"
                    f"<br>Latitude: {float(lat):.5f}"
                    f"<br>Longitude: {float(lon):.5f}"
                ),
                max_width=320,
            ),
        ).add_to(m)




    # Geographic reference points only.
    # These are not simulated closures or verified road access points.
    places = load_geojson(
        "Dashboard/highway_place_references.geojson"
    )

    if not places.empty:
        places = places.to_crs("EPSG:4326")

        if highway_name is not None:
            places = places.loc[
                places["highway"] == highway_name
            ].copy()

        places_layer = folium.FeatureGroup(
            name="Places & Landmarks (reference only)",
            show=True,
            control=False
        )

        # Display only places near the currently mapped routes.
        # A geographic buffer also includes nearby detour references.
        route_bounds = gdf.to_crs("EPSG:4326").total_bounds
        west, south, east, north = route_bounds

        nearby_places = places.cx[
            west - 0.08:east + 0.08,
            south - 0.08:north + 0.08
        ]

        for _, place in nearby_places.iterrows():
            lat = float(place.geometry.y)
            lon = float(place.geometry.x)
            name = str(place["place"])
            kind = str(place["reference_type"])

            # Avoid placing a second marker directly on top
            # of the selected red closure-reference marker.
            if closure_point is not None:
                closure_lat, closure_lon = closure_point
                if (
                    abs(lat - float(closure_lat)) < 0.00001
                    and abs(lon - float(closure_lon)) < 0.00001
                ):
                    continue

            marker_color = (
                "#7c3aed"
                if kind == "Nearby detour reference"
                else "#2563eb"
            )

            folium.CircleMarker(
                location=[lat, lon],
                radius=5,
                color="white",
                weight=2,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.95,
                tooltip=name,
                popup=folium.Popup(
                    f"<b>{name}</b><br>"
                    "Geographic reference point; "
                    "not a simulated blockage.",
                    max_width=250
                )
            ).add_to(m)

            # Place names remain available on hover/click.


        # Landmark markers are attached directly to the map.

    # Modeled highway exit and connection for Junction 1 only.
    if highway_name == "Pasang Lhamu" and scenario_id == "JUNCTION_1":
        route_info = gdf.iloc[0]
        route_coords = list(route_info.geometry.coords)

        junction_points = [
            (
                "Pipal Taar, Bidur-05 — modeled bypass entry",
                route_coords[0],
                "#16a34a",
            ),
            (
                "Bidur-04 — modeled bypass exit",
                route_coords[-1],
                "#f97316",
            ),
        ]

        for label, (lon, lat), color in junction_points:
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                color="white",
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=1,
                tooltip=label,
                popup=folium.Popup(
                    f"<b>{label}</b><br>"
                    "Graph-derived corridor connection; "
                    "not field-verified.",
                    max_width=300,
                ),
            ).add_to(m)

    folium.LayerControl(
        collapsed=True
    ).add_to(m)

    st_folium(
        m,
        height=550,
        width="stretch"
    )

    st.caption(
        "The 5 km polygons show retrospective 2018 Random "
        "Forest susceptibility scores. These are uncalibrated "
        "model outputs, not confirmed landslide locations "
        "or forecasts. Route lines show validated modeled "
        "alternatives, not field-verified safe roads."
    )


def closure_only_map(highway, selected):
    """Show a saved simulated closure without inventing a detour."""
    closure_point = get_saved_closure_reference(highway, selected)

    if closure_point is None:
        st.warning("No saved geographic reference is available.")
        return

    lat, lon = closure_point

    m = folium.Map(
        location=[lat, lon],
        zoom_start=13,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # Use only saved closure geometries.
    closure_geometry = None

    if highway.startswith("Pasang"):
        if str(selected).startswith("JUNCTION_"):
            junction_id = int(str(selected).split("_")[1])
            footprints = load_geojson(
                "Routes/pasang_nh18_nh42_junction_footprints.geojson"
            )
            match = footprints.loc[
                footprints["junction_id"] == junction_id
            ]
        else:
            parts = str(selected).split("_")
            match = gpd.GeoDataFrame()

            if len(parts) == 3:
                designation = parts[0]
                section_id = int(parts[1][1:])
                position = int(parts[2])

                footprints = load_geojson(
                    "Routes/pasang_northern_nh18_nh42_locations_corrected.geojson"
                )
                match = footprints.loc[
                    (footprints["designation"] == designation)
                    & (footprints["section_id"] == section_id)
                    & (footprints["closure_position_pct"] == position)
                ]

        if len(match) == 1:
            closure_geometry = match.geometry.iloc[0]

    # Display nearby RF-scored highway sections as optional context.
    sections = load_geojson(
        "Data/two_highway_rf_road_sections_rebuilt_2018.geojson"
    )

    pad = 0.025
    nearby = sections.cx[
        lon - pad : lon + pad,
        lat - pad : lat + pad
    ].copy()

    highway_layer = folium.FeatureGroup(
        name="RF-scored highway sections (2018)",
        show=True
    )

    for _, row in nearby.iterrows():
        if row.geometry is None or row.geometry.is_empty:
            continue

        folium.GeoJson(
            row.geometry.__geo_interface__,
            style_function=lambda feature: {
                "color": "#64748b",
                "weight": 3,
                "opacity": 0.7
            },
            tooltip="Modeled highway section (2018)"
        ).add_to(highway_layer)

    highway_layer.add_to(m)

    # Highlight the saved modeled closure footprint when available.
    if closure_geometry is not None and not closure_geometry.is_empty:
        folium.GeoJson(
            closure_geometry.__geo_interface__,
            name="Saved simulated closure footprint",
            style_function=lambda feature: {
                "color": "#dc2626",
                "weight": 6,
                "opacity": 0.95,
                "fillColor": "#dc2626",
                "fillOpacity": 0.18
            },
            tooltip="Simulated closure — not an observed landslide"
        ).add_to(m)

        minx, miny, maxx, maxy = closure_geometry.bounds
        if maxx > minx and maxy > miny:
            m.fit_bounds([[miny, minx], [maxy, maxx]])

    folium.CircleMarker(
        location=[lat, lon],
        radius=9,
        color="white",
        weight=3,
        fill=True,
        fill_color="#dc2626",
        fill_opacity=1,
        tooltip=public_closure_label(highway, selected),
        popup=(
            public_closure_label(highway, selected)
            + "<br>Saved simulated closure reference"
            + "<br>Not an observed landslide"
        )
    ).add_to(m)

    folium.LayerControl(collapsed=True).add_to(m)

    st_folium(m, height=550, width="stretch")

    st.caption(
        "Map interpretation: Red indicates a saved simulated closure "
        "or reference location, not necessarily the exact blocked-road "
        "geometry. No alternative route is displayed because none was "
        "identified in the modeled road network under the tested "
        "conditions. This does not mean that no alternative exists "
        "in the real world."
    )


def comparison_chart(df, distance_col, score_col, label_col):
    plot = df.copy()
    plot[label_col] = plot[label_col].astype(str)

    fig = px.scatter(
        plot,
        x=distance_col,
        y=score_col,
        color=label_col,
        hover_data=list(plot.columns[:3]),
        labels={
            distance_col: "Route distance (km)",
            score_col: "2018 RF exposure score"
        },
        title="Distance versus retrospective RF exposure"
    )
    st.plotly_chart(fig, width="stretch")


if page == "Landslide Route Explorer":
    st.header("Interactive Landslide & Alternative Route Explorer")

    st.write(
        "Select a highway and a previously validated hypothetical "
        "road-closure scenario. The dashboard displays its "
        "retrospective landslide susceptibility and available "
        "alternative routes."
    )

    highway = st.radio(
        "Choose highway",
        ["Arniko Highway (NH34)", "Pasang Lhamu Highway (NH18/NH42)"],
        horizontal=True,
        key="explorer_highway"
    )

    if highway.startswith("Arniko"):
        results = load_csv(
            "Results/arniko_final_12_route_research_table.csv"
        )
        routes = load_geojson(
            "Routes/arniko_5km_corridor_alternative_routes.geojson"
        )

        scenarios = load_csv(
            "Routes/arniko_highway_wide_closure_scenarios.csv"
        )

        scenarios = scenarios.sort_values(
            ["component", "closure_position_pct"]
        )

        arniko_status = load_csv(
            "Dashboard/arniko_local_bypass_status.csv"
        )

        # Only the six approved Arniko scenarios appear
        # in the public explorer. Research files are unchanged.
        public_arniko_scenarios = {
            (0, 40),  # Dolalghat
            (0, 80),  # Itafu
            (1, 20),  # Dandakateri
            (1, 40),  # Gati
            (1, 60),  # Panthali
            (1, 80),  # Larcha
        }

        options = [
            (int(r.component), int(r.closure_position_pct))
            for r in scenarios.itertuples()
            if (int(r.component), int(r.closure_position_pct))
            in public_arniko_scenarios
        ]

        assert len(options) == 6, (
            "Expected exactly six public Arniko scenarios."
        )

        selected = st.selectbox(
            "Choose a simulated road blockage",
            options,
            format_func=lambda x: public_closure_label(
                "Arniko", x
            ),
            key="explorer_arniko_scenario"
        )

        subset = results.loc[
            (results["component"] == selected[0]) &
            (results["closure_position_pct"] == selected[1])
        ].sort_values("alternative_rank")

        geo_subset = routes.loc[
            (routes["component"] == selected[0]) &
            (routes["closure_position_pct"] == selected[1])
        ].copy()

        selected_scenario_id = (
            f"ARNIKO_C{selected[0]}_{selected[1]}"
        )

        assessment = arniko_status.loc[
            arniko_status["scenario_id"] == selected_scenario_id
        ]

        assert len(assessment) == 1
        assessment_status = assessment.iloc[0]["assessment_status"]

        if assessment_status == "VALIDATED_GRAPH_DERIVED_BYPASS":
            st.success("Graph-derived local bypass candidate identified.")
        elif assessment_status == "PROVISIONAL_GRAPH_DERIVED_BYPASS":
            st.warning(
                "Provisional local bypass candidate. Avoidance of all "
                "originally blocked road edges has not been independently "
                "reproduced. Road passability and safety are unverified."
            )
        elif assessment_status in [
            "NO_BYPASS_FOUND_WITHIN_TESTED_LIMITS",
            "NO_QUALIFYING_BYPASS_UNDER_TESTED_CONSTRAINTS",
        ]:
            pass
        elif assessment_status == "REJECTED_SAME_SIDE_JUNCTIONS":
            st.warning(
                "No qualifying local bypass is currently established "
                "for this simulated closure."
            )
        else:
            st.info(
                "Local bypass assessment has not yet been completed "
                "for this simulated closure."
            )

        # The original route geometries represent the earlier
        # full-journey methodology. Only approved local-bypass scenarios
        # with validated or explicitly provisional status may show maps.
        map_eligible_statuses = {
            "VALIDATED_GRAPH_DERIVED_BYPASS",
            "PROVISIONAL_GRAPH_DERIVED_BYPASS",
        }
        if assessment_status not in map_eligible_statuses:
            subset = subset.iloc[0:0].copy()
            geo_subset = geo_subset.iloc[0:0].copy()

        # Dolalghat: local graph-derived bypass for map presentation only.
        # Original research routes and RF results remain untouched.
        if selected in [(0, 40), (0, 80), (1, 20), (1, 40)]:
            local_filename = {
                (0, 40): "dashboard_dolalghat_local_bypass.geojson",
                (0, 80): "dashboard_itafu_local_bypass.geojson",
                (1, 20): "dashboard_dandakateri_local_bypass.geojson",
                (1, 40): "dashboard_arniko_c1_40_local_bypass.geojson",
            }[selected]
            local_path = (
                Path(__file__).resolve().parents[1]
                / "Routes" / local_filename
            )
            available_local_routes = (
                gpd.read_file(local_path)
                .to_crs("EPSG:4326")
                .sort_values("alternative_rank")
            )

            # Show a route selector only when multiple local bypasses exist.
            if len(available_local_routes) > 1:
                route_options = available_local_routes[
                    "alternative_rank"
                ].astype(int).tolist()

                selected_route_rank = st.selectbox(
                    "Choose one local bypass alternative",
                    options=route_options,
                    format_func=lambda rank: (
                        f"Alternative {rank} — "
                        f"{float(available_local_routes.loc[available_local_routes['alternative_rank'].astype(int) == rank, 'distance_km'].iloc[0]):.3f} km"
                    ),
                    key=f"arniko_local_route_{selected[0]}_{selected[1]}",
                )
            else:
                selected_route_rank = int(
                    available_local_routes.iloc[0]["alternative_rank"]
                )

            # Only the chosen alternative is passed to the map.
            geo_subset = available_local_routes.loc[
                available_local_routes["alternative_rank"].astype(int)
                == selected_route_rank
            ].copy()

            selected_local_route = geo_subset.iloc[0]

            # Preserve the original research table; use its first row
            # only as a presentation shell for the local bypass metrics.
            subset = subset.loc[
                subset["alternative_rank"].astype(int) == 1
            ].copy()

            # Salgarhi has a validated local bypass GeoJSON,
            # but no corresponding original research result row.
            # Build a presentation-only row without changing
            # the original research data.

            subset["alternative_rank"] = selected_route_rank
            subset["distance_km"] = float(
                selected_local_route["distance_km"]
            )

            # Details update when the selected alternative changes.
            st.markdown(
                f"**Selected:** Alternative {selected_route_rank} "
                f"— {float(selected_local_route['distance_km']):.3f} km"
            )
            entry_lon, entry_lat = list(
                selected_local_route.geometry.coords
            )[0]
            exit_lon, exit_lat = list(
                selected_local_route.geometry.coords
            )[-1]

            st.write(
                f"🟢 **Entry:** {selected_local_route['entry_name']} "
                f"({entry_lat:.6f}, {entry_lon:.6f})"
            )
            st.write(
                f"🟠 **Exit:** {selected_local_route['exit_name']} "
                f"({exit_lat:.6f}, {exit_lon:.6f})"
            )
            st.caption(
                "Junction names are descriptive, not officially verified. "
                "The selected route is graph-derived and has not been "
                "field-verified."
            )

        score_col = "matched_rf_score"
        coverage_col = "coverage_pct"
        extra_col = "additional_distance_km"

    else:
        results = load_csv(
            "Results/pasang_final_33_alternatives.csv"
        )

        north = load_geojson(
            "Routes/pasang_multiple_alternative_routes.geojson"
        )
        south = load_geojson(
            "Routes/pasang_southern_nh18_alternatives.geojson"
        )

        routes = gpd.GeoDataFrame(
            pd.concat([north, south], ignore_index=True),
            geometry="geometry",
            crs="EPSG:4326"
        )

        # Six public scenarios selected for the local-detour demonstration.
        # Research CSV and GeoJSON files remain unchanged.
        public_scenarios = [
            "JUNCTION_1",   # Pipal Taar
            "NH42_S1_25",   # Near Batar Bazaar
            "NH42_S1_75",   # Near Trishuli
            "NH42_S0_50",   # Near Gerkhu
            "NH18_S1_50",   # Near Ramche
            "NH18_S1_75",   # Near Dhunche
        ]

        # Scenarios with NO_ROUTE_IN_GRAPH legitimately have no
        # rows in the alternatives CSV.
        scenario_research = load_csv(
            "Results/pasang_final_17_scenario_research_table.csv"
        )

        known_scenarios = set(
            scenario_research["scenario_id"].astype(str)
        )

        missing = [
            sid for sid in public_scenarios
            if sid not in known_scenarios
        ]

        if missing:
            st.error(
                "Saved scenario metadata is missing for: "
                + ", ".join(missing)
            )
            st.stop()

        options = public_scenarios

        selected = st.selectbox(
            "Choose a simulated road blockage",
            options,
            format_func=lambda x: public_closure_label(
                "Pasang Lhamu", x
            ),
            key="explorer_pasang_scenario"
        )

        subset = results.loc[
            results["scenario_id"] == selected
        ].sort_values("alternative_rank")

        geo_subset = routes.loc[
            routes["scenario_id"] == selected
        ].copy()

        # Display only selected local-detour alternatives.
        # Keep every original alternative in the research datasets.
        public_route_ranks = {
            "NH42_S2_25": [1, 2, 3],
            "NH42_S2_50": [1, 2, 3],
            "NH42_S1_25": [1, 2],
            "NH42_S1_75": [1],
        }

        if selected in public_route_ranks:
            allowed_ranks = public_route_ranks[selected]

            subset = subset.loc[
                subset["alternative_rank"].astype(int).isin(allowed_ranks)
            ].copy()

            geo_subset = geo_subset.loc[
                geo_subset["alternative_rank"].astype(int).isin(allowed_ranks)
            ].copy()

        # Junction 1: dashboard-derived complete NH18-to-NH42 bypasses.
        # Original research routes and RF results remain unchanged.
        if selected == "JUNCTION_1":
            subset = subset.loc[
                subset["alternative_rank"].isin([1, 3])
            ].copy()

            corrected_path = (
                Path(__file__).resolve().parents[1] / "Routes"
                / "dashboard_junction1_complete_bypasses.geojson"
            )
            corrected_routes = gpd.read_file(corrected_path).to_crs("EPSG:4326")

            # Retain research ranks internally (1, 3), so existing
            # map/legend numbering consistently displays (1, 2).
            corrected_routes["alternative_rank"] = (
                corrected_routes["original_research_rank"].astype(int)
            )
            # Let visitors inspect either saved mapped bypass.
            # Both remain graph-derived and not field-verified.
            corrected_routes = corrected_routes.sort_values(
                "distance_km"
            ).copy()

            junction_choices = corrected_routes[
                "original_research_rank"
            ].astype(int).tolist()

            selected_junction_rank = st.selectbox(
                "Choose a mapped Pipal Taar alternative",
                options=junction_choices,
                format_func=lambda rank: (
                    f"Alternative "
                    f"{junction_choices.index(rank) + 1} — "
                    f"{float(corrected_routes.loc[corrected_routes['original_research_rank'].astype(int) == rank, 'distance_km'].iloc[0]):.2f} km"
                ),
                key="pasang_junction1_route_choice",
            )

            corrected_routes = corrected_routes.loc[
                corrected_routes["original_research_rank"].astype(int)
                == selected_junction_rank
            ].copy()

            geo_subset = corrected_routes.copy()

            subset = subset.loc[
                subset["alternative_rank"].astype(int)
                == selected_junction_rank
            ].copy()

            st.caption(
                "Pipal Taar routes are graph-derived, not field-verified. "
                "The first uses a dashboard-only highway exit; "
                "the second is an extended mapped bypass. "
                "Road access, passability, and safety are unconfirmed."
            )

            corrected_distances = dict(zip(
                corrected_routes["alternative_rank"].astype(int),
                corrected_routes["distance_km"].astype(float)
            ))

            subset["original_segment_distance_km"] = subset["distance_km"]
            subset["distance_km"] = (
                subset["alternative_rank"]
                .astype(int)
                .map(corrected_distances)
            )

        # New graph-validated NH42 local bypasses.
        # Original research data and RF results remain unchanged.
        is_nh42_local = selected in ("NH42_S1_25", "NH42_S1_75")

        if is_nh42_local:
            local_path = (
                Path(__file__).resolve().parents[1]
                / "Routes"
                / "pasang_nh42_validated_local_bypasses.geojson"
            )

            available_nh42_routes = (
                gpd.read_file(local_path)
                .to_crs("EPSG:4326")
            )

            available_nh42_routes = available_nh42_routes.loc[
                available_nh42_routes["scenario_id"] == selected
            ].sort_values("alternative_rank").copy()

            assert not available_nh42_routes.empty

            if len(available_nh42_routes) > 1:
                selected_nh42_rank = st.selectbox(
                    "Choose one local bypass alternative",
                    options=available_nh42_routes[
                        "alternative_rank"
                    ].astype(int).tolist(),
                    format_func=lambda rank: (
                        f"Alternative {rank} — "
                        f"{float(available_nh42_routes.loc[available_nh42_routes['alternative_rank'] == rank, 'alternative_km'].iloc[0]):.3f} km"
                    ),
                    key=f"pasang_nh42_route_{selected}",
                )
            else:
                selected_nh42_rank = 1

            geo_subset = available_nh42_routes.loc[
                available_nh42_routes["alternative_rank"].astype(int)
                == selected_nh42_rank
            ].copy()

            geo_subset["distance_km"] = geo_subset["alternative_km"]
            selected_nh42 = geo_subset.iloc[0]

            subset = subset.iloc[:1].copy()
            subset["alternative_rank"] = selected_nh42_rank
            subset["distance_km"] = float(
                selected_nh42["alternative_km"]
            )
            subset["extra_vs_shortest_km"] = float(
                selected_nh42["additional_km"]
            )
            subset["length_weighted_rf_score_2018"] = float("nan")
            subset["rf_coverage_pct"] = float("nan")

            st.caption(
                f"Selected local bypass: "
                f"{float(selected_nh42['alternative_km']):.3f} km; "
                f"additional distance versus the corresponding "
                f"unblocked NH42 segment: "
                f"+{float(selected_nh42['additional_km']):.3f} km "
                f"({float(selected_nh42['additional_pct']):.1f}%). "
                "Graph-derived; road passability and safety "
                "have not been field-verified."
            )

        score_col = "length_weighted_rf_score_2018"
        coverage_col = "rf_coverage_pct"
        extra_col = "extra_vs_shortest_km"

    st.info(
        "These are previously modeled hypothetical closures, "
        "not reported landslide incidents. Selecting a scenario "
        "does not predict that a landslide will occur there."
    )

    # Determine the outcome from saved scenario metadata,
    # rather than a hard-coded list of scenario identifiers.
    if highway.startswith("Arniko"):
        closure_metadata = load_geojson(
            "Routes/arniko_highway_wide_closure_locations.geojson"
        )
        status_match = closure_metadata.loc[
            (closure_metadata["component"] == selected[0])
            & (closure_metadata["position_pct"] == selected[1])
        ]
    else:
        status_match = scenario_research.loc[
            scenario_research["scenario_id"].astype(str) == str(selected)
        ]

    if len(status_match) != 1:
        st.error(
            "Expected exactly one saved outcome for the selected "
            "scenario. Cannot safely determine its routing status."
        )
        st.stop()

    selected_status = str(status_match.iloc[0]["status"])

    no_bypass_scenario = selected_status == "NO_ROUTE_IN_GRAPH"

    if no_bypass_scenario:
        st.warning(
            "⚠️ No qualifying local bypass identified under "
            "the tested search constraints.\n\n"
            "No qualifying alternative route was identified "
            "in the available road network under the tested "
            "conditions. This does not prove that no alternative "
            "road exists. Road conditions and passability "
            "have not been field-verified."
        )

        st.subheader("Simulated blockage location")
        st.markdown(
            "**Selected simulated blockage:** "
            + public_closure_label(highway, selected)
        )
        closure_only_map(highway, selected)

    elif subset.empty or geo_subset.empty:
        st.warning(
            "No validated alternative geometry is available "
            "for this selection."
        )
    else:
        # Select the shortest displayed route by actual distance,
        # without changing the map or table's alternative ranks.
        shortest = subset.loc[
            pd.to_numeric(
                subset["distance_km"], errors="coerce"
            ).idxmin()
        ]

        c1, c2, c3 = st.columns(3)

        is_dolalghat_local = (
            highway.startswith("Arniko")
            and selected in [(0, 40), (0, 60), (0, 80), (1, 20), (1, 40)]
        )

        c1.metric(
            "Selected mapped bypass distance"
            if highway.startswith("Pasang")
            and selected == "JUNCTION_1"
            else "Selected local bypass distance"
            if highway.startswith("Pasang")
            and selected in ("NH42_S1_25", "NH42_S1_75")
            else "Local bypass distance"
            if is_dolalghat_local
            else "Shortest modeled local detour"
            if highway.startswith("Pasang")
            else "Shortest available alternative",
            f"{float(shortest['distance_km']):.2f} km"
        )

        if is_dolalghat_local:
            c2.metric("Local bypass RF score", "Not evaluated")
        elif highway.startswith("Pasang") and selected == "JUNCTION_1":
            c2.metric("Complete-bypass RF score", "Not evaluated")
        elif highway.startswith("Pasang") and selected in (
            "NH42_S1_25", "NH42_S1_75"
        ):
            c2.metric("Local bypass RF score", "Not evaluated")
        elif pd.notna(shortest[score_col]):
            c2.metric(
                "2018 route RF score",
                f"{float(shortest[score_col]):.3f}"
            )
        else:
            c2.metric("2018 route RF score", "Unavailable")

        if is_dolalghat_local:
            c3.metric("Local bypass RF coverage", "Not evaluated")
        elif highway.startswith("Pasang") and selected == "JUNCTION_1":
            c3.metric("Complete-bypass RF coverage", "Not evaluated")
        elif highway.startswith("Pasang") and selected in (
            "NH42_S1_25", "NH42_S1_75"
        ):
            c3.metric("Local bypass RF coverage", "Not evaluated")
        elif pd.notna(shortest[coverage_col]):
            c3.metric(
                "RF coverage",
                f"{float(shortest[coverage_col]):.1f}%"
            )
        else:
            c3.metric("RF coverage", "Unavailable")

        st.caption(
            "RF scores are retrospective and uncalibrated. "
            "They are not exact probabilities of future landslides."
        )

        # Pipal Taar: compare each selected mapped bypass against
        # its own provisional original-road reconstruction.
        if highway.startswith("Pasang") and selected == "JUNCTION_1":
            pipal_original_baselines = {
                1: 3.637845,
                3: 2.363346,
            }
            pipal_display_ranks = {
                1: 1,
                3: 2,
            }

            chosen_rank = int(selected_junction_rank)
            original_km = pipal_original_baselines[chosen_rank]
            bypass_km = float(shortest["distance_km"])
            additional_km = bypass_km - original_km
            increase_pct = 100 * additional_km / original_km

            st.markdown(
                "**Provisional original-road comparison — "
                f"Alternative {pipal_display_ranks[chosen_rank]}**"
            )

            pc1, pc2, pc3, pc4 = st.columns(4)
            pc1.metric("Original road (provisional)", f"{original_km:.3f} km")
            pc2.metric("Selected mapped bypass", f"{bypass_km:.3f} km")
            pc3.metric("Additional distance (provisional)", f"+{additional_km:.3f} km")
            pc4.metric("Distance increase (provisional)", f"+{increase_pct:.2f}%")

            st.caption(
                "Modeled estimate only: the original-road reconstruction "
                "uses an assumed straight-line connection across a "
                "329.952 m missing road-network section. The alternatives "
                "have different starting points, and each is compared "
                "against its own baseline. These are not field-verified "
                "road distances or safety assessments."
            )

        show_routes = st.button(
            "Simulate blockage and show alternative routes",
            type="primary",
            key="explorer_simulate"
        )

        state_key = "explorer_active_selection"
        current_selection = (
            highway,
            str(selected),
            int(selected_nh42_rank)
            if highway.startswith("Pasang")
            and selected in ("NH42_S1_25", "NH42_S1_75")
            else None,
        )

        if show_routes:
            st.session_state[state_key] = current_selection

        if st.session_state.get(state_key) == current_selection:
            st.subheader("Alternative routes on the map")

            st.markdown(
                "**Selected simulated blockage:** "
                + public_closure_label(highway, selected)
            )

            closure_reference = get_saved_closure_reference(
                highway, selected
            )

            route_map(
                geo_subset,
                closure_point=closure_reference,
                closure_label=public_closure_label(
                    highway, selected
                ),
                highway_name=(
                    "Arniko"
                    if highway.startswith("Arniko")
                    else "Pasang Lhamu"
                ),
                scenario_id=(
                    f"ARNIKO_C{selected[0]}_{selected[1]}"
                    if highway.startswith("Arniko")
                    and selected in [(0, 40), (0, 60), (0, 80), (1, 20), (1, 40)]
                    else None if highway.startswith("Arniko")
                    else selected
                )
            )

            if closure_reference is None:
                st.caption(
                    "A precise blockage reference location is not "
                    "available for this saved scenario."
                )
            else:
                st.caption(
                    "The red marker shows a saved scenario reference "
                    "location, not necessarily the exact blocked edge "
                    "or an observed landslide."
                )

            if highway == "Pasang Lhamu" and selected == "JUNCTION_1":
                st.caption(
                    "Junction 1 shows one dashboard-derived, graph-based "
                    "local bypass segment (4.346 km), from the modeled "
                    "entry near Pipal Taar, Bidur-05, to the modeled "
                    "exit in Bidur-04. These endpoints are based on "
                    "saved route geometry and nearby OSM locality data; "
                    "their road connections and drivability have not "
                    "been independently verified. The route avoids "
                    "the modeled closure, but has not been field-verified. "
                    "Original research RF scores do not evaluate this route."
                )

            if selected == (1, 40) and highway.startswith("Arniko"):
                st.warning(
                    "Gati local bypass is provisional. Its geometry avoids "
                    "the 100 m closure buffer, but avoidance of all "
                    "originally blocked road edges has not been confirmed. "
                    "The route has not been field-verified."
                )

            if is_dolalghat_local:
                st.caption(
                    "This scenario displays one graph-derived local bypass. "
                    f"Entry: {geo_subset.iloc[0]['entry_name']}; "
                    f"exit: {geo_subset.iloc[0]['exit_name']}. "
                    "These are descriptive labels, not official junction names. "
                    "The route has not been field-verified, and the original "
                    "research RF scores do not evaluate this bypass."
                )
                display = subset[
                    ["alternative_rank", "distance_km"]
                ].copy()
            elif highway == "Pasang Lhamu" and selected == "JUNCTION_1":
                display = subset[
                    ["alternative_rank", "distance_km"]
                ].copy()
            else:
                display = subset[
                    [
                        "alternative_rank",
                        "distance_km",
                        extra_col,
                        score_col,
                        coverage_col
                    ]
                ].copy()

            # Preserve validated NH42 alternative identities.
            # Other routes retain their existing display numbering.
            original_ranks = sorted(
                int(rank)
                for rank in geo_subset["alternative_rank"].dropna().unique()
            )

            if highway.startswith("Pasang") and selected in (
                "NH42_S1_25", "NH42_S1_75"
            ):
                displayed_ranks = {
                    rank: rank for rank in original_ranks
                }
            else:
                displayed_ranks = {
                    original_rank: display_rank
                    for display_rank, original_rank in enumerate(
                        original_ranks, start=1
                    )
                }
            display["alternative_rank"] = (
                display["alternative_rank"]
                .astype(int)
                .map(displayed_ranks)
            )

            if is_dolalghat_local:
                display.columns = [
                    "Alternative",
                    "Local bypass distance (km)"
                ]
            elif highway == "Pasang Lhamu" and selected == "JUNCTION_1":
                display.columns = [
                    "Alternative",
                    "Bypass segment distance (km)"
                ]
            else:
                display.columns = [
                    "Alternative",
                    "Distance (km)",
                    "Extra distance (km)",
                    "2018 RF score",
                    "RF coverage (%)"
                ]

            st.subheader("Compare available alternatives")

            # Presentation only: preserve the saved research values.
            # For corrected local Arniko bypasses, compare every saved
            # alternative even though the map shows only the selected one.
            if (
                highway.startswith("Arniko")
                and selected in [(0, 40), (0, 60), (0, 80), (1, 20), (1, 40)]
            ):
                # Presentation-only local baseline; not the
                # highway-wide research baseline or an RF result.
                local_baselines = load_csv(
                    "Dashboard/arniko_local_original_segments.csv"
                )
                local_scenario_id = (
                    f"ARNIKO_C{selected[0]}_{selected[1]}"
                )
                baseline_row = local_baselines.loc[
                    local_baselines["scenario_id"] == local_scenario_id
                ]
                assert len(baseline_row) == 1
                original_km = float(
                    baseline_row.iloc[0]["original_nh34_segment_km"]
                )

                comparison_display = (
                    available_local_routes[
                        ["alternative_rank", "distance_km"]
                    ]
                    .sort_values("alternative_rank")
                    .copy()
                )
                comparison_display.columns = [
                    "Alternative",
                    "Local bypass (km)"
                ]
                comparison_display["Original NH34 segment (km)"] = original_km
                comparison_display["Additional distance (km)"] = (
                    comparison_display["Local bypass (km)"] - original_km
                )
                comparison_display["Increase (%)"] = (
                    comparison_display["Additional distance (km)"]
                    / original_km * 100
                )
                comparison_display = comparison_display[
                    [
                        "Alternative",
                        "Original NH34 segment (km)",
                        "Local bypass (km)",
                        "Additional distance (km)",
                        "Increase (%)",
                    ]
                ]
                comparison_display["Alternative"] = (
                    comparison_display["Alternative"].astype(int)
                )
                comparison_display = comparison_display.round(3)
                st.caption(
                    "Original NH34 segment measured between the same "
                    "modeled bypass endpoints using saved NH34 geometry. "
                    "Distances and increases are modeled estimates, not "
                    "field-verified driving distances. Local bypasses "
                    "have not been evaluated with the 2018 RF model."
                )
            elif highway.startswith("Pasang") and selected in (
                "NH42_S1_25", "NH42_S1_75"
            ):
                comparison_display = available_nh42_routes[
                    [
                        "alternative_rank",
                        "baseline_km",
                        "alternative_km",
                        "additional_km",
                        "additional_pct",
                    ]
                ].copy().round(3)

                comparison_display.columns = [
                    "Alternative",
                    "Original NH42 segment (km)",
                    "Local bypass (km)",
                    "Additional distance (km)",
                    "Increase (%)",
                ]
            else:
                comparison_display = display.round(3).copy()

            table_header_bg = (
                "#edf2f8" if theme == "light" else "#1b2637"
            )
            table_row_bg = (
                "#ffffff" if theme == "light" else "#131f31"
            )
            table_hover_bg = (
                "#f1f5f9" if theme == "light" else "#223249"
            )

            table_id = "research-route-comparison"

            headers_html = "".join(
                f"<th>{html.escape(str(column))}</th>"
                for column in comparison_display.columns
            )

            rows_html = ""
            for row in comparison_display.itertuples(index=False, name=None):
                cells = []
                for value in row:
                    if pd.isna(value):
                        formatted = "—"
                    elif isinstance(value, (int, float)) and not isinstance(value, bool):
                        formatted = str(value)
                    else:
                        formatted = str(value)

                    cells.append(
                        f"<td>{html.escape(formatted)}</td>"
                    )

                rows_html += "<tr>" + "".join(cells) + "</tr>"

            table_html = f"""
            <style>
            .{table_id}-scroll {{
                width: 100%;
                overflow-x: auto;
                border: 1px solid {colors['border']};
                border-radius: 10px;
            }}
            .{table_id} {{
                width: 100%;
                border-collapse: collapse;
                background: {table_row_bg};
                color: {colors['text']};
                font-size: 0.95rem;
                min-width: 650px;
            }}
            .{table_id} th,
            .{table_id} td {{
                padding: 13px 15px;
                border-bottom: 1px solid {colors['border']};
                color: {colors['text']} !important;
                white-space: nowrap;
            }}
            .{table_id} th {{
                background: {table_header_bg} !important;
                font-weight: 600;
                text-align: right;
            }}
            .{table_id} td {{
                background: {table_row_bg} !important;
                text-align: right;
            }}
            .{table_id} th:first-child,
            .{table_id} td:first-child {{
                text-align: left;
            }}
            .{table_id} tbody tr:hover td {{
                background: {table_hover_bg} !important;
            }}
            .{table_id} tbody tr:last-child td {{
                border-bottom: none;
            }}
            .{table_id}-scroll {{
                line-height: 0;
            }}
            .{table_id} {{
                line-height: 1.5;
                margin: 0 !important;
            }}
            </style>
            <div class="{table_id}-scroll">
                <table class="{table_id}">
                    <thead><tr>{headers_html}</tr></thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            """

            st.markdown(table_html, unsafe_allow_html=True)

            st.caption(
                "Routes are ordered by network distance, "
                "not guaranteed safety or minimum landslide risk. "
                "No new routing or model training was performed."
            )

elif page == "Research Overview":

    exposure = load_csv(
        "Data/two_highway_rf_exposure_rebuilt_2018.csv"
    )
    arniko = load_csv(
        "Results/arniko_final_12_route_research_table.csv"
    )
    pasang = load_csv(
        "Results/pasang_final_33_alternatives.csv"
    )

    a, b, c, d = st.columns(4)
    a.metric("Highways", 2)
    b.metric("Arniko alternatives", len(arniko))
    c.metric("Pasang alternatives", len(pasang))
    d.metric("Validation checks", sum(manifest["checks"].values()))

    st.subheader("Mapped corridor RF exposure")
    # Presentation-only table; the original exposure data remains unchanged.
    overview_columns = {
        "corridor": "Highway",
        "mapped_length_km": "Mapped length (km)",
        "rf_scored_length_km": "RF-scored (km)",
        "rf_unscored_length_km": "RF-unscored (km)",
        "rf_coverage_pct": "RF coverage (%)",
        "length_weighted_rf_score": "Weighted RF score",
    }

    overview_table = exposure[list(overview_columns)].rename(
        columns=overview_columns
    ).copy()

    overview_table["Mapped length (km)"] = overview_table["Mapped length (km)"].map(
        lambda x: f"{x:.2f}"
    )
    overview_table["RF-scored (km)"] = overview_table["RF-scored (km)"].map(
        lambda x: f"{x:.2f}"
    )
    overview_table["RF-unscored (km)"] = overview_table["RF-unscored (km)"].map(
        lambda x: f"{x:.2f}"
    )
    overview_table["RF coverage (%)"] = overview_table["RF coverage (%)"].map(
        lambda x: f"{x:.1f}"
    )
    overview_table["Weighted RF score"] = overview_table["Weighted RF score"].map(
        lambda x: f"{x:.4f}"
    )

    table_background = "#131f31" if theme == "dark" else "#ffffff"
    table_foreground = "#f1f5f9" if theme == "dark" else "#17243a"
    table_border = "#2b3a50" if theme == "dark" else "#dce4ef"

    table_html = overview_table.to_html(index=False, escape=True)

    # Render the table as HTML without Markdown indentation.
    table_background = "#131f31" if theme == "dark" else "#ffffff"
    table_foreground = "#f1f5f9" if theme == "dark" else "#17243a"
    table_border = "#2b3a50" if theme == "dark" else "#dce4ef"

    table_css = f"""
    <style>
    .overview-exposure-table {{
        overflow-x: auto;
        border: 1px solid {table_border};
        border-radius: 15px;
        background: {table_background};
    }}
    .overview-exposure-table table {{
        width: 100%;
        border-collapse: collapse;
        color: {table_foreground};
        font-size: 0.95rem;
    }}
    .overview-exposure-table th,
    .overview-exposure-table td {{
        padding: 17px 15px;
        border-bottom: 1px solid {table_border};
        text-align: right;
        white-space: nowrap;
    }}
    .overview-exposure-table th:first-child,
    .overview-exposure-table td:first-child {{
        text-align: left;
    }}
    .overview-exposure-table tr:last-child td {{
        border-bottom: none;
    }}
    </style>
    """

    st.markdown(table_css, unsafe_allow_html=True)
    st.html(
        '<div class="overview-exposure-table">'
        + table_html
        + '</div>'
    )

    fig = px.bar(
        exposure,
        x="corridor",
        y="rf_coverage_pct",
        text_auto=".1f",
        labels={
            "corridor": "Highway",
            "rf_coverage_pct": "RF coverage (%)"
        },
        title="Unequal spatial coverage of 2018 RF scores"
    )
    fig.update_yaxes(range=[0, 105])

    # Match the Plotly chart to the dashboard's selected theme.
    chart_bg = "#131f31" if theme == "dark" else "#ffffff"
    chart_text = "#f1f5f9" if theme == "dark" else "#17243a"
    chart_grid = "#2b3a50" if theme == "dark" else "#dce4ef"

    fig.update_layout(
        paper_bgcolor=chart_bg,
        plot_bgcolor=chart_bg,
        font=dict(color=chart_text),
        title_font=dict(color=chart_text),
        margin=dict(l=25, r=25, t=70, b=35),
    )
    fig.update_xaxes(
        tickfont=dict(color=chart_text),
        title_font=dict(color=chart_text),
        gridcolor=chart_grid,
        zerolinecolor=chart_grid,
    )
    fig.update_yaxes(
        tickfont=dict(color=chart_text),
        title_font=dict(color=chart_text),
        gridcolor=chart_grid,
        zerolinecolor=chart_grid,
    )

    st.plotly_chart(fig, width="stretch")

    st.warning(
        "Highway-wide RF scores should not be interpreted as a "
        "direct ranking of landslide danger because coverage differs."
    )


elif page == "Arniko Highway":
    st.header("Arniko Highway (NH34)")
    st.info(
        "The map shows retrospective 2018 RF susceptibility scores, "
        "not calibrated landslide probabilities."
    )
    st.subheader("2018 Landslide Susceptibility")
    highway_susceptibility_map("Arniko NH34")
    render_highway_research("arniko")


elif page == "Pasang Lhamu Highway":
    st.header("Pasang Lhamu Highway (NH18/NH42)")
    st.info(
        "The map shows retrospective 2018 RF susceptibility scores, "
        "not calibrated landslide probabilities."
    )
    st.subheader("2018 Landslide Susceptibility")
    highway_susceptibility_map("Pasang Lhamu NH18 + NH42")
    render_highway_research("pasang")

elif page == "Machine Learning":
    st.header("Machine Learning Evaluation")

    test = load_csv(
        "Results/spatial_test_final_predictions.csv"
    )

    st.write(
        "The study compares Logistic Regression, Decision Tree "
        "and Random Forest using spatially separated grid cells."
    )

    metrics = pd.DataFrame([
        {
            "Model": "Logistic Regression",
            "Accuracy": 0.629730,
            "F1": 0.460630,
            "ROC-AUC": 0.690778,
            "PR-AUC": 0.376753
        },
        {
            "Model": "Decision Tree",
            "Accuracy": 0.629730,
            "F1": 0.475096,
            "ROC-AUC": 0.689659,
            "PR-AUC": 0.363360
        },
        {
            "Model": "Random Forest",
            "Accuracy": 0.724324,
            "F1": 0.521127,
            "ROC-AUC": 0.732268,
            "PR-AUC": 0.459617
        }
    ])

    st.dataframe(metrics, width="stretch", hide_index=True)

    fig = px.bar(
        metrics,
        x="Model",
        y=["F1", "ROC-AUC", "PR-AUC"],
        barmode="group",
        title="Spatial holdout test performance"
    )
    st.plotly_chart(fig, width="stretch")

    st.caption(
        f"Spatial test observations: {len(test)}. "
        "Thresholds were selected using training out-of-fold "
        "predictions. No SMOTE was used."
    )

    st.warning(
        "The RF outputs are uncalibrated retrospective "
        "susceptibility scores, not future-event probabilities."
    )

else:
    st.header("Methodology and Research Limitations")

    st.markdown("""
    **Machine learning:** Annual grid-cell observations from
    2009–2018, five environmental and terrain predictors,
    spatially separated training and test grid cells, and
    Logistic Regression, Decision Tree and Random Forest.

    **Road-network analysis:** OpenStreetMap-derived highway
    and regional roads, hypothetical closure simulations,
    alternative-route generation, graph validation and
    distance-based ranking.

    **Risk integration:** Route segments are associated with
    2018 Random Forest grid-cell scores where spatial
    coverage is available.

    **Important limitations:**
    - Hypothetical closures are not confirmed real incidents.
    - Graph-valid routes are not guaranteed safe or drivable.
    - Neither highway is verified as fully continuous.
    - The Betrawati crossing remains unresolved.
    - Arniko and Pasang use different network assumptions.
    - Arniko has incomplete RF coverage.
    - RF 2018 outputs are retrospective and uncalibrated.
    - No route is claimed to be globally risk-optimal.
    - NO_ROUTE_IN_GRAPH means no path in the modeled network,
      not necessarily no real-world road.
    """)

    with st.expander("Research freeze metadata"):
        st.json({
            "status": manifest["status"],
            "created_utc": manifest["created_utc"],
            "validation_checks": manifest["checks"]
        })

st.divider()
st.caption(
    "Academic research prototype — not intended for "
    "operational navigation or emergency route guidance."
)
