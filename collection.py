# -*- coding: utf-8 -*-
# @Author: root
# @Date:   2019-04-08 11:03:09
# @Last Modified by:   jmx
# @Last Modified time: 2019-04-26 15:23:54
import urllib.request
from bs4 import BeautifulSoup
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
import pymysql
import json
import sys
import os
import traceback
import datetime


def env(name=''):
    envFile = "%s/.env" % sys.path[0]
    if(os.path.exists(envFile)):
        env = eval(open(envFile).read())
    else:
        return None
    if(name == ''):
        return None
    if(name not in env):
        return None
    return env[name]


class conllection():
    """docstring for conllection"""
    send_headers = {
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "SUB=_2AkMr9jfyf8PxqwJRmP0WzGnmaI9_yQrEieKdqsYpJRMxHRl-yT9jqkIOtRB6AHYZHrat4NIMz68IGbFy6SKmcbU8BmL6;",
        "Host": "weibo.com",
        "Referer": "https: // weibo.com/gushequ?is_all = 1",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    }

    def __init__(self, url, name):
        self.db = mysql()
        self.name = name
        req = urllib.request.Request(url, headers=self.send_headers)
        response = urllib.request.urlopen(req)
        data = response.read().decode('utf-8')
        data = re.sub(r'\\n', '', data)
        data = re.sub(r'\\t', '', data)
        data = re.sub(r'\\r', '', data)
        data = re.sub(r'\\', '', data)
        # 获取发布时间
        pattern = re.compile(
            '<div class="WB_from S_txt2".*?>\s*?</div>')
        create_time_list = re.findall(pattern, data)

        for i in range(len(create_time_list)):
            soup = BeautifulSoup(create_time_list[i], 'html.parser')
            row = soup.find_all('a')[0]
            marker = row.get('href').split('?')[0]
            marker_is_exists = self.db.select(
                "select marker from news_his where marker='%s' limit 1;" % marker)
            if(len(marker_is_exists) == 0):
                create_date = row.get('title')
                create_time = row.get('date')
                if (time.time()-int(create_time)/1000)/(24*3600) > 5:
                    continue
                url = "https://weibo.com"+row.get('href')
                content = self.getDetail(url)
                html = '''
                <div class="main">
                    <table border="1" cellpadding="10" cellspacing="0">
                        <tr>
                            <td>发布时间</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td>原文链接</td>
                            <td><a target="_blank" href="{}">原文链接</a></td>
                        </tr>
                        <tr>
                            <td>内容</td>
                            <td>{}</td>
                        </tr>
                    </table>
                </div>
                '''.format(create_date, url, content)
                is_send = sendEmail(html, name)
                # is_send = 1
                if(is_send):
                    self.db.add(
                        [(marker, url, create_date, json.dumps(content))])

    def getDetail(self, url):
        '''[summary]

        [description]

        Arguments:
                url {[type]} -- [description]
        '''
        req = urllib.request.Request(url, headers=self.send_headers)
        response = urllib.request.urlopen(req)
        data = response.read().decode('utf-8')
        data = re.sub(r'\\n', '', data)
        data = re.sub(r'\\t', '', data)
        data = re.sub(r'\\r', '', data)
        data = re.sub(r'\\', '', data)
        pattern = re.compile(
            '<div class="WB_text W_f14".*?>\s*?</div>')
        content = re.search(pattern, data).group()

        pattern = re.compile('<ul class="WB_media_a.*?".*?>\s*?</ul>')
        imgbox_is_exists = re.search(pattern, data)
        imgbox = ''
        if(imgbox_is_exists):
            soup = BeautifulSoup(imgbox_is_exists.group(), 'html.parser')
            row = soup.find_all('ul')[0]
            actData = row.get('action-data')
            if(actData != None):
                actDataList = actData.split('&')
                for i in actDataList:
                    if(i.find("clear_picSrc") != -1):
                        imgurl = i.split("=")[1].split(",")
                        imgbox = ''
                        for j in imgurl:
                            imgurl = "http:"+j.replace("%2F", '/')
                            imgbox += "<img src='{}'/>".format(imgurl)
        return content+imgbox


def sendEmail(html, name, receivers=env("receivers")):
    '''[summary]

    [description]
    '''
    # 第三方 SMTP 服务
    mail_host = "smtp.qq.com"  # 设置服务器
    mail_user = env("mail_user")  # 用户名
    mail_pass = env("mail_pass")  # 口令

    sender = env("sender")

    message = MIMEText(html, 'html', 'utf-8')
    message['From'] = Header("新浪微博更新监控", 'utf-8')
    # message['To'] = Header("使用者", 'utf-8')

    subject = '<{}>提醒'.format(name)
    message['Subject'] = Header(subject, 'utf-8')
    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(sender, mail_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(sender, receivers, message.as_string())
        print('邮件发送成功')
        return True
    except smtplib.SMTPException:
        print('邮件发送失败')
        return False


class mysql():
    """docstring for mysql"""

    def __init__(self):
        host = env("hosts")
        pwd = env("db_pwd")
        usr = env("db_usr")
        database = env("db_name")
        try:
            self.db = pymysql.connect(host, usr, pwd, database, charset="utf8")
        except Exception as e:
            print(e)
            exit()
        self.cursor = self.db.cursor()

    def select(self, sql):
        try:
            # 执行SQL语句
            self.cursor.execute(sql)
            # 获取所有记录列表
            results = self.cursor.fetchall()
            col_name_list = [tuple[0] for tuple in self.cursor.description]
            data = [{col_name_list[j]:results[i][j]
                     for j in range(len(col_name_list))} for i in range(len(results))]
            return data
        except:
            print("Error: unable to fetch data")

    def add(self, dicts):
        if(isinstance(dicts, list) == False):
            print('数据必须是列表')
            return False
        sql = "INSERT INTO news_his (marker,url,create_time,content) values (%s,%s,%s,%s);"
        try:
            self.cursor.executemany(sql, dicts)
            self.db.commit()
        except:
            self.db.rollback()

    def __del__(self):
        self.db.close()


if __name__ == '__main__':
    try:
        urlList = mysql().select('select * from url_list')
        for i in urlList:
            conllection(i['url'], i['name'])
    except Exception as e:
        traceback.print_exc()
        html = '''
                <div class="main">
                    <table border="1" cellpadding="10" cellspacing="0">
                        <tr>
                            <td>时间</td>
                            <td>{}</td>
                        </tr>
                        <tr>
                            <td>异常信息</td>
                            <td><a target="_blank" href="http://bt.com:8888">{}</a></td>
                        </tr>
                    </table>
                </div>
                '''.format(datetime.datetime.now(), str(e))
        sendEmail(html, '脚本异常', '1837461054@qq.com')
