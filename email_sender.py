
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self):
        self.success = 0
        self.fail = 0
    
    def send_email(self, subject, body, from_email, to_email, pass_word, attachment_path):
        to_email = "tommy.chen@unicomnz.com"
        try:
            message = MIMEMultipart()
            message["Subject"] = subject
            message["From"] = from_email
            message["To"] = to_email
            email_content = """
                <html>
                <head><style>
            body {
                font-family: 'Roboto', sans-serif;
                font-weight: bold;
            }</style></head>
                    <body>
                    <pre>""" + body + """</pre>
                    </body>
                </html>
                """

            message.attach(MIMEText(email_content, "html"))

            if (attachment_path.strip() != ""):
                with open(attachment_path, "rb") as attachment:
                     # Add the attachment to the message
                    attachment_part = MIMEBase("application", "octet-stream")
                    attachment_part.set_payload(attachment.read())
                    encoders.encode_base64(attachment_part)
                    attachment_part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= 'attachment.xlsx'",
                    )
                message.attach(attachment_part)

            
            mailserver = smtplib.SMTP('smtp.office365.com', 587) 
            mailserver.set_debuglevel(1)
            mailserver.ehlo()
            mailserver.starttls()
            mailserver.ehlo()
            mailserver.login(from_email,pass_word)
            mailserver.sendmail(from_email,to_email,message.as_string())
            mailserver.quit()
            print(f"邮件给 {to_email} 发送成功\n\n\n")
            self.success += 1
            
        except Exception as e:
            print(f'给 {to_email} 的邮件发送失败: ', e)
            self.fail += 1
