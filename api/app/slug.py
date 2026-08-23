import re

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text or "untitled")[:80]


def is_valid_slug(value: str) -> bool:
    return bool(value) and len(value) <= 80 and SLUG_RE.fullmatch(value)
