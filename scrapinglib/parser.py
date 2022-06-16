# -*- coding: utf-8 -*-

import json
import re
from lxml import etree, html

from . import httprequest
from .utils import getTreeElement, getTreeAll

class Parser:
    """ 基础刮削类
    """
    source = 'base'
    # poster: `0` 复制 `1` 裁剪 
    imagecut = 1
    uncensored = False
    allow_number_change = False
    # update
    proxies = None
    verify = None
    extraheader = None
    cookies = None
    morestoryline = False

    number = ''
    detailurl = ''
    # xpath expr
    expr_number = ''
    expr_title = ''
    expr_studio = ''
    expr_studio2 = ''
    expr_runtime = ''
    expr_runtime2 = ''
    expr_release = ''
    expr_outline = ''
    expr_director = ''
    expr_actor = ''
    expr_tags = ''
    expr_label = ''
    expr_label2 = ''
    expr_series = ''
    expr_series2 = ''
    expr_cover = ''
    expr_cover2 = ''
    expr_smallcover = ''
    expr_extrafanart = ''
    expr_trailer = ''
    expr_actorphoto = ''
    expr_uncensored = ''
    expr_userrating = ''
    expr_uservotes = ''

    def __init__(self) -> None:
        pass

    def scrape(self, number, core: None):
        """ 刮削番号
        """
        self.updateCore(core)
        result = self.search(number)
        return result

    def search(self, number):
        self.number = number
        self.detailurl = self.queryNumberUrl(number)
        htmltree = self.getHtmlTree(self.detailurl)
        result = self.dictformat(htmltree)
        return result

    def updateCore(self, core):
        """ 从`core`内更新参数
        
        针对需要传递的参数: cookies, proxy等
        子类继承后修改
        """
        if core.proxies:
            self.proxies = core.proxies
        if core.verify:
            self.verify = core.verify
        if core.morestoryline:
            self.morestoryline = True

    def queryNumberUrl(self, number):
        """ 根据番号查询详细信息url
        
        备份查询页面,预览图可能需要
        """
        url = httprequest.get(number)
        return url

    def getHtml(self, url, type = None):
        """ 访问网页
        """
        resp = httprequest.get(url, cookies=self.cookies, proxies=self.proxies, extra_headers=self.extraheader, verify=self.verify, return_type=type)
        if '<title>404 Page Not Found' in resp \
            or '<title>未找到页面' in resp \
            or '404 Not Found' in resp \
            or '<title>404' in resp \
            or '<title>お探しの商品が見つかりません' in resp:
            return 404
        return resp

    def getHtmlTree(self, url, type = None):
        """ 访问网页,返回`etree`
        """
        resp = self.getHtml(url, type)
        if resp == 404:
            return 404
        ret = etree.fromstring(resp, etree.HTMLParser())
        return ret

    def dictformat(self, htmltree):
        try:
            dic = {
                'number': self.getNum(htmltree),
                'title': self.getTitle(htmltree),
                'studio': self.getStudio(htmltree),
                'year': self.getYear(htmltree),
                'outline': self.getOutline(htmltree),
                'runtime': self.getRuntime(htmltree),
                'director': self.getDirector(htmltree),
                'actor': self.getActors(htmltree),
                'release': self.getRelease(htmltree),
                'cover': self.getCover(htmltree),
                'cover_small': self.getSmallCover(htmltree),
                'extrafanart': self.getExtrafanart(htmltree),
                'trailer': self.getTrailer(htmltree),
                'imagecut': self.imagecut,
                'tag': self.getTags(htmltree),
                'label': self.getLabel(htmltree),
                'actor_photo': self.getActorPhoto(htmltree),
                'website': self.detailurl,
                'source': self.source,
                'series': self.getSeries(htmltree),
                'uncensored': self.getUncensored(htmltree),
                'userrating': self.getUserRating(htmltree),
                'uservotes': self.getUserVotes(htmltree)
            }
            dic = self.extradict(dic)
        except Exception as e:
            print(e)
            dic = {"title": ""}
        js = json.dumps(dic, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        return js

    def extradict(self, dic:dict):
        """ 额外修改dict
        """
        return dic

    def getNum(self, htmltree):
        """ 增加 strip 过滤
        """
        return self.getTreeElement(htmltree, self.expr_number)

    def getTitle(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_title).strip()

    def getRelease(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_release).strip().replace('/','-')

    def getYear(self, htmltree):
        """ year基本都是从release中解析的
        """
        try:
            release = self.getRelease(htmltree)
            return str(re.findall('\d{4}', release)).strip(" ['']")
        except:
            return release

    def getRuntime(self, htmltree):
        return self.getTreeElementbyExprs(htmltree, self.expr_runtime, self.expr_runtime2).strip().rstrip('mi')

    def getOutline(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_outline).strip()

    def getDirector(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_director).strip()

    def getActors(self, htmltree) -> list:
        return self.getTreeAll(htmltree, self.expr_actor)

    def getTags(self, htmltree) -> list:
        alls = self.getTreeAll(htmltree, self.expr_tags)
        return [ x.strip() for x in alls if x.strip()]

    def getStudio(self, htmltree):
        return self.getTreeElementbyExprs(htmltree, self.expr_studio, self.expr_studio2)

    def getLabel(self, htmltree):
        return self.getTreeElementbyExprs(htmltree, self.expr_label, self.expr_label2)

    def getSeries(self, htmltree):
        return self.getTreeElementbyExprs(htmltree, self.expr_series, self.expr_series2)

    def getCover(self, htmltree):
        return self.getTreeElementbyExprs(htmltree, self.expr_cover, self.expr_cover2)

    def getSmallCover(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_smallcover)

    def getExtrafanart(self, htmltree) -> list:
        return self.getTreeAll(htmltree, self.expr_extrafanart)

    def getTrailer(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_trailer)

    def getActorPhoto(self, htmltree) -> dict:
        return {}

    def getUncensored(self, htmlree) -> bool:
        if self.expr_uncensored:
            u = self.getTreeAll(htmlree, self.expr_uncensored)
            return bool(u)
        else:
            return self.uncensored

    def getUserRating(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_userrating)

    def getUserVotes(self, htmltree):
        return self.getTreeElement(htmltree, self.expr_uservotes)

    def getTreeElement(self, tree: html.HtmlElement, expr, index=0):
        """ 根据表达式从`xmltree`中获取匹配值,默认 index 为 0
        """
        return getTreeElement(tree, expr, index)

    def getTreeAll(self, tree: html.HtmlElement, expr):
        """ 根据表达式从`xmltree`中获取全部匹配值
        """
        return getTreeAll(tree, expr)

    def getTreeElementbyExprs(self, tree: html.HtmlElement, expr, expr2=''):
        """ 多个表达式获取element
        使用内部的 getTreeElement 防止继承修改后出现问题
        """
        try:
            first = self.getTreeElement(tree, expr).strip()
            if first:
                return first
            second = self.getTreeElement(tree, expr2).strip()
            if second:
                return second
            return ''
        except:
            return ''

    def getTreeAllbyExprs(self, tree: html.HtmlElement, expr, expr2=''):
        """ 多个表达式获取所有element
        合并并剔除重复元素
        """
        try:
            result1 = self.getTreeAll(tree, expr)
            result2 = self.getTreeAll(tree, expr2)
            clean = [ x.strip() for x in result1 if x.strip() and x.strip() != ',']
            clean2 = [ x.strip() for x in result2 if x.strip() and x.strip() != ',']
            result =  list(set(clean + clean2))
            return result
        except:
            return []