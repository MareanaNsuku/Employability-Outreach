
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'outreach.db')

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            contact_name TEXT,
            email TEXT UNIQUE,
            industry TEXT,
            tier INTEGER DEFAULT 1,
            city TEXT,
            phone TEXT,
            website TEXT,
            status TEXT DEFAULT 'pending',
            sent_at TIMESTAMP,
            followup_sent INTEGER DEFAULT 0,
            bounced_at TIMESTAMP,
            fail_reason TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_pending_contacts(cur, limit):
    cur.execute("SELECT * FROM contacts WHERE status='pending' AND email != '' ORDER BY RANDOM() LIMIT ?", (limit,))
    return cur.fetchall()

def mark_sent(contact_id, subject, template, followup_id):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("UPDATE contacts SET status='sent', sent_at=CURRENT_TIMESTAMP WHERE id=?", (contact_id,))
    conn.commit(); conn.close()

def mark_bounced(contact_id, reason):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("UPDATE contacts SET status='bounced', bounced_at=CURRENT_TIMESTAMP, fail_reason=? WHERE id=?", (reason, contact_id))
    conn.commit(); conn.close()

def get_contacts_needing_followup(cur):
    cur.execute("SELECT * FROM contacts WHERE status='sent' AND followup_sent=0 AND date(sent_at) <= date('now', '-3 days')")
    return cur.fetchall()

def mark_followup(contact_id):
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("UPDATE contacts SET followup_sent=1 WHERE id=?", (contact_id,))
    conn.commit(); conn.close()

def delete_contacts_without_email():
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE email='' OR email IS NULL")
    deleted = cur.rowcount
    conn.commit(); conn.close()
    return deleted
