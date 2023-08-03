from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import configparser
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

app = Flask(__name__)

pttWeb = 'https://www.pttweb.cc'

token = 'eCGdzlx7BTCyeIm4rC8yW6mk2u2m6uq0sLaDG4fRpEF'
groupToken = 'iFqDeL2KowA0n8CWH0VwFyqnEMUs3wQ3dObmrYkSZWs'
file = 'D:\\project\\linebot\\ptt\\articles.csv'

retentionDay = 3

def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + groupToken,
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code

if __name__ == "__main__":

    currentTimestamp = int(datetime.now().timestamp())

    newFileData = pd.DataFrame()

    # sendData = pd.read_csv(file).sort_values(by=['timestamp'])
    sendData = pd.read_csv(file)
    sendData.drop_duplicates(inplace=True)

    for index, row in sendData.iterrows():
        print(row['title'])

        if row['send'] == 'N':
            line = '\n' + row['title'] + '\n' + '(' + row['time'] + ')' + '\n' + row['link']
            lineNotifyMessage(token, line)

        else:
            if row['timestamp'] <= currentTimestamp - (retentionDay * 24 * 60 * 60):
                continue

        newFileLine = row['board'] + '\t' + row['title'] + '\t' + row['link'] + '\t' + row['time'] + '\t' + str(
            row['timestamp']) + '\t' + 'Y'
        lineList = newFileLine.split(',')
        newFileData = newFileData.append(pd.DataFrame([lineList]))


    if not newFileData.empty:
        newFileData.columns = ['board', 'title', 'link', 'time', 'timestamp', 'send']
        newFileData.to_csv(file, header=True, mode='w', index=False)


    # line notify
    # client id: 	xZ9CiFmCRpOqphasC3Hrmr
    # client secret: 	hvzGq0bo3Icz2wmrNszsHHF5OO9mrUKlf3I7hF7h5Yz
    # token: eCGdzlx7BTCyeIm4rC8yW6mk2u2m6uq0sLaDG4fRpEF