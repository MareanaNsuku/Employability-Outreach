import os, re, time, random, sqlite3, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from dotenv import load_dotenv
from templates import generate_email, generate_followup
from database import (
    init_db, get_pending_contacts, mark_sent, mark_bounced,
    get_contacts_needing_followup, mark_followup,
)

load_dotenv()

# ---------- Force send override ----------
FORCE_SEND = False

def set_force_send(val: bool):
    global FORCE_SEND
    FORCE_SEND = val

def is_business_hours(start=7, end=17):
    if FORCE_SEND:
        return True
    now = datetime.now()
    return start <= now.hour < end

def _file_attachment(filepath):
    with open(filepath, 'rb') as f:
        content = f.read()
    filename = os.path.basename(filepath)
    part = MIMEApplication(content, _subtype="pdf")
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    return part

ATTACH_FILES = [
    ("small_Nsuku Mareana Resume.pdf", "Nsuku Mareana Resume.pdf"),
    ("UCT Official Academic Transcript.pdf", "UCT Official Academic Transcript.pdf"),
    ("small_Nsuku Mareana Reference Letter.pdf", "Nsuku Mareana Reference Letter.pdf"),
    ("small_IEEE Reference Letter.pdf", "IEEE Reference Letter.pdf"),
]

def _resolve_attachment_paths():
    docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
    paths = []
    for small, full in ATTACH_FILES:
        small_path = os.path.join(docs_dir, small)
        full_path = os.path.join(docs_dir, full)
        if os.path.exists(small_path):
            paths.append(small_path)
        elif os.path.exists(full_path):
            paths.append(full_path)
    return paths

def _send_msg(to, subject, body, attachments=None):
    """Send email using Gmail SMTP with App Password."""
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('MY_EMAIL')
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        if attachments:
            for att in attachments:
                msg.attach(att)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv('MY_EMAIL'), os.getenv('MY_APP_PASSWORD'))
        server.sendmail(os.getenv('MY_EMAIL'), to, msg.as_string())
        server.quit()
        return True, ''
    except Exception as e:
        return False, str(e)

def send_batch(service, my_info, max_daily=50, min_delay=8, max_delay=10, max_batch=20, test_mode=False, attachments=None):
    init_db()
    if not test_mode and not is_business_hours(my_info['business_start'], my_info['business_end']):
        print("🕒 Outside business hours. Skipping send.")
        return
    if attachments is None:
        attachments = [_file_attachment(p) for p in _resolve_attachment_paths()]
    conn = sqlite3.connect('data/outreach.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM contacts WHERE status='sent' AND date(sent_at)=date('now')")
    sent_today = cur.fetchone()[0]
    remaining = max_daily - sent_today
    if remaining <= 0:
        print(f"📬 Daily limit of {max_daily} reached. Skipping.")
        conn.close()
        return
    limit = min(max_batch, remaining)
    contacts = get_pending_contacts(cur, limit)
    if not contacts:
        print("✅ No more pending contacts.")
        conn.close()
        return
    print(f"📎 Using {len(attachments)} document(s) for this batch.")
    sent = 0
    for contact in contacts:
        contact = dict(contact)
        email = contact['email']
        subject, body = generate_email(contact, my_info, industry_key=contact.get('industry', 'engineering'))
        success, reason = _send_msg(email, subject, body, attachments)
        if success:
            mark_sent(contact['id'], subject, "fixed_template", None)
            print(f"📧 Sent to {email} – {subject}")
            sent += 1
            if sent >= limit:
                break
            time.sleep(random.randint(min_delay, max_delay))
        else:
            mark_bounced(contact['id'], reason)
            print(f"❌ Bounced: {email} – {reason}")
    conn.close()
    print(f"📬 Sent {sent} emails this session.")

def send_followups(service, my_info, attachments=None):
    if attachments is None:
        attachments = [_file_attachment(p) for p in _resolve_attachment_paths()]
    init_db()
    conn = sqlite3.connect('data/outreach.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    contacts = get_contacts_needing_followup(cur)
    conn.close()
    if not contacts:
        print("✅ No follow‑ups needed.")
        return
    for contact in contacts:
        contact = dict(contact)
        email = contact['email']
        subject, body = generate_followup(contact, my_info, industry_key=contact.get('industry', 'engineering'))
        success, _ = _send_msg(email, subject, body, attachments)
        if success:
            mark_followup(contact['id'])
            print(f"📧 Follow‑up sent to {email}")
            time.sleep(random.randint(8, 10))
