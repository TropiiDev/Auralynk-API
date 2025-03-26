import os
from dotenv import load_dotenv
from mailersend import emails
from ..sql import *

load_dotenv()

mailer = emails.NewEmail(os.getenv("MAILERSEND_API_KEY"))

mail_body = {}

def send_welcome_email(email: str, name: str):
    recipients = [
        {
            "name": name,
            "email": email,
        }
    ]

    personalization = [
        {
            "email": email,
            "data": {
                "name": name,
                "account": {
                    "name": "Auralynk"
                }
            }
        }
    ]

    mailer.set_mail_to(recipients, mail_body)
    mailer.set_template("0r83ql3q7v04zw1j", mail_body)
    mailer.set_personalization(personalization, mail_body)

    mailer.send(mail_body)

    return True

def add_user_to_email_list(email: EmailTable, session: SessionDep):
    db_user = EmailList.model_validate(email)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user