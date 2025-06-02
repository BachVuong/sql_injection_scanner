import streamlit as st
import os
from crawler.crawl_urls import find_links_with_params
from scanner.sqli_scanner import inject_payload, load_payloads
from datetime import datetime

# Cấu hình giao diện
st.set_page_config(page_title="SQL Injection Scanner", page_icon="🛡️")

# Khởi tạo session state
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Quét SQLi"
if "selected_report" not in st.session_state:
    st.session_state.selected_report = None

# Sidebar chuyển tab
st.sidebar.title("🔧 Menu")
tab = st.sidebar.radio("Chọn chức năng", ["Quét SQLi", "Xem báo cáo"])
st.session_state.current_tab = tab

REPORT_DIR = "reports"

# ------------------ Tab 1: Quét SQLi ------------------
if st.session_state.current_tab == "Quét SQLi":
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
                            st.warning(f"Phát hiện SQLi: {result}")
                            vulnerable.append(result)
                            break

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(REPORT_DIR, exist_ok=True)
            report_file = f"report_{timestamp}.txt"
            with open(os.path.join(REPORT_DIR, report_file), "w") as f:
                for v in vulnerable:
                    f.write(f"{v}\n")

            st.session_state.selected_report = report_file

            if vulnerable:
                st.success(f"Phát hiện {len(vulnerable)} URL dễ bị tấn công SQLi!")
                st.code("\n".join(vulnerable))
            else:
                st.info("Không phát hiện SQLi nào.")

# ------------------ Tab 2: Xem báo cáo ------------------
elif st.session_state.current_tab == "Xem báo cáo":
    st.title("📄 Danh sách báo cáo đã lưu")

    report_files = os.listdir(REPORT_DIR) if os.path.exists(REPORT_DIR) else []
    report_files.sort(reverse=True)

    selected = st.selectbox("Chọn báo cáo để xem:", [""] + report_files)

    if selected:
        st.session_state.selected_report = selected

    if st.session_state.selected_report:
        filepath = os.path.join(REPORT_DIR, st.session_state.selected_report)
        st.subheader(f"Nội dung: {st.session_state.selected_report}")
        with open(filepath, "r") as f:
            st.code(f.read(), language="text")
