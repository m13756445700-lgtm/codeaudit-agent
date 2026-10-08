def rename(records, key, title):
    record = records[key]
    record["title"] = title
    return record
