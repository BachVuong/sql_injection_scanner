import streamlit as st
from crawler.crawl_urls import find_links_with_params
from scanner.sqli_scanner import inject_payload, load_payloads

# ------------------ Hàm phân loại mức độ nghiêm trọng ------------------
def classify_severity(payload):
    payload = payload.lower()
    if "union" in payload:
        return "High"
    elif "or" in payload:
        return "Medium"
    elif "and" in payload:
        return "Low"
    return "Low"

# ------------------ Cấu hình giao diện ------------------
st.set_page_config(page_title="SQL Injection Scanner", page_icon="🛡️")

st.title("🛡️ SQL Injection Scanner")
st.markdown("Nhập website bạn muốn quét để phát hiện lỗ hổng SQL Injection.")

target = st.text_input("Nhập URL website", "http://testphp.vulnweb.com")
scan_btn = st.button("Bắt đầu quét")

if scan_btn:
    if not target.startswith("http"):
        st.error("URL phải bắt đầu bằng http:// hoặc https://")
    else:
        st.info("🔍 Đang thu thập URL có tham số...")
        urls = find_links_with_params(target)
        st.success(f"Tìm được {len(urls)} URL có tham số")

        payloads = load_payloads("payloads/sqli.txt")
        vulnerable = []

        with st.spinner("Đang inject payload..."):
            for url in urls:
                for payload in payloads:
                    result = inject_payload(url, payload)
                    if result:
                        severity = classify_severity(payload)
                        st.warning(f"Phát hiện SQLi [{severity}]: {result}")
                        vulnerable.append((result, severity))
                        break

        if vulnerable:
            st.success(f"Phát hiện {len(vulnerable)} URL dễ bị tấn công SQLi!")

            st.markdown("### 📊 Mức độ nghiêm trọng:")
            for level in ["High", "Medium", "Low"]:
                count = sum(1 for _, s in vulnerable if s == level)
                if count > 0:
                    st.markdown(f"- **{level}**: {count} lỗ hổng")

            st.markdown("### 🧬 Chi tiết:")
            for v, s in vulnerable:
                st.write(f"[{s}] {v}")
        else:
            st.info("Không phát hiện SQLi nào.")
