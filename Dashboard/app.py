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

        scenarios = (
            results[scenario_cols]
            .drop_duplicates()
            .sort_values(scenario_cols)
        )

        options = [
            (int(r.component), int(r.closure_position_pct))
            for r in scenarios.itertuples()
        ]

        def label(option):
            return (
                f"Arniko component {option[0]} — "
                f"closure at {option[1]}%"
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

        summary = closure_scenarios.copy()
        summary["Scenario"] = summary.apply(
            arniko_scenario_label, axis=1
        )
        summary["Road"] = "NH34"
        summary["Original distance (km)"] = summary["normal_network_km"]
        summary["Alternative distance (km)"] = summary["post_closure_km"]
        summary["Extra distance (km)"] = summary["additional_km"]
        summary["Distance increase (%)"] = summary["increase_pct"]
        summary["Result"] = summary["status"].map(
            lambda x: "Detour found"
            if str(x).upper() == "DETOUR_FOUND"
            else "No route in modeled graph"
        )

        total_scenarios = len(summary)
        detours = len(options)
        total_alternatives = len(results)

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

        options = sorted(results["scenario_id"].dropna().unique())

        def label(option):
            row = scenarios.loc[
                scenarios["scenario_id"] == option
            ]

            if row.empty:
                return str(option)

            r = row.iloc[0]
            group = str(r["scenario_group"])

            return f"{group} — {option}"

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
        summary["Result"] = summary["status"].map(
            lambda x: "Detour found"
            if str(x).upper() == "DETOUR_FOUND"
            else "No route in modeled graph"
        )

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
    b.metric("Detours found", detours)
    c.metric("Alternative routes", total_alternatives)

    with st.expander(
        "Detailed route scenarios and research results",
        expanded=False
    ):
        st.subheader("Closure Scenario Outcomes")

        columns = [
            "Scenario",
            "Road",
            "Original distance (km)",
            "Alternative distance (km)",
            "Extra distance (km)",
            "Distance increase (%)",
            "Result"
        ]

        display_summary = summary[columns].copy()

        for col in [
            "Original distance (km)",
            "Alternative distance (km)",
            "Extra distance (km)",
            "Distance increase (%)"
        ]:
            display_summary[col] = pd.to_numeric(
                display_summary[col], errors="coerce"
            ).round(2)

        st.dataframe(
            display_summary,
            width="stretch",
            hide_index=True
        )

        st.caption(
            "No route in modeled graph does not imply that "
            "no real-world alternative road exists."
        )

        st.subheader("Select a Closure Scenario")

        selected = st.selectbox(
            "Hypothetical road closure",
            options,
            format_func=label,
            key=f"{highway}_unified_scenario"
        )

        subset = select_results(selected)
        selected_overlap = select_overlap(selected)

        st.subheader("Alternative Route Comparison")

        comparison = pd.DataFrame({
            "Alternative": subset["alternative_rank"],
            "Distance (km)": subset[distance_col],
            "Extra distance (km)": subset[extra_col],
            "Extra distance (%)": subset[extra_pct_col],
            "2018 RF exposure score": subset[exposure_col],
            "RF coverage (%)": subset[coverage_col],
            "Graph valid": subset[valid_col]
        })

        st.dataframe(
            comparison.round(3),
            width="stretch",
            hide_index=True
        )

        st.subheader("Distance versus Retrospective RF Exposure")

        comparison_chart(
            subset,
            distance_col,
            exposure_col,
            "alternative_rank"
        )

        st.subheader("Route Overlap")

        st.dataframe(
            selected_overlap.round(3),
            width="stretch",
            hide_index=True
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


def route_map(gdf, selected=None, closure_point=None, closure_label=None, highway_name=None):
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

    for _, row in gdf.iterrows():
        rank = int(row["alternative_rank"])
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

    m.fit_bounds([
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]]
    ])

    legend = """
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
        <b>Simulated Road Closure</b><br>
        <span style="color:#dc2626;">&#9679;</span>
        Closure reference location<br>
        <hr style="margin:7px 0;">
        <b>Alternative Routes</b><br>
        <span style="color:#1565C0;">&#9644;</span>
        Alternative 1<br>
        <span style="color:#8E24AA;">&#9644;</span>
        Alternative 2<br>
        <span style="color:#00ACC1;">&#9644;</span>
        Alternative 3<br>
        <small>Distance-ranked, not safety-ranked</small>
    </div>
    """

    m.get_root().html.add_child(
        folium.Element(legend)
    )


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

        scenarios = (
            results[["component", "closure_position_pct"]]
            .drop_duplicates()
            .sort_values(["component", "closure_position_pct"])
        )

        options = [
            (int(r.component), int(r.closure_position_pct))
            for r in scenarios.itertuples()
        ]

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

        options = sorted(results["scenario_id"].unique())

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

        score_col = "length_weighted_rf_score_2018"
        coverage_col = "rf_coverage_pct"
        extra_col = "extra_vs_shortest_km"

    st.info(
        "These are previously modeled hypothetical closures, "
        "not reported landslide incidents. Selecting a scenario "
        "does not predict that a landslide will occur there."
    )

    if subset.empty or geo_subset.empty:
        st.warning(
            "No validated alternative geometry is available "
            "for this selection."
        )
    else:
        shortest = subset.iloc[0]

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Shortest available alternative",
            f"{float(shortest['distance_km']):.2f} km"
        )

        if pd.notna(shortest[score_col]):
            c2.metric(
                "2018 route RF score",
                f"{float(shortest[score_col]):.3f}"
            )
        else:
            c2.metric("2018 route RF score", "Unavailable")

        if pd.notna(shortest[coverage_col]):
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

        show_routes = st.button(
            "Simulate blockage and show alternative routes",
            type="primary",
            key="explorer_simulate"
        )

        state_key = "explorer_active_selection"
        current_selection = (highway, str(selected))

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

            display = subset[
                [
                    "alternative_rank",
                    "distance_km",
                    extra_col,
                    score_col,
                    coverage_col
                ]
            ].copy()

            display.columns = [
                "Alternative",
                "Distance (km)",
                "Extra distance (km)",
                "2018 RF score",
                "RF coverage (%)"
            ]

            st.subheader("Compare available alternatives")

            # Presentation only: preserve the saved research values.
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
