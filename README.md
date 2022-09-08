# JDComment_project

## Data mining and analysis of JD product comments.

### 项目结构

```
JDComment_project
└─── code
│   │   config_loader.py  配置读取模块
│   │   crawler.py  单个爬虫调度模块
│   │   data_saver.py  数据存储模块
│   │   export_data_from_cache.py  可以从缓存文件导出更多字段
│   │   html_parser.py  网页解析模块
│   │   html_visitor.py  网页访问模块
│   │   jd_spider.py  总调度模块
│   
└─── config  配置文件
│   │   seed_list.txt
│   │   setting.conf
│   │   user_agent_list.txt
│
└─── data  缓存文件
│   └─── html
│       │   pid100008847233.score0
│       │   pid100008847233.score1
│       │   ...
│   
└─── output
│   │   after_analysis.csv
│   │   jd_comment.db
│   │   jd_comment_data.csv
│   │   test.csv
│   │   test.db
│
│    README.md
│    jd_analysis.ipynb  数据分析
│    stop_word.txt  停用词表
```
