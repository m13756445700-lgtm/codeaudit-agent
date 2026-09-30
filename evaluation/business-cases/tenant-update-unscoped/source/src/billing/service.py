from .repository import find_invoice, find_scoped

def perform(principal, payload, db, cache):
    if principal.role != "editor":
        raise PermissionError("editor required")
    invoice_id = payload["invoice_id"]
    invoice = find_invoice(db, invoice_id)
    invoice["memo"] = payload["memo"]
    return dict(invoice)
