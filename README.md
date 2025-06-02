SQL Injection Scanner

Mục tiêu
Crawl website, phát hiện URL có tham số, inject payload để phát hiện SQLi (SQL Injection).

Công nghệ sử dụng
- Python 3
- Requests
- BeautifulSoup
- Manual payload injection

Cách chạy

```bash
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
streamlit run app.py
