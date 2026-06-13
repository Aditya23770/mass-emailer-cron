import pandas as pd
import yagmail
import time
import os
import re
import json
from datetime import datetime
import random as rd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)
except ImportError:
    pass


def load_config():
    config_path = os.path.join(BASE_DIR, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    cfg['gmail_address'] = os.environ.get('GMAIL_ADDRESS', '')
    cfg['gmail_app_password'] = os.environ.get('GMAIL_APP_PASSWORD', '')
    cfg['sender_name'] = os.environ.get('SENDER_NAME', 'Your Name')
    cfg['sender_phone'] = os.environ.get('SENDER_PHONE', '+91-XXXXXXXXXX')
    cfg['sender_linkedin'] = os.environ.get('SENDER_LINKEDIN', 'linkedin.com/in/your-profile')
    cfg['sender_github'] = os.environ.get('SENDER_GITHUB', 'github.com/YourUsername')
    if os.environ.get('RESUME_PATH'):
        cfg['pdf_attachment'] = os.environ.get('RESUME_PATH')
    return cfg


def load_contacts(cfg):
    csv_file = os.path.join(BASE_DIR, cfg['csv_file'])
    sent_file = os.path.join(BASE_DIR, cfg['sent_file'])
    try:
        df = pd.read_csv(csv_file).dropna(how='all')
        df = df.dropna(subset=['Name', 'Email', 'Company'])
        if os.path.exists(sent_file):
            sent_df = pd.read_csv(sent_file)
            df = df[~df['Email'].isin(sent_df['Email'])]
        return df
    except FileNotFoundError:
        print(f"Error: Contacts file not found at {csv_file}")
        return pd.DataFrame()


def save_sent_contacts(sent_emails, cfg):
    sent_file = os.path.join(BASE_DIR, cfg['sent_file'])
    if os.path.exists(sent_file):
        sent_df = pd.read_csv(sent_file)
        sent_df = pd.concat([sent_df, pd.DataFrame(sent_emails)], ignore_index=True)
    else:
        sent_df = pd.DataFrame(sent_emails)
    sent_df.drop_duplicates(subset=['Email'], inplace=True, keep='last')
    sent_df.to_csv(sent_file, index=False)


def load_templates(cfg):
    templates = []
    for name in cfg['template_files']:
        file_path = os.path.join(BASE_DIR, name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                templates.append(f.read())
        except FileNotFoundError:
            print(f"Warning: Template file not found at {file_path}. It will be skipped.")
    return templates


def log_email_result(email, name, company, result, cfg):
    log_file = os.path.join(BASE_DIR, cfg['log_file'])
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().isoformat()},{email},{name},{company},{result}\n")


def send_emails(num_to_send, delay_seconds):
    cfg = load_config()
    contacts = load_contacts(cfg)
    if contacts.empty:
        print('No new contacts to email.')
        return

    templates = load_templates(cfg)
    if not templates:
        print('No email templates found.')
        return

    yag = yagmail.SMTP(cfg['gmail_address'], cfg['gmail_app_password'])
    pdf_path = os.path.join(BASE_DIR, cfg['pdf_attachment'])
    attachment = pdf_path if os.path.exists(pdf_path) else None
    if not attachment:
        print(f"Warning: PDF not found at {pdf_path}. Sending without attachment.")
    sent_emails_log = []
    num_templates = len(templates)

    for count, (index, row) in enumerate(contacts.head(num_to_send).iterrows()):
        template_index = count % num_templates
        current_template = templates[template_index]
        print(f"--- Sending email {count + 1}/{num_to_send} (using template {template_index + 1}) ---")

        name = row['Name']
        email = row['Email']
        company = row['Company']
        body = current_template.format(
            name=name, company=company,
            sender_name=cfg['sender_name'], sender_phone=cfg['sender_phone'],
            sender_linkedin=cfg['sender_linkedin'], sender_github=cfg['sender_github'],
        )
        subjects = cfg.get('subjects', ['Application for AI/ML/Data Roles at {company}'])
        subject_template = subjects[template_index % len(subjects)]
        subject = subject_template.format(name=name, company=company)

        try:
            yag.send(to=email, subject=subject, contents=body, attachments=attachment)
            print(f"Sent to {name} <{email}>")
            result = 'Success'
            delivery_message = '250'
        except Exception as e:
            print(f"Failed to send to {email}: {e}")
            result = 'Failed'
            error_code_match = re.search(r'\b(\d{3})\b', str(e))
            delivery_message = error_code_match.group(1) if error_code_match else str(e)

        sent_emails_log.append({'Name': name, 'Email': email, 'Company': company, 'Log': result, 'Delivery Message': delivery_message})
        log_email_result(email, name, company, f"{result} - {delivery_message}", cfg)

        if count < num_to_send - 1:
            print(f'Waiting {delay_seconds} seconds...')
            time.sleep(delay_seconds)

    if sent_emails_log:
        save_sent_contacts(sent_emails_log, cfg)
    print("\nEmail sending run complete.")


def send_test_email(test_email, test_name='Test Person', test_company='Test Company', template_index=0):
    cfg = load_config()
    templates = load_templates(cfg)
    if not templates:
        print("No template files found. Cannot send a test email.")
        return

    if template_index < 0 or template_index >= len(templates):
        print(f"Invalid template index {template_index}, defaulting to 0.")
        template_index = 0

    template = templates[template_index]
    pdf_path = os.path.join(BASE_DIR, cfg['pdf_attachment'])
    attachment = pdf_path if os.path.exists(pdf_path) else None
    body = template.format(
        name=test_name, company=test_company,
        sender_name=cfg['sender_name'], sender_phone=cfg['sender_phone'],
        sender_linkedin=cfg['sender_linkedin'], sender_github=cfg['sender_github'],
    )
    subjects = cfg.get('subjects', ['Application for AI/ML/Data Roles at {company}'])
    subject_template = subjects[template_index % len(subjects)]
    subject = 'TEST: ' + subject_template.format(name=test_name, company=test_company)

    yag = yagmail.SMTP(cfg['gmail_address'], cfg['gmail_app_password'])
    try:
        yag.send(to=test_email, subject=subject, contents=body, attachments=attachment)
        print(f"Test email sent successfully to {test_email}")
        log_email_result(test_email, test_name, test_company, f"TEST - Success - 250", cfg)
    except Exception as e:
        print(f"Failed to send test email: {e}")
        log_email_result(test_email, test_name, test_company, f"TEST - Failed - {e}", cfg)


if __name__ == '__main__':
    try:
        test_mode = input('Test mode? (y/n): ').strip().lower() == 'y'

        if test_mode:
            cfg = load_config()
            test_contacts = cfg.get('test_contacts', [])
            if not test_contacts:
                print('No test contacts found in config.json.')
            else:
                print('Test contacts:')
                for i, c in enumerate(test_contacts, 1):
                    print(f"  {i}. {c['name']} <{c['email']}> — {c['company']}")
                raw = input(f'Pick contact(s) (e.g. 1 2 or "all"): ').strip().lower()
                if raw == 'all':
                    chosen = test_contacts
                else:
                    indices = [int(x) - 1 for x in raw.split()]
                    chosen = [test_contacts[i] for i in indices]
                num_templates = len(cfg.get('template_files', []))
                t_idx = int(input(f'Template (1-{num_templates}): ')) - 1
                for contact in chosen:
                    send_test_email(
                        test_email=contact['email'],
                        test_name=contact['name'],
                        test_company=contact['company'],
                        template_index=t_idx,
                    )
        else:
            num_to_send = int(input('How many emails to send? '))
            delay_seconds = int(input('Delay between each email (seconds)? '))
            send_emails(num_to_send, delay_seconds)

    except (ValueError, IndexError):
        print('Invalid input.')
