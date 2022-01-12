from django.db import models
from datetime import datetime

class User(models.Model):
    userId = models.PositiveIntegerField(primary_key=True) # 학번
    name = models.CharField(max_length=5)
    pw = models.CharField(max_length=20)
    userType = models.BooleanField(null=True) # true: 멘토, false: 멘티, null: 지정X
    registerDate = models.DateField(auto_now_add=True, auto_now=False)
    activated = models.BooleanField(default=False)
    
class Mentor(models.Model):
    mentorId = models.AutoField(primary_key=True)
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField() # 0동계, 1 1학기, 2하계 , 3 2학기
    activated = models.BooleanField(default=False)
    matchedNum = models.PositiveSmallIntegerField(default=0)
    
class Mentee(models.Model):
    menteeId = models.AutoField(primary_key=True)
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    mentorId =  models.ForeignKey("Mentor", on_delete=models.CASCADE, null=True)
    year = models.PositiveSmallIntegerField()
    semester = models.PositiveSmallIntegerField() # 0동계, 1 1학기, 2하계 , 3 2학기
    activated = models.BooleanField(default=False)
    
class Telegram(models.Model):
    telegramId = models.AutoField(primary_key=True)
    senderId = models.ForeignKey("User", on_delete=models.CASCADE, related_name="senderId")
    receiverId = models.ForeignKey("User", on_delete=models.CASCADE, related_name="receiverId")
    date = models.DateTimeField(auto_now_add=True, auto_now=False)
    read = models.BooleanField(default=False)
    content = models.CharField(max_length=100)

class Document(models.Model):
    docId = models.BigAutoField(primary_key=True)
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    registerDate = models.DateField(auto_now_add=True, auto_now=False)
    content = models.TextField()
    docType = models.PositiveSmallIntegerField() # 1: 5감사, 2: 선행, 3: 독후감, 4: 절약
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
    
# 멘토 멘티 신청 리스트 신청내역에 쓸 내용이 없다면 테이블 삭제 가능
class Signup(models.Model):
    userId = models.ForeignKey("User", on_delete=models.CASCADE)
    userType = models.BooleanField() # true: 멘토, false: 멘티
    content = models.CharField(max_length=100,null=True)

# 거절 사유
class Reject(models.Model):
    userId = models.PositiveIntegerField(primary_key=True) # 학번, fk아니라 별도 처리 필요
    reason = models.CharField(max_length=100)

"""
CREATE TABLE  User(
   studentId INT PRIMARY KEY, # 학번
   type BOOLEAN DEFAULT NULL, # true: 멘토, false: 멘티, null: 지정X
   registerDate DATE  DEFAULT NOW()
);
CREATE TABLE  Mentor(
   mentorId AUTO_INCREMENT PRIMARY KEY,
   userId INT NOT NULL,
   year SMALLINT NOT NULL,
   semester TINYINT(1) NOT NULL, # 0동계, 1 1학기, 2하계 , 3 2학기

   FOREIGN KEY (userId)
   REFERENCES User(studentId) ON DELETE CASCADE
);
CREATE TABLE  Mentee(
   menteeId AUTO_INCREMENT PRIMARY KEY,
   userId INT NOT NULL,
   mentorId INT NOT NULL,
   year SMALLINT NOT NULL,
   semester TINYINT(1) NOT NULL, # 0동계, 1 1학기, 2하계 , 3 2학기

   FOREIGN KEY (userId)
   REFERENCES User(userId) ON DELETE CASCADE
   FOREIGN KEY (mentorId)
   REFERENCES Mentor(mentorId) ON DELETE CASCADE
);
CREATE TABLE  Telegram(
   telegramId AUTO_INCREMENT PRIMARY KEY,
   senderId INT NOT NULL,
   receiverId INT NOT NULL,
   date DATE  DEFAULT NOW()
   read BOOLEAN DEFAULT FALSE,
   content VARCHAR(100) NOT NULL,

   FOREIGN KEY (senderId)
   REFERENCES User(studentId) ON DELETE CASCADE   
   FOREIGN KEY (receiverId)
   REFERENCES User(studentId) ON DELETE CASCADE         
);
CREATE TABLE Document (
   docId BIGINT AUTO_INCREMENT PRIMARY KEY,
   userId INT NOT NULL,
   category VARCHAR(20),
   year SMALLINT NOT NULL,
   month SMALLINT NOT NULL,
   day SMALLINT NOT NULL,
   registerDate DATE DEFAULT NOW(),
   editedDate DATE,
   content TEXT NOT NULL,
   fileUrl VARCHAR(50),
   title VARCHAR(50) NOT NULL

   FOREIGN KEY (userId)
   REFERENCES User(studentId) ON DELETE CASCADE
);
CREATE TABLE  Comment (
   commentId AUTO_INCREMENT PRIMARY KEY,
   docId BIGINT NOT NULL,
   userId INT NOT NULL
   registerDate DATE DEFAULT NOW(),
   editedDate DATE,
   comment VARCHAR(100)
   
   
   FOREIGN KEY (docId)
   REFERENCES Document(docId) ON DELETE CASCADE
   FOREIGN KEY (userId)
   REFERENCES User(studentId) ON DELETE CASCADE
);
CREATE TABLE  Like (
   likeId AUTO_INCREMENT PRIMARY KEY,
   docId BIGINT NOT NULL,
   userId INT NOT NULL,

   FOREIGN KEY (docId)
   REFERENCES Document(docId) ON DELETE CASCADE
   FOREIGN KEY (userId)
   REFERENCES User(studentId) ON DELETE CASCADE
);

CREATE TABLE  Manager (
   id VARCHAR(20) PRIMARY KEY,
   pw VARCHAR(20) 
);

# 신청 관리
CREATE TABLE  Signup(
   id AUTO_INCREMENT PRIMARY KEY,
   userId INT NOT NULL,
   type BOOLEAN NOT NULL, # true: 멘토, false: 멘티
   date DATE DEFAULT NOW(),
   content VARCHAR(100)

   FOREIGN KEY (userId)
   REFERENCES User(studentId) ON DELETE CASCADE
);
"""