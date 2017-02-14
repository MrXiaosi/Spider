# coding:utf-8
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

class PersonSinaSpider(Spider):
    name = 'person_sina'
    allowed_domains = ['weibo.cn']
    start_urls = [
        'http://weibo.cn/1910440104/info'
    ]

    def start_requests(self):
        yield Request(url='http://weibo.cn/1910440104/info', method='get', callback=self.parse, cookies=self.get_cookies())

    def parse(self, response):
        sel = Selector(response)
        c_div = sel.xpath('//div[@class="c"]/text()')

        print "MY DEBUG INFO:"
        for each in c_div:
            tmp = each.extract().encode("gb18030")
            if unicode("昵称", "utf-8").encode("gb18030") == tmp[:4]:
                print tmp
            elif unicode("认证", "utf-8").encode("gb18030") == tmp[:4]:
                print tmp
            elif unicode("性别", "utf-8").encode("gb18030") == tmp[:4]:
                print tmp
            elif unicode("地区", "utf-8").encode("gb18030") == tmp[:4]:
                print tmp
            elif unicode("认证信息", "utf-8").encode("gb18030") == tmp[:4]:
                print tmp
            elif unicode("简介", "utf-8").encode("gb18030") == tmp[:4]:
                print tmp
            else:
                continue

    def get_cookies(self):
        '''
            生成登陆cookies
        '''
        cookies = {
            'login_sid_t' : 'c3c7941bf3900fccce90ed0494572212',
            '_s_tentry' : '-',
            'Apache' : '7729941129218.787.1487050772128',
            'ULV' : '1487050772180:1:1:1:7729941129218.787.1487050772128:',
            'SINAGLOBAL' : '7729941129218.787.1487050772128',
            'UOR' : 'widget.weibo.com,login.sina.com.cn',
            'SSOLoginState' : '1487054336',
            'un' : '13459400403',
            'wvr' : '6',
            'SCF' : 'AlwBknm4fJ8w4AXTRXORwp-x7jy6yDR5sXglOalrNraLy_Hqu82FrxYndSCXU3mwqe7r4w3pDX3XHV6jWu0Io0Q.',
            'SUB' : '_2A251ptj1DeRxGeRO41UX8ivPyD-IHXVW0k09rDV8PUJbmtAKLVDukW8Ernbo3gudai2sftCIVkN2GS832Q..',
            'SUBP' : '0033WrSXqPxfM725Ws9jqgMF55529P9D9WWy-me7T3SdgWJKurW_V.k.5JpX5o2p5NHD95QEehnNSozfe0e0Ws4DqcjHi--fi-z7iKysi--fiKLFiKLFeKnp',
            'SUHB' : '0u5gtC2w_cCbQJ',
            'ALF' : '1518590335'
        }
        return cookies