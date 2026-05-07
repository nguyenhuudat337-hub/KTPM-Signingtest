import imaplib
import email
import re
from email.header import decode_header
# Kết nối tới Gmail (Ví dụ)

def get_otp(mail_name, pass_word):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(mail_name, pass_word) # Sử dụng App Password

    mail.select("inbox")

    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    latest_email_id = email_ids[-1]

    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    # Decode subject
    subject_raw = msg["Subject"]
    decoded_subject = ""

    for part, encoding in decode_header(subject_raw):
        if isinstance(part, bytes):
            decoded_subject += part.decode(encoding or "utf-8", errors="ignore")
        else:
            decoded_subject += part

    # Lấy OTP
    match = re.search(r"\b\d{6}\b", decoded_subject)
    return int(match.group())
