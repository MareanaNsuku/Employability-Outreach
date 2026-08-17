
import csv, sqlite3, os
from database import init_db

DB = os.path.join(os.path.dirname(__file__), 'data', 'outreach.db')

def import_contacts(csv_path):
    init_db()
    conn = sqlite3.connect(DB); cur = conn.cursor()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            email = row.get('email', '').strip().lower()
            if not email:
                continue
            cur.execute(
                "INSERT OR IGNORE INTO contacts (company_name, contact_name, email, industry, tier, city, phone, website) VALUES (?,?,?,?,?,?,?,?)",
                (row.get('company_name',''), row.get('contact_name',''), email,
                 row.get('industry',''), int(row.get('tier',1)), row.get('city',''),
                 row.get('phone',''), row.get('website',''))
            )
            if cur.rowcount:
                count += 1
    conn.commit(); conn.close()
    print(f"✅ {count} contacts imported.")
