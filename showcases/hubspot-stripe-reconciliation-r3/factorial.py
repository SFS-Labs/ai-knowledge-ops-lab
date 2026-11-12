"""Execute the frozen Revision 3 factorial design using the Revision 2 evaluator."""
import json
import sys
from itertools import product
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hubspot-stripe-reconciliation"))
from evaluate import CRITICAL, evaluate


def assess(metrics):
    count = metrics["obligation_day_evaluations"]
    return (
        count > 0
        and metrics["exact_status_matches"] == count
        and metrics["exact_alert_set_matches"] == count
        and metrics["false_alert_snapshots"] == metrics["missed_critical_alert_snapshots"] == 0
        and set(metrics["by_alert"]) == CRITICAL
        and all(
            event["missed_events"] == event["false_alert_episodes"] == 0
            and event["max_detection_delay_days"] == (0 if event["detected_events"] else None)
            for event in metrics["by_alert"].values()
        )
    )


def main():
    failed = False
    for cell, (volume, incidence) in enumerate(product((3, 6, 18), (.05, .28, .40))):
        runs = []
        for seed in range(20261201 + 12 * cell, 20261213 + 12 * cell):
            run = evaluate(seed, volume, incidence)
            run.pop("median_local_core_ms")
            runs.append(run)
        workflow = [run["metrics"]["workflow"] for run in runs]
        pairs = [m["unique_obligation_alert_pairs"] for m in workflow]
        passed = all(assess(m) for run in runs for m in run["metrics"].values())
        failed |= not passed
        print(json.dumps({
            "daily_deals": volume, "injected_incidence": incidence, "passed": passed,
            "evaluations_per_method": sum(m["obligation_day_evaluations"] for m in workflow),
            "alert_pairs_min_median_max": [min(pairs), median(pairs), max(pairs)],
            "open_events": sum(e["open_at_horizon"] for m in workflow for e in m["by_alert"].values()),
            "exposure_by_alert": {a: sum(m["by_alert"][a]["occurred_events"] for m in workflow) for a in sorted(CRITICAL)},
            "runs": runs,
        }, sort_keys=True, separators=(",", ":")), flush=True)
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
