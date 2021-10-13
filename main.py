from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
import requests
import json
import re

SELECTOR = ['#postlist_block > div.list_block__WkcEG > div > div.list__fJdGM > ul > li:nth-child(', ') > div:nth-child(', ') > div:nth-child(2) > div > a']
HEADER = {"USER-AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.78"}

NUMBER_OF_ARTICLES = 62

with open('index.html', 'r', encoding='UTF-8') as f:
    rawIndexPage = f.read()

indexPage = BeautifulSoup(rawIndexPage, 'lxml')

totalStartTime = datetime.now()

targetList = OrderedDict()
serialCount = 1

for order in range(NUMBER_OF_ARTICLES, 0, -1):
    for row in range(2, 0, -1):
        startTime = datetime.now()

        targetSerial = str(serialCount).zfill(3)

        targetHtml = indexPage.select_one(SELECTOR[0] + str(order) + SELECTOR[1] + str(row) + SELECTOR[2])
        
        targetTitle = targetHtml.select_one('strong > span')
        if targetTitle:
            targetTitle = targetTitle.get_text()[8:]
        else:
            continue

        actPos = targetTitle.find("부")
        chapterPos = targetTitle.find("화")

        if actPos == -1 or chapterPos == -1:
            pass
        else:
            act = targetTitle[:actPos]
            chapter = targetTitle[actPos+2:chapterPos]

            targetTitle = f"{act}부 {chapter.zfill(2)}화"

        print(f"{targetSerial} 색인 진행- ", end="")
        
        targetUrl = targetHtml['href']

        targetList[targetSerial] = {
            'title': targetTitle,
            'URL': targetUrl,
        }

        serialCount += 1

        endTime = datetime.now()
        timeEslaped = (endTime - startTime).microseconds
        print(f"완료({str(timeEslaped).zfill(5)}ms)- {targetTitle}")

with open("list.json", "w", encoding="UTF-8") as f:
    json.dump(targetList, f, indent=4, ensure_ascii=False)

totalEndTime = datetime.now()

totalTimeEslaped = (totalEndTime - totalStartTime).seconds
print(f"\n모든 색인 완료- {totalTimeEslaped}s 소요")
print("자세한 내역은 list.json 파일을 참조하십시오\n\n")

totalStartTime = datetime.now()

for serial in targetList:
    startTime = datetime.now()

    targetUrl = targetList[serial]['URL']
    targetTitle = targetList[serial]['title']

    print(f"{serial} 스크래핑 진행- ", end="")
    
    rawTargetHtml = requests.get(targetUrl, headers=HEADER)
    targetHtml = BeautifulSoup(rawTargetHtml.text, 'lxml')

    targetBody =  targetHtml.select_one('.post_ct  ').select('p')
    content = ""

    for element in targetBody:
        element = BeautifulSoup(str(element).replace("<br/>", "\n"), 'lxml').get_text().strip()
        element = re.sub(r"\n[ ﻿ ]+", r"\n", element)
        element = re.sub(r"\n{3,}", r"\n\n", element)
        content = content + element + "\n"

    with open(f"./text/{serial} {targetTitle}.txt", "w", encoding="UTF-8") as f:
        f.write(content)

    endTime = datetime.now()
    timeEslaped = (endTime - startTime).microseconds

    print(f"완료({timeEslaped/1000000}s)- {targetTitle}({len(content)}자)")

totalEndTime = datetime.now()
totalTimeEslaped = (totalEndTime - totalStartTime).seconds

print(f"\n모든 스크래핑 완료- {totalTimeEslaped}s 소요")
print(f"결과물은 text 폴더를 확인하십시오")
