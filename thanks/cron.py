# from flask import session
from .models import Message
import datetime

# def sessionClearExpired():
#     session.clear_expired()

def tokenClearExpired():
    before = (datetime.datetime.now() - datetime.timedelta(weeks=5)).date()
    Message.objects.filter(registerDate__lte = before).delete()

