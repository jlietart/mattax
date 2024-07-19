# MATTAX (Mail Attachment Extractor)

A script to extract email attachments from your inbox. Useful when you need to gather your bills or proof of purchase sent by email.

## Usage

Extract attachments from the current month

```
python mattax.py --this-month
```

Extract attachments from the previous month

```
python mattax.py --last-month
```

Extract from a specified month

```
python mattax.py --month=6
```

## Configure the script

```ini
[Global]
# If not specified, will be stored in "./attachments"
root_dir = "./mypath/to/store/attachments"

[Credentials]
username = myemail@gmail.com
# For gmail you have to use an app password (https://support.google.com/mail/answer/185833?hl=en)
password = youremailpassword
imap_url = imap.gmail.com

[Filters]
# If not specified, will fetch all emails in your inbox
from = bills@compta.fr,no_reply@provider.net
# If not specified, will fetch all attachments of your mails
filetype = pdf,png

```
