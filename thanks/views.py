from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Mentor, Mentee, Telegram, Document, Manager, Signup
import json
from django.db.models.functions import Cast
from django.db.models import TextField
from datetime import datetime
from django.core.exceptions import *
from django.shortcuts import render


def index(request):
    return HttpResponse("hello world")
def admin(request):
    return render(request, 'admin.html');

def createUser(request): # args : {userId: 8자리 숫자 }
    if('userId' not in request.GET):
        return HttpResponse('{"status":"not enough data"}')
    
    if(not checkId(request.GET['userId'])):
        return HttpResponse('{"status":"user id is not matched format"}')
    
    User.objects.create(pk=request.GET['userId'])
    
    return HttpResponse('{"status":"OK"}') # return : {"status": OK or error msg}


def create5Thanks(request):# args : userId, data:'["content~", ...]'
    try:
        data = json.loads(request.GET['data'])
        checkData = ""
        userId = User.objects.get(pk=request.GET['userId'])
        inputData = [] # 필요한 인수만 넣기 위해서

        for val in data:
            if(not val):
                return HttpResponse('{"status":"content is empty"}')
            inputData.append({'userId':userId, 'docType':1, 'content':val})
        
        for val in inputData:
            print(val)
            Document.objects.create(**val)
        
    except ValueError:
        return HttpResponse('{"status":"data json decode error"}')
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    return HttpResponse('{"status":"OK"}')

# type 별로 통합적으로 생성  2: 선행, 3: 독후감, 4: 절약, 5: 공모전
def create1Doc(request): # agrgs : userId, docType, content, fileUrl?
    try:
        if(request.GET['docType'] == "1"):
            return HttpResponse('{"status":"not this url"}')
        
        catchError = checkDocument(**(request.GET.dict()))
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        data = {'userId':User.objects.get(pk=request.GET['userId']), 'docType': request.GET['docType'], 'content':request.GET['content']}
        
        if(data['docType'] == "2"):
            if(not 'fileUrl' in request.GET):
                return HttpResponse('{"status":"required fileUrl"}')
            data['fileUrl'] = request.GET['fileUrl']
            
        Document.objects.create(**data)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    return HttpResponse('{"status":"OK"}')


def updateDocument(request):
    # obj = Document.objects.get(pk=8)
    # obj.registerDate = datetime(2022,1,7).date()
    # obj.save()
    return HttpResponse("hello world")

def deleteDocument(request):
    return HttpResponse("hello world")


def writeChat(request): # args :  senderId, receiverId, content
    try:
        catchError = checkChat(**(request.GET.dict()))
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        data = {'content':request.GET['content']}
        data['senderId'] = User.objects.get(pk=request.GET['senderId'])
        data['receiverId'] = User.objects.get(pk=request.GET['receiverId'])
        
        
        Telegram.objects.create(**data)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    return HttpResponse('{"status":"OK"}')

# 채팅방 들어갔을 때 그동안 기록 전부 담기? or 못받은 데이터만 하기? 
# 일단은 전부 
# 후자는 폰에 데이터 저장 따로해서 처리 복잡하지만 서버부하줄이고 속도향상 기대
# 전자는 서버부하 가능성있지만 앱단에서 처리 쉬움
def readChat(request): # args : senderId, receiverId
    try:
        catchError = checkChat(**(request.GET.dict()))
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        
        
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    return HttpResponse('{"status":"OK"}')
# 마지막 대화와 안읽은 개수 확인
def readLastChat(request):
    try:
        catchError = checkChat(**(request.GET.dict()))
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        
        # annotate? -> count?
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    return HttpResponse('{"status":"OK"}')


def createSignup(request):
    return HttpResponse("hello world")


def selectDocument(request): # args : userId, date:yyyy-mm-dd
    try:
        yearMonth = request.GET['date'][0:8]
        result = list(Document.objects.filter(userId=User.objects.get(
            pk=request.GET['userId']), registerDate=request.GET['date'],
            docType__gte=1, docType__lt=5).exclude(docType=3).values(
                'docType','content','fileUrl'
        ))
        book =  Document.objects.filter(userId=User.objects.get(
            pk=request.GET['userId']), docType=3, registerDate__range=[(yearMonth+"01"), (yearMonth+"31")]).values(
            'docType','content','fileUrl'
        )
        if(len(book) == 1): # 한달에 한권만 등록
            result.append(book[0])
            
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except ValidationError:
        return HttpResponse('{"status":"date format not recognized"}')
    
    result = json.dumps(result, ensure_ascii=False)
    return HttpResponse('{"status":"OK","data":"'+result+'"}')# data: [{docType, title, content, fileUrl}, ...] 


def checkId(_id):
    return _id.isdigit() and len(_id) == 8

def checkDocument(**kwargs):
    if('docId' in kwargs and not kwargs['docId'].isdigit()):
        return "document id is not int"
    if('userId' in kwargs and not checkId(kwargs['userId'])):
        return "user id is not matched format"
    if('content' in kwargs and not kwargs['content']):
        return "content is empty"
    # if('fileUrl' in kwargs and not kwargs['fileUrl']): # 파일은 다른 처리 필요
    #     return "file url is empty"
    if('docType' in kwargs and not('1' <= kwargs['docType'] and kwargs['docType'] <= '5')):
        return "document type is not matched format"
    return "OK"

def checkChat(**kwargs):
    if('senderId' in kwargs and not checkId(kwargs['senderId'])):
        return "id is not matched format"
    if('receiverId' in kwargs and not checkId(kwargs['receiverId'])):
        return "id is not matched format"
    if('senderId' in kwargs and 'receiverId' in kwargs and kwargs['receiverId'] == kwargs['senderId']):
        return "same sender and reciver"
    if('content' in kwargs and not kwargs['content'] or 100 < len(kwargs['content'])):
        return "content is empty or too long"
    
"""
자동승인? 
매칭된 멘티 확인
매칭된 멘토 매칭 여부 확인, 매칭된 멘티 확인
멘토멘티 승인
멘토멘티 매칭
"""