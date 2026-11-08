"""Shared build/check settings; no dependency or remote configuration writes."""
import os
import re

BASE = os.environ.get('PAGES_BASE_PATH', '/pentagrama').rstrip('/')
if not re.fullmatch(r'(?:/[A-Za-z0-9_-]+)*', BASE):
    raise ValueError('PAGES_BASE_PATH must be empty or an absolute path without query/fragment')
NOINDEX = os.environ.get('SITE_NOINDEX', '0') == '1'
SEARCH_DEMO = os.environ.get('SEARCH_DEMO', '0') == '1'
if SEARCH_DEMO and not NOINDEX:
    raise ValueError('SEARCH_DEMO requires SITE_NOINDEX=1; demonstration must not ship to production')
