# coding=utf-8
import os
from models import Employee
from bs4 import BeautifulSoup
from config import Config
from mparser import ProfileParser
from mparser import get_doc_bySelenium


# @brief: 函数将过滤结果转化为Employee数据
# @tag: 输入为待处理的BeautifulSoup的tag对象
# @output:输出employee
def handler(tag):
    employee = Employee(name=tag.string, url=tag['href'])
    return employee

def set_attr_hook(name,value):
    if name == 'departments':
        if len(value) > 32:
            return None
    elif name == 'email':
        idx = value.find('nju.edu.cn')
        if idx != -1:
            value = value[:idx] + 'nju.edu.cn'
        value = value.replace('#','@')
    return value

# @doc: 输入为个人详情页的整个网页源码
# @output:输出employee，如果没有检测到内容返回None          
# employee可用属性(url, name, email, tel, title, profile, research, departments,fax,addr):
def profile_handler(doc, name, url, path):
    filename = os.path.join(path, name + ".html")
    employee = Employee(name=name, url=url)

    # 只保存名称和个人主页，个人简历文件另存当前目录
    soup = BeautifulSoup(doc, Config.SOUP_PARSER)
    divs = soup.find_all(name="table", attrs={"cellpadding":"0","cellspacing":"0"}, limit=1)
    if not divs or len(divs) == 0:
        div = soup
    else:
        div = divs[0]

    if not os.path.exists(filename):
        with open(filename, 'wb') as fp:
            content = div.prettify()
            fp.write(content)
            fp.close()
    
    divs = div.find_all(class_="box_common_line")
    if not divs or len(divs) == 0:
        div = soup
    else:
        div = divs[0]

    #email
    #email_div = soup.find_all(name='a',class_="phy-mail")
    #if email_div and len(email_div) != 0:
    #    employee.email = email_div[0].get_text().strip()
    #
    #te_div = soup.find_all(name='a',class_="phy-phone")
    #if te_div and len(te_div) != 0:
    #    employee.tel = te_div[0].get_text().strip()

    # 使用纯文本方式处理
    lines = div.stripped_strings
    # text=div.get_text(strip=True)
    parser = ProfileParser(lines=lines,employee=employee,set_attr_hook=set_attr_hook,max_line=256)
    return parser.parse()
