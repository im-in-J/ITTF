"""이메일 발송 도구 — Gmail SMTP"""

import os
import ssl
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


async def send_email(
    to: str | list[str],
    subject: str,
    html_body: str,
) -> dict:
    """Gmail SMTP로 이메일을 발송한다."""
    gmail_address = os.getenv("GMAIL_ADDRESS", "")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD", "")

    if not gmail_address or not gmail_password:
        return {"success": False, "error": "Gmail 설정이 없습니다. .env에 GMAIL_ADDRESS, GMAIL_APP_PASSWORD를 설정하세요."}

    recipients = to if isinstance(to, list) else [to]

    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_address
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=465,
            username=gmail_address,
            password=gmail_password,
            use_tls=True,
        )
        return {"success": True, "recipients": recipients}
    except Exception as e:
        return {"success": False, "error": str(e)}
