#!/usr/local/cellar/python/2.7.13/bin/python2.7
# encoding: utf-8

from bs4 import BeautifulSoup
import urllib2
import urllib
import cookielib

import sys
import os
import argparse

parser = argparse.ArgumentParser(description='Download Paper from CVPR')
parser.add_argument('--keyword', type=str, required=True, help='which keyword to search')
parser.add_argument('--conference', type=str, choices=['CVPR', 'ICCV'],default='CVPR', help='which confernece to search')
parser.add_argument('--year', type=int, default=2017, help='which year CVPR open')
parser.add_argument('--operate', type=str, choices=['download', 'show'], default='download', help='download or show')
parser.add_argument('--download', type=str, choices=['percent', 'detail'], default='percent',
                    help='show detail or percent only')
opt = parser.parse_args()

reload(sys)

cookie = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(handler)


def search_paper_list(conference=opt.conference, year=opt.year, word=None):
    """
    :param conference:
    :param year:
    :param word:
    :return:
    """
    data = {
        "query": word
    }
    post_data = urllib.urlencode(data)
    # urllib进行编码
    url = "http://openaccess.thecvf.com/" + conference + str(year) + "_search.py"
    if word is None:
        url = "http://openaccess.thecvf.com/" + conference + str(year) + ".py"
        post_data = None

    response1 = opener.open(fullurl=url, data=post_data)
    source = response1.read()

    # make xml tools
    soup = BeautifulSoup(source, "lxml")

    # find meta
    content_all = soup.find(id="content")
    paper_list = content_all.find_all('dd')[1::2]
    name_list = content_all.find_all('dt')
    content_list = []
    for i in range(len(name_list)):
        content_list.append(deal_single_paper(name_list[i], paper_list[i]))
    return content_list


def deal_single_paper(dt, dd):
    """
    put single xml into diction which is required
    :param dt:  <dt> meta with title information
    :param dd:  <dd> meta with href and supp
    :return:  {dict}
        eg:
        {
        {'href': 'content_cvpr_2017/papers/Tanaka_Material_Classification_Using_CVPR_2017_paper.pdf',
        'title': 'Material Classification Using Frequency- and Depth-Dependent Time-Of-Flight Distortion'
        }
    """
    paper_dict = {'title': dt.text.encode("utf-8"),
                  'supp': None}
    href = dd.find_all('a')[0]
    paper_dict['href'] = href.attrs['href']
    supp = dd.find_all('a')[1]
    if supp.text == 'supp':
        paper_dict['supp'] = supp.attrs['href']
    return paper_dict


def show_search_paper(diction):
    for paper in diction:
        print 'title: ' + paper['title']
        print 'href: ' + "http://openaccess.thecvf.com/" + paper['href']
        if paper['supp'] is not None:
            print 'supplement href: ' + "http://openaccess.thecvf.com/" + paper['supp']


def download_by_keyword(word, diction):
    """
    :param word:
    :param diction:
    :return:
    """
    total = len(diction)
    save_path = word + "_"+opt.conference+"_"+str(opt.year)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    js = 0
    if opt.download != 'detail':
        percent = str(js) + "/" + str(total)
        sys.stdout.write('downloading: ' + percent + '    \r')
        sys.stdout.flush()
    for paper in diction:
        js += 1
        percent = str(js) + "/" + str(total)
        if opt.download == 'detail':
            print "downloading   " + paper['title']
        download_by_url(paper['href'], "./" + save_path + "/" + paper['title'] + ".pdf", percent)
        if paper['supp'] is not None:
            download_by_url(paper['supp'], "./" + save_path + "/" + paper['title'] + "_supplement.pdf", percent)

    print "Done :  "+percent


def download_by_url(url, path, percent):
    """
    download content via given url
    :param url:  full url point to source
    :param path: save path
    :param percent: how much it finish
    :return: None
    """

    url = "http://openaccess.thecvf.com/" + url
    response1 = opener.open(url)
    content = response1.read()
    with open(path, 'wb') as save_file:
        save_file.write(content)
    # show different logo when operate is different
    if opt.download == 'detail':
        print "save " + path
    else:
        sys.stdout.write('downloading: '+percent+'    \r')
        sys.stdout.flush()


def main():
    diction = search_paper_list(word=opt.keyword)
    if opt.operate == 'download':
        download_by_keyword(word=opt.keyword, diction=diction)
    else:
        show_search_paper(diction=diction)

        # download_by_keyword(word='Designing Effective Inter', diction=diction)


if __name__ == "__main__":
    main()
