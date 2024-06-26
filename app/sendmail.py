from email.mime.multipart import MIMEMultipart
from data import DataHandler
import aiosmtplib

class MailSender():
    async def send(*, message: str, to: str, attach: list):
        message: MIMEMultipart = MIMEMultipart()
        message["From"] = "nennneko5787+nyantter@gmail.com"
        message["To"] = to
        message["Subject"] = "Hello World!"
        for _ in attach:
            message.attach(_)

        await aiosmtplib.send(
            message,
            hostname=DataHandler.mail["hostname"],
            local_hostname=DataHandler.mail["hostname"],
            username=DataHandler.mail["username"],
            password=DataHandler.mail["password"],
            port=DataHandler.mail["port"]
        )