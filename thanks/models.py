from django.db import models
from datetime import datetime

class User(models.Model):
    userId = models.PositiveIntegerField(primary_key=True) # 학번
    name = models.CharField(max_length=5)
    registerDate = models.DateField(auto_now_add=True, auto_now=False)
    status = models.PositiveSmallIntegerField(default=0) # 0:가입X, 1:가입만, 2:멘토 신청대기, 3:멘티 신청대기, 4: 멘토, 5:멘티
    
class Mentor(models.Model):
    mentorId = models.AutoField(primary_key=True)
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    term = models.ForeignKey("Term", on_delete=models.CASCADE)
    activated = models.BooleanField(default=False,null=True) # false=신청대기, true=활동중(멘티없을수도), null=활동종료
    matchedNum = models.PositiveSmallIntegerField(default=0)
    
class Mentee(models.Model):
    menteeId = models.AutoField(primary_key=True)
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    term = models.ForeignKey("Term", on_delete=models.CASCADE)
    mentorId =  models.ForeignKey("Mentor", on_delete=models.CASCADE, null=True)
    activated = models.BooleanField(default=False,null=True)
    
class Telegram(models.Model):
    telegramId = models.BigAutoField(primary_key=True)
    senderId = models.ForeignKey("User", on_delete=models.CASCADE, related_name="senderId")
    receiverId = models.ForeignKey("User", on_delete=models.CASCADE, related_name="receiverId")
    date = models.DateTimeField(auto_now_add=True, auto_now=False)
    read = models.BooleanField(default=False)
    content = models.CharField(max_length=100)
    chatRoom = models.ForeignKey("ChatRoom", on_delete=models.CASCADE)

class ChatRoom(models.Model):
    userId1 = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user1")
    userId2 = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user2")


class Document(models.Model):
    docId = models.BigAutoField(primary_key=True)
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    registerDate = models.DateField(auto_now_add=True, auto_now=False)
    content = models.TextField()
    docType = models.PositiveSmallIntegerField() # 0:5감사, 1:절약, 2:선행, 3:독후감
    fileUrl = models.ImageField(upload_to="%Y-%m", null=True)

class Contest(models.Model):
    contentId = models.AutoField(primary_key=True)
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    registerDate = models.DateField(auto_now_add=True, auto_now=False)
    content = models.TextField()
    title = models.CharField(max_length=50)
    fileUrl = models.ImageField(upload_to="contest/", null=True)
    
class Manager(models.Model):
    adminId = models.CharField(max_length=20, primary_key=True)
    pw = models.CharField(max_length=20)

class Term(models.Model):# id가 기수
    year = models.PositiveSmallIntegerField()
    semester = models.CharField(max_length=5) # 동계, 1학기, 하계 , 2학기
    startDate = models.DateField(auto_now_add=False, auto_now=False)
    endDate = models.DateField(auto_now_add=False, auto_now=False)
    activated = models.BooleanField(default=False,null=True) # null:활동종료, false: 모집중, true: 활동중
    
    def save(self, *args, **kwargs):
        def save(self, *args, **kwargs):
            if not User.objects.count():
                self.id = 1
            else:
                self.id = User.objects.last().id + 1
    
        self.year = self.startDate[:4]
        super().save(*args, **kwargs)
    
# 멘토 멘티 신청 리스트 신청내역에 쓸 내용이 없다면 테이블 삭제 가능
class Signup(models.Model):
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    userType = models.BooleanField() # true: 멘토, false: 멘티
    content = models.CharField(max_length=100,null=True)

# 거절 사유
class Reject(models.Model):
    userId = models.PositiveIntegerField() # 학번, fk아니라 별도 처리 필요
    reason = models.CharField(max_length=100)
    
class Message(models.Model):
    token = models.CharField(primary_key=True, max_length=255)
    userId = models.ForeignKey("User", on_delete=models.CASCADE,null=True)
    registerDate = models.DateField(auto_now_add=True, auto_now=False)
    recvChat = models.BooleanField(default=False)
    recvNotice = models.BooleanField(default=False)
    recvDaily = models.BooleanField(default=False)
    
class Notice(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()
    registerDate = models.DateField(auto_now_add=True, auto_now=False)
