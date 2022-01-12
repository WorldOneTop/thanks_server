from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Mentor, Mentee, Telegram, Document, Manager, Signup
import json
from django.db.models.functions import Cast
# from django.db.models import TextField,Value
from datetime import datetime
from django.core.exceptions import *
from django.shortcuts import render
from django.shortcuts import redirect

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def index(request):
    return HttpResponse("hello world")

def createUser(request): # args : {userId: 8자리 숫자, pw, name }
    try:
        catchError = checkUser(**(request.GET.dict()))
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        data = {'userId':request.GET['userId'], 'pw': request.GET['pw'], 'name':request.GET['name']}
        
        User.objects.create(**data)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    
    return HttpResponse('{"status":"OK"}')


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
def readLastChat(request): # args: user:["user id", ...], 
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

# 멘토 or 멘티 신청 
def createSignup(request): # args : userId, year,semester(0동계, 1 1학기, 2하계 , 3 2학기), userType(1:멘토,0:멘티)
    try:
        catchError = checkMen(**(request.GET.dict()))
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        user = User.objects.get(pk=request.GET['userId'])
        
        if(not user.activated):
            return HttpResponse('{"status":"user is not activated"}')
        if(user.userType != None):
            return HttpResponse('{"status":"user is already have type"}')
        if(len(Mentor.objects.filter(userId=request.GET['userId'],isMatched=None)) >= 1 
           or len(Mentee.objects.filter(userId=request.GET['userId'],activated=False)) >= 1):
            return HttpResponse('{"status":"user is already submit"}')
            
        data = {'userId':user,"year":request.GET['year'],"semester":request.GET['semester']}
        
        if(request.GET['userType'] == '1'):
            Mentor.objects.create(**data)
        elif(request.GET['userType'] == '0'):
            Mentee.objects.create(**data)
            
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    return HttpResponse('{"status":"OK"}')

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

"""        ADMIN        """
def admin(request):
    if (not (request.session.get('id') or request.session.get('admin'))):
        return redirect('/login/');
    result = {}
    result['userCount'] = User.objects.filter(activated=False).count()
    result['mentorCount'] = Mentor.objects.filter(activated=False).count()
    result['menteeCount'] = Mentee.objects.filter(activated=False).count()
    result['matchedCount'] = (Mentee.objects.filter(activated=True, mentorId=None).count() 
                              + Mentor.objects.filter(activated=True, matchedNum__lte=5).count())
    
    return render(request, 'overview.html', result);

def signupList(request):
    if (not (request.session.get('id') or request.session.get('admin'))):
        return redirect('/login/');
    
    if('type' not in request.GET):
        result = {'type':'0'}
    else:
        result = {'type':request.GET['type']}
        
    if(request.GET['type'] == '0'): # 가입신청
        result['data'] = list(User.objects.filter(activated=False).values('userId','name','registerDate'))
    else:
        if(request.GET['type'] == '1'): # 멘토신청
            result['data'] = Mentor.objects.select_related().filter(activated=False).values('userId','userId__name','year','semester')
        elif(request.GET['type'] == '2'): # 멘티신청
            result['data'] = Mentee.objects.select_related().filter(activated=False).values('userId','userId__name','year','semester')
        elif(request.GET['type'] == '3'): # 멘티 멘티 매칭
            q1 = Mentor.objects.select_related().filter(
                activated=True, matchedNum__lte=5).values('userId','userId__name','year','semester','matchedNum')
            q2 = Mentee.objects.select_related().filter(
                activated=True,mentorId=None).values('userId','userId__name','year','semester')
            
            
            result['mentors'] = q1
            result['mentees'] = q2
        
        if(request.GET['type'] == '3'):
            semesterToStr(result['mentors'])
            semesterToStr(result['mentees'])
        else:
            semesterToStr(result['data'])
        
    return render(request, 'register.html', result)

def login(request):
    return render(request, 'login.html');

def semesterToStr(objects):
    for obj in objects:
        if(obj['semester'] == 0):
            obj['semester'] = '동계'
        elif(obj['semester'] == 1):
            obj['semester'] = '1학기'
        elif(obj['semester'] == 2):
            obj['semester'] = '하계'
        elif(obj['semester'] == 3):
            obj['semester'] = '2학기'
            
def checkLogin(request):
    try:
        if(Manager.objects.get(pk=request.POST['id']).pw == request.POST['pw']):
            request.session['id'] = request.POST['id']
            return redirect('/admin/');
    except Manager.DoesNotExist:
        pass
    except KeyError:
        pass
    
    with open(BASE_DIR+'/secrets.json', 'r') as f:
        jf = json.load(f)
    if(jf['adminId'] == request.POST['id']):
        if(jf['adminPw'] == request.POST['pw']):
            request.session['admin'] = True
            return redirect('/admin/');
        
    return HttpResponse("<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');history.back();</script>")

# 가입 or 멘토 or 멘티 승인 (signupType 0, 1, 2)
def acceptSignup(request): # args : signupType, userId (없으면 전부다 승인)
    if(request.GET['signupType'] == '0'): #가입
        if('userId' not in request.GET):
            users = User.objects.filter(activated=False)
        else:
            users = User.objects.filter(pk=request.GET['userId'])    
            
        for user in users:
            user.activated = True
            user.save()

    elif(request.GET['signupType'] == '1'): # 멘토
        if('userId' not in request.GET):
            users = Mentor.objects.filter(activated=False)
        else:
            users = Mentor.objects.filter(userId=request.GET['userId'])
            
        for user in users:
            user.activated = True
            user.save()
            user.userId.userType = True
            user.userId.save()
    elif(request.GET['signupType'] == '2'): # 멘티 
        if('userId' not in request.GET):
            users = Mentee.objects.filter(activated=False) 
        else:
            users = Mentee.objects.filter(userId=request.GET['userId'])
            
        for user in users:
            user.activated = True
            user.save()
            user.userId.userType = False
            user.userId.save()
            
    elif(request.GET['signupType'] == '3'): # 매칭?
        if('userId' not in request.GET):
            pass
        else:
            pass
        
    return HttpResponse("<script>alert('승인되었습니다.');location.href = document.referrer;</script>")

# 가입 or 멘토 or 멘티 거절
def acceptReject(request): # args : signupType, userId, reason
    return HttpResponse("")

"""        check data        """
def checkId(_id):
    return _id.isdigit() and len(_id) == 8

def checkUser(**kwargs):
    if('userId' in kwargs and not checkId(kwargs['userId'])):
        return "user id is not matched format"
    if('pw' in kwargs and not kwargs['pw'] or 20 < len(kwargs['pw'])):
        return "pw is empty or too long"
    if('name' in kwargs and not kwargs['name'] or 5 < len(kwargs['name'])):
        return "name is empty or too long"
    return "OK"

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
   
def checkMen(**kwargs):
    if('userId' in kwargs and not checkId(kwargs['userId'])):
        return "id is not matched format"
    if('mentorId' in kwargs and not checkId(kwargs['mentorId'])):
        return "mentor id is not matched format"
    if('userId' in kwargs and 'mentorId' in kwargs and kwargs['userId'] == kwargs['mentorId']):
        return "same mentor and mentee"
    if('year' in kwargs and not('2020' <= kwargs['year'] and kwargs['year'] < '2050' )):
        return "out of range year"
    if('semester' in kwargs and not('0' <= kwargs['semester'] and kwargs['semester'] < '4' )):
        return "out of range semester"
    if('userType' in kwargs and not('0' == kwargs['userType'] or kwargs['userType'] == '1' )):
        return "type is not matched format"
    
    return "OK"
   
    
"""
자동승인? 
매칭된 멘티 확인
매칭된 멘토 매칭 여부 확인, 매칭된 멘티 확인
멘토멘티 승인
멘토멘티 매칭
"""