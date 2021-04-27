from django.shortcuts import render
from django.db import connection,transaction
from Database.forms import Assign_Course,Admin_Auth,Student_Auth,_ContactUs,\
    Teacher_Auth,Add_Course,Exams,_Mcqs,_StudentSubject
from Database.models import Admin,Student,Teacher,Courses,TeacherSubject,\
    Exam,ResultStudent,Mcqs,McqsChoice,Questions,ExamMcqs,\
        ExamMcqsChoice,ExamQuestions,StudentSubject,ResultStubject,\
            quiz_assignment_id,ExamStudentMcqs,ExamStudentAnswer,\
                ExamScanPaper,StudentAnswer,StudentMcqs
import re
from django.contrib import auth
from datetime import date
import uuid
from ocr.tesseract import ExtractText
import collections
from django.conf import settings
import json
import os


def validations(request):
    for i in request.POST:
        str=re.sub(r"[?|$|!|<|>|(|)|^|'|%]",'',request.POST[i])
        if not str == request.POST[i]:
            return False
    return True


''' Main Page '''

def Admin_Signup(request):
    form=Admin_Auth(request.POST)
    if validations(request):
        print(request.POST)
        if form.is_valid():
            form.save()
            return True
        else:
            return False
    else:
        return False


def Admin_Signin(request):
    user=Admin.objects.filter(email = request.POST["email"])
    if len(user) > 0:
        if(user[0].password == request.POST["password"]):
            return True
        else:
            return False
    else:
        return False


def contactus(request):
    c=_ContactUs(request.POST)
    if c.is_valid():
        c.save()


def Student_Signin(request):
    user=Student.objects.filter(regno = request.POST["regno"])
    if len(user) > 0:
        if(user[0].password == request.POST["password"]):
            return True
        else:
            return False
    else:
        return False


def Teacher_Signin(request):
    user=Teacher.objects.filter(email = request.POST["email"]);print(user,request)
    if len(user) > 0:
        if(user[0].password == request.POST["password"]):
            return True
        else:
            return False
    else:
        return False


def Teacher_Signup(request):
    form=Teacher_Auth(request.POST)
    print(request.POST)
    form.save()



def Students_Signup(request):
    form=Student_Auth(request.POST)
    print(request.POST)
    form.save()


def Get_Teachers():
    c= Teacher.objects.all()
    return c

def Get_Students():
    c= Student.objects.all()
    return c

def Delete_Teachers(request):
    c= Teacher.objects.filter(email=request.POST['email']).delete()
    return "Row Deleted where Email : "+ request.POST['email'];

def Update_Teachers(request):
    if validations(request):
        row=Teacher.objects.filter(email=request.POST['pk']).update(name=request.POST['name'],email=request.POST['email'],phonenumber=request.POST['phonenumber'],password=request.POST['password'])
        return "Row Update where Email : "+ request.POST['email'];
    else:
        return "Error"


'''Admin Student '''

def Delete_Student(request):
    c= Student.objects.filter(regno=request.POST['regno']).delete()
    return "Row Deleted where regno : "+ request.POST['regno'];

def Update_Student(request):
    if validations(request):
        row=Student.objects.filter(regno=request.POST['pk']).update(name=request.POST['name'],regno=request.POST['regno'],password=request.POST['password'])
        return "Row Update where regno : "+ request.POST['regno'];
    else:
        return "Error"




'''Admin Add Course'''

def Add_Courses(request):
    Course=Add_Course(request.POST)
    if Course.is_valid():
        Course.save()
        print("Course   <- Add")
    else:
        print("Course   <- Error")


def Ocr_Mode(request):
    f=open(settings.BASE_DIR+"\setting.json",'w')
    f.write("");f.close();os.remove(f.name);
    fw=open(settings.BASE_DIR+"\setting.json",'a+')

    if request.POST['data'] == "online":
        code={ "OCR_MODE" : "online" }
        fd=json.dumps(code);
        fw.write(fd)

    elif request.POST['data'] == "offline":
        code={ "OCR_MODE" : "offline" }
        fd=json.dumps(code);
        fw.write(fd)


def Get_Courses():
    c= Courses.objects.all()
    return c


def Delete_Courses(request):
    TeacherSubject.objects.filter(subject=request.POST['subject']).delete()
    Courses.objects.filter(subject=request.POST['subject']).delete()
    return "Delete Subject : "+ request.POST['subject'];



'''Admin Assign Course'''

def Assign_courses(request):
    c=Assign_Course(request.POST)
    print(c.is_valid())
    if c.is_valid():
        c.save()
    

def get_AssignCourses(*pk):
    if pk!=():
        c= TeacherSubject.objects.filter(email=pk)
    else:
        c= TeacherSubject.objects.filter()
    return c

def Delete_Assign_Course(request):
    c= TeacherSubject.objects.filter(email=request.POST['email'],subject=request.POST['subject']).delete()
    return "Row Deleted where regno : "+ request.POST['email'];



''' Admin Exams '''

def get_Exams(*request):
    c= Exam.objects.filter()
    return c

def merge(res,std):
    data=[];item=[]
    for i,k in zip(res,std):
        for j in i:
            item.append(j)
        for j in k:
            item.append(j)
        data.append(item)
        item=[]
    return data


def Get_Results():
    res=ResultStudent.objects.values_list();std=Student.objects.values_list()
    data=merge(res,std);print(data)
    return data


''' Data -> [[1, 'FA17-BCS-005', 4, 3, 'Hamza', 'FA17-BCS-005', 'admin',
datetime.date(2021, 1, 12)], [2, 'FA17-BCS-006', 4, 4, 'Hamza', 'FA17-BCS-006', 
'admin', datetime.date(2021, 1, 12)]]'''

def Read_Setting():
    f=open(settings.BASE_DIR+"\setting.json",'r')
    data=json.load(f);print(data)
    return data


def Dashboard():
    res=(ResultStudent.objects.values_list('regno').distinct().count())
    Data=[Student.objects.all().count(),Teacher.objects.all().count(),Courses.objects.all().count(),res,Read_Setting()];
    print(Data)
    return Data



'''_______________________________________Teacher__________________________________________________'''

def create_quiz_assignment_id():
    id=quiz_assignment_id.objects.order_by('-uniqueid')
    idlenght=len(id)

    if idlenght<=0:
        id=1
    else:
        id=id[0].uniqueid+1
    return id


def create_mcqs(request,email):
    _uuid=create_quiz_assignment_id();_email=Teacher.objects.filter(email=email)[0];_date=date.today()
    quiz_assignment_id(uniqueid=_uuid,email=_email,pdate=_date,req="mcqs").save()
    _uniqueid=quiz_assignment_id.objects.filter(uniqueid=_uuid)[0]

    items=len(request)-1;Course=request[items]['courses']
    data=request[:items]; _date=date.today()
    for i in data:
        mcqs=Mcqs(subject=Course,mquestion=i[0],manswer=i[2],point=i[3],mdate=_date,uniqueid=_uniqueid)
        mcqs.save();
        _mcqsChoice=McqsChoice(choice=i[1],mquestion=Mcqs.objects.filter(mquestion=i[0])[0])
        _mcqsChoice.save()
    print(data)



def create_subjective(request,email):
    items=len(request)-1;Course=request[items]['courses'];keywords=""
    _email=Teacher.objects.filter(email=email)[0]; _date=date.today()
    data=request[:items]; _quiz_data=[];_assignments_data=[]

    _uuid_quiz=create_quiz_assignment_id();
    quiz_assignment_id(uniqueid=_uuid_quiz,email=_email,pdate=_date,req="question").save()


    _uuid_assignment=create_quiz_assignment_id()
    quiz_assignment_id(uniqueid=_uuid_assignment,email=_email,pdate=_date,req="assignment").save()


    _unique_quiz_id=quiz_assignment_id.objects.filter(uniqueid=_uuid_quiz)[0]
    _unique_assignment_id=quiz_assignment_id.objects.filter(uniqueid=_uuid_assignment)[0]


    print(_unique_quiz_id)


    '''these two lines take that row that contain a list containing Assignment and put a true else false'''
    '''Second line we Combine two list and check if i is true then add to assignment list otherswise add to quiz list'''
    as_assignment_indexs=[ "Assignment" in  j  for j in (i for i in data)]
    [_assignments_data.append(j) if i else _quiz_data.append(j)  for i,j in zip(as_assignment_indexs , data) ]

    print("Assignments -> "+ str(_assignments_data))
    print("Quiz -> "+str(_quiz_data))


    for i in _quiz_data:
        for item in i[2].split(','): 
            if len(item)!=0: keywords =str(item)+","+keywords
        questions=Questions(subject=Course,question=i[0],keywords=keywords,answer=i[1],point=i[3],uniqueid=_unique_quiz_id)
        questions.save();keywords=""
    
    for i in _assignments_data:
        for item in i[2].split(','): 
            if len(item)!=0: keywords =str(item)+","+keywords
        questions=Questions(subject=Course,question=i[0],keywords=keywords,answer=i[1],point=i[3],uniqueid=_unique_assignment_id)
        questions.save();keywords=""



def generateid():
    Examid=Exam.objects.order_by('-examid')
    idlenght=len(Examid)
    
    if idlenght <= 0:
        Examid=1
    else:
        Examid=Examid[0].examid+1
    return Examid


def create_exam(request,email):

    _uuid=generateid();_email=Teacher.objects.filter(email=email)[0]
    Totaltime=request['Totaltime'];Starttime=request['Starttime'];Course=request['courses']
    _mcqs=request['mcqs'];_question=request['question'];_date=date.today()

    print("Exam ->>> ",email,_uuid,_date,Starttime,Totaltime)
    _exam=Exam(email=_email,examid=_uuid ,pdate=_date,ptime=Starttime,time_duration=Totaltime)
    _exam.save()

    for i in _mcqs:
        mcqs=ExamMcqs(Course,i[0],_uuid,i[2],i[3])
        mcqs.save()
        _mcqsChoice=ExamMcqsChoice(choice=i[1],mquestion=ExamMcqs.objects.filter(mquestion=i[0])[0] )
        _mcqsChoice.save()
    
    for i in _question:
        if i[4] =='Handwriten':
            mcqs=ExamQuestions(submit=0,subject=Course,question=i[0],keywords=i[2],examid=Exam.objects.filter(examid=_uuid)[0],answer=i[1],point=i[3])
        elif i[4] == 'Online':
            mcqs=ExamQuestions(submit=1,subject=Course,question=i[0],keywords=i[2],examid=Exam.objects.filter(examid=_uuid)[0],answer=i[1],point=i[3])        
        else:
            mcqs=ExamQuestions(submit=1,subject=Course,question=i[0],keywords=i[2],examid=Exam.objects.filter(examid=_uuid)[0],answer=i[1],point=i[3])        
        
        mcqs.save()

        print(Exam.objects.filter(examid=_uuid)[0])




'''----------------------------------------Students--------------------------------------------------'''

def get_mcqschoice(*pk):
    return ExamMcqsChoice.objects.filter(mquestion=pk).values()[0]

def get_mcqschoice_quiz(*pk):
    return McqsChoice.objects.filter(mquestion=pk).values()[0]


'''Return latest exam id'''
def get_examid(id): 
    for i in  Exam.objects.filter(examid=id).values():
        examid =ExamQuestions.objects.filter(examid=i['examid']).values()
        if len(examid) > 0:
            return i    


def get_quiz_question_id(id): 
    for i in  quiz_assignment_id.objects.filter(uniqueid=id).values():
        examid =Questions.objects.filter(uniqueid=i['uniqueid']).values()
        if len(examid) > 0:
            return i    

def get_quiz_mcqs_id(id): 
    for i in  quiz_assignment_id.objects.filter(uniqueid=id).values():
        examid =Mcqs.objects.filter(uniqueid=i['uniqueid']).values()
        if len(examid) > 0:
            return i    


def _get_mcqs(id):
    return Mcqs.objects.filter(uniqueid=id).values()

def _get_question(id):
    return Questions.objects.filter(uniqueid=id).values()


def Generate_Forms(examid,req):
    if req == "papers": 
        exam=get_examid(examid);Paper=[];Mcqs=[];Subjective=[];
        _subjective=ExamQuestions.objects.filter(examid=exam['examid']).values(); 
        _Mcqs=ExamMcqs.objects.filter(examid=exam['examid']).values()
        TeacherName=Teacher.objects.filter(email=exam['email_id'])[0].name
        
        if len(_Mcqs)>0:   
            for item in _Mcqs:
                ch=get_mcqschoice(item['mquestion'])["choice"].split(',')
                Paper.append({"mcqs":item["mquestion"],"type":"mcqs","choice1":ch[0],"choice2":ch[1],"choice3":ch[2],"point":item["point"]})
            Title=_Mcqs[0]["subject"]
        if len(_subjective)>0:
            for item in _subjective:
                Paper.append({"question":item["question"],"submit":item["submit"],"type":"subjective","point":item["point"]})
            Title=_subjective[0]["subject"]
        else:
            Title = ''
        return {"Paper":Paper,"title":Title,"TeacherName":TeacherName}

    elif req == "quiz" or req == "assignment":
        _mcqs_exam=get_quiz_mcqs_id(examid);_question_exam=get_quiz_question_id(examid)
        question_exam=create_quiz_assignment_id();mcqs_exam=create_quiz_assignment_id()
    

        if _mcqs_exam != None:
            mcqs_exam=_mcqs_exam
        else:
            mcqs_exam=''

        if _question_exam != None:
            question_exam=_question_exam
        else:
            question_exam=''
        

        if mcqs_exam !='':
            Paper=[];Mcqs=[];Subjective=[];print(mcqs_exam,question_exam)
            _Mcqs=_get_mcqs(mcqs_exam['uniqueid']);

            if len(_Mcqs)>0 and mcqs_exam['req']=="mcqs":
                TeacherName=Teacher.objects.filter(email=mcqs_exam['email_id'])[0].name   
                for item in _Mcqs:
                    ch=get_mcqschoice_quiz(item['mquestion'])["choice"].split(',')
                    Paper.append({"mcqs":item["mquestion"],"type":"mcqs","choice1":ch[0],"choice2":ch[1],"choice3":ch[2],"point":item["point"]})
                Title=_Mcqs[0]["subject"]
                print(Paper)
                return {"Paper":Paper,"title":Title,"TeacherName":TeacherName}
        
        if question_exam !='':
            Paper=[];Mcqs=[];Subjective=[];print(mcqs_exam,question_exam)
            _subjective=_get_question(question_exam['uniqueid']);
            if len(_subjective)>0:
                TeacherName=Teacher.objects.filter(email=question_exam['email_id'])[0].name   
                for item in _subjective: 
                    Paper.append({"question":item["question"],"submit":1,"type":"subjective","point":item["point"]})
                Title=_subjective[0]["subject"]
                return {"Paper":Paper,"title":Title,"TeacherName":TeacherName}






def student_assign_course():
    return( TeacherSubject.objects.all() )

def RegisterSubject(_regno):
    print(StudentSubject.objects.filter(regno=_regno))
    return StudentSubject.objects.filter(regno=_regno)

def get_student_courses():
    return StudentSubject.objects.order_by('regno').all()

def Assign_course_student(request):
    req=_StudentSubject(request.POST)
    if req.is_valid():
        req.save()
    return 'Course Assigned'

def get_teacher_subject():
    return TeacherSubject.objects.all()

def Delete_Student_Courses(request):
    req=(request.POST['delete']).split(',')
    StudentSubject.objects.filter(regno=req[0],subject=req[1]).delete()

def get_exam(_email,_subject,_name): 
    for i in  Exam.objects.filter(email=_email).order_by('-examid').values():
        examid =ExamQuestions.objects.filter(examid=i['examid'],subject=_subject).values()
        if len(examid) > 0:
            return {"examid":i['examid'],"PaperTime":i['time_duration'],"subject":_subject,"TeacherName":_name}    


def get_papers(_regno):
    _course=StudentSubject.objects.filter(regno=_regno);exam=[]
    for course in _course:
        _Teachers=TeacherSubject.objects.filter(subject=course.subject.subject).values('email','name')
        for i in  _Teachers:
            _exam=(get_exam(i['email'],course.subject.subject,i['name']))
            if _exam != None : 
                exam.append(_exam)
    print(exam)
    return exam


def get_quiz_assignment(_email,_subject,_name,req):
    for i in  quiz_assignment_id.objects.filter(email=_email).order_by('-uniqueid').values():
        if req == i['req']:
            examid =Questions.objects.filter(uniqueid=i['uniqueid'],subject=_subject).values()
            print(req)
            if len(examid) > 0:
                return {"examid":i['uniqueid'],"subject":_subject,"Pdate":i["pdate"],"TeacherName":_name}
        if req=='mcqs':
            if req==i['req']:
                examid =Mcqs.objects.filter(uniqueid=i['uniqueid'],subject=_subject).values()
                if len(examid) > 0:
                    return {"examid":i['uniqueid'],"subject":_subject,"Pdate":i["pdate"],"TeacherName":_name}


def Student_result_subject(_regno):
    return(ResultStubject.objects.filter(regno=_regno))


def student_quiz(_regno):
    _quiz=[]
    _course=StudentSubject.objects.filter(regno=_regno);exam=[]
    for course in _course:
        _Teachers=TeacherSubject.objects.filter(subject=course.subject.subject).values('email','name')
        for i in  _Teachers:
            quiz_id=(get_quiz_assignment(i['email'],course.subject.subject,i['name'],"question"))
            Mquiz_id=(get_quiz_assignment(i['email'],course.subject.subject,i['name'],"mcqs"))
            print(quiz_id,Mquiz_id)

            if quiz_id != None: 
                _quiz.append(quiz_id)
            if Mquiz_id != None: 
                _quiz.append(Mquiz_id)
                
    return _quiz
    


def student_assignments(_regno):
    _assignment=[]
    _course=StudentSubject.objects.filter(regno=_regno);exam=[]
    for course in _course:
        _Teachers=TeacherSubject.objects.filter(subject=course.subject.subject).values('email','name')
        for i in  _Teachers:
            assignment_id=(get_quiz_assignment(i['email'],course.subject.subject,i['name'],"assignment"))
            if assignment_id != None: 
                _assignment.append(assignment_id)
                
    print(_assignment)
    return _assignment
    

def _process_form(request,regno):
    __subjective_not_upload=[];_subjective_upload=[];req=request['req']
    [__subjective_not_upload.append(i) if i['type']=='type-not-upload' else _subjective_upload.append(i) for i in request['subjective']]
    _mcqs=request['mcqs'];_regno=Student.objects.filter(regno=regno)[0]
    
    _data=[]
    

    if req=="papers":
        _examid=Exam.objects.filter(examid=request['examid'])[0];

        for i in _mcqs:
            try:
                _mquestion=ExamMcqs.objects.filter(mquestion=i['question'])[0]
                exam_mcqs=ExamStudentMcqs(manswer=i['answer'],Examid=_examid,mquestion=_mquestion,regno=_regno)
                exam_mcqs.save()
            except:
                pass

        for i in __subjective_not_upload:
            try:
                _mquestion=ExamQuestions.objects.filter(question=i['question'])[0]
                exam_questions=ExamStudentAnswer(question=_mquestion,answer=i['answer'],Examid=_examid,regno=_regno)
                exam_questions.save()
                _data.append({"question":i['question'],"type":"upload_not_question","Student_answer":i['answer'],"keywords":_mquestion.keywords,"correct":_mquestion.answer})
            except:
                pass

        for i in _subjective_upload:
            try:
                img="\\media\\"+i['answer']
                _answer=(ExtractText("\\media\\"+i['answer']))
                _mquestion=ExamQuestions.objects.filter(question=i['question'])[0]
                ExamScanPaper(answer=_answer,examid=_examid,question=_mquestion,regno=_regno).save()
                _data.append({"question":i['question'],"type":"upload_question","Student_answer":_answer,"keywords":_mquestion.keywords,"correct":_mquestion.answer})
            except:
                return False

        ''' Calculate Paper '''
        Calculate_Papers(_examid,"paper")

    elif req=="quiz":
        _examid=quiz_assignment_id.objects.filter(uniqueid=request['examid'])[0]

        for i in _mcqs:
            _mquestion=Mcqs.objects.filter(mquestion=i['question'])[0]
            _mc=StudentMcqs(manswer=i['answer'],uniqueid=_examid,mquestion=_mquestion,regno=_regno).save()
        
        for i in __subjective_not_upload:
            _mquestion=Questions.objects.filter(question=i['question'])[0]
            _questions=StudentAnswer(question=_mquestion,answer=i['answer'],uniqueid=_examid,regno=_regno).save()
        
        Calculate_Papers(_examid,"quiz")



    elif req=='assignment':
        _examid=quiz_assignment_id.objects.filter(uniqueid=request['examid'])[0]
        for i in __subjective_not_upload:
            _mquestion=Questions.objects.filter(question=i['question'])[0]
            _questions=StudentAnswer(question=_mquestion,answer=i['answer'],uniqueid=_examid,regno=_regno).save()
        
        Calculate_Papers(_examid,"assignment")
    
    return True





def Calculate_Papers(_examid,req):
    mcqs=collections.defaultdict(str);
    subjective=collections.defaultdict(str);
    data=collections.defaultdict(str);

    if req=="paper":
        StdAns=ExamStudentAnswer.objects.filter(Examid=_examid).values()
        McqsAns=ExamStudentMcqs.objects.filter(Examid=_examid).values()
        ScanAnswers=ExamScanPaper.objects.filter(examid=_examid).values()
        
        for i in StdAns:
            question=ExamQuestions.objects.filter(question=i['question_id']).values('question','keywords','answer','point')[0]
            for key in question: subjective[str(key)]=str(question[key])
            subjective["Student_Answer"]=i['answer']
        
        for i in ScanAnswers:
            question=ExamQuestions.objects.filter(question=i['question_id']).values('question','keywords','answer','point')[0]
            for key in question: subjective[str(key)]=str(question[key])
            subjective["Student_Answer"]=i['answer']

        for i in McqsAns:
            question=ExamMcqs.objects.filter(mquestion=i['mquestion_id']).values('mquestion','manswer','point')[0]
            for key in question: mcqs[str(key)]=str(question[key])
            mcqs["Student_Answer"]=i['manswer']

        data["mcqs"]=mcqs;data["subjective"]=subjective;

        print(data)

    elif req ==  "quiz":
        sub_quiz=StudentAnswer.objects.filter(uniqueid=_examid).values()
        mcqs_quiz=StudentMcqs.objects.filter(uniqueid=_examid).values()
        
        for i in sub_quiz:
            question=Questions.objects.filter(question=i['question_id']).values('question','keywords','answer','point')[0]
            for key in question: subjective[str(key)]=str(question[key])
            subjective["Student_Answer"]=i['answer']

        for i in mcqs_quiz:
            _mquestion=Mcqs.objects.filter(mquestion=i['mquestion_id']).values('mquestion','manswer','point')[0]
            for key in _mquestion: mcqs[str(key)]=str(_mquestion[key])
            mcqs["Student_Answer"]=i['manswer']
        
        data["mcqs"]=mcqs; data["subjective"]=subjective;
        print(data)

    elif req ==  "assignment":
        assignment=StudentAnswer.objects.filter(uniqueid=_examid).values()
    
        for i in assignment:
            question=Questions.objects.filter(question=i['question_id']).values('question','keywords','answer','point')[0]
            for key in question: subjective[str(key)]=str(question[key])
            subjective["Student_Answer"]=i['answer']
            print(subjective)            
























