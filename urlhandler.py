import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')

sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')  #Unicode Encoding

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import lxml
import pandas as pd
from datetime import datetime

options = webdriver.ChromeOptions()

options.add_argument('headless')

options.add_argument('window-size=1920x1080')

path = '../../documents/2019-여름/GH_BNT/chromedriver.exe'
driver = webdriver.Chrome(path, options=options)
driver.implicitly_wait(3)

## Prototyping
"""

url = 'https://www.instagram.com/presenterbruce'

driver.get(url)

soup = bs(driver.page_source, 'lxml')
divImage = soup.find('img', {"class": "_6q-tv"})

# close the browser
driver.close()

print(divImage.get('src'))

"""
## END

def get_img_src(name):
    url = "https://instagram.com/" + name
    driver.get(url)
    soup = bs(driver.page_source, 'lxml')

    # Profile Pic
    divImage = soup.find('img', {"class": "_6q-tv"})

    # close the browser
    driver.close()

    # Return the source url
    return(divImage.get('src'))

df = pd.read_csv('influencer_commenters.csv', encoding='utf-8')

## To make a DataFrame and Merge
urls = {'name': [], 'urls': []} # A dictionary of array of arrays

for index, row in df.iterrows():
    t0 = datetime.now()
    print(t0)
    influencer = row['name']
    commenters = row['commenters'] # Which is an array of names
    each = [] # An array to store commenters' profile_pic urls

    for i in range(len(commenters)):
        img_src = get_img_src(commenters[i])
        each.append(img_src)
        print(i, 'out of', len(commenters))

    urls['name'].append(influencer)
    urls['urls'].append(each)
    print(datetime.now()-t0, " per influencer")

output_df = pd.DataFrame(urls)
with_src = pd.merge(df, urls, how='left', left_on='name', right_on='name')
with_src.to_csv("commenters_src.csv", encoding='utf-8', index=False)
