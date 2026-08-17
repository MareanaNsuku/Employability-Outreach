
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), 'data', 'outreach.db')

def show_dashboard():
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT status, COUNT(*) FROM contacts GROUP BY status")
    print("📊 Dashboard:")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]}")
    conn.close()

def export_dashboard_csv(out_path):
    import csv
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT * FROM contacts")
    with open(out_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([desc[0] for desc in cur.description])
        writer.writerows(cur.fetchall())
    conn.close()
    print(f"📤 Exported to {out_path}")
