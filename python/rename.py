# -*- coding: utf-8 -*-
import os,shutil,re,codecs,sqlite3,time,requests
from datetime import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

class k8sDoc:

    # 初始化文档路径'/Users/dxwsker/works/k8smeetup/docs'
    DOCPATH = ''
    DBNAME = ''

    # 获取数据库链接
    def dbconn(self, dbname):
        if dbname.strip() == '':
            dbname = self.DBNAME
        # 连接数据库
        conn = sqlite3.connect(dbname)
        return conn

    def Docfiles(self,files_path):

        if files_path.strip() == '':
            files_path = self.DOCPATH

        current_files = os.listdir(files_path)
        all_files = []
        for file_name in current_files:
            full_file_name = os.path.join(files_path, file_name)
            if (os.path.splitext(full_file_name)[1] == '.md' and os.path.dirname(full_file_name).find(
                    "node_modules") == -1):
                # print(os.path.dirname(full_file_name))
                all_files.append(full_file_name)

            if (os.path.splitext(full_file_name)[1] == '.html' and os.path.dirname(full_file_name).find(
                    "node_modules") == -1):
                all_files.append(full_file_name)

            if os.path.isdir(full_file_name):
                next_level_files = self.Docfiles(full_file_name)
                all_files.extend(next_level_files)

        return all_files

    # 移除日期文件
    def RemoveDateFiles(self,files_path):

        files = self.Docfiles(files_path)

        for i in range(0, len(files)):
            if re.search(r'\d{4}(\-|\/|\.)\d{1,2}\1\d{1,2}',files[i]):
                os.remove(files[i])

        return '日期文件移除完成'

    # 移除原始英文
    def RemoveEnglish(self,files_path):

        files = self.Docfiles(files_path)

        for i in range(0, len(files)):
            # 读取文件内容
            with open(files[i], encoding='utf8') as file:
                try:
                    content = file.read()
                except UnicodeDecodeError as e:
                    print(e)
                    print(files[i])

            # 将原始英文移除掉
            with open(files[i], 'w', encoding='utf8') as file:
                filter_conetnet = re.sub(r'<!--[\n\s\S]*?-->', '', content)
                # 移除首行换行符
                if filter_conetnet[:3] != '---':
                    filter_conetnet = re.sub('\n', '', filter_conetnet, 1)
                file.write(filter_conetnet)

        return '原始英文处理完成'

    # 日期文件重命名
    def RenameFiles(self,files_path,date='2017-9-15'):

        files = self.Docfiles('')

        for i in range(0, len(files)):

            fileArr = os.path.splitext(files[i])

            filename = fileArr[0] + '-' + date + fileArr[1]

            os.rename(files[i], filename)

            # 拷贝文件
            # shutil.copyfile(filename,files[i])
        return '文件重命名完成'

    # 每月更新一次SQLite数据库文件
    def MonthUpdate(self, dbname):

        # 获取更新的文件列表
        files = self.Docfiles('')

        # 连接数据库
        conn = self.dbconn(dbname)
        # 创建一个Cursor
        cursor = conn.cursor()

        for i in range(0, len(files)):
            file_date = files[i].split('k8s-update')[1]
            file_array = file_date.split('-2017-9-15')
            file = file_array[0]+file_array[1]

            select_sql = "select * from tasks where files = '"+file+"'"
            update_sql = "update tasks set version = '2017-09-15', renew = 'Yes' where files='" + file + "'"

            now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            insert_sql = "insert into tasks(files, version, renew, status,createdAt, updatedAt) values('"+file+"','2017-09-15','No','Not Started','"+now_time+ "','"+now_time+ "')"

            cursor.execute(select_sql)
            exist = cursor.fetchone()
            if exist is None:
                try:
                    cursor.execute(insert_sql)

                except BaseException as e:
                    print(e)
                    print(file)
            else:
                cursor.execute(update_sql)

        cursor.close()
        conn.commit()
        conn.close()
        return "月度文档更新成功"

    # 每月文章清理 - 对未翻译的文章更新到最新版本，并删除老版本
    def MonthCleanUp(self, dbname, old_date, new_date):
        # 连接数据库
        conn = self.dbconn(dbname)
        # 创建一个Cursor
        cursor = conn.cursor()

        select_sql = "select * from Tasks where status ='Not Started'"

        cursor.execute(select_sql)

        tasks = cursor.fetchall()

        BasePath = '/Users/dxwsker/works/k8smeetup/kubernetes.github.io'

        for task in tasks:
            update_sql = "update tasks set version = '2017-09-15', renew = 'No' where files='" + task[1] + "'"
            cursor.execute(update_sql)

            fileArr = os.path.splitext(task[1])

            old_file = fileArr[0] + '-' + old_date + fileArr[1]
            new_file = fileArr[0] + '-' + new_date + fileArr[1]

            try:
                os.remove(BasePath + old_file)
                os.rename(BasePath + task[1])

            except BaseException as e:
                print(e)

            # 更新翻译文档
            try:
                shutil.copyfile(BasePath + new_file, BasePath + task[1])
            except FileNotFoundError as e:
                # 未更新版本
                shutil.copyfile(BasePath + task[1], BasePath + new_file)

        cursor.close()
        conn.commit()
        conn.close()
        return "月度文档清理成功"


    # 每周更新文档状态
    def WeekUpdate(self, dbname):
        # 连接数据库
        conn = self.dbconn(dbname)
        # 创建一个Cursor
        cursor = conn.cursor()

        # files = open("weekupdate.txt", "r+", encoding='utf-8')
        # MDfiles = files.readlines()

        select_sql = "select * from article where repeat=0 order by week_number desc"

        cursor.execute(select_sql)
        arts = cursor.fetchall()

        for art in arts:
        # for i in range(0, len(MDfiles)):
        #     file = MDfiles[i].strip("\n")
            file = '/'+str(art[2])
            select_sql = "select * from tasks where files like '" + file + "%'"

            cursor.execute(select_sql)
            task = cursor.fetchone()
            if task is None:
                pass
            else:
                if task[6] == None:
                    update_sql = "update tasks set status = 'Pull Request Merged', internal_reviewer = '何小龙 (Caicloud)',internal_reviewer_status = 'Done' where files = '" + task[1] + "'"
                else:
                    update_sql = "update tasks set status = 'Pull Request Merged', internal_reviewer_status = 'Done' where files = '" + task[1] + "'"
                cursor.execute(update_sql)

        cursor.close()
        conn.commit()
        conn.close()
        return "每周文档更新成功"

    # 每周 PR 链接生成
    def WeekPR(self,base_url, dbname):
        content = requests.get(base_url).content
        soup_pages = BeautifulSoup(content, 'html.parser')

        # 获取分页数
        # https://www.v2ex.com/t/285244
        max = soup_pages.find("div", {"class": "pagination"}).find_all("a")[-2].text

        # 连接数据库
        conn = self.dbconn(dbname)
        # 创建一个Cursor
        cursor = conn.cursor()

        # 如果数据表不存在，即创建一个
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='request_pull'")
        is_article = cursor.fetchone()

        if is_article is None:
            cursor.execute('''
                create table request_pull(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    pr_name varchar(300), 
                    process smallint
                )''')

        # 解析所有的 PR 链接
        # exit_flag = False
        for i in range(int(max), -1, -1):
            page = 'https://github.com/k8smeetup/kubernetes.github.io/pulls?page='+str(i)+'&q=is%3Apr+is%3Aclosed'
            page_content = requests.get(page).content
            bs_content = BeautifulSoup(page_content, 'html.parser')

            # 获取所有链接
            for span in reversed(bs_content.find_all('span', {'aria-label': 'Merged pull request'})):
                link = span.parent.parent.a['href']
                # print(link)
                cursor.execute("select * from request_pull where pr_name = '"+ link +"'")
                is_exist = cursor.fetchone()
                if is_exist is None:
                    # process 0: 未处理 1已处理
                    cursor.execute("insert into request_pull (pr_name, process) values ('"+ link +"', 0)")
                # else:
                    # 跳出最外层循环标记
                    # exit_flag = True
                    # break
            # if exit_flag == True:
            #     break
            # print("\n ------------ \n")
        cursor.close()
        conn.commit()
        conn.close()
        return "每周 PR 链接更新成功"

    # 检测或创建数据表
    def CreateArticleTable(self,dbname):
        # 连接数据库
        conn = self.dbconn(dbname)
        # 创建一个Cursor
        cursor = conn.cursor()

        # 如果数据表不存在，即创建一个
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='article'")
        is_article = cursor.fetchone()

        '''
        pr_id： PR 链接 ID
        article_name: 文章名称
        article_author: 文章译者
        week_number: Week 周期
        repeat: 0 无重复 1 有重复
        process: 0 未处理 1 已处理 (未使用: 未来扩展需要)
        '''
        if is_article is None:
            cursor.execute('''
                        create table article (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            pr_id INTEGER, 
                            article_name varchar(300), 
                            article_author varchar(50), 
                            week_datetime datetime,
                            week_number INTEGER, 
                            repeat smallint,
                            process smallint
                        )''')

        # 获取未处理的 PR 链接（必须为降序才能获取到所有的文章列表，升序会丢失部分文章-原因未知）
        select_sql = "select * from request_pull where process=0 order by id desc"
        cursor.execute(select_sql)
        prs = cursor.fetchall()
        return conn,cursor,prs

    # 获取 PR 的文章名
    def WeekArticle(self, dbname, isfix=False):

        # chrome 驱动下载地址
        # https://sites.google.com/a/chromium.org/chromedriver/downloads
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), chrome_options=chrome_options)

        conn, cursor, prs = self.CreateArticleTable(dbname)

        for pr in prs:
            pr_id = str(pr[0])
            update_sql = "update request_pull set process=1 where pr_name='"+ pr[1] +"'"
            # pr_html = requests.get("https://github.com" + pr[1] + "/files").content
            try:

                driver.get("https://github.com" + pr[1] + "/files")
                # driver.get("https://github.com/k8smeetup/kubernetes.github.io/pull/7/files")
                WebDriverWait(driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.link-gray-dark')))
                pr_html = driver.page_source
            except TimeoutException as e:
                print("异常：" + pr[1] + "\n")
                print(e)

            # pr_html = requests.get("https://github.com/k8smeetup/kubernetes.github.io/pull/7/files").content
            pr_content = BeautifulSoup(pr_html, 'html.parser')

            # 获取文章作者
            article_author = pr_content.find_all('span', {'class': 'css-truncate-target user'})[-1].text

            # 获取 Merge 合并时间
            week_merge = pr_content.find('div', {'class': 'gh-header-meta'})
            week_datetime = week_merge.find('relative-time')['datetime']
            # http://blog.csdn.net/crazyhacking/article/details/12751845
            week_number = datetime.strptime(week_datetime, '%Y-%m-%dT%H:%M:%SZ').strftime('%W')

            # 获取文章列表
            art_files = pr_content.find_all('div', {'class': 'file-info'});
            # art_ajax_files = pr_content.find_all('div', {'class': 'js-diff-progressive-container'});

            print("----" + pr[1] + ": ----" + "\n")

            # PR 文章汇总
            pr_arts = []
            for art in art_files:
                file_name = art.find('a', {'class': 'link-gray-dark'}).text
                pr_arts.append(file_name)

            # for art_ajax in art_ajax_files:
            #     include_file = art_ajax.find('include-fragment')
            #     if include_file is None:
            #         pass
            #     else:
            #         art_html = requests.get("https://github.com/"+include_file['src']).content
            #         art = BeautifulSoup(art_html, 'html.parser')
            #     # 空白内容不解析
            #     try:
            #         file_name = art_ajax.find('div', {'class': 'file-header'})['data-path']
            #     except BaseException as e:
            #         continue
            #     pr_arts.append(file_name)

            # 文章去重
            pr_arts = list(set(pr_arts))

            for pr_art in pr_arts:
                # 跳过版本文件
                if re.search(r'\d{4}(\-|\/|\.)\d{1,2}\1\d{1,2}', pr_art):
                    continue

                print(pr_id+":"+pr_art+"\n")
                # 是否重复
                repeat = 0
                select_sql = "select * from article where article_name='"+ pr_art +"'"
                cursor.execute(select_sql)
                is_repeat = cursor.fetchone()
                if is_repeat is None:
                    pass
                else:
                    repeat = 1

                if isfix == False:
                    insert_sql = "insert into article (pr_id, article_name,article_author,week_datetime,week_number,repeat,process) " \
                                 "values (" + pr_id + ", '" + pr_art + "','" + article_author + "','" + week_datetime + "'," + str(
                        week_number) + "," + str(repeat) + ",0)"
                    cursor.execute(insert_sql)
                else:
                    # 文件采集修补处理(部分PR文件列表采集不完整)
                    select_sql = "select * from article where pr_id='"+ pr_id +"' and article_name='"+ pr_art +"'"
                    cursor.execute(select_sql)

                    is_fix = cursor.fetchone()
                    if is_fix is None:
                        insert_sql = "insert into article (pr_id, article_name,article_author,week_datetime,week_number,repeat,process) " \
                                     "values (" + pr_id + ", '" + pr_art + "','" + article_author + "','" + week_datetime + "'," + str(
                            week_number) + "," + str(repeat) + ",0)"
                        cursor.execute(insert_sql)

            # print(insert_sql+"\n")
            # 更新 PR 任务表
            cursor.execute(update_sql)
            conn.commit()
        driver.close()
        cursor.close()
        conn.close()
        return "每周文章链接更新成功"


    # 检测文章内容-更新文章所在周
    def CheckArt(self,dbname):
        # 连接数据库
        conn = self.dbconn(dbname)
        # 创建一个Cursor
        cursor = conn.cursor()

        files = open("weekupdate.txt", "r+", encoding='utf-8')
        MDfiles = files.readlines()

        for i in range(0, len(MDfiles)):
            file = MDfiles[i].strip("\n")
            select_sql = "select * from article where article_name like '" + file[1:] + "%'"

            cursor.execute(select_sql)
            art = cursor.fetchone()
            if art is None:
                print(file)

        cursor.close()
        conn.close()

    # 根据日期返回表头信息（游标，周数，当前时间,是否更新）
    def getWeekInfo(self, cursor, week_number, curtime, repeat):
        dayscount = timedelta(days=curtime.isoweekday())
        dayfrom = curtime - dayscount + timedelta(days=1)
        dayto = curtime - dayscount + timedelta(days=7)
        week_info = ' ~~ '.join([str(dayfrom.strftime('%Y-%m-%d')), str(dayto.strftime('%Y-%m-%d'))])

        # 统计合并文章数量
        count_sql = "select count(*) from article where repeat='"+repeat+"' and week_number='" + str(week_number) + "'"
        cursor.execute(count_sql)
        week_arts_number = cursor.fetchone()
        week_head = "### 第 " + str(week_number - 29) + " 周：" + week_info + " - 有效合并 " + str(week_arts_number[0]) + " 篇"
        return week_head

    # 生成周报(0 生成新增的文章 1 生成更新的文章)
    def WeekReport(self,dbname,repeat='0'):
        # 连接数据库
        conn = self.dbconn(dbname)
        # 创建一个Cursor
        cursor = conn.cursor()

        # select_sql = "select * from article order by week_datetime"
        select_sql = "select * from article where repeat='"+repeat+"' order by week_number desc"

        cursor.execute(select_sql)
        arts = cursor.fetchall()

        file = open("test.txt", "a", encoding='utf-8')

        if repeat == '0':
            file_head = "# K8SMeetup 中文翻译社区每周文章贡献汇编\n\n本文档只包含新增更新，[更新参考](contribution-update.md)。"
        elif repeat == '1':
            file_head = "# K8SMeetup 中文翻译社区每周文章更新汇编"

        file.write(file_head + "\n\n")

        # 初始化周数字
        cur_week = 0
        for art in arts:
            # 根据时间生成周号码
            week_datetime = art[4]
            curtime = datetime.strptime(week_datetime, '%Y-%m-%dT%H:%M:%SZ')
            # week_number = datetime.strptime(week_datetime, '%Y-%m-%dT%H:%M:%SZ').strftime('%W')
            # update_sql = "update article set week_number='"+week_number+"' where id='" + str(art[0]) + "'"
            # cursor.execute(update_sql)

            week_number = art[5]
            if cur_week == 0:
                week_info = self.getWeekInfo(cursor, week_number, curtime, repeat)
                cur_week = week_number
                file.write("\n"+week_info+"\n\n")

            elif week_number < cur_week:
                week_info = self.getWeekInfo(cursor, week_number, curtime, repeat)
                cur_week = week_number
                file.write("\n"+week_info+"\n\n")

            filename = 'https://k8smeetup.github.io/'+os.path.splitext(art[2])[0]
            author = art[3]
            report = '['+filename+']('+filename+') by ['+author+'](https://github.com/'+author+')'

            file.write(report+"\n\n")
        # conn.commit()
        cursor.close()
        conn.close()
        return "第周报表更新完毕！"


if __name__ == '__main__':

    k8s = k8sDoc()
    k8s.DOCPATH = "/Users/dxwsker/works/k8smeetup/k8s/docs"
    # k8s.DOCPATH = "/Users/dxwsker/works/k8smeetup/k8s-update/docs"
    k8s.DBNAME = '/Users/dxwsker/WebstormProjects/google/db.sqlite'

    # 预览库使用
    # result = k8s.RemoveDateFiles('')
    # result = k8s.RemoveEnglish('')

    # NodeJS 同步之后-更新任务表格
    # result = k8s.WeekUpdate('')

    # 获取所有PR链接地址
    # base_url = 'https://github.com/k8smeetup/kubernetes.github.io/pulls?q=is%3Apr+is%3Aclosed'
    # result = k8s.WeekPR(base_url,'')

    # 获取所有文章链接地址
    # result = k8s.WeekArticle('')

    # 修复模式-解决 PR 文章列表不完整的问题
    # result = k8s.WeekArticle('',True)
    # result = k8s.CheckArt('')

    # 周报更新
    # result = k8s.WeekReport('')
    # result = k8s.WeekReport('','1')


    # 月度更新时使用
    # 日期文件重命名
    # result = k8s.RenameFiles('','2017-9-15')
    # result = k8s.MonthUpdate('')
    # result = k8s.MonthCleanUp('','2017-8-15','2017-9-15')

    print(result)
