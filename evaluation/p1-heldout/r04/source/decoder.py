import base64
import pickle

def unpack(body):
    decoded = base64.b64decode(body, validate=True)
    return pickle.loads(decoded)
