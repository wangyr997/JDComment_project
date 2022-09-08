"""
网页访问模块
"""

import config_loader
from fake_useragent import UserAgent
import requests
import retry
import time

from selenium import webdriver

web_browser_driver = None

def get_selenium_driver_source(url, call_func=None):
    """
    用浏览器模拟打开指定页面并返回源码
    """
    global web_browser_driver
    if web_browser_driver is None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 开启实验性功能
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")  # 去除特征值
        #options.add_argument('user-agent=%s' % UserAgent().random)

        web_browser_driver = webdriver.Chrome(options=options)  # 获取谷歌浏览器的driver

        web_browser_driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": '''
          Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }
          '''
        })

        requests.adapters.DEFAULT_RETERIES = 5  # 默认重试次数
        requests.packages.urllib3.disable_warnings()
        s = requests.sessions()
        s.keep_alive = False
        web_browser_driver.get("https://jd.com")
        print("wait for login, then press y")
        while input().strip() != "y":
            pass
    web_browser_driver.get(url)
    if callable(call_func):
        call_func()
    return web_browser_driver.page_source  # .decode("utf-8")

def get_html(url, headers, user_selenium=False, call_func=None):
    """
    获取指定网站的源码
    """
    if user_selenium:
        return get_selenium_driver_source(url, call_func)
    else:
        return requests.get(url, headers=headers).text

@retry.retry(tries=5, delay=3, backoff=2)
def get(url):
    """
    调用requests.get获取网页源码
    """
    ua = UserAgent()
    headers = {
        "accept": "*/*",
        "user-agent": ua.random,
        #"user-agent": config_loader.get_ua(f_user_agent),
        "referer": "https://item.jd.com/",
    }
    html = get_html(url, headers, True)
    if len(html) < 100:
        raise Exception("unexpected response: %s" % html[:200])
    return html

def test_get():
    """
    测试 get 函数
    """
    url = "https://search.jd.com/Search?keyword=%E4%BA%AC%E5%93%81%E5%AE%B6%E7%94%B5%E7%A9%BA%E8%B0%83&enc=utf-8"
    html = get(url)
    import re
    for i in re.findall('href="//(item.jd.com/1000\d+.html)#comment"', html):
        print("https://" + i)


if __name__ == "__main__":
    test_get()