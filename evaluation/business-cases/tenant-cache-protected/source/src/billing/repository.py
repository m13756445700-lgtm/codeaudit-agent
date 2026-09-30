def find_invoice(db, invoice_id):
    return db.get(invoice_id)

def find_scoped(db, tenant_id, invoice_id):
    invoice = db.get(invoice_id)
    if invoice is None or invoice["tenant_id"] != tenant_id:
        raise PermissionError("not found")
    return invoice
