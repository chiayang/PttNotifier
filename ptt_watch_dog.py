from __future__ import unicode_literals
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from datetime import datetime
import os

pttWeb = 'https://www.pttweb.cc'
# board = 'stock'
pttStock = pttWeb + '/bbs/Stock'

# boardList = ['Stock','Lifeismoney']
boardList = ['Lifeismoney']
goodCnt = 50

boardDict = {
    'Stock' : 30,
    'Lifeismoney' : 30,
    'creditcard' : 30
}

boardKeyWord = {
    'Lifeismoney' : ['foodpanda','food panda','ubereats','uber eats'],
    'soho' : ['徵才 python','徵才 前端','徵才 後端']
    # 'Gamesale' : ['售 健身環']
}

# searchGoonCntWeb = pttStock + "/search/s/" + str(goodCnt)

# articleClass = 'e7-right-top-container e7-no-outline-all-descendants'
# articleClass = 'e7-show-if-device-is-not-xs'
# articleClass = 'e7-grey-text'
articleClass = 'e7-right ml-2'
articleTitleClass = 'e7-show-if-device-is-not-xs'
articleTimeClass = 'e7-grey-text'

# timeClass = 'e7-grey-text'
# timeClass = 'e7-head-small'

timeClass = 'text-no-wrap'

articleLinkClass = 'text-no-wrap mr-4 text-no-wrap'

# ----------------------
#    subroutine
# ----------------------
def GetArticleId(css_class):
    global articleClass
    if(css_class != None):
        if articleClass in css_class:
            return css_class

def GetArticleTimeId(css_class):
    global articleClass
    if(css_class != None):
        if articleTimeClass in css_class:
            return css_class

def GetArticleTime(css_class):
    global timeClass
    if (css_class != None):
        if timeClass in css_class:
            return css_class

def GetPttArticles(web):
    result = pd.DataFrame()
    currentTimestamp = int(datetime.now().timestamp())
    checkHour = 1
    checkTimestamp = currentTimestamp - (checkHour * 60 * 60)

    res = requests.get(web, timeout=30)
    # soup = BeautifulSoup(res.text, 'lxml')
    soup = BeautifulSoup(res.text, 'html.parser')

    # header_info = soup.find_all(class_=GetArticleId)
    header_info = soup.find_all(class_=articleClass)

    articleList = []
    articleLinkList = []
    articleDatelist = []

    for item in header_info:
        allTimeText = item.find_all(class_=articleTimeClass)
        timeText = allTimeText[0].text
        timeText = timeText.replace(' ','')

        before = timeText.split(',')[0]
        date = timeText.split(',')[1]

        if re.search('分鐘', before):

            articleText = item.find_all(class_=articleTitleClass)
            articleList.append(articleText[0].text)

            articleLink = ''
            for link in item.find_all('a'):
                if re.search('/bbs/', link.get('href')):
                    articleLink = link.get('href')
            articleLinkList.append(articleLink)

            articleDatelist.append(date)


    # articleLinkList = []
    # articleTimelist = []
    # articleTimeStampList = []
    # links = soup.find_all('a', class_=articleLinkClass)
    # for link in links:
    #     articleLinkList.append(link.get('href'))

        # articleRes = requests.get(pttWeb + link.get('href'), timeout=30)
        #
        # articleSoup = BeautifulSoup(articleRes.text, 'html.parser')
        #
        # articleTexts = articleSoup.find_all(class_=GetArticleTime)
        #
        # for line in articleTexts:
        #     timeMatch = re.search('\(([0-9]{4}/[0-9]{2}/[0-9]{2}.+)\)', line.text)
        #     if timeMatch:
        #         timeText = timeMatch.group(1)
        #         articleTimelist.append(timeText)
        #         articleTimeStampList.append(int(datetime.strptime(timeText, '%Y/%m/%d %H:%M').timestamp()))
        #         continue

    # articleTimeBeforeList = []
    # articleTimelist = []
    # articleTimeStampList = []
    # times = soup.find_all(class_=GetArticleTime)
    # for time in times:
    #     timeText = time.text
    #     timeText = timeText.replace('\n','')
    #     timeText = timeText.replace(' ', '')
    #     print(timeText)
    # exit()
    #     if re.search('回應', time.text):
    #         continue
    #     if re.search('推文', time.text):
    #         continue
    #     if ',' not in time.text:
    #         continue
    #
    #     timeText = time.text.replace(", ", ",")
    #     print(timeText)
    #     articleTimeBeforeList.append(timeText.split(',')[0])  # 幾小時前
    #     articleTimelist.append(timeText.split(',')[1])  # 2020/07/26 15:15:20
    #     articleTimeStampList.append(int(datetime.strptime(timeText.split(',')[1], '%Y/%m/%d %H:%M').timestamp()))

    result['article'] = articleList
    result['link'] = articleLinkList
    result['date'] = articleDatelist
    # result['timestamp'] = articleTimeStampList
    # newResult = pd.DataFrame()
    # newResult = result[result['timestamp'] > checkTimestamp]
    # return newResult
    return result

def GetInsertData(df):
    global pttFile
    global insertDf

    existDf = pd.read_csv(pttFile)
    # existDf['key'] = existDf['board'] + ',' + existDf['article'] + ',' + existDf['link'] + ',' + existDf[
    #     'timestamp'].astype(str)
    existDf['key'] = existDf['board'] + ',' + existDf['article'] + ',' + existDf['link']

    for index, row in df.iterrows():
        articleLink = pttWeb + row['link']

        # check if exist
        # insertKey = board + "," + row['article'] + "," + articleLink + "," + str(row['timestamp'])
        insertKey = board + "," + row['article'] + "," + articleLink
        if insertKey in existDf['key'].values:
            continue
        if re.search('已刪文',row['article']):
            continue

        # insert data
        # insertLine = board + "," + row['article'] + "," + articleLink + "," + row['time'] + "," + str(
        #     row['timestamp']) + "," + "N"
        insertLine = board + "," + row['article'] + "," + articleLink + "," + "N"
        insertList = insertLine.split(',')
        insertDf = insertDf.append(pd.DataFrame([insertList]))

# ----------------------
#          main
# ----------------------
if __name__ == "__main__":

    pttFile = 'D:\\project\\linebot\\ptt\\articles.csv'
    insertDf = pd.DataFrame()

    for board in boardDict.keys():
        print(board)
        web = pttWeb + "/bbs/" + board + "/search/s/" + str(boardDict[board])
        print(web)
        df = GetPttArticles(web)
        print(df)
        GetInsertData(df)

        # existDf = pd.read_csv(pttFile)
        # existDf['key'] = existDf['board'] + ',' + existDf['article'] + ',' + existDf['link'] + ',' + existDf['timestamp'].astype(str)
        #
        # for index, row in df.iterrows():
        #     articleLink = pttWeb + row['link']
        #
        #     # check if exist
        #     insertKey = board + "," + row['article'] + "," + articleLink + "," + str(row['timestamp'])
        #     if insertKey in existDf['key'].values:
        #         continue
        #
        #     # insert data
        #     insertLine = board + "," + row['article'] + "," + articleLink + "," + row['time'] + "," + str(row['timestamp']) + "," + "N"
        #     insertList = insertLine.split(',')
        #     insertDf = insertDf.append(pd.DataFrame([insertList]))

    for board in boardKeyWord.keys():
        print(board)
        for keyWord in boardKeyWord[board]:
            keyWord = keyWord.replace(' ','%20')
            web = pttWeb + "/bbs/" + board + "/search/t/" + keyWord
            print(web)
            df = GetPttArticles(web)
            print(df)
            GetInsertData(df)

    insertDf.drop_duplicates()
    print(insertDf)
    insertDf.to_csv(pttFile, header=False, mode='a', index=False)

