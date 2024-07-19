import imaplib
import email
import os
from datetime import datetime
import configparser
import argparse

config = configparser.ConfigParser()

config.read('config.ini')

username = config.get('Credentials', 'username')
password = config.get('Credentials', 'password')
imap_url = config.get('Credentials', 'imap_url')
root_dir = config.get('Global', 'root_dir') if config.has_option('Global', 'root_dir') else './attachments'
from_filter = config.get('Filters', 'from').split(',') if config.has_option('Filters', 'from') else None
file_types_filter = config.get('Filters', 'file_types').split(',') if config.has_option('Filters', 'file_types') else None

parser = argparse.ArgumentParser(description="Get emails from a specific month and year")
parser.add_argument('--this-month', action='store_true', help='Get emails from the current month')
parser.add_argument('--last-month', action='store_true', help='Get emails from the last month')
parser.add_argument('--month', type=int, help='Get emails from a specific month')

args = parser.parse_args()

def get_month_year(args):
    now = datetime.now()

    if args.this_month:
        month = now.month
        year = now.year

    if args.last_month:
        month = now.month - 1 if now.month > 1 else 12
        year = now.year if now.month > 1 else now.year - 1

    if args.month:
        month = args.month
        year = now.year

    return month, year

def write_files_from_mail_query(mail, attachments_dir, query):
    result, data = mail.uid('search', None, query)

    for num in data[0].split():
        result, data = mail.uid('fetch', num, '(BODY.PEEK[])')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        for part in email_message.walk():
            
            if part.get_content_maintype() == "multipart":
                continue
            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            
            if filename is not None and any(filename.lower().endswith('.' + file_type) for file_type in file_types_filter):
                if bool(filename):
                    os.makedirs(attachments_dir, exist_ok=True)
                    filepath = os.path.join(attachments_dir, filename)
                    if not os.path.isfile(filepath):
                        print("writing: " + filepath)
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                    else:
                        print("skipping: " + filepath)



def execute_script():
    month,year = get_month_year(args)
    month_dir = datetime(year, month, 1).strftime("%m-%Y")

    print(f"Getting attachments from {month_dir}...")

    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(username, password)
    mail.select("inbox")

    # Get the first day of the month and the first day of the next month
    first_day = datetime(year, month, 1).strftime("%d-%b-%Y")

    if month == 12:
        last_day = datetime(year + 1, 1, 1).strftime("%d-%b-%Y")
    else:
        last_day = datetime(year, month + 1, 1).strftime("%d-%b-%Y")

    if from_filter:
        for email_address in from_filter:
            print(f"Getting emails from {email_address}...")
            attachments_dir = os.path.join(root_dir, month_dir, email_address)
            write_files_from_mail_query(mail, attachments_dir, f'(FROM "{email_address}" SINCE "{first_day}" BEFORE "{last_day}")')
    else:
        attachments_dir = os.path.join(root_dir, month_dir)
        write_files_from_mail_query(mail, attachments_dir, f'(SINCE "{first_day}" BEFORE "{last_day}")')

# Run the script
execute_script()