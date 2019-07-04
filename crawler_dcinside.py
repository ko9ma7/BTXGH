#### UTF encoding

import sys

import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')

sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')



#### Importing Required Modules

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import requests
import lxml
import pandas as pd

#### Webdriver options setting

options = webdriver.ChromeOptions()

options.add_argument('headless')

options.add_argument('window-size=1920x1080')

path = 'chromedriver.exe'
driver = webdriver.Chrome(path, options=options)
driver.implicitly_wait(3)

#### Save Data in dict

posts = {'post_id' : [],
'제목' : [],
'글쓴이' : [],
'작성일' : [],
'조회수' : [],
'추천수' : [],
}

#### Crawl over posts pages

epoch = 90

url = "https://gall.dcinside.com/board/lists/?id=cosmetic&page="

for i in range(1, epoch+1):

    driver.get(url+str(i))

    driver.implicitly_wait(4)

    page_html = driver.page_source

    html_parsed = bs(page_html, 'html.parser')

    #### Main table where postings are displayed

    table = html_parsed.find("tbody")

    #### Each post

    lists = table.find_all("tr")

    #### TO Pandas Dataframe



    for post in lists:
        title_id = post.find("td").text
        posts['post_id'].append(title_id.strip())
        posts['제목'].append(post.find("td").find_next_sibling("td").text.strip())
        posts['글쓴이'].append(post.find("td").find_next_sibling("td").find_next_sibling("td").text.strip())
        posts['작성일'].append(post.find("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text.strip())
        posts['조회수'].append(post.find("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text.strip())
        posts['추천수'].append(post.find("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").find_next_sibling("td").text.strip())

postings = pd.DataFrame(posts)
postings.to_csv("DCinside_cosmetics.csv", index=False, encoding='utf-8')
print("CSV 저장 완료!")
