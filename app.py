import streamlit as st
from crawler.crawl_urls import find_links_with_params
from scanner.sqli_scanner import inject_payload, load_payloads

st.set_page_config(page_title="SQL Injection Scanner", page_icon="🛡️")

st.title("🛡️ SQL Injection Scanner")
st.markdown("Nhập website bạn muốn quét để phát hiện lỗ hổng SQL Injection.")

target = st.text_input("🔗 Nhập URL website", "http://testphp.vulnweb.com")
scan_btn = st.button("🚀 Bắt đầu quét")

if scan_btn:
    if not target.startswith("http"):
        st.error("❌ URL phải bắt đầu bằng http:// hoặc https://")
    else:
        st.info("🔍 Đang thu thập URL có tham số...")
        urls = find_links_with_params(target)
        st.success(f"✅ Tìm được {len(urls)} URL có tham số")

        payloads = load_payloads("payloads/sqli.txt")
        vulnerable = []

        with st.spinner("🧪 Đang inject payload..."):
            for url in urls:
                for payload in payloads:
                    result = inject_payload(url, payload)
                    if result:
                        st.warning(f"⚠️ Phát hiện SQLi: {result}")
                        vulnerable.append(result)
                        break

        with open("reports/report.txt", "w") as f:
            for v in vulnerable:
                f.write(f"{v}\n")

        if vulnerable:
            st.success(f"🎉 Phát hiện {len(vulnerable)} URL dễ bị tấn công SQLi!")
            if st.button("📄 Tiếp tục kiểm tra"):
                st.code("\n".join(vulnerable))
        else:
            st.info("✅ Không phát hiện SQLi nào.")

