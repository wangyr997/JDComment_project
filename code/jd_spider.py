"""
总调度模块
"""

import config_loader
import crawler
import html_parser
import logging
import queue

class JDSpider(object):
    """
    京东数据总调度模块
    """
    def __init__(self, config):
        self.config = config
        self.seed_queue = queue.Queue()
        self.comment_queue = queue.Queue()
        self.crawlers = []
        self.craw_num = self.config.getint("main", "crawler_number")
        for _ in range(self.craw_num):
            self.crawlers.append(crawler.JDCrawler(self.config, self.seed_queue, self.comment_queue))

    def start(self):
        """
        启动爬虫
        """
        for seed in config_loader.load_seed(self.config["file"]["seed_file"]):
            pid = seed.rsplit("/")[-1].split(".")[0]
            self.seed_queue.put(html_parser.URL_PATTERN.format(pid=pid, score=0, t_sort=5, page=0))
        # 开始执行爬虫
        for craw in self.crawlers:
            craw.start()

    def wait(self):
        """
        等待所有爬虫单元结束
        """
        for craw in self.crawlers:
            craw.wait()

def main(cfg_path):
    # 载入配置
    config = config_loader.load_config(cfg_path)
    if not config:
        logging.critical("config load failed")
        return 1
    # 初始化
    spider = JDSpider(config)
    spider.start()
    spider.wait()

if __name__ == "__main__":
    fmt_str = "%(levelname)s: %(asctime)s - %(filename)s:L%(lineno)d:%(funcName)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt_str)
    main("setting.conf")