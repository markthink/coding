# -*- coding: utf-8 -*-
import os,shutil,re,time,requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

# 下载资料使用
class Aliyun:

    # 云栖大会-2016
    def Down2016(self):
        base_url = "https://yq.aliyun.com/activity/147?spm=5176.100239.blogcont69316.22.ZLFE7w"
        content = requests.get(base_url).content
        html = BeautifulSoup(content, 'html.parser')

        pdf_html = html.find_all("div", {"class": "floor-list"})


        # chrome 驱动下载地址
        # https://sites.google.com/a/chromium.org/chromedriver/downloads
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), chrome_options=chrome_options)


        for pdf in pdf_html:
            link = pdf.find('a').attrs['href']
            filename = pdf.find('p', {"class": "tit"}).text

            driver.get(link)
            pr_html = driver.page_source



            # r = requests.get(link)
            # with open('1.pdf', 'wb') as f:
            #     f.write(r.content)
            #
            # print(pdf)
            fox=1



if __name__ == '__main__':
    aliyun = Aliyun()
    aliyun.Down2016()


