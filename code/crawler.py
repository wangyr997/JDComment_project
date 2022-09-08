"""
单个爬虫调度模块
"""

import data_saver
import html_parser
import html_visitor
import logging
import queue
import random
import threading
import time

class JDCrawler(object):
    """
    京东数据单个爬虫类
    """
    def __init__(self, config, seed_queue, comment_queue):
        self.config = config
        self.seed_queue = seed_queue
        self.comment_queue = comment_queue
        self.sleep_interval = self.config.getfloat("main", "sleep_interval")
        self.th_list = []
        self.res_file = "../output/jd_comment.db"

    def start(self):
        """
        开始爬虫
        """
        self.start_index_page()
        self.wait()
        logging.info("get_index_page finished (%s items), start getting comment page\n" % self.comment_queue.qsize())
        self.start_comment_page()

    def start_index_page(self):
        """
        开始处理索引页
        """
        self.load_index_cache()
        if self.comment_queue.qsize() > 0:
            return
        logging.info("seed_queue.qsize = %d" % self.seed_queue.qsize())
        html_queue = queue.Queue()
        html_queue2 = queue.Queue()  # 复制一份，用于解析网页内容
        content_queue = queue.Queue()
        self.th_list = [
            threading.Thread(target=get_html_thread,
                             args=(self.seed_queue, html_queue, self.res_file, self.sleep_interval)),
            threading.Thread(target=parse_html_thread,
                             args=(html_queue, self.comment_queue, html_queue2, self.res_file, html_parser.parser_index_page)),
            # 首页既可以解析索引页，也可以解析出首页的内容，减少重复访问
            # 解析源码线程
            threading.Thread(target=parse_html_thread,
                             args=(html_queue2, content_queue, None, self.res_file, html_parser.parser_comment_page)),
            # 保存关键信息线程
            threading.Thread(target=save_comment_thread, args=(content_queue, self.res_file))
        ]
        for th in self.th_list:
            th.start()

    def start_comment_page(self):
        """
        开始处理评论内容页面
        """
        html_queue = queue.Queue()
        content_queue = queue.Queue()
        self.th_list = [
            # 获取源码线程
            threading.Thread(target=get_html_thread,
                             args=(self.comment_queue, html_queue, self.res_file, self.sleep_interval)),
            # 解析源码线程
            threading.Thread(target=parse_html_thread,
                             args=(html_queue, content_queue, None, self.res_file, html_parser.parser_comment_page)),
            # 保存关键信息线程
            threading.Thread(target=save_comment_thread, args=(content_queue, self.res_file))
        ]
        for th in self.th_list:
            th.start()

    def wait(self):
        """
        等待所有过程完成
        """
        for th in self.th_list:
            th.join()

    def load_index_cache(self):
        """
        载入缓存中的索引页结果
        """
        mgr = data_saver.DataSaverMgr(self.res_file)
        index_cache = mgr.get_url_cache("index#%")
        if index_cache > 7000:
            for url, dt in mgr.get_url_cache("index#%", 0):
                self.comment_queue.put(url[6:])
            self.comment_queue.put(None)
            logging.info("load index cache(%d) succeed." % index_cache)



def get_html_thread(in_queue, out_queue, res_file, sleep_interval):
    """
    从 in_queue 队列取 URL 获取结果存放到 out_queue 队列
    """
    mgr = data_saver.DataSaverMgr(res_file)
    cnt = 0
    while not in_queue.empty():
        url = in_queue.get()
        try:
            if mgr.get_url_cache(url):
                logging.info("ignore url(%s): hit cache" % url)
                continue
            if not url:
                continue
            html = html_visitor.get(url).replace("\n", "\\n")
            data_saver.save_html_file(url, html, "data/html")
        except Exception as e:
            logging.error("visit %s failed: %s" % (url, e))
            continue
        out_queue.put((url, html))
        cnt += 1
        mgr.set_url_cache(url)
        if not in_queue.empty():
            time.sleep(sleep_interval + random.random())
    out_queue.put((None, None))  # 插入特殊元素，标记结果
    logging.info("get_html_thread finished, output %d items." % cnt)

def parse_html_thread(in_queue, out_queue, cp_queue, res_file, parse_func):
    """
    从 in_queue 队列获取源码解析后存放到 out_queue
    """
    mgr = data_saver.DataSaverMgr(res_file)
    cnt = 0
    while True:
        try:
            url, html = in_queue.get()
            if cp_queue:
                cp_queue.put((url, html))
            if not html:  # 结束标记元素
                break
            for res in parse_func(html):
                out_queue.put(res)
                cnt += 1
                if cp_queue:
                    mgr.set_url_cache("index#" + res)
        except Exception as e:
            logging.error("parse %s failded: %s" % (url, e))
    out_queue.put(None)
    logging.info("parse_html_thread finished, output %d items." % cnt)

def save_comment_thread(content_queue, res_file):
    """
    保存评论内容到 csv 文件或数据库
    """
    cnt = 0
    mgr = data_saver.DataSaverMgr(res_file)
    while True:
        try:
            content = content_queue.get()
            if not content:
                break
            mgr.save_row(content)
            cnt += 1
        except Exception as e:
            logging.error("save comment(%s) failed: %s" % (content, e))
    logging.info("save_comment_thread finished, output %d items" % cnt)
