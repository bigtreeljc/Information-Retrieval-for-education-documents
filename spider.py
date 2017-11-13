#!/usr/bin/python
import pickle
import urllib
import urllib2
import re
import logging
import copy
import os

class book_spider:
    def proxy_support(self):
        proxy_support = urllib2.ProxyHandler( {"http": "http://192.168.0.166:3128"} )
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

    def __init__(self):
        self.pickle_name = "keywords.pickle"
        self.keyword_entries = {}
        self.proxy_support()

        self.base_path = "/home/jlu/stored_courses/"
        if not os.path.isdir(self.base_path):
            os.mkdir(self.base_path)

        self.base_url = "http://www.dzkbw.com/"
        self.tag = "books/"
        self.versions = ["rjb/", "sjb/", "bsd/", "hjb/", "ljb/", "yjb/", "zjb"]
        self.courses = ["yuwen", "shuxue", "yingyu", "wuli",
                        "huaxue", "shengwu", "lishi", "zhengzhi", "dili"]
        for course in self.courses:
            self.keyword_entries[course] = []

        #self.courses = self.append_slash_to_url(self.courses)
        logging.debug(self.courses)
        self.nianji = ["yinianji-all", "ernianji-all", "sannianji-all", "sinianji-all", "wunianji-all", "liunianji-all",
                       "liunianji-all", "qinianji-all", "banianji-all", "jiunianji-all", "gaoyi-all",
                       "gaoer-all", "gaosan-all"]
        self.crawed_urls_by_version_course = {}

        for version in self.versions:
            self.crawed_urls_by_version_course[version] = {}
            for course in self.courses:
                self.crawed_urls_by_version_course[version][course] = []

        # url = base_url + tag + versions + [course|nianji]
    def get_url_content(self, url, course, version):
        logging.info("get data from page " + url)
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        return response.read().decode('gbk'), course, version

    def append_slash_to_url(self, tags):
        ret = []
        for i in range(len(tags)):
            ret.append(tags[i] + "/")
        strs = str()
        for ss in ret:
            strs += ss + " "
        #logging.DEBUG("ret = " + strs)
        return ret

    def get_course_urls(self, content, course, version):
        '''
        Example:
        <LI><A href="/books/rjb/shuxue/xs5x_new/" title="" target=_blank></A></LI>
        '''
        reg_exp = "<A  class=\"ih3\" href=\"([^\"]+)\" title=\"([^\"]+)\"  target=_blank>([^<]+)</A>"
        pattern = re.compile(
            reg_exp,
            re.S)
        items = re.findall(pattern, content)

        for item in items:
            self.crawed_urls_by_version_course[version][course].append((item[0], item[1], item[2]))

    def get_course_content_by_url(self):
        '''
        :return: 
        '''
        os.chdir(self.base_path)
        for course in self.courses:
            if not os.path.isdir(course):
                os.mkdir(course)
            os.chdir(course)
            for version in self.versions:
                if not os.path.isdir(version):
                    os.mkdir(version)
                os.chdir(version)
                for book_url, fullname, small_name in self.crawed_urls_by_version_course[version][course]:
                    self.store_appendix_from_book_url_pwd(book_url, version, course, fullname)
                    break
                os.chdir("../")
            os.chdir(self.base_path)

    def store_appendix_from_book_url_pwd(self, book_url, version, course, course_name):
        if book_url.startswith("/books"):
            book_url = self.base_url + book_url[1:] if book_url[0] == '/' else book_url
        #print book_url
        response = self.get_url_content(book_url, version, course)
        response = str(response)
        #print response.decode('unicode_escape')
        reg_exp_content = "<a href=\"([^\"]+)\">([^<]+)</a><BR>"
        reg_exp_highlight = "<a href=\"([^\"]+)\"><B>([^<]+)</B></a><BR>"
        pattern_content = re.compile(
            reg_exp_content,
            re.S)
        items_content = re.findall(pattern_content, response)
        pattern_highlight = re.compile(
            reg_exp_highlight,
            re.S)
        items_highlight = re.findall(pattern_highlight, response)
        self.persist(items_highlight, items_content, version, course, course_name)

    def filter(self, entries):
        return entries

    def persist(self, items_highlight, items_content, version, course, course_name):
        f_name = course_name
        if os.path.exists(f_name):
            os.remove(f_name)
        f = open(f_name, 'w')
        for item in items_highlight + items_content:
            #print item[0], item[1]
            self.keyword_entries[course].append(item[1])
            f.write(item[1] + '\n')
            # eascaped_str = str(item[1]).decode('unicode_escape')

        os.chdir(self.base_path)
        self.persist_as_pickle()

    def persist_as_pickle(self):
        self.filter(self.keyword_entries)
        os.chdir(self.base_path)
        pickle_file = open(self.pickle_name, 'w')
        pickle.dump(self.keyword_entries, pickle_file, True)
        pickle_file.close()

def test_api():
    logging.basicConfig(level=logging.DEBUG)
    spider = book_spider()
    test_url = spider.base_url + spider.tag + spider.versions[0] + spider.courses[0]
    version = spider.versions[0]
    course = spider.courses[0]
    respond, c, v = spider.get_url_content(test_url, course, version)
    spider.get_course_urls(respond, c, v)
    logging.debug("spider_size " + str(len(spider.crawed_urls_by_version_course[v][c])))
    spider.get_course_content_by_url()
    #print respond
    # test complete

def ir_url(url, version, course, spider):
    respond, c, v = spider.get_url_content(url, course, version)
    spider.get_course_urls(respond, c, v)
    logging.debug("spider_size " + str(len(spider.crawed_urls_by_version_course[v][c])))
    spider.get_course_content_by_url()

def get_all_url(base_url, tag, version, course):
    head = base_url + tag
    ret = []
    for v in version:
        for c in course:
            ret.append( (head + v + c, v, c) )
    logging.debug("Got %d urls" % (len(ret)))
    return ret

def get_dataset():
    logging.basicConfig(level=logging.DEBUG)
    spider = book_spider()
    base_url = spider.base_url
    tag = spider.tag
    version = spider.versions[:4]
    course = spider.courses

    urls_tuple = get_all_url(base_url, tag, version, course)

    for i, url_t in enumerate(urls_tuple):
        logging.debug( "---- %dth iteration for url %s ----" %(i, url_t[0]) )
        url = url_t[0]
        version = url_t[1]
        course = url_t[2]

        ir_url(url, version, course, spider)

if __name__ == "__main__":
    get_dataset()