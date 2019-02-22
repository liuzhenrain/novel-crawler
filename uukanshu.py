from requests import Response
import os, io
from bs4 import BeautifulSoup
import threading
import re, time

SITE = "https://www.uukanshu.com/"


def parse_menu(content: str):
    soups = BeautifulSoup(content, "html5lib")
    title: str = soups.find("span", class_="show").text
    cTitle = title.replace("手机阅读", "")
    chapter_list = soups.select("#chapterList li a")
    chapter_list.reverse()
    return cTitle, chapter_list


def parse_content(content: str):
    soups = BeautifulSoup(content, "html5lib")
    section_text = soups.find("div", id='contentbox')
    for ss in section_text.select("script"):
        ss.decompose()
    text = re.sub('\s+', '\r\n\t', section_text.text).strip('\r\n')
    return text
