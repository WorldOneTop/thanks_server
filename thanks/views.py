from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Mentor, Mentee, Telegram, Document, Comment, Like, Manager, Signup
import json

def index(request):
    return HttpResponse("hello world")

def createUser(request): # args : {userId: 8자리 숫자 }
    if('userId' not in request.GET):
        return HttpResponse('{"status":"not enough data"}')

    result = {'status' : checkUser(**(request.GET.dict()))}
    
    if(result['status'] != 'OK'):
        return HttpResponse(json.dumps(result, ensure_ascii=False))
    User.objects.create(pk=request.GET['userId'])
    
    return HttpResponse(json.dumps(result, ensure_ascii=False)) # return : {"status": OK or error msg}


def create5Thanks(request):# args : userId, data:'[{"title": ,"content": }]'
    try:
        data = json.loads(request.GET['data'])
        checkData = ""
        userId = User.objects.get(pk=request.GET['userId'])
        
        for val in data:
            checkData = checkDocument(**val)
            if(checkData != "OK"):
                return HttpResponse('{"status":"'+checkData+'"}')
            val['userId'] = userId
            val['docType'] = 1
        
        for val in data:
            Document.objects.create(**val)
        
    except ValueError:
        return HttpResponse('{"status":"data json decode error"}')
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    return HttpResponse('{"status":"OK"}')

def create1Kind(request):# args : userId, title, content, fileUrl
    try:
        data = request.GET.dict()
        catchError = checkDocument(**data)
        
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        data['userId'] = User.objects.get(pk=data['userId'])
        data['title'], data['content'], data['fileUrl'] # required args
        
        data['docType'] = 2
        Document.objects.create(**data)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    return HttpResponse('{"status":"OK"}')

def create1Book(request):# args : userId, title, content
    try:
        data = request.GET.dict()
        catchError = checkDocument(**data)
        
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        data['userId'] = User.objects.get(pk=data['userId'])
        data['title'], data['content'] # required args
        
        data['docType'] = 3
        Document.objects.create(**data)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    return HttpResponse('{"status":"OK"}')

def create1Save(request):# args : userId, title, content
    try:
        data = request.GET.dict()
        catchError = checkDocument(**data)
        
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        data['userId'] = User.objects.get(pk=data['userId'])
        data['title'], data['content'] # required args
        
        data['docType'] = 4
        Document.objects.create(**data)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    return HttpResponse('{"status":"OK"}')

def createContest(request):# args : userId, title, content
    try:
        data = request.GET.dict()
        catchError = checkDocument(**data)
        
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        data['userId'] = User.objects.get(pk=data['userId'])
        data['title'], data['content'] # required args
        
        data['docType'] = 5
        Document.objects.create(**data)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    return HttpResponse('{"status":"OK"}')

def updateDocument(request):
    return HttpResponse("hello world")

def deleteDocument(request):
    return HttpResponse("hello world")

def selectDocument(request):
    return HttpResponse("hello world")


def writeChat(request):
    return HttpResponse("hello world")

def selectChat(request):
    return HttpResponse("hello world")


def createSignup(request):
    return HttpResponse("hello world")




def checkUser(**kwargs):
    try:
        int(kwargs['userId'])
    except ValueError:
        return "student id is not int"
    if(len(kwargs['userId']) != 8):
        return "student id is not 8 letter"
    
    return "OK"

def checkDocument(**kwargs):
    if('docId' in kwargs and not kwargs['docId'].isdigit()):
        return "document id is not int"
    if('userId' in kwargs and not kwargs['userId'].isdigit()):
        return "user id is not int"
    if('category' in kwargs and len(kwargs['category']) > 20):
        return "category out of max length"
    if('year' in kwargs and not('2000' < kwargs['year'] and kwargs['year'] < '2100')):
        return "year out of range"
    if('month' in kwargs and not('1' <= kwargs['month'] and kwargs['month'] <= '12')):
        return "month out of range"
    if('day' in kwargs and not('1' <= kwargs['day'] and kwargs['day'] <= '31')):
        return "day out of range"
    if('content' in kwargs and not kwargs['content']):
        return "content is empty"
    if('fileUrl' in kwargs and not kwargs['fileUrl']):
        return "file url is empty"
    if('title' in kwargs and not kwargs['title'] or 50 < len(kwargs['title'])):
        return "title is empty or to long"
    
    return "OK"
"""

자동승인? 
매칭된 멘티 확인
매칭된 멘토 매칭 여부 확인, 매칭된 멘티 확인
멘토멘티 승인
멘토멘티 매칭
"""