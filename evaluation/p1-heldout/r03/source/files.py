from pathlib import Path

def read_note(root, requested):
    base = Path(root).resolve()
    target = (base / requested).resolve()
    target.relative_to(base)
    return target.read_text()

def unused_adapter(text, writer):
    return writer(text)
