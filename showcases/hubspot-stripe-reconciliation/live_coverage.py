import contextlib, io, json, sys
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit
from urllib.request import Request, urlopen
from urllib.error import URLError
from unittest.mock import patch
import reconcile
from verify_sandbox_http import ACCOUNT, IDS, ORIGINAL_DEALS, request, read_invoice, restore, save

root = Path(sys.argv[1])
root.mkdir()
assert request('/v1/account')['id'] == ACCOUNT
before = [read_invoice(i) for i in IDS]
for row, deal, total in zip(before, ORIGINAL_DEALS, (100000,190000), strict=True):
    assert row['status'] == 'draft' and row['auto_advance'] is False
    assert row['amount_paid'] == 0 and row['attempted'] is False
    assert row['total'] == total and row['currency'] == 'usd'
    assert row['metadata'] == {'hubspot_deal_id': deal, 'sfs_fixture': 'hubspot_reconciliation_20261112'}

def check(rows, expected, fault=None):
    p = root/'input.csv'
    p.write_text('deal_id,amount_minor,currency,issue_due,pay_due\n' + ''.join(
        f'{i},{n},{c},2026-11-12,2026-11-26\n' for i,n,c in rows))
    audit = root/'audit.json'
    calls = 0
    def transport(req, timeout):
        nonlocal calls
        url = urlsplit(req.full_url)
        assert url.scheme == 'https' and url.netloc == 'api.stripe.com' and url.path == '/v1/invoices'
        params = dict(parse_qsl(url.query))
        params['limit'] = 1
        real = Request(urlunsplit(url._replace(query=urlencode(params))), headers=dict(req.header_items()))
        with urlopen(real, timeout=timeout) as response:
            body = response.read()
        calls += 1
        if calls == 2 and fault == 'second_page_empty':
            assert json.loads(body)['data']
            body = b'{"data":[],"has_more":true}'
        if calls == 2 and fault == 'transport_error':
            raise URLError('injected after real response')
        return io.BytesIO(body)
    stdout = io.StringIO()
    exit_code = 0
    with patch.object(reconcile, 'urlopen', transport), patch.object(sys, 'argv', [
        'reconcile.py', str(p), '--as-of', '2026-11-26', '--audit', str(audit)]), contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
        try:
            reconcile.main()
        except SystemExit as exc:
            exit_code = exc.code
    a = json.loads(audit.read_text())
    assert calls == 2
    if fault:
        assert exit_code == 1 and a['run_status'] == 'incomplete' and not a['decisions_published'] and not stdout.getvalue()
        report = []
    else:
        assert exit_code == 0 and a['run_status'] == 'complete' and a['invoice_population'] == 'pagination_completed'
        assert a['invoice_count'] == 2 and a['deal_count'] == len(rows)
        report = json.loads(stdout.getvalue())
        assert {r['deal_id']:(r['status'],r['alerts'],sorted(r['invoice_ids'])) for r in report} == expected
    return {'real_http_responses': calls, 'audit': a, 'results': report}

native = json.loads((Path(__file__).parent.parent/'hubspot-stripe-reconciliation-r3/native-export-projection.json').read_text())
from decimal import Decimal
rows = [(r['Record ID'],int(Decimal(r['Amount'])*100),'usd') for r in native['records']]
A,B = ORIGINAL_DEALS
C = '539817448636'
normal = {
    A: ('invoice_draft',['missing_invoice'],[IDS[0]]),
    B: ('amount_mismatch',['amount_mismatch','missing_invoice'],[IDS[1]]),
    C: ('missing_invoice',['missing_invoice'],[]),
}
cycles = []
for i in range(1,11):
    fault = {3:'missing_input',6:'second_page_empty',9:'transport_error'}.get(i)
    if fault == 'missing_input':
        truncated = rows[:-1]
        assert {r[0] for r in truncated} != set(normal)
        initial = {'audit':{'run_status':'incomplete','decisions_published':False},'real_http_responses':0,'reason':'population check before CLI'}
    else:
        initial = check(rows,normal,fault)
    cycles.append({'cycle':i,'fault':fault,'initial':initial,'retry':check(rows,normal) if fault else None})
currency = check([(A,100000,'eur')],{A:('currency_mismatch',['currency_mismatch','missing_invoice'],[IDS[0]])})
save(root/'metadata-backup.json',{'invoices':before})
try:
    request('/v1/invoices/'+IDS[1],{'metadata[hubspot_deal_id]':A})
    duplicate = check([(A,100000,'usd')],{A:('multiple_invoices',['amount_mismatch','missing_invoice','multiple_invoices'],sorted(IDS))})
finally:
    restore(root)
restoration = json.loads((root/'restoration.json').read_text())
print('COVERAGE_EVIDENCE '+json.dumps({'cycles':cycles,'currency':currency,'duplicate':duplicate,'restoration':restoration}))
