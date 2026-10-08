from ledger import rename

def change_title(identity, payload, records):
    if not identity["authenticated"]:
        raise PermissionError("login required")
    return rename(records, payload["record_key"], payload["title"])
