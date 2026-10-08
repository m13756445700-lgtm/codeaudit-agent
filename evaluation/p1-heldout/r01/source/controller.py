from service import schedule

def post(payload):
    return schedule(payload["label"])
