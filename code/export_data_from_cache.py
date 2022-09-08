"""
从缓存文件导出更多字段
"""

import csv
import data_saver
import glob
import html_parser
import io
import logging
import sys

SCHEMA = u"商品ID,用户ID,会员等级,总打分数,总回复数,购买时间,评论时间,评论天数间隔,打分,商品名称,评论内容".split(",")
# 商品ID自动写入，无需添加到key
KEYS = "id,plusAvailable,usefulVoteCount,replyCount,referenceTime,creationTime,days,score,referenceName,content".split(",")

def export_data(f_path):
    """
    导出数据
    """
    mgr = data_saver.DataSaverMgr("jd_comment_data.csv", schema=SCHEMA)
    for fname in glob.glob(f_path):
        logging.info("loading " + fname)
        with open(fname, encoding='utf-8') as f_in:
            for ln in f_in:
                for comment in html_parser.parser_comment_page(ln.strip(), KEYS):
                    mgr.save_row(comment)

if __name__ == "__main__":
    fmt_str = "%(levelname)s: %(asctime)s - %(filename)s:L%(lineno)d:%(funcName)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt_str)
    export_data("".join(sys.argv[1:2]) or "data/html/*")