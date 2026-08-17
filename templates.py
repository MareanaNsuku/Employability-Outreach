
MY_NAME = 'Nsuku Mareana'
MY_PHONE = '+27 68 078 9360'
MY_EMAIL = 'mareanansuku@gmail.com'
MY_LINKEDIN = 'https://www.linkedin.com/in/nsukumareana'

INDUSTRY_TEMPLATES = {
    'mech_engineering': {
        "subject": "[IMPORTANT] Mechanical & Mechatronics Engineering Student – Graduate & Internship Enquiry",
        "body": "Dear {name},\n\nI hope you are well.\n\nMy name is {full_name}, and I am a third-year Mechanical & Mechatronics Engineering student at the University of Cape Town.\n\nI am reaching out to enquire about possible graduate, internship, vacation work, or experiential training opportunities within your organisation.\n\nI am particularly looking for opportunities during the period from late November through December, and I will be available in Randburg, Johannesburg at that time.\n\nI have attached my CV, Academic Transcript, and Reference Letter for your reference.\n\nThank you for your time and consideration.\n\nKind regards,\n{full_name}\n📞 {phone}\n✉️ {email}\nLinkedIn: {linkedin}"
    },
    'tech': {
        "subject": "[IMPORTANT] UCT Engineering Student – Tech & Software Opportunities Enquiry",
        "body": "Dear {name},\n\nI hope you are well.\n\nMy name is {full_name}, and I am a third-year Mechanical & Mechatronics Engineering student at the University of Cape Town with a strong interest in technology and software development.\n\nI am reaching out to enquire about possible graduate, internship, or experiential training opportunities within your tech team.\n\nI am particularly looking for opportunities during the period from late November through December, and I will be available in Randburg, Johannesburg at that time.\n\nI have attached my CV, Academic Transcript, and Reference Letter.\n\nThank you for your time.\n\nKind regards,\n{full_name}\n📞 {phone}\n✉️ {email}\nLinkedIn: {linkedin}"
    },
    'fintech': {
        "subject": "[IMPORTANT] UCT Engineering Student – FinTech Opportunities Enquiry",
        "body": "Dear {name},\n\nI hope you are well.\n\nMy name is {full_name}, and I am a third-year Mechanical & Mechatronics Engineering student at the University of Cape Town with a keen interest in financial technology.\n\nI am reaching out to enquire about possible graduate, internship, or experiential training opportunities within your organisation.\n\nI am particularly looking for opportunities during the period from late November through December, and I will be available in Randburg, Johannesburg at that time.\n\nI have attached my CV, Academic Transcript, and Reference Letter.\n\nThank you for your time.\n\nKind regards,\n{full_name}\n📞 {phone}\n✉️ {email}\nLinkedIn: {linkedin}"
    },
    'ict': {
        "subject": "[IMPORTANT] UCT Engineering Student – ICT Opportunities Enquiry",
        "body": "Dear {name},\n\nI hope you are well.\n\nMy name is {full_name}, and I am a third-year Mechanical & Mechatronics Engineering student at the University of Cape Town with a strong interest in ICT and telecommunications.\n\nI am reaching out to enquire about possible graduate, internship, or experiential training opportunities.\n\nI am particularly looking for opportunities during the period from late November through December, and I will be available in Randburg, Johannesburg at that time.\n\nI have attached my CV, Academic Transcript, and Reference Letter.\n\nThank you for your time.\n\nKind regards,\n{full_name}\n📞 {phone}\n✉️ {email}\nLinkedIn: {linkedin}"
    },
    'green_energy': {
        "subject": "[IMPORTANT] UCT Engineering Student – Renewable Energy & Green Economy Enquiry",
        "body": "Dear {name},\n\nI hope you are well.\n\nMy name is {full_name}, and I am a third-year Mechanical & Mechatronics Engineering student at the University of Cape Town with a passion for renewable energy and sustainability.\n\nI am reaching out to enquire about possible graduate, internship, or experiential training opportunities.\n\nI am particularly looking for opportunities during the period from late November through December, and I will be available in Randburg, Johannesburg at that time.\n\nI have attached my CV, Academic Transcript, and Reference Letter.\n\nThank you for your time.\n\nKind regards,\n{full_name}\n📞 {phone}\n✉️ {email}\nLinkedIn: {linkedin}"
    },
    'ai': {
        "subject": "[IMPORTANT] UCT Engineering Student – AI & Machine Learning Opportunities Enquiry",
        "body": "Dear {name},\n\nI hope you are well.\n\nMy name is {full_name}, and I am a third-year Mechanical & Mechatronics Engineering student at the University of Cape Town with a strong interest in artificial intelligence and machine learning.\n\nI am reaching out to enquire about possible graduate, internship, or experiential training opportunities.\n\nI am particularly looking for opportunities during the period from late November through December, and I will be available in Randburg, Johannesburg at that time.\n\nI have attached my CV, Academic Transcript, and Reference Letter.\n\nThank you for your time.\n\nKind regards,\n{full_name}\n📞 {phone}\n✉️ {email}\nLinkedIn: {linkedin}"
    }
}

DEFAULT_TEMPLATE = {
    "subject": "[IMPORTANT] UCT Engineering Student – Career Opportunities Enquiry",
    "body": "Dear {name},\n\nI hope you are well.\n\nMy name is {full_name}, and I am a third-year Mechanical & Mechatronics Engineering student at the University of Cape Town.\n\nI am reaching out to enquire about possible graduate, internship, vacation work, or experiential training opportunities within your organisation.\n\nI am particularly looking for opportunities during the period from late November through December, and I will be available in Randburg, Johannesburg at that time.\n\nI have attached my CV, Academic Transcript, and Reference Letter for your reference.\n\nThank you for your time and consideration.\n\nKind regards,\n{full_name}\n📞 {phone}\n✉️ {email}\nLinkedIn: {linkedin}"
}

def clean_salutation(name):
    if not name: return "Sir/Madam"
    return name.split()[0]

def get_template(industry_key):
    t = INDUSTRY_TEMPLATES.get(industry_key, DEFAULT_TEMPLATE)
    return t["subject"], t["body"]

def generate_email(contact, my_info, industry_key="engineering"):
    name = contact.get('contact_name', '').strip()
    name = clean_salutation(name)
    subject, body_template = get_template(industry_key)
    body = body_template.format(
        name=name,
        full_name=my_info.get('name', MY_NAME),
        phone=my_info.get('phone', MY_PHONE),
        email=my_info.get('email', MY_EMAIL),
        linkedin=my_info.get('linkedin', MY_LINKEDIN)
    )
    return subject, body

def generate_followup(contact, my_info, industry_key="engineering"):
    name = contact.get('contact_name', '').strip()
    name = clean_salutation(name)
    subject, _ = get_template(industry_key)
    followup_subject = f"Follow-up: {subject}"
    body = f"Dear {name},\n\nI hope you are well. I just wanted to follow up on my previous message regarding possible graduate, internship, or experiential training opportunities.\n\nI am particularly looking for opportunities during the period from late November through December, and I will be available in Randburg, Johannesburg at that time.\n\nKind regards,\n{MY_NAME}"
    return followup_subject, body
