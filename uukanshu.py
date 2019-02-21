from requests import Response
import os, io
from bs4 import BeautifulSoup
import threading
import re, time

SITE = "https://www.uukanshu.com/"


def parse_menu(content: Response):
    soups = BeautifulSoup(content, "html5lib")
    chapter_list = soups.select("#chapterList li")
    print(len(chapter_list))
    chapter_list.reverse()
    print(len(chapter_list))
    return "None"
