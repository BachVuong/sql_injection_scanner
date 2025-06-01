import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def load_payloads(file_path):
    with open(file_path) as f:
        return [line.strip() for line in f if line.strip()]

def inject_payload(url, payload):
    parts = urlparse(url)
    query = parse_qs(parts.query)

    for param in query:
        original = query[param]
        query[param] = [payload]
        new_query = urlencode(query, doseq=True)
        new_url = urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, new_query, parts.fragment))

        try:
            res = requests.get(new_url, timeout=5)
            if res.status_code == 500 or "sql" in res.text.lower():
                return new_url
        except:
            continue

        query[param] = original

    return None
