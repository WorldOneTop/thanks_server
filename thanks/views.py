from django.shortcuts import render
from django.http import HttpResponse
from .models import User, Mentor, Mentee, Document, Manager, Signup, Term, Message, Notice
import json
from django.core.exceptions import *
from django.shortcuts import render
from django.shortcuts import redirect
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt 
from . import firebase
import os
from datetime import datetime
from django.db.models import Count
import random, string, hashlib # 토큰발행
from django.db import connections



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_MENTEE = 5

def index(request):
    return render(request, 'pre_register.html')

"""        FIREBASE    """
def onNewToken(request): # args : token=""    // 굳이 할필요 없음(로그인에서 처리)
    try:
        Message.objects.create(pk=request.GET['token'],userId=None)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    return HttpResponse('{"status":"OK"}')



"""        USER        """
def userLogin(request): # args : {userId, pw, token}
    try:
        # with connections['oracle_db'].cursor() as cursor:
        #     cursor.execute("select ILBAN.NF_USER_LOGIN('S','"+request.GET['userId']+"','"+request.GET['pw']+"') from dual;")
        #     if(cursor.fetchall()[0][0] != 'true'):
        #         return HttpResponse('{"status":"User does not find"}')

        user = User.objects.filter(pk=request.GET['userId'])

        # if(len(user) < 1):
        #     data = {'userId':id, 'name':' ',status:1}
        #     user =  User.objects.create(**data)
        # else:
        user = user[0]

        user.CSRF = createCSRF()
        user.save()

        token = Message.objects.get(pk=request.GET['token'])
        if(token.userId != user):
            token.userId = user

        token.registerDate = datetime.today()
        token.save()

    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except Message.DoesNotExist:
        Message.objects.create(pk=request.GET['token'], userId=user)

    return HttpResponse('{"status":"OK","userStatus":'+str(user.status)+',"CSRF":"'+user.CSRF+'"}') # return : status:OK userStatus:0, CSRF:asdf

def accountInfo(request): # args : userId, CSRF
    try:
        user = User.objects.get(pk=request.GET['userId'],CSRF=request.GET['CSRF'])
        result = {"id":user.userId,"name":user.name,"registerDate":str(user.registerDate)}
        result['documents'] = list(Document.objects.filter(userId=user).values('docType').annotate(count=Count('docType')))
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    result = json.dumps(result, ensure_ascii=False)
    return HttpResponse('{"status":"OK","data":'+result+'}') # "data":"[{"id": , "name": , "registerDate": , "documents": }]

"""        Term       """
def selectTerm(request): # args : activated(Boolean?(0, 1, False, True X))
    try:
        if("activated" in request.GET):
            result = list(Term.objects.filter(activated = request.GET['activated']).values('id','startDate','endDate','activated'))
        else:
            result = list(Term.objects.values('id','startDate','endDate','activated'))

        for r in result:
            r['startDate'] = str(r['startDate'])
            r['endDate'] = str(r['endDate'])
        
    except ValidationError:
        return HttpResponse('{"status":"date format not recognized"}')
    result = json.dumps(result, ensure_ascii=False)
    return HttpResponse('{"status":"OK","data":'+result+'}') # "data":[{"id": 0, "startDate": "", "endDate": "", "activated": null }]
    
# 멘토 or 멘티 신청 
def createSignup(request): # args : userId, term(기수), userType(1:멘토,0:멘티), CSRF
    try:
        catchError = checkMen(**(request.GET.dict()))
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        user = User.objects.get(pk=request.GET['userId'],CSRF=request.GET['CSRF'])
        
        if(user.status != 1):
            return HttpResponse('{"status":"user is already have type"}')
        if(request.GET['userType'] == '1' and 1 > len(Mentee.objects.filter(userId=request.GET['userId']))):
            return HttpResponse('{"status":"user have never been mentee"}') 
        
        term = Term.objects.get(pk=request.GET['term'])
        if(term.activated != False):
            return HttpResponse('{"status":"not recruitment term"}')
        
        data = {'userId':user,"term":term}
        
        if(request.GET['userType'] == '1'):
            Mentor.objects.create(**data)
            user.status = 2
            user.save()
        elif(request.GET['userType'] == '0'):
            Mentee.objects.create(**data)
            user.status = 3
            user.save()
            
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    except Term.DoesNotExist:
        return HttpResponse('{"status":"term does not exist"}')
    return HttpResponse('{"status":"OK"}')
    
"""        DOCUMENT        """

# type 별로 통합적으로 생성  1: 감사 2: 선행, 3: 독후감, 4: 절약, 5: 공모전

@csrf_exempt
def createDoc(request): # args : userId, docType, content(\n때매 POST방식으로), image?, CSRF  
    try:
        catchError = checkDocument(**(request.GET.dict()))
        if(catchError != "OK"):
            return HttpResponse('{"status":"'+catchError+'"}')
        
        data = {'userId':User.objects.get(pk=request.GET['userId'],CSRF=request.GET['CSRF']), 'docType': request.GET['docType'], 'content':request.POST['content']}
        
        if(data['docType'] == "2"):
            if('image' in request.FILES): 
                data['fileUrl'] = request.FILES['image']
                # return HttpResponse('{"status":"required fileUrl"}') # 여기 변경됨@@@@@@@@@@@@@@@@@ 처리 X
            
        obj = Document.objects.create(**data)
        result = {"docId":obj.docId, "content":obj.content, "docType":int(obj.docType), "registerDate": obj.registerDate.strftime("%Y-%m-%d"), "fileUrl": obj.fileUrl if obj.fileUrl else ""}
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    
    result = json.dumps(result, ensure_ascii=False)
    return HttpResponse('{"status":"OK","data":'+result+'}') # return {"status":"OK","data":{"docId": 0, "content": "", "docType": 0, "registerDate": "", "fileUrl": ""}}

def updateDocument(request): # args : docId, content, image?
    try:
        doc = Document.objects.get(pk=request.GET['docId'])
        
        if(doc.registerDate != datetime.now().strftime("%Y-%m-%d")):
            return HttpResponse('{"status":"not today"}')
        
        
        if('image' in request.FILES): 
            doc.fileUrl = request.FILES['image']
            
        doc.content = request.POST['content']
        doc.save()
        
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except Document.DoesNotExist:
        return HttpResponse('{"status":"document does not exist"}')
    
    result = json.dumps(result, ensure_ascii=False)
    return HttpResponse('{"status":"OK"}')

def selectDocument(request): # args : userId, date:yyyy-mm-dd
    try:
        year = request.GET['date'][0:4]
        month = request.GET['date'][5:7]
        result = list(Document.objects.filter(userId=request.GET['userId'], registerDate=request.GET['date'], docType__lt=3).values(
                'docId','docType','content','fileUrl'
        ))
        book =  list(Document.objects.filter(userId=request.GET['userId'],
                                        docType=3, registerDate__year=year, registerDate__month=month).values(
            'docId','docType','content','fileUrl'
        ))
        for b in book:
            result.append(b)
            
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except ValidationError:
        return HttpResponse('{"status":"date format not recognized"}')
    
    result = json.dumps(result, ensure_ascii=False)
    return HttpResponse('{"status":"OK","data":'+result+'}')# data: [{docId, docType, title, content, fileUrl}, ...] 

def deleteDocument(request): # args : docId
    try:
        doc = Document.objects.get(pk=request.GET['docId'])
        if(doc.registerDate != datetime.now().strftime("%Y-%m-%d")):
            return HttpResponse('{"status":"not today"}')
        
        doc.delete()
    except Document.DoesNotExist:
        return HttpResponse('{"status":"document does not exist"}')
    return HttpResponse('{"status":"OK"}')

def getMenteesDoc(request): # args : userId, date:yyyy-mm-dd, CSRF
    try:
        userId = User.objects.get(pk=request.GET['userId'],CSRF=request.GET['CSRF']).id
        mentorId = Mentor.objects.filter(userId=userId).exclude(term__activated=None).order_by("term__id").values("mentorId").last()
        if(mentorId==None):
            return HttpResponse('{"status":"mentor does not exist"}')
        
        result = list(Mentee.objects.filter(mentorId=mentorId['mentorId']).values("userId","userId__name","term"))
        
        for obj in result:
            obj['thanks'] = Document.objects.filter(registerDate=request.GET['date'], userId=obj['userId'],docType=0).count()
            obj['kind'] =  Document.objects.filter(registerDate=request.GET['date'], userId=obj['userId'],docType=1).count()
            obj['save'] =  Document.objects.filter(registerDate=request.GET['date'], userId=obj['userId'],docType=2).count()
            obj['book'] =  Document.objects.filter(registerDate=request.GET['date'], userId=obj['userId'],docType=3).count()

    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    except Term.DoesNotExist:
        return HttpResponse('{"status":"term does not exist"}')
    result = json.dumps(result, ensure_ascii=False)
    return HttpResponse('{"status":"OK","data":'+result+'}') # return {status, data : [{"userId":0,"userId__name":"","term":0,"thanks":0,"kind":0, "save":0, "book":0,}, ...]}

"""        NOTICE           """
def getNotice(request): # args : X , 성능 이슈 예상으로 최대 최근 100개항목만 가져옴
    result = list(Notice.objects.all().order_by('-id').values()[:100])
    for r in result:
        r['registerDate'] = str(r['registerDate'])
    result = json.dumps(result, ensure_ascii=False)
    return HttpResponse('{"status":"OK","data":'+result+'}') # return : ['title':'','content':'','registerDate':'']

"""        CHANTTING        """

def readChat(request): # args: senderId, receiverId, CSRF
    try:
        userId = User.objects.get(pk=request.GET['senderId'],CSRF=request.GET['CSRF']).id
        tokens = list(Message.objects.filter(userId=request.GET['receiverId']).values('token'))
        if(len(tokens)==0):
            return HttpResponse('{"status":"received user does not exist"}')
            
        firebase.readChat(tokens,userId)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"user does not exist"}')
    return HttpResponse('{"status":"OK"}')
    
@csrf_exempt    
def sendChat(request): # args: senderId, receiverId, content, CSRF
    try:
        userName = User.objects.get(pk=request.GET['senderId'],CSRF=request.GET['CSRF']).name
        users = list(Message.objects.filter(userId=request.GET['receiverId']).values('token'))
        date = datetime.now().strftime("%Y.%m.%d %H:%M")
        if(len(users)==0):
            return HttpResponse('{"status":"received user does not exist","date":"'+date+'"}')
        
        firebase.sendChat(users,request.GET['senderId'],request.POST['content'],userName,date)
    except KeyError:
        return HttpResponse('{"status":"not enough data"}')
    except User.DoesNotExist:
        return HttpResponse('{"status":"User does not exist"}')
    return HttpResponse('{"status":"OK","date":"'+date+'"}')
    
"""        ADMIN PAGE       """
def preRegisterUpload(request): # 파일 원형 : [["학번","학과","이름","전화번호","비밀번호"]]
    result = request.POST.dict()
    del result['csrfmiddlewaretoken']
    with open(BASE_DIR+'/waitSignup.json', 'r') as f:
        jf = json.load(f)
        
        for item in jf:
            if(item[0] == result['studentNumber']):
                return HttpResponse("<script>alert('등록이 완료된 사용자입니다.');history.back();</script>")
            
        jf.append(list(result.values()))
        with open(BASE_DIR+'/waitSignup.json', 'w') as outfile:
            json.dump(jf, outfile, indent=4, ensure_ascii=False)
    return HttpResponse("<script>alert('등록되었습니다.');history.back();</script>")

def admin(request):
    if (not (request.session.get('id') or request.session.get('admin'))):
        return redirect('/amdinLogin/');
    result = {}
    result['userCount'] = User.objects.filter(status=0).count()
    result['mentorCount'] = Mentor.objects.filter(activated=False).count()
    result['menteeCount'] = Mentee.objects.filter(activated=False).count()
    result['matchedCount'] = (Mentee.objects.filter(activated=True, mentorId=None,term__activated=False,).count() 
                              + Mentor.objects.filter(activated=True, matchedNum__lt=MAX_MENTEE,term__activated=False).count())
    result['managerLen'] = Manager.objects.all().count()
    result['termMax'] = Term.objects.all().count()
    result['studentLen'] = User.objects.all().count()
    result['noticeLen'] = Notice.objects.all().count()
    
    
    with open(BASE_DIR+'/waitSignup.json', 'r') as f:
        jf = json.load(f)
        result['waitSignup'] = jf
        result['waitSignupLen'] = len(jf) -1
    
    return render(request, 'overview.html', result);

def signupList(request):
    if (not (request.session.get('id') or request.session.get('admin'))):
        return redirect('/amdinLogin/');
    
    if('type' not in request.GET):
        result = {'type':'0'}
    else:
        result = {'type':request.GET['type']}
        
    if(result['type'] == '0'): # 가입신청
        result['data'] = list(User.objects.filter(status=0).values('userId','name','registerDate'))
    else:
        if(result['type'] == '1'): # 멘토신청
            result['data'] = Mentor.objects.select_related().filter(activated=False).values(
                'mentorId','userId','userId__name','term__year','term__semester','term__id')
        elif(result['type'] == '2'): # 멘티신청
            result['data'] = Mentee.objects.select_related().filter(activated=False).values(
                'menteeId','userId','userId__name','term__year','term__semester','term__id')
        elif(result['type'] == '3'): # 멘티 멘티 매칭
            q1 = Mentor.objects.select_related().filter(term__activated=False,activated=True,
                matchedNum__lt=MAX_MENTEE).values('userId','userId__name','term__year','term__semester','matchedNum','term__id','mentorId')
            q2 = Mentee.objects.select_related().filter(term__activated=False,
                activated=True,mentorId=None).values('userId','userId__name','term__year','term__semester','term__id','menteeId')
            
            result['mentors'] = q1
            result['mentees'] = q2
            result['currentTerm'] = ', '.join([str(d['id']) for d in Term.objects.filter(activated=False).values('id')])
            
    return render(request, 'register.html', result)

def management(request):
    if (not (request.session.get('id') or request.session.get('admin'))):
        return redirect('/amdinLogin/');
    
    if('type' not in request.GET):
        result = {'type':'0'}
    else:
        result = {'type':request.GET['type']}
    if(result['type'] == '2'):
        if(not request.session.get('admin')):
            return HttpResponse("<script>alert('관리자만 접근할 수 있습니다.');history.back();</script>")

    if(result['type'] == '0'):
        result['data'] = getUserData()
    elif(result['type'] == '1'):
        result['data'] = getTermDate()
        result['lastTerm'] = Term.objects.all().count()+1
    elif(result['type'] == '2'):
        result['data'] = list(Manager.objects.all().values('adminId'))
    elif(result['type'] == '3'):
        pass
    elif(result['type'] == '4'):
        result['data'] = list(Notice.objects.all().order_by('-id').values())
    
    return render(request, 'management.html', result)

def amdinLogin(request):
    return render(request, 'login.html')

def amdinLogout(request):
    request.session.flush()
    request.session.clear_expired()
    return render(request, 'login.html')


"""        ADMIN POPUP PAGE    """
def userDetail(request):
    uId = request.GET['id']
    user = statusToStr(User.objects.filter(pk=uId).values('userId','name','registerDate','status'))[0]
    
    if(user['status'] == 4):
        mentor = Mentor.objects.get(userId=uId, activated=True)
        user['term'] = mentor.term_id
        if(mentor.matchedNum == 0):
            user['add'] = {'none' : True}
        else:
            user['add'] = Mentee.objects.select_related('userId').filter(mentorId=mentor).values('userId_id','userId__name')
            
        
    elif(user['status'] == 5):
        mentee = Mentee.objects.select_related('mentorId').get(userId=uId, activated = True)
        user['term'] = mentee.term_id
        if(mentee.mentorId == None):
            user['add'] = {'none' : True}
        else:
            user['add'] = [{'userId_id':mentee.mentorId.userId_id, 'userId__name':mentee.mentorId.userId.name}]
            
    
    mentorRows = Mentee.objects.select_related().filter(
        mentorId__userId=uId, activated=None).values('term','userId','userId__name','term__startDate','term__endDate').order_by('term')
    
    mentors = []
    if(len(mentorRows) > 0):
        for row in mentorRows:
            if(not mentors):
                mentors = [row]
                mentors[0]['users'] = [{'id':mentors[0]['userId'],'name':mentors[0]['userId__name']}]
                continue
            if(row['term'] != mentors[-1]['term']):
                mentors.append(row)
                mentors[-1]['users'] = [{'id':mentors[-1]['userId'],'name':mentors[-1]['userId__name']}]
            else:
                mentors[-1]['users'].append({'id':row['userId'],'name':row['userId__name']})
    
    mentees = list(Mentee.objects.select_related().filter(
        userId=uId, activated=None).values('term','mentorId__userId','mentorId__userId__name','term__startDate','term__endDate').order_by('term'))
    
    sorted_profile = sorted(mentors+mentees, key = lambda item: item['term'])

    result = {'user':user,'portfolio':sorted_profile}
    
    
    return render(request, 'detail.html', result)

def adminSearch(request):
    result = request.GET.dict()
    if(request.GET['type'] == '1'): # 맨토를 검색
        result['myType'] = '멘티'
        result['yourType'] = '멘토'
        result['data'] = Mentor.objects.select_related('userId').filter(
            activated=True,matchedNum__lt=MAX_MENTEE,term=request.GET['term']).values(
            'mentorId','userId__name','userId','matchedNum')
    else:
        result['myType'] = '멘토'
        result['yourType'] = '멘티'
        result['data'] =  Mentee.objects.select_related('userId').filter(
            activated=True,mentorId=None,term=request.GET['term']).values(
            'menteeId','userId__name','userId')
    
    return render(request, 'search.html',result)

"""        ADMIN FORM ACTION    """

def appendNotice(request):
    data = {'title':request.POST['title'],'content':request.POST['content']}
    notice = Notice.objects.create(**data)
    firebase.sendNotice(data['title'],data['content'], str(notice.registerDate))
    return HttpResponse("<script>alert('등록 및 발송되었습니다.');location.href = document.referrer;</script>")

def removeNotice(request):
    Notice.objects.filter(pk=request.GET['id']).delete()
    return HttpResponse("<script>alert('삭제되었습니다.');location.href = document.referrer;</script>")

def appendTerm(request):
    data = request.POST.dict()
    data.pop('csrfmiddlewaretoken')
    Term.objects.create(**data)
    return HttpResponse("<script>alert('등록되었습니다.');location.href = document.referrer;</script>")

def updateTerm(request):
    if(request.POST['startDate'] >= request.POST['endDate'] ):
        return HttpResponse("<script>alert('종료일이 시작일보다 앞섭니다.');history.back();</script>")
    data = request.POST.dict()
    data.pop('csrfmiddlewaretoken')
    term = Term.objects.filter(pk=request.GET['id'])
    
    if(term[0].activated == False and data['activated'] == '1'): # 모집중 -> 활동중
        # 매칭이 되지 않은 승인된 멘토, 멘티들과 멘토, 멘티 대기자들 거절
        delMentor = Mentor.objects.filter(term=request.GET['id'], matchedNum=0)
        delMentee = Mentee.objects.filter(term=request.GET['id'], mentorId=None)
        title = request.GET['id']+ "기 멘토링 모집 종료"
        content = request.GET['id']+"기 멘토링 활동 시작까지 매칭이 되지 않아 신청이 거절되었습니다."
        for row in delMentor:
            users = list(Message.objects.filter(userId=row.userId).values('token'))
            firebase.sendReject(users, request.GET['id'], True, title, content)

            row.userId.status = 1
            row.userId.save()
        for row in delMentee:
            users = list(Message.objects.filter(userId=row.userId).values('token'))
            firebase.sendReject(users, request.GET['id'], True, title, content)

            row.userId.status = 1
            row.userId.save()
            
        delMentor.delete()
        delMentee.delete()
    
    
    elif(data['activated'] == '' and term[0].activated != None): # 활동 종료로 변경
        # 승인 안된 멘토, 멘티 대기자들 거절
        delMentor = Mentor.objects.filter(term=request.GET['id'], activated=False)
        delMentee = Mentee.objects.filter(term=request.GET['id'], activated=False)
        title = request.GET['id']+ "기 멘토링 모집 종료"
        content = request.GET['id']+"기 멘토링 모집 종료로 인하여 멘토링 신청이 거절되었습니다."
        for row in delMentor:
            users = list(Message.objects.filter(userId=request.GET['userId']).values('token'))
            firebase.sendReject(users, request.GET['id'], True, title, content)

            row.userId.status = 1
            row.userId.save()
        for row in delMentee:
            users = list(Message.objects.filter(userId=request.GET['userId']).values('token'))
            firebase.sendReject(users, request.GET['id'], True, title, content)

            row.userId.status = 1
            row.userId.save()
            
        delMentor.delete()
        delMentee.delete()
        
        
        # 멘토링과정 유저들 정상 상태로
        mentorRows = Mentor.objects.select_related('userId').filter(term=request.GET['id'])
        mentorRows.update(activated=None)
        for row in mentorRows:
            row.userId.status = 1
            row.userId.save()
            
        menteeRows = Mentee.objects.select_related('userId').filter(term=request.GET['id'])
        menteeRows.update(activated=None)
        for row in menteeRows:
            row.userId.status = 1
            row.userId.save()
    term.update(**data)
    return HttpResponse("<script>alert('수정되었습니다.');location.href = document.referrer;</script>")

def manager(request):
    if(request.GET['isCreate'] =='1'):
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')
        Manager.objects.create(**data)
        return HttpResponse("<script>alert('생성되었습니다.');location.href = document.referrer;</script>")
    else:
        Manager.objects.get(pk=request.GET['id']).delete()
        return HttpResponse("<script>alert('삭제되었습니다.');location.href = document.referrer;</script>")
    
def managerPw(request):
    if(request.session.get('admin')):
        with open(BASE_DIR+'/secrets.json', 'r') as f:
            jf = json.load(f)
        if(jf['adminPw'] != request.POST['oldPw']):
            return HttpResponse("<script>alert('비밀번호가 일치하지 않습니다.');location.href = document.referrer;</script>")
            
        jf['adminPw'] = request.POST['newPw']
        with open(BASE_DIR+'/secrets.json', 'w') as outfile:
            json.dump(jf, outfile, indent=4)
    else:
        try:
            manager = Manager.objects.get(pk=request.session['id'],pw=request.POST['oldPw'])
            manager.pw = request.POST['newPw']
            manager.save()
        except Manager.DoesNotExist:
            return HttpResponse("<script>alert('비밀번호가 일치하지 않습니다.');location.href = document.referrer;</script>")
    
    return HttpResponse("<script>alert('변경되었습니다.');location.href = document.referrer;</script>")

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
    if(request.GET['signupType'] == '1'): # 멘토
        if('userId' not in request.GET):
            users = Mentor.objects.filter(activated=False)
        else:
            users = Mentor.objects.filter(userId=request.GET['userId'])
            
        for user in users:
            user.activated = True
            user.save()
            user.userId.status = 4
            user.userId.save()
    elif(request.GET['signupType'] == '2'): # 멘티 
        if('userId' not in request.GET):
            users = Mentee.objects.filter(activated=False) 
        else:
            users = Mentee.objects.filter(userId=request.GET['userId'])
            
        for user in users:
            user.activated = True
            user.save()
            user.userId.status = 5
            user.userId.save()
    
    title = "감사 운동 멘토링의 "
    if(request.GET['signupType'] == '1'):
        title += "멘토"
    else:
        title += "멘티"
    title += "로 선발되었습니다."
    
    firebase.sendAccept(users, request.GET['signupType'] == '1', title)
        
    return HttpResponse("<script>alert('승인되었습니다.');location.href = document.referrer;</script>")

# 멘토 멘티 매칭
@transaction.atomic
def adminMatched(request):
    mentor = Mentor.objects.get(pk = request.GET['mentor'])
    mentor.matchedNum += 1
    mentor.save()
    
    mentee = Mentee.objects.get(pk = request.GET['mentee'])
    mentee.mentorId = mentor
    mentee.save()
    
    if(request.GET['close'] == '1'):
        return HttpResponse("<script>alert('승인되었습니다.');window.close();</script>")
    else:
        return HttpResponse("<script>alert('승인되었습니다.');" +
                            "var a = document.referrer.substr(0,document.referrer.length-1);"+
                            "location.href = a + (document.referrer[document.referrer.length-1]*1+1);</script>")

# 가입 or 멘토 or 멘티 거절
def acceptReject(request): 
    user = User.objects.get(pk=request.GET['userId'])
    user.status = 1
    user.save()
    
    users = list(Message.objects.filter(userId=request.GET['userId']).values('token'))
    title = request.GET['term']+"기 멘토링 "
    if(request.GET['type'] == 1):
        title += "멘토"
    elif(request.GET['type'] == 2):
        title += "멘티"
    title += " 승인이 거부되었습니다."

    firebase.sendReject(users, request.GET['term'], request.GET['type'] == 1, title, request.GET['reason'])
    
    if(request.GET['type'] == '1'): # 멘토 신청 거절
        Mentor.objects.get(pk=request.GET['menId']).delete()
    elif(request.GET['type'] == '2'): # 멘티 신청 거절
        Mentee.objects.get(pk=request.GET['menId']).delete()
        
    
    return HttpResponse("<script>alert('완료되었습니다.');location.href = document.referrer;</script>")



"""        ADMIN FUNCTION    """
def getUserData():
    q0 = statusToStr(list(User.objects.all().values('userId','name','registerDate','status')))
    # q1 = list(Mentor.objects.select_related().filter(activated=True, matchedNum=5).values(
    #     'userId','userId__name','term__year','term__semester','matchedNum','term__id','userId__registerDate'))
    # q2 = list(Mentee.objects.select_related().filter(activated=True).exclude(mentorId=None).values(
    #     'userId','userId__name','term__year','term__semester','term__id','userId__registerDate','mentorId__userId'))
            
    return q0 #+ q1 + q2

def getTermDate():
    result = Term.objects.all().order_by('-id').values()
    for obj in result:
        obj['mentorCount'] = Mentor.objects.filter(term = obj['id']).count()
        obj['menteeCount'] = Mentee.objects.filter(term = obj['id']).count()
        if(obj['activated'] == None):
            obj['activated'] = '활동 종료'
        elif(obj['activated']):
            obj['activated'] = '활동 중'
        else:
            obj['activated'] = '모집 중'
            
    return result

def statusToStr(objects):
    for obj in objects:
        if(obj['status']==0):
            obj['statusStr']= '가입 대기'
        elif(obj['status']==1):
            obj['statusStr']= '유저'
        elif(obj['status']==2):
            obj['statusStr']= '멘토 신청'
        elif(obj['status']==3):
            obj['statusStr']= '멘티 신청'
        elif(obj['status']==4):
            obj['statusStr']= '멘토'
        elif(obj['status']==5):
            obj['statusStr']= '멘티'
    return objects

def termToStr(objects):
    for obj in objects:
        if(obj['activated'] == None):
            obj['activated'] = '활동 종료'
        elif(obj['activated']):
            obj['activated'] = '활동 중'
        else:
            obj['activated'] = '모집 중'
    return objects


"""        functions        """
def createCSRF():
    randomStr = "".join([random.choice(string.ascii_letters+string.digits) for _ in range(10)])
    return hashlib.sha256(randomStr.encode()).hexdigest()
    
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
    if('docType' in kwargs and not('0' <= kwargs['docType'] and kwargs['docType'] <= '3')):
        return "document type is not matched format   docType:" + kwargs['docType']
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
    return "OK"

def checkMen(**kwargs):
    if('userId' in kwargs and not checkId(kwargs['userId'])):
        return "id is not matched format"
    if('mentorId' in kwargs and not checkId(kwargs['mentorId'])):
        return "mentor id is not matched format"
    if('userId' in kwargs and 'mentorId' in kwargs and kwargs['userId'] == kwargs['mentorId']):
        return "same mentor and mentee"
    if('term' in kwargs and not kwargs['term'].isdigit()):
        return "term is not matched format"
    if('userType' in kwargs and not('0' == kwargs['userType'] or kwargs['userType'] == '1' )):
        return "type is not matched format"
    
    return "OK"
   
    