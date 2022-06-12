from firebase_admin import messaging
from .models import Message

# 공지사항 알람 받으려면 "notice" 구독해야함

def sendNotice(_id, title, content, date):
    message = messaging.Message(
        data={
            'category': 'notice',
             'id':str(_id),
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
                'senderId': str(senderId),
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
        
def sendReject(users, term, isMentor, title, content):
    for user in users:
        message = messaging.Message(
            data={
                'category': 'mentoringReject',
                'title':title,
                'content':content,
                'term':str(term),
                'isMentor': "1" if isMentor else "0",
            },
            token=user['token']
        )
        sendAndCatchErr(message,user['token'])
        
def sendAccept(users, isMentor, title, status):
    for user in users:
        message = messaging.Message(
            data={
                'category': 'mentoringAccept',
                'title':title,
                'userStatus':str(status),
                'isMentor': "1" if isMentor else "0",
            },
            token=user['token']
        )
        sendAndCatchErr(message,user['token'])
        
    
def sendAndCatchErr(message, token):
    try:
        messaging.send(message)
        
    except messaging.UnregisteredError: # 유효하지 않은 토큰 https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging?hl=ko
        Message.objects.get(pk=token).delete()
    except:
        pass
        # Message.objects.get(pk=token).delete()
