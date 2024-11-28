from cloudinary import uploader

from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_confirm_code(email: str, username: str, code: str,):
    html_content = render_to_string('confirm_code.html', {
        'code': code,
        'name': username
    })

    email = EmailMessage(
        subject='Confirm code - LostMinerCommunity',
        body=html_content,
        from_email='noreplay-@lmc.com',
        to=[email]
    )

    email.content_subtype = 'html'
    email.send()


def upload_image(file, folder: str) -> str:
    upload_result = uploader.upload_image(file, folder=folder + '/')

    return upload_result.url
