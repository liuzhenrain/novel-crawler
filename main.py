import os, time, datetime
import getProxy
import uukanshu
import requests
import urllib.parse
import threading

req_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
}

novel_netloc = [
    "www.uukanshu.com",
    "www.qu.la",
]

novel_location = [
    "https://www.uukanshu.com/"
]

UUKANSHU_SITE = "https://www.uukanshu.com/"
UU_TYPE = "1"
PROXIES = []
proxy_file = "proxies.txt"
novel_title = ""
MAX_THREAD_COUNT = 30


def get_content_thread(chapter_index, c_title: str, url: str, callback):
    base_url = novel_location[netloc_index]
    abs_path = urllib.parse.urljoin(base_url, url)
    proxy = PROXIES.pop().strip()
    print("小说 {0} 章节 《 {1} 》正在下载\n".format(novel_title, c_title))
    r = requests.get(abs_path, proxies={"http": proxy})
    if r.ok:
        PROXIES.append(proxy)
        if netloc_index == 0:
            text = uukanshu.parse_content(r.text)
            print("小说 {0} 《 {1} 》下载完成\n".format(novel_title, c_title))
        elif netloc_index == 1:
            pass

        data = {
            'title': c_title,
            'content': text
        }
        callback(chapter_index, data)
    else:
        print("小说 {0} 章节 《 {1} 》下载失败，重新开始\n".format(novel_title, c_title))
        get_content_thread(url)


def save_novel(n_name: str, content_list: {}):
    fp = open(n_name + ".txt", "ab+")
    fp.flush()
    fp.write((n_name + "\r\n").encode("UTF_8"))
    content_length = len(content_list.items())
    for index in range(0, content_length):
        if str(index) in content_list.keys():
            data = content_list.get(str(index))
            c_title: str = data['title']
            fp.write((c_title + "\r\n").encode("UTF-8"))
            fp.write((data['content'] + "\r\n").encode("UTF-8"))
    fp.close()


def get_novel_text(chapter_list: []):
    global PROXIES
    PROXIES = open(proxy_file, "r").readlines()
    content_pool = []

    novel_content_list = {}

    def save_novel_text(c_index, data):
        novel_content_list[str(c_index)] = data

    # 为了方便线程里面能够拿到下标数值
    chapter_dic = {}
    for i in range(len(chapter_list)):
        chapter_dic[str(i)] = chapter_list[i]

    def get_charpter():
        if (len(chapter_dic.items()) > 0):
            chapter = chapter_dic.popitem()
            chapter_index = int(chapter[0])
            href = chapter[1]['href']
            c_title = chapter[1].text
            title_array = c_title.split(" ")
            _start = title_array[0].startswith("第")
            _end = title_array[0].endswith("章")
            if not _start and not _end:
                title_array[0] = "第{0}章".format(chapter_index + 1)
            if not _start and _end:
                title_array[0] = "第" + title_array[0]
            if _start and not _end:
                title_array[0] = title_array[0] + "章"
            c_title = " ".join(title_array)
            get_content_thread(chapter_index, c_title, href, save_novel_text)
            get_charpter()
        else:
            return None

    for i in range(0, MAX_THREAD_COUNT):
        t = threading.Thread(target=get_charpter)
        content_pool.append(t)
        t.start()

    for t in content_pool:
        t.join()

    save_novel(novel_title, novel_content_list)


def get_novel(url: str):
    r = requests.get(url, headers=req_header)
    if r.status_code == requests.codes.get('ok'):
        if netloc_index == 0:  # 悠悠看书
            global novel_title
            novel_title, novel_chapter_list = uukanshu.parse_menu(r.text)
        elif netloc_index == 1:  # 笔趣阁
            pass
        get_novel_text(novel_chapter_list)
    else:
        print("检查你的网络是否能正常访问你输入的网址", url)
        exit(0)


if __name__ == "__main__":
    novel_site = input("请输入小说目录页地址：")
    # novel_site = 'https://www.uukanshu.com/b/84182/'
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
    get_novel(novel_site)
