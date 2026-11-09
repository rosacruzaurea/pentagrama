"""Optional public engine identifier and narrowly scoped search policy."""
import json
import re
from pathlib import Path


def validate_engine_id(value):
    if not isinstance(value, str) or (value and not re.fullmatch(r'[A-Za-z0-9:_-]{1,100}', value)):
        raise ValueError('programmableSearchId must be empty or a valid public engine ID, not an embed/URL/key')
    return value


ENGINE_ID = validate_engine_id(json.loads((Path(__file__).resolve().parents[1] / 'content/search.json').read_text())['programmableSearchId'])
SEARCH_ROUTES = {'/buscar/', '/livros/', '/revistas/'}


def content_security_policy(embedded=False):
    # No executable inline code/eval, wildcard script hosts or ad-network grants.
    scripts = "'self'"
    styles = "'self'"
    images = "'self'"
    connections = "'self'"
    frames = ""
    if embedded:
        scripts += ' https://cse.google.com https://www.google.com https://www.googleapis.com'
        styles += " 'unsafe-inline' https://www.google.com"
        images += ' https://www.google.com https://cse.google.com https://encrypted-tbn0.gstatic.com https://encrypted-tbn1.gstatic.com data:'
        connections += ' https://cse.google.com https://www.google.com https://www.googleapis.com'
        frames = 'frame-src https://www.google.com; '
    return f"default-src 'self'; script-src {scripts}; style-src {styles}; img-src {images}; media-src 'self' https://github.com https://*.githubusercontent.com; connect-src {connections}; {frames}object-src 'none'; base-uri 'none'; form-action 'self' https://www.google.com/search"
