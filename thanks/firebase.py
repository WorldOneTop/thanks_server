from firebase_admin import messaging
from .models import Message
import requests
import json
import os

URL = 'https://fcm.googleapis.com/fcm/send'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(BASE_DIR+'/secrets.json', 'r') as f:
    jf = json.load(f)
    HEADER = {'Authorization': jf['firebaseKey'],'Content-Type': 'application/json; UTF-8'}
    
# 공지사항 알람 받으려면 "notice" 구독해야함

def sendNotice(_id, title, content, date):
    sendData = {
            'category': 'notice',
             'id':str(_id),
             'title':title,
             'body':content,
            'date' : date
        }
    sendMsg('/topics/notice', sendData)
    # message = messaging.Message(
    #     data=sendData,
    #     topic='notice',
    # )
    # response = messaging.send(message) # android
    
    # ios
    # content ={
    #     "to":"/topics/notice",
    #     "priority" : "high",
    #     "notification" : sendData,
    #     "data":sendData,
    #     "content_available" : True
    # }
    # push_req = requests.post(URL, data=json.dumps(content), headers=HEADER)
    
def readChat(users, senderId): # push를 받은 사람의 채팅방에 들어갔을 경우
    for token in users:
        sendMsg(token['token'], {
                'category': 'readChat',
                'senderId': str(senderId),
            })
        # message = messaging.Message(
        #     data={
        #         'category': 'readChat',
        #         'senderId': str(senderId),
        #     },
        #     token=token['token'],
        #     content_available = True
        # )
        # sendAndCatchErr(message,token['token'])

def sendChat(users,senderId, content, name,date): # push를 받은 사람한테 보내는거
    for user in users:
        sendMsg(user['token'], {'category': 'sendChat',
                 'senderId':senderId,
                 'content':content,
                 'senderName':name,
                 'date':date,
            })

        # message = messaging.Message(
        #     data={
        #         'category': 'sendChat',
        #          'senderId':senderId,
        #          'content':content,
        #          'senderName':name,
        #          'date':date,
        #     },
        #     token=user['token'],
        #     content_available = True
        # )
        # sendAndCatchErr(message,user['token'])
        
def sendReject(users, term, isMentor, title, content):
    for user in users:
        sendMsg(user['token'], {
                'category': 'mentoringReject',
                'title':title,
                'content':content,
                'term':str(term),
                'isMentor': "1" if isMentor else "0",
            })

        # message = messaging.Message(
        #     data={
        #         'category': 'mentoringReject',
        #         'title':title,
        #         'content':content,
        #         'term':str(term),
        #         'isMentor': "1" if isMentor else "0",
        #     },
        #     token=user['token'],
        #     content_available = True
        # )
        # sendAndCatchErr(message,user['token'])
        
def sendAccept(users, isMentor, title, status):
    for user in users:
        sendMsg(user['token'], {
                'category': 'mentoringAccept',
                'title':title,
                'userStatus':str(status),
                'isMentor': "1" if isMentor else "0",
            })
        # message = messaging.Message(
        #     data={
        #         'category': 'mentoringAccept',
        #         'title':title,
        #         'userStatus':str(status),
        #         'isMentor': "1" if isMentor else "0",
        #     },
        #     token=user['token'],
        #     content_available = True
        # )
        # sendAndCatchErr(message,user['token'])
        
    
def sendAndCatchErr(message, token):
    try:
        messaging.send(message)
        
    except messaging.UnregisteredError: # 유효하지 않은 토큰 https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging?hl=ko
        Message.objects.get(pk=token).delete()
    except:
        pass
        # Message.objects.get(pk=token).delete()

def sendMsg(to, data):
    try:
        content ={
            "to":to,
            "priority" : "high",
            "notification" : data,
            "data":data,
            "content_available" : True
        }
        push_req = requests.post(URL, data=json.dumps(content), headers=HEADER)
    except Exception as e:
        print(e)

    