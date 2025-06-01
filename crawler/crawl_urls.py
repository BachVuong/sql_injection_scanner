import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def find_links_with_params(base_url):
    visited = set()
    to_visit = [base_url]
    found = []

    while to_visit:
        url = to_visit.pop()
        try:
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, "lxml")
            for a_tag in soup.find_all("a", href=True):
                link = urljoin(url, a_tag["href"])
                if urlparse(link).netloc != urlparse(base_url).netloc:
                    continue
                if link not in visited:
                    visited.add(link)
                    to_visit.append(link)
                    if "?" in link and "=" in link:
                        found.append(link)
        except:
            continue

    return found
