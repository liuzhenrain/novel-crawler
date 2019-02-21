import os, random, time, datetime
import getProxy
import uukanshu
import requests
import urllib.parse

req_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'fcip=111; ASP.NET_SessionId=wufktsfuinko3v1k5l15iqto; lastread=5366%3D30159%3D%u4E00%20%u751F%u6B7B%u52FF%u8BBA',
    'DNT': '1',
    'Host': 'www.uukanshu.com',
    'Referer': 'https://www.google.com/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}

novel_netloc = [
    "www.uukanshu.com",
    "www.qu.la",
]

UUKANSHU_SITE = "https://www.uukanshu.com/"
UU_TYPE = "1"
PROXIES = list()


def __get_menu_url(novel_site, menu_page_no):
    menu_url = ""
    if novel_site == UU_TYPE:
        menu_url = UUKANSHU_SITE + '/b/' + menu_page_no
    return menu_url


def _get_menu_parse_func(novel_site):
    if novel_site == UU_TYPE:
        return uukanshu.parse_menu


def _parse_menu(novel_site, menu_url):
    menu_page = requests.get(menu_url, headers=req_header)
    menu_parse_func = _get_menu_parse_func(novel_site)
    return menu_parse_func(menu_page)


def get_text(novel_site: str, menu_page: str):
    fp = open('proxies.txt', 'r')
    ips = fp.readlines()
    for p in ips:
        proxy = {"proxy": p}
        PROXIES.append(proxy)
    menu_url = __get_menu_url(novel_site, menu_page)
    chapter_dic = _parse_menu(novel_site, menu_url)


def get_novel(novel_index: int, url: str):
    r = requests.get(url, headers=req_header)
    if r.status_code == requests.codes.get('ok'):
        if novel_index == 0:  # 悠悠看书
            novel_chapter = uukanshu.parse_menu(r.text)
        elif novel_index == 1:  # 笔趣阁
            pass
    else:
        print("检查你的网络是否能正常访问你输入的网址", url)
        exit(0)


if __name__ == "__main__":
    novel_site = input("请输入小说目录页地址：")
    url = urllib.parse.urlparse(novel_site)
    netloc_index = 0
    if url.netloc in novel_netloc:
        netloc_index = novel_netloc.index(url.netloc)
    else:
        print("此工具暂时不支持 悠悠看书 [www.uukanshu.com],笔趣阁[www.qu.la]以外的网站")
        exit(0)
    if not os.path.exists('proxies.txt'):
        print("开始更新代理信息")
        getProxy.start_get_proxy()
    ModifiedTime = time.localtime(os.stat('proxies.txt').st_mtime)
    cur_time = datetime.datetime.now()
    mtime = datetime.datetime(ModifiedTime.tm_year, ModifiedTime.tm_mon, ModifiedTime.tm_mday)
    if (cur_time - mtime).days > 10:
        print("代理文件已经过期，现在开始更新代理文件")
        getProxy.start_get_proxy()
    get_novel(novel_index=netloc_index, url=novel_site)
