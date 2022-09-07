"""
数据存储模块
"""

import csv
import io
import logging
import os
import sqlite3
import time

class DataSaverMgr(object):
    """
    数据保存管理类
    """
    def __init__(self, f_name, fmt="db", schema=None):
        # 判断文件是否存在
        is_file_exist = os.path.exists(f_name)
        # 创建目标文件，生成操作目标
        if fmt == "csv" or f_name.endswith(".csv"):
            self.__fmt = "csv"
            self.__handle = io.open(f_name, "a+", encoding="utf-8", newline='')
            self.cur = csv.writer(self.__handle)
        else:
            if fmt != "db":
                logging.warning("fmt must be 'db' or 'csv', default to 'db'")
            self.__fmt = "db"
            self.__handle = sqlite3.connect(f_name)
            self.__tb_name = "comment_info"
            self.cur = self.__handle.cursor()
        # 写入表头
        if not schema:
            self.schema = u"商品ID,用户ID,评论内容,购买时间,点赞数,回复数,打分,评论时间,型号".split(",")
        else:
            self.schema = schema
        self.s_type = "integer,integer,text,datetime,integer,integer,integer,datetime,varchar(128)".split(",")
        if not is_file_exist:
            self.__save_header()


    def __del__(self):
        self.__handle.close()

    def __exec(self, sql, level=logging.DEBUG):
        logging.log(level, "run: " + sql)
        self.cur.execute(sql)
        self.__handle.commit()

    def __save_header(self):
        if self.__fmt == "csv":
            self.cur.writerow(self.schema)
        else:
            fields = ", ".join("%s %s" % (i[0], i[1]) for i in zip(self.schema, self.s_type))
            sql = """create table if not exists %s(id integer primary key autoincrement, %s)""" % (self.__tb_name, fields)
            self.__exec(sql)
            sql = """create table if not exists url_cache(url varchar (256) primary key, update_time)"""
            self.__exec(sql)

    def save_row(self, data_row):
        """
        保存一行数据，即一条记录
        """
        if self.__fmt == "csv":
            logging.debug("insert record: %s" % data_row)
            self.cur.writerow(data_row)
        else:
            sql = "insert into %s('%s') values('%s')" % (self.__tb_name, "','".join(self.schema), "','".join(data_row))
            self.__exec(sql)

    def get_url_cache(self, url, ret_count=True):
        """
        ret_count=True 时，返回一条 URL 是否在 cache 中已存在
        否则返回命中结果
        """
        if self.__fmt == "csv":
            return False
        if not ret_count:
            sql = "select * from url_cache where url like '%s'" % url
            return self.__exec(sql)
        sql = "select count(*) from url_cache where url like '%s'" % url
        self.__exec(sql)
        res = self.cur.fetchone()
        return res and res[0]

    def set_url_cache(self, url):
        """
        保存一条 URL cache，即访问过的 URL
        """
        if self.__fmt == "csv":
            return
        cur_time = time.strftime("%Y/%m/%d %H:%M:%S")
        sql = "insert into url_cache('url', 'update_time') values('%s', '%s')" % (url, cur_time)
        self.__exec(sql)

def save_html_file(url, html, path):
    """
    保存 URL 对应源码 HTML 到 path 目录的文件中
    """
    if not os.path.exists(path):
        os.makedirs(path)
    args = dict([i.split("=") for i in url.split("?", 1)[1].split("&")])
    f_name = "pid%s.score%s" % (args["productId"], args["score"])
    with io.open("%s/%s" % (path, f_name), "a", encoding="utf-8") as f_w:
        f_w.write("page:%s sort_type:%s\t%s\n" % (args["page"], args["sortType"], html))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    mgr = DataSaverMgr("test.csv")
    mgr.save_row(list(map(str, range(1, 10))))

    mgr = DataSaverMgr("test.db")
    mgr.save_row(list(map(str, range(1, 10))))
