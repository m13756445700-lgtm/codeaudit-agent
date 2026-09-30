from .identity import authenticate
from .service import perform

def invoice_endpoint(request, sessions, db, cache):
    principal = authenticate(request, sessions)
    return perform(principal, request.json, db, cache)
