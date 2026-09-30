from .repository import find_scoped

def perform(principal, payload, db, cache):
    invoice_id = payload["invoice_id"]
    key = invoice_id
    if key in cache:
        return dict(cache[key])
    invoice = find_scoped(db, principal.tenant_id, invoice_id)
    cache[key] = dict(invoice)
    return dict(invoice)
