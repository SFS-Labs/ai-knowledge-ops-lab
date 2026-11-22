"""Transform a captured HubSpot MCP population; never fabricate a HubSpot export."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal
from pathlib import Path

from reconcile import read_deals

ROOT = Path(__file__).resolve().parent


def prepare(source_path, plan_path, output):
    source = json.loads(source_path.read_text())
    plan = json.loads(plan_path.read_text())
    account = source["account"]["accountInformation"]
    search = source["search"]
    rows = search["results"]
    assert source["portal_id"] == account["accountId"] == 149743226
    assert search["total"] == len(rows) == 1, "Bounded source population incomplete"
    assert not source["independent_get"]["notFound"]
    assert len(source["independent_get"]["objects"]) == 1
    observed = rows[0]
    checked = source["independent_get"]["objects"][0]
    assert str(observed["id"]) == str(checked["id"]) == plan["deal_id"]
    fields = observed["properties"]
    for field in ("hs_object_id", "dealstage", "pipeline", "amount", "deal_currency_code", "hs_is_closed_won"):
        assert fields.get(field) == checked["properties"].get(field), f"Source verification differs: {field}"
    assert fields["hs_object_id"] == plan["deal_id"]
    assert fields["dealstage"] == "closedwon" and fields["hs_is_closed_won"] == "true"
    pipeline = next(p for p in source["pipelines"]["pipelineResults"]["results"] if p["id"] == fields["pipeline"])
    stage = next(s for s in pipeline["stages"] if s["id"] == fields["dealstage"])
    assert stage["label"] == "Closed Won" and Decimal(stage["metadata"]["probability"]) == 1
    currency = fields.get("deal_currency_code")
    currency_source = "deal_currency_code"
    if not currency:
        assert account["companyCurrency"] == "USD" and account["additionalCurrencies"] == [], "Ambiguous missing deal currency"
        currency, currency_source = "USD", "account.companyCurrency; no additional currencies; deal field absent"
    assert currency.upper() == "USD", "This bounded test supports USD only"
    total = Decimal(fields["amount"]) * 100
    assert total == total.to_integral_value() and total > 0
    assert plan["modeled_tax_minor"] == 0
    installments = plan["installments"]
    assert len(installments) == 2 and {r["obligation_id"] for r in installments} == {"1", "2"}
    assert sum(r["amount_minor"] for r in installments) == total, "Installments do not conserve exported deal amount"
    assert all(type(r["amount_minor"]) is int and r["amount_minor"] == 100000 for r in installments)
    assert all(r["issue_due"] == plan["as_of"] for r in installments)
    output.mkdir(parents=True, exist_ok=True)
    with (output / "hubspot-closed-won.csv").open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["deal_id", "dealstage", "amount_major", "currency", "currency_source"])
        writer.writerow([plan["deal_id"], fields["dealstage"], fields["amount"], currency.upper(), currency_source])
    with (output / "obligations.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["deal_id", "obligation_id", "amount_minor", "currency", "issue_due", "pay_due"], lineterminator="\n")
        writer.writeheader()
        for row in installments:
            writer.writerow({"deal_id": plan["deal_id"], "currency": currency.lower(),
                             **{k: row[k] for k in ("obligation_id", "amount_minor", "issue_due", "pay_due")}})
    assert len(read_deals(output / "obligations.csv")) == 2
    provenance = {
        "data_path": source["data_path"], "ui_export_tested": False,
        "portal_id": source["portal_id"], "source_rows": 1, "obligation_rows": 2,
        "source_amount_minor": int(total), "installment_sum_minor": sum(r["amount_minor"] for r in installments),
        "currency_source": currency_source,
        "field_origins": {"deal_id": "HubSpot hs_object_id, confirmed by object id and separate get",
                          "dealstage": "HubSpot dealstage, hs_is_closed_won and pipeline stage",
                          "amount_minor": "Separate test-plan allocation of Decimal(HubSpot amount) * 100; sum conserved; modeled tax 0",
                          "currency": currency_source,
                          "obligation_id": "Separate synthetic installment plan",
                          "issue_due": "Separate synthetic installment plan; ISO date",
                          "pay_due": "Separate synthetic installment plan; first payment control day; ISO date"},
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                   (source_path, plan_path, output / "hubspot-closed-won.csv", output / "obligations.csv")},
    }
    (output / "transformation.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return provenance


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence/derived")
    args = parser.parse_args()
    prepare(ROOT / "evidence/hubspot-source.json", ROOT / "evidence/installment-plan.json", args.output)
    print("PASS: verified one captured Closed-Won source row and two amount-conserving obligations.")
