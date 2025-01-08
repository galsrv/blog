from os import getenv
from smtplib import SMTP

from django.core.mail import send_mail

def send_mail_smtplib():
    server = SMTP(
        getenv('SMTP_EMAIL_HOST'),
        getenv('SMTP_EMAIL_PORT'),
        timeout=getenv('EMAIL_TIMEOUT'),
        local_hostname='localhost')

    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(getenv('EMAIL_HOST_USER'), getenv('EMAIL_HOST_PASSWORD'))

    server.sendmail(
        msg='message',
        from_addr=getenv('EMAIL_HOST_USER'),
        to_addrs=[getenv('EMAIL_HOST_USER'), ],)

    server.quit()

def send_mail_django():    

    send_mail(
        subject='Subject here',
        message='Here is the message.',
        from_email=getenv('EMAIL_HOST_USER'),
        recipient_list=[getenv('EMAIL_HOST_USER'), ],
        fail_silently=False,
    )

