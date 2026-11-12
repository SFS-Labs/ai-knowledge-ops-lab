import csv, json, os, subprocess, tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

key = os.environ['STRIPE_API_KEY']
assert key.startswith(('sk_test_', 'rk_test_'))
tag = 'sfs-overdue-' + os.environ['GITHUB_RUN_ID'] + '-' + os.environ['GITHUB_RUN_ATTEMPT']
deal = tag + '-synthetic-deal'

def stripe(path, fields=None, suffix=None):
    headers = {'Authorization': 'Bearer ' + key}
    if suffix:
        headers['Idempotency-Key'] = tag + '-' + suffix
    req = Request('https://api.stripe.com/v1/' + path,
                  data=urlencode(fields).encode() if fields is not None else None, headers=headers)
    try:
        with urlopen(req, timeout=20) as response:
            return json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f'Stripe {path.split("/")[0]} HTTP {exc.code}') from None

def guard(inv, status):
    assert inv['livemode'] is False and inv['status'] == status
    assert inv['metadata']['hubspot_deal_id'] == deal and inv['metadata']['sfs_fixture'] == tag
    assert inv['auto_advance'] is False and inv['collection_method'] == 'send_invoice'
    assert inv['amount_paid'] == 0 and inv['attempted'] is False

assert stripe('account')['id'] == 'acct_1Uaj2tE19wsOrukR'
customer = stripe('customers', {'name': 'SFS synthetic overdue fixture', 'metadata[sfs_fixture]': tag}, 'customer')
assert customer['livemode'] is False and not customer.get('email')
invoice = stripe('invoices', {'customer': customer['id'], 'collection_method': 'send_invoice',
    'days_until_due': 1, 'auto_advance': 'false', 'pending_invoice_items_behavior': 'exclude',
    'metadata[hubspot_deal_id]': deal, 'metadata[sfs_fixture]': tag}, 'draft')
path = 'invoices/' + invoice['id']
checks = []
try:
    guard(invoice, 'draft')
    item = stripe('invoiceitems', {'customer':customer['id'], 'invoice':invoice['id'],
        'amount':100000,'currency':'usd','description':'Synthetic reconciliation fixture'}, 'item')
    assert item['livemode'] is False and item['invoice'] == invoice['id']
    opened = stripe(path+'/finalize', {'auto_advance':'false'}, 'finalize')
    guard(opened, 'open')
    assert opened['total'] == 100000 and opened['currency'] == 'usd'
    issue = datetime.fromtimestamp(opened['status_transitions']['finalized_at'], timezone.utc).date()
    due = datetime.fromtimestamp(opened['due_date'], timezone.utc).date()
    cutoff = due + timedelta(days=1)
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp)
        with (p/'input.csv').open('w', newline='') as stream:
            w = csv.writer(stream)
            w.writerow(['deal_id','amount_minor','currency','issue_due','pay_due'])
            w.writerow([deal,100000,'usd',issue,cutoff])
        for day, status, alerts in [(cutoff-timedelta(days=1),'invoice_open',[]),
                                    (cutoff,'payment_overdue',['payment_overdue'])]:
            data = subprocess.check_output(['python3','reconcile.py',str(p/'input.csv'),
                '--as-of',str(day),'--audit',str(p/'audit.json')])
            rows = json.loads(data)
            audit = json.loads((p/'audit.json').read_text())
            assert audit['run_status'] == 'complete' and audit['invoice_population'] == 'pagination_completed'
            assert rows == [{'deal_id':deal,'status':status,'alerts':alerts,'invoice_ids':[invoice['id']]}]
            checks.append({'audit':audit,'results':rows})
finally:
    current = stripe(path)
    if current['status'] == 'open':
        guard(current,'open')
        stripe(path+'/void', {}, 'void')
        current = stripe(path)
        guard(current,'void')
    elif current['status'] == 'draft':
        guard(current,'draft')
    else:
        guard(current,'void')
assert current['status'] == 'void'
print('OVERDUE_EVIDENCE ' + json.dumps({'stripe_account':'acct_1Uaj2tE19wsOrukR',
    'fixture':'separate synthetic obligation; explicit hypothetical as-of dates',
    'stripe_due_date_utc':str(due),'control_cutoff_utc':str(cutoff),'checks':checks,
    'readback':{k:current[k] for k in ('id','status','livemode','auto_advance','collection_method','amount_paid','attempted','status_transitions')}}))
