
from collections import Counter
from html import escape


PITCH_WIDTH = 720
PITCH_HEIGHT = 480
MARGIN = 40

SVG_WIDTH = 800
SVG_HEIGHT = 680


def get_position(event):
    """Get the event's starting and ending coordinates safely."""

    start_x = event.get("start_x")
    start_y = event.get("start_y")
    end_x = event.get("end_x")
    end_y = event.get("end_y")

    # Fall back to x/y when start or end coordinates are unavailable.
    if start_x in (None, ""):
        start_x = event.get("x")
    if start_y in (None, ""):
        start_y = event.get("y")
    if end_x in (None, ""):
        end_x = event.get("x")
    if end_y in (None, ""):
        end_y = event.get("y")

    try:
        return (
            float(start_x),
            float(start_y),
            float(end_x),
            float(end_y)
        )
    except (TypeError, ValueError):
        return None


def pitch_x(x):
    return MARGIN + (x / 120) * PITCH_WIDTH


def pitch_y(y):
    return MARGIN + (y / 80) * PITCH_HEIGHT


def create_match_svg(match_events, match_id=""):
    """
    Create an SVG visualisation for one match.

    The function receives the selected match's events directly.
    It does not read a CSV or choose a match automatically.
    """

    event_counts = Counter(
        event.get("event", "") for event in match_events
    )

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_WIDTH}" height="{SVG_HEIGHT}" '
        f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">'
    )

    # Background
    svg.append(
        f'<rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" '
        f'fill="#ffffff"/>'
    )

    # Pitch
    svg.append(
        f'<rect x="{MARGIN}" y="{MARGIN}" '
        f'width="{PITCH_WIDTH}" height="{PITCH_HEIGHT}" '
        f'fill="#174f3a" stroke="#ffffff" stroke-width="2"/>'
    )

    # Halfway line
    halfway_x = MARGIN + PITCH_WIDTH / 2
    svg.append(
        f'<line x1="{halfway_x}" y1="{MARGIN}" '
        f'x2="{halfway_x}" y2="{MARGIN + PITCH_HEIGHT}" '
        f'stroke="#ffffff" stroke-width="2"/>'
    )

    # Centre circle
    svg.append(
        f'<circle cx="{halfway_x}" '
        f'cy="{MARGIN + PITCH_HEIGHT / 2}" r="55" '
        f'fill="none" stroke="#ffffff" stroke-width="2"/>'
    )

    # Centre spot
    svg.append(
        f'<circle cx="{halfway_x}" '
        f'cy="{MARGIN + PITCH_HEIGHT / 2}" r="3" '
        f'fill="#ffffff"/>'
    )

    # Penalty areas
    penalty_width = 110
    penalty_height = 240
    penalty_y = MARGIN + (PITCH_HEIGHT - penalty_height) / 2

    svg.append(
        f'<rect x="{MARGIN}" y="{penalty_y}" '
        f'width="{penalty_width}" height="{penalty_height}" '
        f'fill="none" stroke="#ffffff" stroke-width="2"/>'
    )

    svg.append(
        f'<rect x="{MARGIN + PITCH_WIDTH - penalty_width}" '
        f'y="{penalty_y}" width="{penalty_width}" '
        f'height="{penalty_height}" '
        f'fill="none" stroke="#ffffff" stroke-width="2"/>'
    )

    # Goal areas
    goal_width = 40
    goal_height = 110
    goal_y = MARGIN + (PITCH_HEIGHT - goal_height) / 2

    svg.append(
        f'<rect x="{MARGIN}" y="{goal_y}" '
        f'width="{goal_width}" height="{goal_height}" '
        f'fill="none" stroke="#ffffff" stroke-width="2"/>'
    )

    svg.append(
        f'<rect x="{MARGIN + PITCH_WIDTH - goal_width}" '
        f'y="{goal_y}" width="{goal_width}" '
        f'height="{goal_height}" '
        f'fill="none" stroke="#ffffff" stroke-width="2"/>'
    )

    # Event markers
    for event in match_events:
        event_type = event.get("event", "")
        position = get_position(event)

        if position is None:
            continue

        start_x, start_y, end_x, end_y = position

        x1 = pitch_x(start_x)
        y1 = pitch_y(start_y)
        x2 = pitch_x(end_x)
        y2 = pitch_y(end_y)

        if event_type == "pass":
            colour = (
                "#00e69a"
                if event.get("outcome") == "completed"
                else "#ff5544"
            )

            svg.append(
                f'<line x1="{x1}" y1="{y1}" '
                f'x2="{x2}" y2="{y2}" '
                f'stroke="{colour}" stroke-width="2.5" '
                f'stroke-linecap="round" opacity="0.9"/>'
            )

            svg.append(
                f'<circle cx="{x2}" cy="{y2}" r="3" '
                f'fill="{colour}"/>'
            )

        elif event_type == "carry":
            svg.append(
                f'<line x1="{x1}" y1="{y1}" '
                f'x2="{x2}" y2="{y2}" '
                f'stroke="#54b9ff" stroke-width="3" '
                f'stroke-linecap="round" opacity="0.9"/>'
            )

            svg.append(
                f'<circle cx="{x2}" cy="{y2}" r="3.5" '
                f'fill="#54b9ff"/>'
            )

        elif event_type == "shot":
            svg.append(
                f'<circle cx="{x2}" cy="{y2}" r="9" '
                f'fill="none" stroke="#ffd447" '
                f'stroke-width="3"/>'
            )

        elif event_type == "goal":
            svg.append(
                f'<circle cx="{x2}" cy="{y2}" r="11" '
                f'fill="#ffd447"/>'
            )
            svg.append(
                f'<text x="{x2}" y="{y2 + 4}" '
                f'text-anchor="middle" font-size="10" '
                f'font-weight="bold" fill="#174f3a">G</text>'
            )

        elif event_type == "interception":
            svg.append(
                f'<line x1="{x2 - 6}" y1="{y2 - 6}" '
                f'x2="{x2 + 6}" y2="{y2 + 6}" '
                f'stroke="#ff5544" stroke-width="3"/>'
            )
            svg.append(
                f'<line x1="{x2 + 6}" y1="{y2 - 6}" '
                f'x2="{x2 - 6}" y2="{y2 + 6}" '
                f'stroke="#ff5544" stroke-width="3"/>'
            )

        elif event_type == "turnover":
            svg.append(
                f'<rect x="{x2 - 5}" y="{y2 - 5}" '
                f'width="10" height="10" '
                f'fill="#bd83ff"/>'
            )

    # Match label
    label = escape(str(match_id)) if match_id else "Match visualisation"

    svg.append(
        f'<text x="{MARGIN}" y="25" '
        f'font-size="16" font-weight="bold" '
        f'fill="#202020">{label}</text>'
    )

    # Legend
    legend_y = 565

    legend_items = [
        ("#00e69a", "Completed pass"),
        ("#ff5544", "Unsuccessful pass"),
        ("#54b9ff", "Carry"),
        ("#ffd447", "Shot / Goal"),
        ("#bd83ff", "Turnover")
    ]

    legend_x = MARGIN

    for colour, label in legend_items:
        svg.append(
            f'<circle cx="{legend_x + 6}" cy="{legend_y}" '
            f'r="5" fill="{colour}"/>'
        )

        svg.append(
            f'<text x="{legend_x + 17}" y="{legend_y + 4}" '
            f'font-size="11" fill="#333333">{label}</text>'
        )

        legend_x += 145

    # Event totals
    summary = (
        f"Passes: {event_counts['pass']}    "
        f"Carries: {event_counts['carry']}    "
        f"Shots: {event_counts['shot']}    "
        f"Goals: {event_counts['goal']}    "
        f"Interceptions: {event_counts['interception']}"
    )

    svg.append(
        f'<text x="{MARGIN}" y="610" '
        f'font-size="12" fill="#555555">{summary}</text>'
    )

    svg.append("</svg>")

    return "\n".join(svg)


# Optional standalone test:
# Run this file directly to visualise the first match in the CSV.
if __name__ == "__main__":
    import csv

    from pathlib import Path

    csv_path = Path(__file__).resolve().parent / "football_events.csv"

    with open(csv_path, "r", newline="") as file:
        all_events = list(csv.DictReader(file))

    if all_events:
        first_match_id = all_events[0]["match_id"]

        selected_events = [
            event for event in all_events
            if event["match_id"] == first_match_id
        ]

        svg_content = create_match_svg(
            selected_events,
            first_match_id
        )

        output_path = Path(__file__).resolve().parent / "ball_patterns.svg"
        output_path.write_text(svg_content, encoding="utf-8")

        print(f"Visualisation saved to {output_path}")
    else:
        print("No events found in football_events.csv")
