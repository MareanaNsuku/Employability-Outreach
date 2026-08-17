
import sqlite3, re
from database import init_db   # <-- added

DB = 'data/outreach.db'

JUNK_PATTERNS = [
    'user@domain.com', 'your@email.com', 'email@example.com', 'example.com',
    'sentry', 'wixpress', 'noreply', 'no-reply', 'test@', 'admin@example.com',
    'foo@bar.com', 'example@', 'sample@', 'placeholder', 'yourname@', 'you@',
    '.png', '.jpg', '.jpeg', 'ingest'
]

def is_junk(email):
    email_lower = email.lower()
    if any(pattern in email_lower for pattern in JUNK_PATTERNS):
        return True
    domain = email_lower.split('@')[-1]
    if 'sentry' in domain or 'wixpress' in domain or 'example.com' in domain:
        return True
    return False

def score_email(email):
    email_lower = email.lower()
    if email_lower.endswith('.co.za'):
        return 5
    elif email_lower.endswith('.za'):
        return 3
    elif email_lower.endswith('.com'):
        return 2
    return 0

def pick_best_email(email_str):
    if not email_str:
        return ''
    candidates = re.split(r'[,;,\s]+', email_str.strip())
    valid = []
    for c in candidates:
        c = c.strip().lower()
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$', c):
            continue
        if is_junk(c):
            continue
        valid.append(c)
    if not valid:
        return ''
    valid.sort(key=lambda e: (-score_email(e), e))
    return valid[0]

def main():
    init_db()   # <-- creates the table if missing
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, email FROM contacts WHERE email != ''")
    rows = cur.fetchall()
    updates = []
    for cid, email in rows:
        best = pick_best_email(email)
        if best != email:
            updates.append((best, cid))
    for best, cid in updates:
        cur.execute("UPDATE contacts SET email=? WHERE id=?", (best, cid))
    conn.commit()
    conn.close()
    print(f"✅ Cleaned {len(updates)} email(s).")

if __name__ == '__main__':
    main()
