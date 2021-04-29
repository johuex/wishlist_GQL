import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import Config


class EmailHost:
    # set up the SMTP server
    s = smtplib.SMTP(host=Config.EMAIL_HOST, port=Config.EMAIL_PORT)
    s.starttls()
    s.login(Config.EMAIL_LOGIN, Config.EMAIL_PASSWORD)

    def read_template(self, filename):
        with open(filename, 'r', encoding='utf-8') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)

    def send_email(self, email_to, subject, user_name, template_path, code=None):
        msg = MIMEMultipart()  # create a message
        message_template = self.read_template(template_path)

        # add in the actual person name and code (for resetting password) to the message template
        if code is None:
            message = message_template.substitute(PERSON_NAME=user_name)
        else:
            message = message_template.substitute(PERSON_NAME=user_name, CODE=code)

        # setup the parameters of the message
        msg['From'] = Config.EMAIL_HOST
        msg['To'] = email_to
        msg['Subject'] = subject

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        self.s.send_message(msg)

        del msg


# e_host = EmailHost()
