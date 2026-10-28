import csv
from collections import defaultdict
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from main import generate_matches, run_simulation
from visualize import create_match_svg
from broadcast import analyze_match


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TraceBall | Football Intelligence",
    page_icon="⚽",
    layout="wide"
)


# --------------------------------------------------
# STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #17252a;
    }

    h1, h2, h3 {
        color: #17252a;
    }

    .main-title {
        font-size: 48px;
        font-weight: 800;
        color: #069494;
        margin-bottom: 0;
    }

    .subtitle {
        color: #64748b;
        font-size: 16px;
        margin-top: 0;
    }

    .section-title {
        color: #069494;
        font-weight: 700;
        font-size: 22px;
    }

    div[data-testid="stMetric"] {
        background-color: #f4fafa;
        border: 1px solid #dceeee;
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stMetricValue"] {
        color: #069494;
    }

    .insight-card {
        background-color: #f4fafa;
        border-left: 4px solid #069494;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 12px;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        padding: 30px;
        font-size: 13px;
    }

    button[kind="primary"] {
        background-color: #069494;
        border-color: #069494;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DATA HANDLING
# --------------------------------------------------

def group_events_by_match(events):
    matches = defaultdict(list)

    for event in events:
        matches[event["match_id"]].append(event)

    return dict(matches)


def load_initial_matches():
    csv_path = Path("football_events.csv")

    if csv_path.exists():
        with open(csv_path, "r", newline="", encoding="utf-8") as file:
            events = list(csv.DictReader(file))

        return group_events_by_match(events)

    generated_events = generate_matches(
        number_of_matches=50,
        duration=30
    )

    return group_events_by_match(generated_events)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "matches" not in st.session_state:
    st.session_state.matches = load_initial_matches()

if "next_match_number" not in st.session_state:
    existing_numbers = []

    for match_id in st.session_state.matches:
        try:
            existing_numbers.append(int(match_id.split("_")[-1]))
        except ValueError:
            pass

    st.session_state.next_match_number = (
        max(existing_numbers, default=0) + 1
    )

if "match_selector" not in st.session_state:
    st.session_state.match_selector = sorted(
        st.session_state.matches.keys()
    )[0]


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">Ball.</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Turning football movement into match intelligence.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# --------------------------------------------------
# MATCH SELECTION AND GENERATION
# --------------------------------------------------

header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.markdown("### Match Explorer")

with header_col2:
    generate_button = st.button(
        "＋ Generate Match",
        type="primary",
        use_container_width=True
    )

if generate_button:
    new_match_id = (
        f"MATCH_{st.session_state.next_match_number:03d}"
    )

    new_events = run_simulation(
        duration=30,
        match_id=new_match_id
    )

    st.session_state.matches[new_match_id] = new_events
    st.session_state.next_match_number += 1
    st.session_state.match_selector = new_match_id

    st.rerun()


match_ids = sorted(st.session_state.matches.keys())

selected_match_id = st.selectbox(
    "Select a match",
    options=match_ids,
    key="match_selector"
)

selected_events = st.session_state.matches[selected_match_id]


if not selected_events:
    st.warning("This match has no recorded events yet.")
    st.stop()


# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

report = analyze_match(selected_events)

dataset = report["dataset"]

st.divider()


# --------------------------------------------------
# MATCH VISUALIZATION
# --------------------------------------------------

st.markdown(
    '<div class="section-title">Match Visualization</div>',
    unsafe_allow_html=True
)

match_svg = create_match_svg(
    selected_events,
    selected_match_id
)

components.html(
    match_svg,
    height=680,
    scrolling=True
)


# --------------------------------------------------
# MATCH STATISTICS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">Match Statistics</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Events",
    dataset["total_events"]
)

col2.metric(
    "Phases",
    dataset["total_phases"]
)

col3.metric(
    "Shot Phases",
    dataset["shot_phases"]
)

col4.metric(
    "Goal Phases",
    dataset["goal_phases"]
)

st.divider()


# --------------------------------------------------
# ATTACKING PATTERNS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">Attacking Movement Patterns</div>',
    unsafe_allow_html=True
)

shot_patterns = report["shot_movement_patterns"]

if shot_patterns:
    for movement, count in shot_patterns.items():
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>{movement}</strong>
                <span style="float:right;color:#069494;">
                    {count} occurrences
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No shot-related movement patterns were identified.")


# --------------------------------------------------
# DEFENSIVE REACTIONS
# --------------------------------------------------

st.markdown(
    '<div class="section-title">Movements Before Defensive Disruptions</div>',
    unsafe_allow_html=True
)

defensive_patterns = report[
    "movements_before_defensive_disruptions"
]

if defensive_patterns:
    for movement, count in defensive_patterns.items():
        st.markdown(
            f"""
            <div class="insight-card">
                <strong>{movement}</strong>
                <span style="float:right;color:#069494;">
                    {count} occurrences
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No defensive disruptions were identified.")


# --------------------------------------------------
# BROADCAST OVERVIEW
# --------------------------------------------------

st.markdown(
    '<div class="section-title">Broadcast Overview</div>',
    unsafe_allow_html=True
)

explanations = report["broadcast_explanations"]

st.markdown(
    f"""
    <div class="insight-card">
        <h4>Attacking Pattern</h4>
        <p>{explanations["attacking_pattern"]}</p>
    </div>

    <div class="insight-card">
        <h4>Defensive Reaction</h4>
        <p>{explanations["defensive_reaction"]}</p>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="footer">'
    'TRACEBALL · Football Movement Intelligence'
    '</div>',
    unsafe_allow_html=True
)
