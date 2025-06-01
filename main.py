from crawler.crawl_urls import find_links_with_params
from scanner.sqli_scanner import inject_payload, load_payloads

target = "http://testphp.vulnweb.com"  # hoặc website bạn muốn kiểm tra

urls = find_links_with_params(target)
payloads = load_payloads("payloads/sqli.txt")

print("=== SQL Injection Scan Started ===")
vulnerable = []

for url in urls:
    for payload in payloads:
        result = inject_payload(url, payload)
        if result:
            print(f"[+] SQLi Found: {result}")
            vulnerable.append(result)
            break

with open("reports/report.txt", "w") as f:
    for v in vulnerable:
        f.write(f"{v}\n")

print("=== Scan Completed ===")
