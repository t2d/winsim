
import os
import requests
from bs4 import BeautifulSoup
import config


# --- CONFIGURATION ---
USERNAME = config.USERNAME
PASSWORD = config.PASSWORD
LOGIN_URL = 'https://service.winsim.de/'
INVOICE_URL = 'https://service.winsim.de/mytariff/invoice/showAll'
DOWNLOAD_DIR = './invoices'


os.makedirs(DOWNLOAD_DIR, exist_ok=True)

with requests.Session() as session:
    # Step 1: Get login page to fetch cookies and possible CSRF token
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, 'html.parser')

    # Find CSRF token for login
    csrf_token = None
    token_input = soup.find('input', {'name': 'UserLoginType[_token]'})
    if token_input:
        csrf_token = token_input.get('value')

    # Step 2: Prepare login payload (update field names as needed)
    payload = {
        'UserLoginType[alias]': USERNAME,
        'UserLoginType[password]': PASSWORD,
        'UserLoginType[_token]': csrf_token if csrf_token else '',
    }

    # Step 3: Post login form to the correct action URL
    login_action_url = 'https://service.winsim.de/public/login_check'
    resp = session.post(login_action_url, data=payload)
    if 'Zeit neu starten' not in resp.text.lower():
        print('Login failed. Please check credentials or update field names.')
        with open('login_debug.html', 'w', encoding='utf-8') as debug_file:
            debug_file.write(resp.text)
        print('Saved login response HTML to login_debug.html for inspection.')
        exit(1)

    # Step 4: Go to invoice page
    invoice_page = session.get(INVOICE_URL)
    soup = BeautifulSoup(invoice_page.text, 'html.parser')

    # Step 5: Find all invoice download links (showPDF URLs)
    import re
    invoice_links = soup.find_all('a', href=lambda h: h and '/mytariff/invoice/showPDF/' in h)
    if not invoice_links:
        print('No invoice download links found.')
        exit(1)

    for link in invoice_links:
        invoice_url = link['href']
        if not invoice_url.startswith('http'):
            invoice_url = 'https://service.winsim.de' + invoice_url

        invoice_resp = session.get(invoice_url, stream=True)
        # Try to get filename from Content-Disposition header
        content_disp = invoice_resp.headers.get('Content-Disposition', '')
        import re
        file_from_header = None
        match = re.search(r'filename\*=UTF-8\'\'?([^\s;]+)', content_disp)
        if match:
            file_from_header = match.group(1)
        else:
            match = re.search(r'filename="?([^";]+)"?', content_disp)
            if match:
                file_from_header = match.group(1)
        if file_from_header:
            # Remove duplicate .pdf extension if present
            base, ext = os.path.splitext(file_from_header)
            if ext.lower() == '.pdf' and base.lower().endswith('.pdf'):
                file_from_header = base
            filename = os.path.join(DOWNLOAD_DIR, file_from_header)
        if os.path.exists(filename):
            print(f'Skipping already downloaded invoice: {filename}')
            continue
        with open(filename, 'wb') as f:
            for chunk in invoice_resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f'Invoice downloaded to {filename}')

