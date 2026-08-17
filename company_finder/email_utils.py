import re, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}')

def extract_emails_from_url(url, timeout=8):
    emails = set()
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code != 200:
            return emails
        emails.update(EMAIL_REGEX.findall(resp.text))
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            if a['href'].startswith('mailto:'):
                email = a['href'][7:].split('?')[0].strip().lower()
                if re.match(EMAIL_REGEX, email):
                    emails.add(email)
    except:
        pass
    return emails

def find_contact_pages(base_url):
    candidates = []
    try:
        resp = requests.get(base_url, headers=HEADERS, timeout=8)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            text = a.get_text(strip=True).lower()
            if any(w in href for w in ['contact', 'about', 'team', 'people', 'reach-us', 'support']) or \
               any(w in text for w in ['contact', 'about', 'team', 'support']):
                full = urljoin(base_url, a['href'])
                candidates.append(full)
    except:
        pass
    return list(set(candidates))[:5]

def scrape_emails(website):
    if not website or 'google.com' in website:
        return ''
    all_emails = extract_emails_from_url(website)
    if not all_emails:
        for page in find_contact_pages(website):
            all_emails.update(extract_emails_from_url(page, timeout=5))
    clean = {e for e in all_emails if not e.startswith('noreply@') and not e.startswith('no-reply@')}
    return ','.join(clean) if clean else ''
