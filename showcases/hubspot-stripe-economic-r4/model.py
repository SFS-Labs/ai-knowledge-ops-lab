"""R4: cost-model extension of frozen R3 cell summaries; Python 3.12+ stdlib only.

No production data, no real stopwatch measurements, no claimed cash savings.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
R3_RESULTS = HERE.parent / "hubspot-stripe-reconciliation-r3" / "RESULTS.md"
PARAM_FILE = HERE / "PARAMETERS.json"
EXPECTED_R3_GIT_BLOB = "698c1ae6b899616aa3b68d2fd3313cb6e0b7b291"
EXPECTED_R3_HEAD = "b52bea2f9651334ffb2b3662f2e706ee180fbc45"
DAYS = 100
REPLICATES = 12
GRID = {(v, r) for v in (3, 6, 18) for r in (5, 28, 40)}
LINE = re.compile(
    r"^\| (3|6|18) \| (5|28|40)% \| (\d+) \| "
    r"([\d.]+) / ([\d.]+) / ([\d.]+) \| (\d+) \| bestanden \|$"
)

def git_blob_sha(payload):
    return hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\x00" + payload).hexdigest()

def load_cells():
    raw = R3_RESULTS.read_bytes()
    if git_blob_sha(raw) != EXPECTED_R3_GIT_BLOB:
        raise ValueError("Frozen R3 RESULTS.md blob changed: do not silently rebase R4 inputs")
    cells = []
    for line in raw.decode("utf-8").splitlines():
        match = LINE.fullmatch(line.strip())
        if not match:
            continue
        deals, incidence, evaluations, minpairs, medianpairs, maxpairs, open_events = match.groups()
        deals, incidence, evaluations = int(deals), int(incidence), int(evaluations)
        cells.append({
            "deals_per_day": deals, "incidence_pct": incidence,
            "replicates": REPLICATES, "days": DAYS,
            "deals_per_100_days": deals * DAYS,
            "evaluations_across_12_runs": evaluations,
            "evaluations_per_run_mean": evaluations / REPLICATES,
            "alert_pairs_min_per_run": float(minpairs),
            "alert_pairs_median_per_run": float(medianpairs),
            "alert_pairs_max_per_run": float(maxpairs),
            "open_events_across_12_runs": int(open_events),
        })
    if {(c["deals_per_day"], c["incidence_pct"]) for c in cells} != GRID or len(cells) != 9:
        raise ValueError("R3 3x3 grid is incomplete, duplicated or malformed")
    if sum(c["evaluations_across_12_runs"] for c in cells) != 6631538:
        raise ValueError("R3 exposure denominator inconsistent with frozen report")
    return sorted(cells, key=lambda c: (c["deals_per_day"], c["incidence_pct"]))

def base_parameters():
    registry = json.loads(PARAM_FILE.read_text(encoding="utf-8"))
    if registry["base_r3_commit"] != EXPECTED_R3_HEAD:
        raise ValueError("R4 parameters must point to frozen R3 head")
    p = {entry["id"]: entry["value"] for entry in registry["parameters"]}
    return {
        "days": p["DAYS"], "wage": p["DESTATIS_LABOR_2025"],
        "m_daily": p["M_DAILY"], "m_per_eval": p["M_PER_EVAL"],
        "a_daily": p["A_DAILY"], "common_review": p["COMMON_REVIEW"],
        "extra_review": p["A_EXTRA_REVIEW"], "maintenance": p["MAINTENANCE"],
        "incident": p["INCIDENT"], "operating": p["OPERATING"],
        "setup_hours": p["SETUP"], "utilization": p["UTILIZATION"],
    }

def calculate(cell, p):
    for key in ("days", "wage", "m_daily", "m_per_eval", "a_daily",
                "common_review", "extra_review", "maintenance", "incident",
                "operating", "setup_hours", "utilization"):
        value = p[key]
        if not isinstance(value, (int, float)) or not (float("-inf") < value < float("inf")):
            raise ValueError("Nonfinite or nonnumeric parameter: " + key)
        if value < 0:
            raise ValueError("Negative parameter: " + key)
    if p["wage"] <= 0 or not 0 <= p["utilization"] <= 1 or p["days"] != DAYS:
        raise ValueError("Invalid wage, utilization or frozen study horizon")
    if cell["replicates"] != REPLICATES or cell["days"] != DAYS:
        raise ValueError("Invalid R3 cell population")
    n = cell["evaluations_per_run_mean"]
    alerts = cell["alert_pairs_median_per_run"]
    if n <= 0 or alerts < 0:
        raise ValueError("Invalid exposure or alert count")
    manual = DAYS * p["m_daily"] + n * p["m_per_eval"] + alerts * p["common_review"]
    automated = (DAYS * p["a_daily"] + alerts * (p["common_review"] + p["extra_review"])
                 + p["maintenance"] + p["incident"])
    capacity_min = manual - automated
    capacity_eur = capacity_min * p["wage"] / 60
    net_full = capacity_eur - p["operating"]
    opportunity_eur = capacity_eur * p["utilization"] if capacity_min >= 0 else capacity_eur
    net = opportunity_eur - p["operating"]
    setup = p["setup_hours"] * p["wage"]
    # No phantom payback at a floating-point zero threshold.
    payback = DAYS * setup / net if net > 1e-9 else None
    base_labor = (DAYS * (p["a_daily"] - p["m_daily"]) + alerts * p["extra_review"]
                  + p["maintenance"] + p["incident"])
    threshold_labor = base_labor / n
    if p["utilization"] > 0:
        required_minutes = p["operating"] * 60 / (p["wage"] * p["utilization"])
        threshold_econ = (base_labor + required_minutes) / n
        max_extra = (
            DAYS * (p["m_daily"] - p["a_daily"]) + n * p["m_per_eval"]
            - p["maintenance"] - p["incident"] - required_minutes
        ) / alerts if alerts else None
    else:
        threshold_econ = None
        max_extra = None
    return {
        "manual_minutes": manual,
        "automated_minutes": automated,
        "capacity_minutes": capacity_min,
        "capacity_hours": capacity_min / 60,
        "capacity_eur": capacity_eur,
        "net_full_use_eur": net_full,
        "net_economic_eur": net,
        "verified_cash_savings_eur": 0,
        "setup_eur": setup,
        "payback_days": payback,
        "break_even_m_per_eval_labor": threshold_labor,
        "break_even_m_per_eval_economic": threshold_econ,
        "break_even_extra_review_economic": max_extra,
    }

def _round_structure(obj):
    if isinstance(obj, dict):
        return {key: _round_structure(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_round_structure(item) for item in obj]
    if isinstance(obj, float):
        return round(obj, 9)
    return obj

def compile_results():
    p = base_parameters()
    cells = load_cells()
    records = [{**cell, **calculate(cell, p)} for cell in cells]
    reference = next(c for c in cells if c["deals_per_day"] == 6 and c["incidence_pct"] == 28)
    variations = [
        ("manual_batch_fast", {"m_per_eval": 0.005}),
        ("manual_batch_slow", {"m_per_eval": 0.06}),
        ("workflow_extra_review_zero", {"extra_review": 0}),
        ("workflow_extra_review_eight", {"extra_review": 8}),
        ("capacity_unusable", {"utilization": 0}),
        ("maintenance_incident_fees_stress", {"maintenance": 480, "incident": 240, "operating": 300}),
    ]
    selected = [
        {"scenario": name, "changed": change, **calculate(reference, {**p, **change})}
        for name, change in variations
    ]
    # Nonparametric interpolation across 3 artificial incidences. Not an estimated real failure rate.
    incidence_crossings = []
    for volume in (3, 6, 18):
        records_for_volume = [r for r in records if r["deals_per_day"] == volume]
        crossing = None
        for low, high in zip(records_for_volume, records_for_volume[1:]):
            a, b = low["net_economic_eur"], high["net_economic_eur"]
            if a >= 0 > b or a <= 0 < b:
                crossing = low["incidence_pct"] + (high["incidence_pct"]-low["incidence_pct"]) * (-a) / (b-a)
                break
        incidence_crossings.append({"deals_per_day": volume, "interpolated_injected_incidence_pct": crossing})
    return _round_structure({
        "metadata": {
            "label": "R4 cost scenario; NOT a measured economic impact",
            "frozen_r3_head": EXPECTED_R3_HEAD,
            "r3_results_git_blob": EXPECTED_R3_GIT_BLOB,
            "r3_exposure": "mean over twelve runs per R3 cell",
            "r3_alerts": "median unique obligation/alert-type pairs per full run",
            "no_measured_manual_timing": True,
            "no_actual_cash_savings": True,
            "reference_profile": "80 assumed staff, EUR 12m assumed revenue, 6 new deals/day",
            "source": "R3/RESULTS.md and R4/PARAMETERS.json",
        },
        "base_parameters": p,
        "cells": records,
        "selected_sensitivities": selected,
        "illustrative_incidence_crossings": incidence_crossings,
    })

def _num(value, digits=2):
    return "n/a" if value is None else f"{value:,.{digits}f}"

def render_report(result):
    p = result["base_parameters"]
    out = [
        "# R4 — Kostenmodell: Ergebnisse (bedingte Szenarien)",
        "",
        "**Kein gemessener menschlicher Zeitgewinn, kein gemessener ROI und keine realisierten Einsparungen.**",
        "Die Ergebnisse hängen substanziell von NICHT empirisch gemessenen Minuten je Kontrolle/Alert,",
        "Wartung, Nutzungsgrad und dem als Proxy eingesetzten deutschen Arbeitskosten-Mittel ab.",
        "",
        f"Extern kalibrierter Kostensatz: {p['wage']:.0f} EUR/Stunde (Destatis 2025, sektorübergreifend).",
        f"Unbeobachtete Hypothesen: {p['m_per_eval']*60:.1f} Sekunden je wiederholter Tabellenbewertung, "
        f"{p['m_daily']:.1f} min manuelle Vorbereitung/Tag, {p['a_daily']:.1f} min A-Aufsicht/Tag, "
        f"{p['extra_review']:.1f} min Zusatztriage/Alertpaar, "
        f"{p['maintenance']:.0f} min Wartung/100 Tage, "
        f"{p['operating']:.0f} EUR Betrieb/100 Tage, {p['setup_hours']:.0f} h Setup, "
        f"{p['utilization']:.0%} nutzbare positive Kapazität.",
        "",
        "## Modellierte Kosten je 100 Geschäftstage",
        "",
        "| Deals/Tag | Injizierte Szenarioinzidenz | Prüfbewertungen je Lauf (Mittel) | Alertpaare je Lauf (Median) | Nettozeit h | Kapazitätswert EUR | Bedingter Nettoeffekt EUR | Amortisation Arbeitstage |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for c in result["cells"]:
        out.append(
            f"| {c['deals_per_day']} | {c['incidence_pct']}% | {c['evaluations_per_run_mean']:,.1f} "
            f"| {_num(c['alert_pairs_median_per_run'],1)} | {_num(c['capacity_hours'])} | {_num(c['capacity_eur'])} "
            f"| {_num(c['net_economic_eur'])} | {_num(c['payback_days'],0)} |"
        )
    out += [
        "",
        "Die **Kapazitätsstunden** sind brutto differenzierte Modellstunden. Der **bedingte Nettoeffekt**",
        "bewertet positive Differenzen nur mit 50% wirtschaftlicher Nutzbarkeit, negative vollständig,",
        "abzüglich illustrativer Betriebsgebühren. Er ist **kein** Geldzufluss. Setup ist nicht im",
        "periodischen Netto enthalten, sondern ausschließlich in bedingter Amortisation.",
        "",
        "## Wirtschaftliche Kippschwellen",
        "",
        "| Deals/Tag | Inzidenz | erforderliche manuelle min je Bewertung für Netto=0 | maximaler A-Zusatzreview min/Alertpaar für Netto=0 |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for c in result["cells"]:
        out.append(f"| {c['deals_per_day']} | {c['incidence_pct']}% | {_num(c['break_even_m_per_eval_economic'],4)} | {_num(c['break_even_extra_review_economic'],2)} |")
    out += [
        "",
        "Negative Zusatzreview-Grenzen bedeuten: Selbst bei **null** Zusatzreview wäre",
        "der Nettoeffekt unter den übrigen Annahmen nicht positiv. Bei höherem Aufwand je",
        "Bewertung als der angegebenen Untergrenze kann ein positiver Nettoeffekt entstehen.",
        "",
        "Interpolierte (nicht empirische) Null-Durchgänge der injizierten Generator-Inzidenz:",
    ]
    for crossing in result["illustrative_incidence_crossings"]:
        out.append(
            f"- {crossing['deals_per_day']} Deals/Tag: "
            f"{_num(crossing['interpolated_injected_incidence_pct'],1)}%."
        )
    out += [
        "Zwischen den drei diskreten Inzidenzfaktoren wird linear interpoliert; dies ist keine",
        "geschätzte reale Fehlerquote, kein Konfidenzintervall und keine Extrapolation.",
        "",
        "## Adversarial Sensitivität — Referenzprofil 6 Deals/Tag, 28%",
        "",
        "| Variante | Modifikation gegenüber Basis | Nettozeit h | Bedingter Nettoeffekt EUR/100 Tage |",
        "| --- | --- | ---: | ---: |",
    ]
    for row in result["selected_sensitivities"]:
        change = ", ".join(f"{k}={v}" for k,v in row["changed"].items())
        out.append(f"| {row['scenario']} | {change} | {_num(row['capacity_hours'])} | {_num(row['net_economic_eur'])} |")
    out += [
        "",
        "Menschlicher gemeinsamer Ausnahmeaufwand ist auf beiden Seiten symmetrisch erfasst.",
        "Mehrfachmeldungen eines Verpflichtungs-/Alerttyps an verschiedenen Tagen werden nicht als",
        "neue Alertpaare gezählt. R3-eigene Simulations-Fehlerinzidenzen sind nicht repräsentativ",
        "für deutsche Dienstleistungsunternehmen. Tagesbewertungen sind abhängige Bestandssnapshots,",
        "nicht neue Rechnungen oder unabhängige Beobachtungen. Der Mittelwert der Bewertungen und",
        "der Median der Alertpaare stammen nicht notwendig aus demselben R3-Lauf.",
        "",
        "**Freigegebene Interpretation:** Parametrisches bedingtes Kostenmodell mit amtlichem",
        "Arbeitskostenanker; kein Beleg für tatsächliche oder branchenrepräsentative",
        "Zeitersparnis, Cash-Einsparungen, produktive E2E-Gleichwertigkeit oder ROI.",
        "",
        "Reproduktion: `python3 model.py --json | diff - RESULTS.json -` und",
        "`python3 model.py --report | diff - RESULTS.md -` aus diesem Verzeichnis.",
        "Tests: `python3 -m unittest discover -s . -p 'test_model.py' -v`.",
    ]
    return "\n".join(out) + "\n"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--json", action="store_true")
    group.add_argument("--report", action="store_true")
    args = parser.parse_args()
    results = compile_results()
    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(render_report(results), end="")

if __name__ == "__main__":
    main()
