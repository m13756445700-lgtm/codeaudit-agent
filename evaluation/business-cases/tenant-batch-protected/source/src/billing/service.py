from .repository import find_invoice, find_scoped

def perform(principal, payload, db, cache):
    ids = payload["invoice_ids"]
    if not ids:
        return []
    find_scoped(db, principal.tenant_id, ids[0])
    selected = [find_scoped(db, principal.tenant_id, invoice_id) for invoice_id in ids]
    return [dict(invoice) for invoice in selected]
