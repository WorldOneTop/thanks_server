from firebase_admin import messaging
# 공지사항 알람 받으려면 "notice" 구독해야함

def sendNotice(title, content, date):
    message = messaging.Message(
        data={
            'category': 'notice',
             'title':title,
             'body':content,
            'date' : date
        },
        notification=messaging.Notification(
             title=title,
             body=content,
         ),
        topic='notice',
    )
    response = messaging.send(message)
    
def send_to_firebase_cloud_messaging():
    # This registration token comes from the client FCM SDKs.
    registration_token = 'deWxx1ytQ2i4wUnZ-l6im2:APA91bG0nhfKfRuLc5nxZ9mSGQtEovHHM-2YkKTuKVu-E3bOGB0Hihf_tjZSo6zsGhhjrPoDa_ae2yg247q-_7idfGcbepSTF5qzqbrnSivVtnALJv_ZNOzvgiD1RtlpREKXpKjWl0U3'

    # See documentation on defining a message payload.
    message = messaging.Message(
    notification=messaging.Notification(
        title='안녕하세요 타이틀 입니다',
        body='안녕하세요 메세지 입니다',
    ),
    token=registration_token,
    )

    try:
        response = messaging.send(message)
        # Response is a message ID string.
        print('Successfully sent message:', response)
    except Exception as e:
        print('예외가 발생했습니다.', e)