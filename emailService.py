import os
import smtplib


from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.message import EmailMessage


# Mail configs
sender = os.environ['SENDER']
recipient = os.environ['RECEIPIENT']
password = os.environ['PASSWORD']


def send_success_mail(app_name, img_file_path, base_url, img_text: str, img_before, matching_regex):
    # save image
    img_before.save(img_file_path)


    msg = MIMEMultipart('alternative')

    msg['Subject'] = f"{app_name}: Interessante Aktion"
    msg['From'] = sender
    msg['To'] = recipient

    regex_rules_msg = ''
    for mr in matching_regex:
        regex_rules_msg += f'<li>{mr}</li>'

    text = MIMEText(f"""
                    <div>
                        <h1> Interessante Aktion: </h1>
                        <a href="{base_url}">
                        <img src="cid:image1">
                        </a>
                    </div>
                    <br>
                    <br>
                    <div>
                        <h4> Folgende Regel(n) haben angeschlagen: </h4>
                            <ul>
                                {regex_rules_msg}
                            </ul>
                    </div>
                    <br>
                    <div>
                        <h4> Extrahierter Text: </h4>
                        <div style="background-color:#6C6C6C ; padding:10px; border-radius: 15px">
                            {img_text}
                        </div>
                    </div>
                    """, 'html')
    msg.attach(text)

    image = MIMEImage(open(img_file_path, 'rb').read())

    # Define the image's ID as referenced in the HTML body above
    image.add_header('Content-ID', '<image1>')
    msg.attach(image)


    smtp = smtplib.SMTP("smtp.office365.com", port=587)
    smtp.starttls()
    smtp.login(sender, password)
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()


def send_failed_mail(e, subject: str, app_name):
    email = EmailMessage()
    email["From"] = app_name
    email["To"] = recipient
    email["Subject"] = f'{app_name}: Exception occured - {subject}'
    email.set_content(e)

    smtp = smtplib.SMTP("smtp.office365.com", port=587)
    smtp.starttls()
    smtp.login(sender, password)
    smtp.sendmail(sender, recipient, email.as_string())
    smtp.quit()