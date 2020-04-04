# -*- coding:utf-8 -*-
#!/usr/bin/python

logo ='''
 _                            _       
| |_ ___  ___ _ __  _   _  __| | __ _ 
| __/ _ \/ _ \ '_ \| | | |/ _` |/ _` |
| ||  __/  __/ | | | |_| | (_| | (_| |
 \__\___|\___|_| |_|\__, |\__,_|\__,_|
                    |___/             
'''

import requests
import re
from bs4 import BeautifulSoup
from http import cookiejar
import web

fileName = 'Marx.txt'
fileName2 = 'Engels.txt'

loginUrl = 'http://33.cxint.com/index/login/index.html'
couserUrl = 'http://33.cxint.com/index/exam/index.html'
host = 'http://33.cxint.com'
users = []

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'PHPSESSID=bhf0ojrfdqm7t8dj484e2uqoc6; UM_distinctid=171401722d741a-07e0b39f912b32-396b7f07-11cc40-171401722d8768; CNZZDATA1278517598=962657474-1585918190-null%7C1585918190',
    'Host': '33.cxint.com',
    'Referer': 'http://33.cxint.com/index/exam/lists/course_id/13.html',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}

# 请求路径
# 分别是首页,添加手机号,移除手机号
urls = (
    '/', 'index',
    '/(js|css|images)/(.*)', 'static',
    '/login', 'login',
    '/selectcouser', 'selectcouser',
    '/getPage', 'getpage',
    '/getAnswer', 'getanswer',
    '/fileDown', 'fileDown',
    '/getAllAnswer', 'getallanswer'
)
# web应用
app = web.application(urls, globals())
# templates模版文件夹
render = web.template.render('templates/')

# 首页：http://localhost:8080/index
class index(object):
    def GET(self):
        return render.index()

class login(object):
    def POST(self):
        user = web.input()
        print(user)
        username = user.username
        password = user.password
        message,result,sessionId = doLogin(username, password)
        if result:
            return sessionId
        else:
            raise MultipleChoices(message)

class selectcouser(object):
    def GET(self):
        param = web.input()
        sessionId = param.sessionId
        user = getUserBySessionId(sessionId)
        if user:
            cousers = user.cousers
            return render.couser(cousers)

class getpage(object):
    def GET(self):
        print('getPage')
        param = web.input()
        couserId = param.couserId
        sessionId = param.sessionId
        user = getUserBySessionId(sessionId)
        examLists(user, int(couserId))
        return render.examlist(user.exams)

class getanswer(object):
    def GET(self):
        param = web.input()
        examId = param.examId
        sessionId = param.sessionId
        user = getUserBySessionId(sessionId)
        success = answerList(user, int(examId))
        if success:
            # http://www.mamicode.com/info-detail-1185283.html
            web.header('Content-type','text/plain; charset=utf-8')
            web.header('Content-transfer-encoding','binary') 
            web.header('Content-Disposition', 'attachment; filename={}'.format(fileName))
            return open(fileName, 'rb').read()
        else:
            web.header('Content-type','text/plain; charset=utf-8')
            return '未作答!'


class getallanswer(object):
    def GET(self):
        param = web.input()
        sessionId = param.sessionId
        user = getUserBySessionId(sessionId)
        success = allAnswerList(user)
        if success:
            # http://www.mamicode.com/info-detail-1185283.html
            web.header('Content-type','text/plain; charset=utf-8')
            web.header('Content-transfer-encoding','binary') 
            web.header('Content-Disposition', 'attachment; filename={}'.format(fileName2))
            return open(fileName2, 'rb').read()
        else:
            web.header('Content-type','text/plain; charset=utf-8')
            return '未作答!'

# 500
class MultipleChoices(web.HTTPError):
    def __init__(self, msg):
        status = '500'
        headers = {'Content-Type': 'text/html'}
        web.HTTPError.__init__(self, status, headers, msg)

class fileDown():
    def GET(self):
        path = 'text.txt'
        web.header('Content-type','images/jpeg')
        web.header('Content-transfer-encoding','binary') 
        web.header('Content-Disposition', 'attachment; filename="马克思.txt"')
        return open(path, 'rb').read()

class User(object):
    username = ''
    password = ''
    sessionId = ''
    cookie = ''
    cousers = []
    exams = []
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cousers.clear()
        self.exams.clear()
    
class Couser(object):
    couserId = 0
    couserName = ''
    couserUrl = ''
    def __init__(self,couserId, couserName, couserUrl):
        self.couserId = couserId
        self.couserName = couserName
        self.couserUrl = couserUrl

class Exam(object):
    examId = 0
    title = ''
    examUrl = ''
    def __init__(self,examId, title, examUrl):
        self.examId = examId
        self.title = title
        self.examUrl = examUrl

def analysisHtml(url, user):
    headers['Cookie'] = user.cookie
    response = requests.get(url, headers=headers, timeout=5)
    content = response.content
    # print(content)
    soup = BeautifulSoup(content, "html.parser", from_encoding="utf-8")
    return soup

# chapter第几章
def outWitTheMilk(soup,chapter, f_w):
    unanswer = soup.find(id='submitQuestions')
    if unanswer:
        print('未作答')
        return False

    f_w.write(chapter + '\n')
    questions = soup.find_all(id=re.compile(r'question\d+'))
    # print(questions)
    for question in questions:
        # 题目question_title
        question_title_el = question.find(attrs={'class':'question_title'})
        # type = question_title_el.find('font').get_text()
        # number = question_title_el.find('strong').get_text()
        title = question_title_el.get_text().replace('\n', '')
        # print('number',number)
        # print('title', title)

        f_w.write(title + '\n')
        print(title)

        # 选项
        labels = question.find_all('label')
        for label in labels:
            option = label.get_text().strip()
            f_w.write(option + '\n')
            print(option)

        # 你的选项
        you_option = question.find('div').get_text().replace('\n','').strip()
        f_w.write(you_option + '\n')
        print(you_option)
        f_w.write('-'*40 + '\n')
        print('-'*40)
    
    return True

def doLogin(username,password):

    message = ''
    sessionId = None

    print('登陆')
    formData = {
        'username': username,
        'password': password
    }
    response = requests.post(loginUrl, data=formData)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    # find()将返回符合条件的第一个Tag
    login_error = soup.find(attrs={'class':'error'})
    
    if login_error:
        message = login_error.get_text()
        print(message)
        return message,False,sessionId
    else:
        login_success = soup.find(attrs={'class':'success'})
        user = User(username, password)
        if login_success:
            message = login_success.get_text()
            print(message)
            # 获取cookie
            cookies = requests.utils.dict_from_cookiejar(response.cookies)
            cookiesValue = ''
            for key in cookies.keys():
                cookiesValue += key + '=' + cookies.get(key) + ';'
                if key == 'PHPSESSID':
                    sessionId = user.sessionId = cookies.get(key)

            user.cookie = cookiesValue
            getCourse(user)
            users.append(user)
            return message,True,sessionId
            # getCourse()
        else:
            print('未知错误！')
            return '未知错误！请检查用户名', False,sessionId


# 选择课程
def getCourse(user):
    soup = analysisHtml(couserUrl, user)
    widgets = soup.find_all(attrs={'class': 'widget'})
    id = 0
    for widget in widgets:
        couserName = widget.find(attrs={'class': 'text-light'}).get_text()
        print('[{}]{}'.format(id, couserName))
        a = widget.find('a', href=True)
        url = host + a['href']
        couser = Couser(id, couserName, url)
        user.cousers.append(couser)
        id += 1

# 考试列表   
def examLists(user,couserId):
    couser = user.cousers[couserId]
    user.exams.clear()
    soup = analysisHtml(couser.couserUrl, user)
    titles = soup.find_all(attrs={'class': 'text-dark'})
    id = 0
    for title_elem in titles:
        title = title_elem.get_text()
        examUrl = host + title_elem['href']
        exam = Exam(id, title, examUrl)
        user.exams.append(exam)
        id += 1

def answerList(user, examId):
    exam = user.exams[examId]
    soup = analysisHtml(exam.examUrl, user)
    with open(fileName,"w",encoding="utf-8") as f_w:
        res = outWitTheMilk(soup, exam.title.strip(), f_w)
    return res

def allAnswerList(user):
    flag = False
    with open(fileName2,"w",encoding="utf-8") as f_w:
        for exam in user.exams:
            f_w.write('\n\n')
            soup = analysisHtml(exam.examUrl, user)
            res = outWitTheMilk(soup, exam.title.strip(), f_w)
            if res:
                flag = True
    return flag

def getUserBySessionId(sessionId):
    for user in users:
        if sessionId == user.sessionId:
            return user
    
    return None

if __name__ == "__main__":
    print(logo)
    app.run()