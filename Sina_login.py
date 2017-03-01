# coding:utf-8

import sys
import urllib
import urllib2
import cookielib
import base64
import re
import json
import rsa
import binascii
import logging
import lxml.html as HTML
#　import requests
#　from bs4 import BeautifulSoup

#　新浪微博的模拟登陆
class weiboLogin:
    def enableCookies(self):
        #　获取一个保存cookies的对象
        cj = cookielib.CookieJar()
        #　将一个保存cookies对象和一个HTTP的cookie的处理器绑定
        cookie_support = urllib2.HTTPCookieProcessor(cj)
        #　创建一个opener,设置一个handler用于处理http的url打开
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        #　安装opener，此后调用urlopen()时会使用安装过的opener对象
        urllib2.install_opener(opener)

    #　预登陆获得 servertime, nonce, pubkey, rsakv
    def getServerData(self):
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=ZW5nbGFuZHNldSU0MDE2My5jb20%3D&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1442991685270'
        data = urllib2.urlopen(url).read()
        p = re.compile('\((.*)\)')
        try:
                json_data = p.search(data).group(1)
                data = json.loads(json_data)
                servertime = str(data['servertime'])
                nonce = data['nonce']
                pubkey = data['pubkey']
                rsakv = data['rsakv']
                return servertime, nonce, pubkey, rsakv
        except:
                print 'Get severtime error!'
                return None
                
    #　获取加密的密码
    def getPassword(self, password, servertime, nonce, pubkey):
        rsaPublickey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublickey, 65537)            #　创建公钥
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #　拼接明文js加密文件中得到
        passwd = rsa.encrypt(message, key)                  #　加密
        passwd = binascii.b2a_hex(passwd)                   #　将加密信息转换为16进制。
        return passwd

    #　获取加密的用户名
    def getUsername(self, username):
        username_ = urllib.quote(username)
        username = base64.encodestring(username_)[:-1]
        return username

     #　获取需要提交的表单数据   
    def getFormData(self,userName,password,servertime,nonce,pubkey,rsakv):
        userName = self.getUsername(userName)
        psw = self.getPassword(password,servertime,nonce,pubkey)
        
        form_data = {
            'entry':'weibo',
            'gateway':'1',
            'from':'',
            'savestate':'7',
            'useticket':'1',
            'pagerefer':'http://weibo.com/p/1005052679342531/home?from=page_100505&mod=TAB&pids=plc_main',
            'vsnf':'1',
            'su':userName,
            'service':'miniblog',
            'servertime':servertime,
            'nonce':nonce,
            'pwencode':'rsa2',
            'rsakv':rsakv,
            'sp':psw,
            'sr':'1366*768',
            'encoding':'UTF-8',
            'prelt':'115',
            'url':'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype':'META'
            }
        formData = urllib.urlencode(form_data)
        return formData

    #　登陆函数
    def login(self,username,psw):
        self.enableCookies()
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        servertime,nonce,pubkey,rsakv = self.getServerData()
        formData = self.getFormData(username,psw,servertime,nonce,pubkey,rsakv)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'}
        req  = urllib2.Request(
                url = url,
                data = formData,
                headers = headers
        )
        result = urllib2.urlopen(req)
        text = result.read()

        #　重定位网址，包含在脚本中，获取到之后才能真正地登陆
        p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')
        try:
                login_url = p.search(text).group(1)
                #由于之前的绑定，cookies信息会直接写入
                urllib2.urlopen(login_url)
                logging.info("Login success!")
        except:
                logging.info('Login error!')
                return 0

def catch_person_info(url):
    '''
        CATCH个人信息
    '''
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    text = response.read()

    # 提取个人信息代码
    html = ""
    p = re.compile("<script>FM.view.*</script>")
    match = p.findall(text)
    for eachFm in match:
        if "Pl_Official_PersonalInfo__58" in eachFm and \
            "main_title W_fb W_f14" in eachFm:
            index = eachFm.find("html")
            eachFm = eachFm[index+9:-12]
            eachFm = js_fmview2html(eachFm)
            html = eachFm
            break

    doc = HTML.fromstring(unicode(html, "utf-8"))

    # 基本信息
    data_1 = doc.xpath(
        '//div[1][@class="WB_cardwrap S_bg2"]//div[@class="PCD_text_b PCD_text_b2"]//' + \
            'div[@class="WB_innerwrap"]//div//ul'
    )
    if 0 == len(data_1):            # 没有找到
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
    
def js_fmview2html(text):
    '''
        网页中<script>FM.view内代码转换为HTML
    '''
    text = text.replace("\\t", "\t")
    text = text.replace("\\n", "\n")
    text = text.replace("\\r", "")
    text = text.replace("\\/", "/")
    text = text.replace("\\\"", "\"")
    return text

def save_file(filename, text):
    '''
        text保存到文件
    '''
    fp = open(filename, "wb+")
    fp.write(text)
    fp.close()

if __name__ == "__main__":
    #　日志配置
    logging.basicConfig(format='%(asctime)s  %(levelname)s : %(message)s', level=logging.INFO)

    wblogin = weiboLogin()
    print 'sina login...'
    username = raw_input(u'username:')
    password = raw_input(u'password:')
    wblogin.login(username,password)

    url = 'http://weibo.com/p/1005051910440104/info'
    catch_person_info(url)
