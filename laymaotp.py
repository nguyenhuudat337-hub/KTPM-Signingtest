
import imaplib
import email
import re
from bs4 import BeautifulSoup


def get_otp(mail_name, pass_word):

    # Kết nối Gmail
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(mail_name, pass_word)

    # Chọn inbox
    mail.select("inbox")

    # Lấy danh sách email
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()

    # Duyệt từ mail mới nhất -> cũ hơn
    for email_id in reversed(email_ids):

        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]

        # Chuyển email thành object
        msg = email.message_from_bytes(raw_email)

        body = ""

        # Lấy nội dung mail
        if msg.is_multipart():

            for part in msg.walk():

                content_type = part.get_content_type()

                try:
                    payload = part.get_payload(decode=True)

                    if payload:

                        text = payload.decode(errors="ignore")

                        # Lấy cả plain text và html
                        if content_type in ["text/plain", "text/html"]:
                            body += text

                except:
                    pass

        else:

            try:
                body = msg.get_payload(decode=True).decode(errors="ignore")
            except:
                pass

        # Chuyển HTML -> text
        soup = BeautifulSoup(body, "html.parser")
        clean_text = soup.get_text()

        # Tìm OTP 6 số
        match = re.search(r"\b\d{6}\b", clean_text)

        if match:
            return match.group(0)

    return None


