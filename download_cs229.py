from bs4 import BeautifulSoup
import urllib2
import os
import cookielib

import sys

reload(sys)

cookie = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(handler)


menu = ['', "Lecture Notes", "Supplemental Notes", "Section Notes"]
head_url = "http://cs229.stanford.edu/"


def search_note_list():
    url = "http://cs229.stanford.edu/materials.html"
    print url

    response1 = opener.open(fullurl=url)

    source = response1.read()
    # print source

    # make xml tools
    soup = BeautifulSoup(source, "lxml")

    # find meta
    content_all = soup.find_all('ul',type="disc")
    for i in range(3,4):
        download_li(content_all[i],menu[i])


def download_li(content,menu_name):
    """
    :param content:  content html
    :param menu_name:  this dir name
    :return: none
    """
    li_list = content.find_all('li')
    if not os.path.exists("./"+menu_name):
        os.mkdir("./"+menu_name)
    for li in li_list:
        str_text = li.text
        # print str_text
        index = str_text.find("&nbsp")
        li_name = str_text[index+6:][:-2]
        if li_name.find(".m") != -1:
            continue

        href_list = li.find_all("a")
        href = href_list[-1].attrs['href']
        href = head_url + href
        print href
        response1 = opener.open(href)
        content = response1.read()
        path = "./"+menu_name+"/"+li_name
        if path.endswith('.'):
            path += "pdf"
        else:
            path += ".pdf"

        print path
        with open(path, 'wb') as save_file:
            save_file.write(content)
            print "finish"

search_note_list()