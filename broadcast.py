from collections import defaultdict, Counter


def movement_sequence(phase, stop_event):
    movements = []

    for event in phase:
        if event["event"] == stop_event:
            break

        if event["event"] in ("carry", "pass"):
            movements.append(event["event"])

    return movements


def last_movement(phase, stop_events):
    disruption_index = None

    for i, event in enumerate(phase):
        if event["event"] in stop_events:
            disruption_index = i
            break

    if disruption_index is None:
        return None

    for event in reversed(phase[:disruption_index]):
        if event["event"] in ("carry", "pass"):
            return event["event"]

    return None


def analyze_match(events):
    """
    Analyse the events from one match and return its report.

    This function does not read or write files.
    """

    # Group events into attacking phases.
    phases = defaultdict(list)

    for event in events:
        key = event["phase_id"]
        phases[key].append(event)

    for phase in phases.values():
        phase.sort(
            key=lambda e: float(e.get("timestamp") or 0)
        )

    # Analyse shot patterns and defensive disruptions.
    shot_patterns = Counter()
    defensive_preceding_movements = Counter()

    shot_phases = 0
    goal_phases = 0
    disrupted_phases = 0

    for phase in phases.values():

        event_types = [event["event"] for event in phase]

        # Attacking opportunities.
        if "shot" in event_types:
            shot_phases += 1

            movements = movement_sequence(phase, "shot")

            for i in range(len(movements) - 1):
                pair = movements[i] + " -> " + movements[i + 1]
                shot_patterns[pair] += 1

        if "goal" in event_types:
            goal_phases += 1

        # Defensive disruptions.
        disruption = next(
            (
                event for event in phase
                if event["event"] in ("interception", "turnover")
            ),
            None
        )

        if disruption:
            disrupted_phases += 1

            previous = last_movement(
                phase,
                {"interception", "turnover"}
            )

            if previous:
                defensive_preceding_movements[previous] += 1

    # Generate broadcast explanations.
    most_common_shot_pattern = shot_patterns.most_common(1)
    most_common_defensive_movement = (
        defensive_preceding_movements.most_common(1)
    )

    if most_common_shot_pattern:
        pattern, count = most_common_shot_pattern[0]

        shot_explanation = (
            f"The sequence {pattern} appeared {count} times "
            "in attacking phases that reached a shot. "
            "It is a recurring attacking sequence in this simulation."
        )
    else:
        shot_explanation = (
            "There were not enough recorded movement pairs "
            "before shots to identify a recurring pattern."
        )

    if most_common_defensive_movement:
        movement, count = most_common_defensive_movement[0]

        defensive_explanation = (
            f"A {movement} was the last recorded attacking movement "
            f"before a defensive disruption in {count} phases. "
            "This is worth examining as a possible defensive trigger."
        )
    else:
        defensive_explanation = (
            "No preceding attacking movements could be identified "
            "for defensive disruptions."
        )

    # Create the report.
    report = {
        "dataset": {
            "total_events": len(events),
            "total_phases": len(phases),
            "shot_phases": shot_phases,
            "goal_phases": goal_phases,
            "defensively_disrupted_phases": disrupted_phases
        },

        "shot_movement_patterns": dict(shot_patterns),

        "movements_before_defensive_disruptions": (
            dict(defensive_preceding_movements)
        ),

        "broadcast_explanations": {
            "attacking_pattern": shot_explanation,
            "defensive_reaction": defensive_explanation
        }
    }

    return report


# Optional standalone test:
# Run this file directly to analyse all matches in the CSV.
if __name__ == "__main__":
    import csv
    import json
    from pathlib import Path

    csv_path = Path(__file__).resolve().parent / "football_events.csv"

    with open(csv_path, "r", newline="") as file:
        events = list(csv.DictReader(file))

    matches = defaultdict(list)

    for event in events:
        matches[event["match_id"]].append(event)

    for match_id, match_events in matches.items():
        report = analyze_match(match_events)

        print(f"\n===== {match_id} =====")
        print("DATASET SUMMARY:")

        for key, value in report["dataset"].items():
            print(f"{key}: {value}")

        print("\nATTACKING:", report["broadcast_explanations"]["attacking_pattern"])
        print("DEFENDING:", report["broadcast_explanations"]["defensive_reaction"])

        output_path = Path(__file__).resolve().parent / f"{match_id}_report.json"

        with open(output_path, "w") as file:
            json.dump(report, file, indent=4)

    print("\nAnalysis complete.")
