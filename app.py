import streamlit as st
import os
from crawler.crawl_urls import find_links_with_params
from scanner.sqli_scanner import inject_payload, load_payloads
from datetime import datetime

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

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Quét SQLi"
if "selected_report" not in st.session_state:
    st.session_state.selected_report = None

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
                            severity = classify_severity(payload)
                            st.warning(f"Phát hiện SQLi [{severity}]: {result}")
                            vulnerable.append((result, severity))
                            break

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(REPORT_DIR, exist_ok=True)
            report_file = f"report_{timestamp}.txt"
            with open(os.path.join(REPORT_DIR, report_file), "w") as f:
                f.write("SQL Injection Scan Report\n")
                f.write(f"Target: {target}\n")
                f.write(f"Time: {timestamp}\n")
                f.write(f"Total Vulnerabilities: {len(vulnerable)}\n\n")
                severity_count = {"High": 0, "Medium": 0, "Low": 0}

                for v, s in vulnerable:
                    f.write(f"[{s}] {v}\n")
                    severity_count[s] += 1

                f.write("\nSeverity Summary:\n")
                for level in ["High", "Medium", "Low"]:
                    f.write(f"- {level}: {severity_count[level]}\n")

            st.session_state.selected_report = report_file

            if vulnerable:
                st.success(f"Phát hiện {len(vulnerable)} URL dễ bị tấn công SQLi!")

                st.markdown("Mức độ nghiêm trọng:")
                for level in ["High", "Medium", "Low"]:
                    count = sum(1 for _, s in vulnerable if s == level)
                    if count > 0:
                        st.markdown(f"- **{level}**: {count} lỗ hổng")

                st.markdown("Chi tiết:")
                for v, s in vulnerable:
                    st.write(f"[{s}] {v}")
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
