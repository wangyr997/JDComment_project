"""
网页解析模块
"""

import json
import logging

URL_PATTERN = "https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98"\
              "&productId={pid}&score={score}&sortType={t_sort}&page={page}&pageSize=10&isShadowSku=0&rid=0&fold=1"

def parser_index_page(html):
    """
    解析索引页
    """
    def _gen_url(pid, score, sort_type, max_page):
        url_list = []
        for pg in range(max_page):
            url_list.append(URL_PATTERN.format(pid=pid, score=score, t_sort=sort_type, page=pg))
        return url_list

    res = json.loads(html[html.find('{'):-16])  # 取到{...}
    pid = res["productCommentSummary"]["productId"]
    comment_urls = []
    if res["maxPage"] < 100:
        return _gen_url(pid, 0, 5, res["maxPage"])
    for i in range(1, 6):
        n_score_i = res["productCommentSummary"]["score%dCount" % i]
        if n_score_i <= 1000:
            comment_urls.extend(_gen_url(pid, i, 5, (n_score_i + 9) // 10))
        else:
            comment_urls.extend(_gen_url(pid, i, 5, 100))
            comment_urls.extend(_gen_url(pid, i, 6, 100))
    return comment_urls

def parser_comment_page(html, keys=None):
    """
    解析评论内容
    """
    res = json.loads(html[html.find('{'):html.find('null});')+len('null}')])
    pid = str(res["productCommentSummary"]["productId"])
    if not keys:
        keys = "id,content,referenceTime,usefulVoteCount,replyCount,score,creationTime,referenceName".split(",")
    comment_list = []
    for comm in res["comments"]:
        comment_list.append([pid] + list(str(comm[k]) for k in keys))
    return comment_list

def test_parse_index_page():
    """
    测试 parser_index_page 函数
    """
    url = "https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=100019386660&score=0&sortType=5&page=7&pageSize=10&isShadowSku=0&rid=0&fold=1"
    import html_visitor
    html = html_visitor.get(url)
    print(parser_index_page(html)[:10])

def test_parser_comment_page():
    """
    测试 parser_comment_page 函数
    """
    url = "https://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98&productId=100019386660&score=0&sortType=5&page=7&pageSize=10&isShadowSku=0&rid=0&fold=1"
    import html_visitor
    html = html_visitor.get(url)
    print(parser_comment_page(html))

if __name__ =="__main__":
    test_parse_index_page()
    #test_parser_comment_page()