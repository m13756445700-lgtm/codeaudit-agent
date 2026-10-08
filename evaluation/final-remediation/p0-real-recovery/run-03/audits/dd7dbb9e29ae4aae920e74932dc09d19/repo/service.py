from security_config import may_read

def fetch_invoice(user, records, invoice_id):
    invoice = records[invoice_id]
    if not may_read(user, invoice):
        raise PermissionError("access denied")
    return {"amount": invoice["amount"], "tenant_id": invoice["tenant_id"]}
