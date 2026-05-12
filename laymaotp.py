import imaplib
import email
import re
from email.header import decode_header


def get_otp(mail_name, pass_word):
    # Kết nối Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(mail_name, pass_word)

    # Chọn inbox
    mail.select("inbox")

    # Lấy danh sách email
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    # Không có email
    if not email_ids:
        return None

    # Lấy email mới nhất
    latest_email_id = email_ids[-1]

    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    raw_email = msg_data[0][1]

    # Chuyển thành object email
    msg = email.message_from_bytes(raw_email)

    # Nội dung email
    body = ""

    # Nếu email có nhiều phần
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Chỉ lấy text, bỏ file đính kèm
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True).decode()
                    break
                except:
                    pass
    else:
        # Email thường
        body = msg.get_payload(decode=True).decode()


    # Tìm OTP 6 số
    match = re.search(r"\b\d{6}\b", body)

    if match:
        return int(match.group())

    return None