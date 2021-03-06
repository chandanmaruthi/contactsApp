import sys
from django.db import models




# Create your models here.
class UserIdentity(models.Model):
	slackUserID  = models.CharField(max_length=500)
	nAccessToken = models.CharField(max_length=500)
	first_name = models.CharField(max_length=500)
	last_name = models.CharField(max_length=500)
	age_range_min = models.CharField(max_length=500)
	gender = models.CharField(max_length=500)
	location = models.CharField(max_length=500)
	locale = models.CharField(max_length=500)
	timezone = models.CharField(max_length=500)
	birthday = models.CharField(max_length=500)
	hometown = models.CharField(max_length=500)
class Meta:
	app_label = 'curiousWorkbench'


class UserActions(models.Model):
	ID = models.IntegerField(primary_key=True)
	User_ID = models.CharField(max_length=100)
	Create_Date = models.DateTimeField(auto_now=True)
	Module_ID = models.IntegerField()
	Content_ID = models.IntegerField()
	Challenge_ID = models.IntegerField()
	Action = models.CharField(max_length=10)
	Shared_By = models.CharField(max_length=100)
	Team_ID =models.IntegerField()

#
# class Progress(models.Model):
# 	userID = models.CharField(max_length=500)
# 	contentID= models.CharField(max_length=500)
# 	SKILL_CODE= models.CharField(max_length=500)
# 	Status = models.CharField(max_length=500)
# 	StartDate = models.CharField(max_length=500)
# 	LastActivityDate = models.CharField(max_length=500)
# 	LastActivityUserID = models.CharField(max_length=500)
# 	ExpectedEndDate = models.CharField(max_length=500)
# 	Credits = models.IntegerField(default=0)
#
class UserSkillStatus(models.Model):
	userID = models.CharField(max_length=500)
	skill = models.CharField(max_length=500)
	points = models.CharField(max_length=500)
	LastActivityDate = models.DateTimeField(auto_now=True)
#
# class Skill(models.Model):
# 	skillCode = models.CharField(max_length=500)
# 	skillTitle = models.CharField(max_length=500)
# 	skillDescription = models.CharField(max_length=500)
# 	skillFlag = models.CharField(max_length=500)
# 	skillImage = models.CharField(max_length=500)
#
# class Certification(models.Model):
# 	ID = models.IntegerField(primary_key=True)
# 	Title = models.CharField(max_length=500)
# 	Description = models.CharField(max_length=500)
# 	Image = models.CharField(max_length=500)
# 	Module_ID = models.IntegerField()
#
# class UserCertification(models.Model):
# 	userID = models.CharField(max_length=500)
# 	Module_ID =  models.IntegerField()
# 	certificationID = models.CharField(max_length=500)
# 	date = models.DateTimeField(auto_now=True)
# 	Title = models.CharField(max_length=500)
# 	Author = models.CharField(max_length=500)
# 	AuthorURL = models.CharField(max_length=500)
# 	SKILL_CODE = models.CharField(max_length=500)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
class UserState(models.Model):
	UserID = models.CharField(primary_key=True, max_length=100)
	UserName = models.CharField(max_length=500)
	UserEmail = models.CharField(max_length=500)
	UserGender = models.CharField(max_length=500)
	UserCurrentState = models.CharField(max_length=500)
	UserLastAccessedTime = models.DateTimeField('date created')
	UserRole = models.CharField(max_length=500)
	UserCompany = models.CharField(max_length=500)
	Location_PIN = models.CharField(max_length=500)
	Current_Module_ID = models.IntegerField(null=True)
	UserStateDict = models.CharField(max_length=1000)
	Notify_Subscription = models.CharField(max_length=500, default='FALSE')
	Notify_Time = models.CharField(max_length=500)
	UserTimeZone = models.FloatField(default= -8.0)
	Org_ID = models.CharField(max_length=100)
	DM_ID = models.CharField(max_length=100)
	UserPhone= models.CharField(max_length=500)
	UserImageSmall= models.CharField(max_length=500)
	UserImageBig= models.CharField(max_length=500)
#
# class StateMachine(models.Model):
# 	Event_Code = models.CharField(max_length=100)
# 	SM_ID = models.AutoField(primary_key=True)
# 	ExpectedState = models.CharField(max_length=500)
# 	State = models.CharField(max_length=500)
# 	Expiry = models.CharField(max_length=500)
# 	Action_old = models.CharField(max_length=500)
# 	NextEvent = models.CharField(max_length=500)
# 	CallFunction = models.CharField(max_length=500)
# 	ParentSystem= models.CharField(max_length=500)
# 	MessageID_old =  models.CharField(max_length=500)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
# class MessageLibrary(models.Model):
# 	ID = models.AutoField(primary_key=True)
# 	Action_old = models.CharField(max_length=100)
# 	MsgOrder = models.IntegerField(null=False, default=0)
# 	MessageType = models.CharField(max_length=500)
# 	MessageText = models.CharField(max_length=500)
# 	MessageImage = models.CharField(max_length=500)
# 	MessageVideo = models.CharField(max_length=500)
# 	MessageButtons = models.CharField(max_length=500)
# 	MessageQuickReplies = models.CharField(max_length=500)
# 	EventID = models.IntegerField()
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
# #Role,Skill_ID,Location,CompanyClass,Skill,SKILL_CODE,Percentage,Enabled
# class RoleDemandInfo(models.Model):
# 	Role = models.CharField(max_length=500)
# 	ID = models.IntegerField(primary_key=True)
# 	Location = models.CharField(max_length=500)
# 	CompanyClass = models.CharField(max_length=500)
# 	Skill = models.CharField(max_length=500)
# 	SKILL_CODE = models.CharField(max_length=500)
# 	Percentage = models.CharField(max_length=500)
# 	Enabled = models.CharField(max_length=500)
# 	Demand_Count = models.IntegerField(null=False)
# 	World_Count = models.IntegerField(null=False)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
# class ContentLibrary(models.Model):
# 	ID = models.AutoField(primary_key=True)
# 	Module_ID =  models.IntegerField(null=True)
# 	Content_Order =  models.IntegerField(default=0)
# 	Message_Type = models.CharField(max_length=500, null=True)
# 	Text = models.CharField(max_length=500, null=True)
# 	Title = models.CharField(max_length=500, null=True)
# 	Subtitle = models.CharField(max_length=500, null=True)
# 	ImageURL = models.CharField(max_length=500,null=True )
# 	LinkURL	= models.CharField(max_length=500, null=True)
# 	Embed_ID = models.CharField(max_length=500, null=True)
# 	Type = models.CharField(max_length=500, null=True)
# 	# Skill = models.CharField(max_length=500, null=True)
# 	# Questions = models.CharField(max_length=500, null=True)
# 	# AnswerOptions = models.CharField(max_length=500, null=True)
# 	# RightAnswer = models.CharField(max_length=500, null=True)
# 	# Right_Ans_Response = models.CharField(max_length=500, null=True)
# 	# Wrong_Ans_Response = models.CharField(max_length=500, null=True)
# 	Rating = models.IntegerField(null=True, default=5)
# 	Tags = models.CharField(max_length=500, null=True)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
#
# class Module(models.Model):
# 	ID = models.AutoField(primary_key=True)
# 	Title = models.CharField(max_length=500)
# 	UserID = models.CharField(max_length=500)
# 	Description = models.CharField(max_length=500)
# 	Goal = models.CharField(max_length=500)
# 	Author = models.CharField(max_length=500)
# 	AuthorAffiliation = models.CharField(max_length=500)
# 	AuthorURL = models.CharField(max_length=500)
# 	Days = models.IntegerField(null=True)
# 	UnitsPerDay = models.IntegerField(null=True)
# 	Units = models.IntegerField(null=True)
# 	CertificateURL =  models.CharField(max_length=500)
# 	CertificateTest =models.BooleanField(default=False)
# 	Live = models.BooleanField(default=False)
# 	MinPoints = models.IntegerField(null=True)
# 	SKILL_CODE = models.CharField(max_length=500)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
# class UserModuleProgress(models.Model):
# 	ModuleID = models.IntegerField()
# 	UserID = models.CharField(max_length=500)
# 	CurrentPosition = models.IntegerField(null=True)
# 	Content_ID = models.IntegerField()
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
# class PlatformCredentials(models.Model):
# 	ID = models.AutoField(primary_key=True)
# 	SlackAccessToken = models.CharField(max_length=500, null=False)
# 	SlackScope = models.CharField(max_length=500, null=True)
# 	SlackTeamName = models.CharField(max_length=500, null=True)
# 	SlackTeamID = models.CharField(max_length=500, null=True)
# 	SlackBotUserID = models.CharField(max_length=500, null=True)
# 	SlackBotAccessToken = models.CharField(max_length=500, null=False)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
# class Challenge(models.Model):
# 	id = models.AutoField(primary_key=True)
# 	Content_ID = models.IntegerField(null=True)
# 	# Challenge_Text = models.CharField(max_length=500, null=True)
# 	# Challenge_Image = models.CharField(max_length=500, null=True)
# 	# Challenge_Video = models.CharField(max_length=500, null=True)
# 	Question_Text = models.CharField(max_length=500, null=False)
# 	Option_A = models.CharField(max_length=500, null=True)
# 	Option_B = models.CharField(max_length=500, null=True)
# 	Option_C = models.CharField(max_length=500, null=True)
# 	Option_D = models.CharField(max_length=500, null=True)
# 	Option_E = models.CharField(max_length=500, null=True)
# 	Correct_Answer = models.CharField(max_length=1, null=False)
# 	reg_date = models.DateTimeField(auto_now=True)
# 	UserID  = models.CharField(max_length=500)
# 	Tags = models.CharField(max_length=500, null=True)
# 	Module_ID = models.IntegerField(null=True)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
# class ChallengeResultSummary(models.Model):
# 	id = models.AutoField(primary_key=True)
# 	Challenge_ID = models.IntegerField(null=False)
# 	Option_A_Count = models.IntegerField(null=False, default = 0)
# 	Option_B_Count = models.IntegerField(null=False, default = 0)
# 	Option_C_Count = models.IntegerField(null=False, default = 0)
# 	Option_D_Count = models.IntegerField(null=False, default = 0)
# 	Option_E_Count = models.IntegerField(null=False, default = 0)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
# class ChallengeResultUser(models.Model):
# 	id = models.AutoField(primary_key=True)
# 	UserID = models.CharField(max_length=100,null=False)
# 	Challenge_ID = models.IntegerField(null=False)
# 	Ans  = models.CharField(max_length=1, null=False)
# 	IsCorrect  = models.CharField(max_length=1, null=False)
# 	TestedDate = models.DateTimeField(auto_now=True)
# 	CreatedUser = models.CharField(max_length=500)
# 	CreatedDate = models.DateTimeField(auto_now=True)
# 	LastUpdatedUser = models.CharField(max_length=500)
# 	LastUpdatedDate = models.DateTimeField(auto_now=True)
#
# class SignUp(models.Model):
# 	id = models.AutoField(primary_key=True)
# 	UserName = models.CharField(max_length=500)
# 	UserEmail = models.CharField(max_length=500)
# 	SignUpDate =  models.DateTimeField(auto_now=True)
# 	ApprovalDate =  models.DateTimeField(auto_now=True)
# 	Approved = models.CharField(max_length=500)
