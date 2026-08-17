
import argparse, os, sqlite3
from dotenv import load_dotenv
from contacts import import_contacts
from sender import send_batch, send_followups, _file_attachment, _resolve_attachment_paths, _send_msg
from templates import generate_email
from database import init_db, mark_sent, delete_contacts_without_email

load_dotenv()

MY_INFO = {
    'name': os.getenv('MY_NAME'),
    'phone': os.getenv('MY_PHONE'),
    'linkedin': os.getenv('MY_LINKEDIN'),
    'email': os.getenv('MY_EMAIL'),
    'business_start': int(os.getenv('BUSINESS_HOURS_START', 7)),
    'business_end': int(os.getenv('BUSINESS_HOURS_END', 17)),
}

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command')

    imp = sub.add_parser('import')
    imp.add_argument('csv')

    send = sub.add_parser('send')
    send.add_argument('--test', action='store_true')
    send.add_argument('--batch', type=int, default=20)
    send.add_argument('--email', help='Send to a specific email address')
    send.add_argument('--cv')
    send.add_argument('--transcript')
    send.add_argument('--refletter', action='append', default=[])
    send.add_argument('--attach', action='append', default=[])
    send.add_argument('--force', action='store_true', help='Send even outside business hours')

    fup = sub.add_parser('followup')
    fup.add_argument('--cv')
    fup.add_argument('--transcript')
    fup.add_argument('--refletter', action='append', default=[])
    fup.add_argument('--attach', action='append', default=[])

    sub.add_parser('clean')
    dash = sub.add_parser('dashboard')
    dash.add_argument('--watch', action='store_true')
    exp = sub.add_parser('export')
    exp.add_argument('--out', default='data/export.csv')

    args = parser.parse_args()

    if args.command == 'import':
        import_contacts(args.csv)
    elif args.command == 'clean':
        deleted = delete_contacts_without_email()
        print(f"🧹 Removed {deleted} contacts with empty emails.")
    elif args.command in ('send', 'followup'):
        if hasattr(args, 'force') and args.force:
            from sender import set_force_send
            set_force_send(True)

        paths = []
        if hasattr(args, 'cv') and args.cv: paths.append(args.cv)
        if hasattr(args, 'transcript') and args.transcript: paths.append(args.transcript)
        paths.extend(args.refletter)
        paths.extend(args.attach)

        attachments = []
        for p in paths:
            if not os.path.exists(p):
                print(f"❌ Attachment not found: {p}")
                return
            attachments.append(_file_attachment(p))

        if args.command == 'send' and args.email:
            init_db()
            conn = sqlite3.connect('data/outreach.db')
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM contacts WHERE email=?", (args.email.strip().lower(),))
            contact = cur.fetchone()
            conn.close()
            if not contact:
                print(f"❌ Email {args.email} not found in database.")
                return
            contact = dict(contact)
            subject, body = generate_email(contact, MY_INFO, industry_key=contact.get('industry', 'engineering'))
            success, reason = _send_msg(args.email, subject, body, attachments)
            if success:
                mark_sent(contact['id'], subject, "fixed_template", None)
                print(f"📧 Sent to {args.email}")
            else:
                print(f"❌ Failed: {reason}")
        else:
            if args.command == 'send':
                send_batch(None, MY_INFO, max_daily=int(os.getenv('MAX_DAILY_EMAILS', 50)),
                           max_batch=args.batch, test_mode=args.test, attachments=attachments)
            else:
                send_followups(None, MY_INFO, attachments=attachments)
    elif args.command == 'dashboard':
        from dashboard import show_dashboard
        show_dashboard()
    elif args.command == 'export':
        from dashboard import export_dashboard_csv
        export_dashboard_csv(args.out)

if __name__ == '__main__':
    main()
