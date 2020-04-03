#!/usr/bin/python
import requests
import re
from bs4 import BeautifulSoup


def analysisHtml(url):
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
    response = requests.get(url, headers=headers)
    content = response.content
    soup = BeautifulSoup(content, "html.parser", from_encoding="utf-8")
    return soup

def outWitTheMilk(soup):
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
        print(title)

        # 选项
        labels = question.find_all('label')
        for label in labels:
            option = label.get_text().strip()
            print(option)

        # 你的选项
        you_option = question.find('div').get_text().replace('\n','').strip()
        print(you_option)
        print('-'*40)


if __name__ == "__main__":
    # soup = analysisHtml('http://33.cxint.com/index/exam/show/id/94.html')
    soup = analysisHtml('http://33.cxint.com/index/exam/show/id/93.html')
    outWitTheMilk(soup)