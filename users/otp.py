import random
import string
from django.core.mail import send_mail
from django.conf import settings


# OTP generation function
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))
    return otp


# Send OTP to user's email
def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}. It is valid for 5 minutes.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
