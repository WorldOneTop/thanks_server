from firebase_admin import messaging
from .models import Message

# 공지사항 알람 받으려면 "notice" 구독해야함

def sendNotice(title, content, date):
    message = messaging.Message(
        data={
            'category': 'notice',
             'title':title,
             'body':content,
            'date' : date
        },
        topic='notice',
    )
    response = messaging.send(message)
    
def readChat(users, senderId): # push를 받은 사람의 채팅방에 들어갔을 경우
    for token in users:
        message = messaging.Message(
            data={
                'category': 'readChat',
                'senderId': senderId,
            },
            token=token['token']
        )
        sendAndCatchErr(message,token['token'])

def sendChat(users,senderId, content, name,date): # push를 받은 사람한테 보내는거
    for user in users:
        message = messaging.Message(
            data={
                'category': 'sendChat',
                 'senderId':senderId,
                 'content':content,
                 'senderName':name,
                 'date':date,
            },
            token=user['token']
        )
        sendAndCatchErr(message,user['token'])
    
def sendAndCatchErr(message, token):
    try:
        messaging.send(message)
        
    except messaging.UnregisteredError as e: # 유효하지 않은 토큰 https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging?hl=ko
        Message.objects.get(pk=token).delete()
