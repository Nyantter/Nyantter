from email.mime.multipart import MIMEMultipart
from .data import DataHandler
import aiosmtplib

class MailSender():
    async def send(*, subject:str, to: str, attach: list):
        message: MIMEMultipart = MIMEMultipart()
        message["From"] = DataHandler.mail["address"]
        message["To"] = to
        message["Subject"] = subject
        for _ in attach:
            message.attach(_)

        await aiosmtplib.send(
            message,
            hostname=DataHandler.mail["host"],
            local_hostname=DataHandler.mail["host"],
            username=DataHandler.mail["username"],
            password=DataHandler.mail["password"],
            port=DataHandler.mail["port"]
        )