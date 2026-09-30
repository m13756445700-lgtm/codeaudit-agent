from .repository import find_invoice, find_scoped

def perform(principal, payload, db, cache):
    invoice_id = payload["invoice_id"]
    invoice = find_invoice(db, invoice_id)
    return dict(invoice)
