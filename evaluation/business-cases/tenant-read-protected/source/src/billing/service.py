from .repository import find_invoice, find_scoped

def perform(principal, payload, db, cache):
    invoice_id = payload["invoice_id"]
    invoice = find_scoped(db, principal.tenant_id, invoice_id)
    return dict(invoice)
