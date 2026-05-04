import requests
import os
import json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionVhains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

product_code = input('Provide product code: ')
page = 1
next = True
headers ={
    "Host": "www.ceneo.pl",
    "Cookie": "sv3=1.0_7d330b44-3cbb-11f1-bbeb-dfb946e97857; urdsc=1; userCeneo=ID=c835bda2-7584-4c39-b5e5-26daab7154dd; __RequestVerificationToken=MXIgE6e6PlKM9dHXVWApMOebaxM1PJWB5VoMX_td8t_Kktj3F0oXp7okkafn-tz_nRnD27W7PcDWPyT3LDt89eu6d7Sj1n_FYJq651TnHck1; ai_user=UTcgc|2026-04-20T13:18:58.527Z; __utmf=b005f137479d61dcd846fea07a2e7c2c_Dsgqi6QMc9CtX7buqOpcIw%3D%3D; ai_session=1HLzD|1776691139013.1|1776691139013.1; appType=%7B%22Value%22%3A1%7D; cProdCompare_v2=; __rtbh.uid=%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22unknown%22%2C%22expiryDate%22%3A%222027-04-20T13%3A18%3A59.690Z%22%7D; __rtbh.aid=%7B%22eventType%22%3A%22aid%22%2C%22id%22%3A%227d330b44-3cbb-11f1-bbeb-dfb946e97857%22%2C%22expiryDate%22%3A%222027-04-20T13%3A18%3A59.691Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22OSf8kFLBXPXuaOiwelcJ%22%2C%22expiryDate%22%3A%222027-04-20T13%3A18%3A59.693Z%22%7D; browserBlStatus=0",
    "User_Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
}
url = f"https://www.ceneo.pl/{product_code}/opinie-{page}"
path_to_driver = "D:\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"
s = Service(path_to_driver)
driver = webdriver.Chrome(service=s)
driver.get(url)
driver.maximize_window()
driver.find_element(by="xpath", value="//*[@id="js_cookie-consent-general"]/div/div[2]/button[1]").click()
all_opinions = []
while next:
    url = f"https://www.ceneo.pl/{product_code}/opinie-{page}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        page_dom = BeautifulSoup(response.text, "html.parser")
        product_name = page_dom.find("h1").get_text() if page == 1 else product_name
        opinions = page_dom.select('div.js_product-review:not(.user-post--highlight)')
        print(len(opinions))
        for opinion in opinions:
            single_opinion = {
                'opinion_id': opinion.get("data-entry-id"),
                'author': opinion.select_one("span.user-post__author-name").get_text().strip(),
                'recommendation': opinion.select_one('span.user-post__author-recomendation > em').get_text() if opinion.select_one('span.user-post__author-recomendation > em') else None,
                'score': opinion.select_one('span.user-post__score-count').get_text(),
                'content': opinion.select_one('div.user-post__text').get_text(),
                'pros': [p.get_text() for p in opinion.select('div.review-feature__item--positive')],
                'cons': [c.get_text() for c in opinion.select('div.review-feature__item--negative')],
                'helpful': opinion.select_one('button.vote-yes > span').get_text(),
                'unhelpful': opinion.select_one('button.vote-no > span').get_text(),
                'publish_date': opinion.select_one('span.user-post__published > time:nth-child(1)[datetime]').get('datetime'),
                'purchase_date': opinion.select_one('span.user-post__published > time:nth-child(2)[datetime]').get('datetime') if opinion.select_one('span.user-post__published > time:nth-child(2)[datetime]') else None
            }
            all_opinions.append(single_opinion)
    next = True if  page_dom.select_one('button.pagination__next') else False
    if next: page +=1
if not os.path.exists("./opinions"):
    os.mkdir("./opinions")
with open(f'./opinions/{product_code}.json','w', encoding="UTF-8") as jf:
    json.dump(all_opinions, jf, indent=4, ensure_ascii=False)