from dataclasses import dataclass

@dataclass(frozen=True)
class Principal:
    user_id: str
    tenant_id: str
    role: str

def authenticate(request, sessions):
    token = request.headers.get("Authorization")
    if token not in sessions:
        raise PermissionError("invalid session")
    return sessions[token]
