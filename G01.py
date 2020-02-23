import requests
from bs4 import BeautifulSoup
import os
import re


def fileDir_get(title):
    # 利用正则表达式替换文件名中的非法字符
    title = re.sub(r'[<.>\'?|*:"/\\]', '_', title)
    file_path = '.\\' + title
    isExists = os.path.exists(file_path)
    if not isExists:
        os.makedirs(file_path)
        print(os.path.abspath(file_path) + '：创建成功！')
    else:
        print(os.path.abspath(file_path) + '：已经存在！')

    return file_path


def download_file(page):
    # 下载每一条规章链接的附件与正文
    # 传入CSS选择器，定位规章链接标签
    # 定义请求Header参数
    headers = {}
    headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'
    headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    headers['Connection'] = 'keep-alive'
    headers['Upgrade-Insecure-Requests'] = '1'
    url = 'http://www.caac.gov.cn/was5/web/search?page=' + str(page) + '&channelid=269689'
    html_str = requests.get(url, headers=headers)
    analy_str = BeautifulSoup(html_str.text, features="lxml")
    data = analy_str.select(".t_table > tbody > tr> td> a")
    for item in data:
        # 获取规章链接
        url_item = item.get('href')
        # 获取规章标题
        item_title = item.get('name')
        # 获取规章链接html文本
        item_html = requests.get(url_item, headers=headers)
        item_str = BeautifulSoup(item_html.text, features="lxml")
        # 定位规章正文部分标签
        item_text = item_str.select(".content > p")
        # 定位规章附件部分标签
        item_pdf = item_str.select("#id_tblAppendix > p > a")
        file_path = fileDir_get(item_title)
        for link_pdf in item_pdf:
            temp_item = url_item.split("/")
            temp_pdf = link_pdf.get('href').split("/")
            temp_item[-1] = temp_pdf[-1]
            url_pdf = '/'.join(temp_item)
            # 利用正则表达式替换PDF文件名中的非法字符
            file_name = file_path + '\\' + re.sub(r'[<>\'?|*:"/\\]', '-', str(link_pdf.string))
            pdf_html = requests.get(url_pdf, headers=headers)
            fo = open(file_name, 'wb')
            fo.write(pdf_html.content)
            fo.close()
        file_name = file_path + '\\' + re.sub(r'[<>\'?|*:"/\\]', '-', item_title) + '.txt'
        fo = open(file_name, 'w', encoding='utf-8')
        for line_text in item_text:
            temp_soup = BeautifulSoup(str(line_text), 'lxml').text
            fo.writelines(temp_soup)
            fo.writelines('\n')
        fo.close()

    return


for i in range(26, 0, -1):
    download_file(page=i)
