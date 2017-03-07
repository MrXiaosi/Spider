# coding : utf-8

import scrapy
import urllib2
import re
import lxml.html as HTML

class SinaSpider():
    '''
        sina spider
    '''
    start_url = ""
    url_pool_info = []
    url_pool_follows = []
    url_pool_fans = []

    def __init__(self, start_url):
        p = re.compile("http://weibo.com/p/\d+/info")
        match = p.findall(start_url)
        if 1 == len(match):
            self.start_url = start_url
        else:
            self.start_url = ""

    def start(self):
        '''
            start spider
        '''
        self.__catch_person_info(self.start_url)
    
    def __catch_page_id(self, url):
        '''
            get page_id
        '''
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        text = response.read()
        
        page_id_start = text.find("['page_id']=")
        page_id_end = text.find("';", page_id_start)
        page_id = text[page_id_start+13:page_id_end]
        # fans_page_url = "http://weibo.com/p/" + page_id + "/follow?relate=fans&"
        # follow_page_url = "http://weibo.com/p/" + page_id + "/follow?"
    
        return page_id

    def __catch_person_info(self, url):
        '''
            catch person info
        '''
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        text = response.read()

        # get page_id
        page_id_start = text.find("['page_id']=")
        page_id_end = text.find("';", page_id_start)
        page_id = text[page_id_start+13:page_id_end]

        fans_page_url = "http://weibo.com/p/" + page_id + "/follow?relate=fans&"
        follow_page_url = "http://weibo.com/p/" + page_id + "/follow?"

        # get script code contains person infomation
        html = ""
        p = re.compile("<script>FM.view.*</script>")
        match = p.findall(text)
        for eachFm in match:
            if "Pl_Official_PersonalInfo__58" in eachFm and \
                "main_title W_fb W_f14" in eachFm:
                index = eachFm.find("html")
                eachFm = eachFm[index+9:-12]
                eachFm = self.js_fmview2html(eachFm)
                html = eachFm
                break

        doc = HTML.fromstring(unicode(html, "utf-8"))

        # get person infomation
        data_1 = doc.xpath(
            '//div[1][@class="WB_cardwrap S_bg2"]//div[@class="PCD_text_b PCD_text_b2"]//' + \
                'div[@class="WB_innerwrap"]//div//ul'
        )
        if 0 == len(data_1):            # no found
            return
        
        name = data_1[0].xpath('li[1]//span[2]/text()')
        address = data_1[0].xpath('li[2]//span[2]/text()')
        sex = data_1[0].xpath('li[3]//span[2]/text()')
        blog = data_1[0].xpath('li[4]//a/text()')
        brif_introduction = data_1[0].xpath('li[6]//span[2]/text()')
        create_time = data_1[0].xpath('li[7]//span[2]/text()')

        print name[0] if 0!=len(name) else ""
        print address[0] if 0!=len(address) else ""
        print sex[0] if 0!=len(sex) else ""
        print blog[0] if 0!=len(blog) else ""
        print brif_introduction[0].strip() if 0!=len(brif_introduction) else ""
        print create_time[0].strip() if 0!=len(create_time) else ""

        self.__catch_follows(fans_page_url)

    def __catch_follows(self, url):
        '''
            catch follows uid, and make their infomation url
        '''
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        text = response.read()

        # get script code about follows
        html = ""
        p = re.compile("<script>FM.view.*</script>")
        match = p.findall(text)
        for eachFm in match:
            if "followTab" in eachFm:
                index = eachFm.find("html")
                eachFm = eachFm[index+7:-12]
                eachFm = self.js_fmview2html(eachFm)
                html = eachFm
                break

        doc = HTML.fromstring(unicode(html, "utf-8"))
        data = doc.xpath('//li[@class="follow_item S_line2"]/@action-data')

        # get person info url
        for i in data:
            # print i
            s = i.split("&")
            uid = s[0][4:]
            main_url = "http://weibo.com/u/" + uid
            info_url = "http://weibo.com/p/" + self.__catch_page_id(main_url) + "/info"
            print info_url
            # self.__catch_person_info(info_url)

    def js_fmview2html(self, text):
        '''
            trans <script>FM.view to HTML
        '''
        text = text.replace("\\t", "\t")
        text = text.replace("\\n", "\n")
        text = text.replace("\\r", "")
        text = text.replace("\\/", "/")
        text = text.replace("\\\"", "\"")
        return text