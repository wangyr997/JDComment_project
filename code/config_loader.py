"""
配置读取模块
"""

import configparser
import io
import logging
import os
import random

user_agent_list = []

def load_config(ini_path):
    """
    载入ini配置文件
    """
    cfg = configparser.ConfigParser()
    # 检查文件是否存在
    if not os.path.exists(ini_path):
        logging.error("config file '%s' not exist" % ini_path)
        return None
    cfg.read(ini_path)
    return cfg

def load_seed(f_seed):
    """
    载入种子文件，生成种子链接，以迭代器方式返回
    """
    with io.open(f_seed) as f_in:
        for seed_url in f_in:
            if seed_url.strip() == "" or seed_url.startswith("#"):
                continue
            yield seed_url.strip()

def get_ua(f_user_agent):
    """
    随即返回一个user_agent
    """
    global user_agent_list
    if not user_agent_list:
        with io.open(f_user_agent) as f_ua:
            for ln in f_ua:
                user_agent_list.append(ln.strip())
    return random.choice(user_agent_list)

if __name__ == "__main__":
    cfg = load_config("../config/setting.conf")
    print(cfg.get("file", "seed_file"))
    print(cfg.get("main", "sleep_interval"))

    print("测试load_seed")
    # 测试load_seed
    for url in load_seed(cfg.get("file", "seed_file")):
        print(url)

    print("\n测试get_ua")
    for _ in range(3):
        print(get_ua(cfg.get("file", "user_agent_file")))
