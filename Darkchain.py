import requests
import json
import re
import html
import threading
import base64
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#########fofa########
def load_config():
    with open('config.ini', 'r') as f:
        config=f.readlines()
        if len(config)!=2:
            print('请先正确配置好fofa API的key和email')
            exit()
        return config
def input_keyword():
    print('先确保你已经在config.ini配置好fofa的api参数\n每个url的检测报告会实时输出到result.txt下\n微信公众号：台下言书')
    string=input("请输入fofa关键字:\n")
    a = base64.b64encode(string.encode())
    size=input('API获取的条数：\n')
    full=input('1.一年内数据   2.全部数据')
    keyword=str(a,encoding="utf8")
    return keyword,size,full

def API(config,keyword,size,full):
    if full =='1':
        url='https://fofa.so/api/v1/search/all?email={}&key={}&qbase64={}&size={}'.format(config[0].replace('\n',''),config[1],keyword,size)
    else:
        url = 'https://fofa.so/api/v1/search/all?email={}&key={}&qbase64={}&size={}&full=true'.format(config[0].replace('\n', ''),
                                                                                            config[1], keyword, size)
    print('获取资产中...')
    try:
        response = requests.get(url)  # 获取网页源代码内容
        response.raise_for_status()  # 失败请求(非200响应)抛出异常
        response.encoding = "utf-8"  # 设置网页编码
        fofa_data = response.text
        return fofa_data
    except:
        print('请求错误，请检查网络情况！')

def get_urls(fofa_json):
    a = fofa_json['results']
    for b in a:
        c = b[0]
        if re.findall('http', c) == []:
            c = 'http://' + c
            urls_list.append(c)

###########find##########
def FindDarkchain(urls):
    headers={
        'User-Agent':'Mozilla/5.0 (compatible;Baiduspider-render/2.0; +http://www.baidu.com/search/spider.html)',
        'Referer':'https://www.baidu.com/'
    }
    for url in urls:
        try:
            res=requests.get(url,headers=headers,timeout=10).text
            respose=html.unescape(res)
            rules = []#匹配到的标签
            host=True
            for re_rules in re_rules_list:
                chashuibiao=re.findall(r'{}'.format(re_rules),respose,re.S|re.I)
                if chashuibiao !=[]:
                    rules.append(re_rules)
                    host=False
            if host ==False:
                with open("result.txt", "a") as file:
                    file.write('地址：{}\n匹配项：{}\n\n'.format(url,rules))
                print('{}:{} 存在暗链，已保存！'.format(threading.current_thread().name,url))
            else:
                print('{}:{} 未检测出暗链'.format(threading.current_thread().name,url))
        except:
            print('{}:{}请求出错'.format(threading.current_thread().name,url))




banner='''

     _              __ _           _ 
    | |            / _(_)         | |
  __| | ___ ______| |_ _ _ __   __| |
 / _` |/ __|______|  _| | '_ \ / _` |
| (_| | (__       | | | | | | | (_| |
 \__,_|\___|      |_| |_|_| |_|\__,_|                     
    -------------------------------
      多线程批量暗链检查工具  v1.0
    公众号：台下言书    author：说书人      
    -------------------------------                                 
'''
print(banner)
print('1.从fofa获取   2.从本地获取')
howget=input('请选择：')
xc=int(input('线程数:'))
with open('rules.txt', 'r',encoding='utf-8') as s:
    re_rules_list = s.read().split('\n')
if howget=='1':
    urls_list = []  # 所有链接
    config = load_config()
    aaa = input_keyword()
    keyword = aaa[0]
    size = aaa[1]
    full = aaa[2]
    fofa_json = json.loads(API(config, keyword, size, full))
    get_urls(fofa_json)
    urls = []
    twoList = [[] for i in range(xc)]
    for i, e in enumerate(urls_list):
        twoList[i % xc].append(e)
    for i in twoList:
        urls.append(i)
    print('主线程开始')
    thread_list = [threading.Thread(target=FindDarkchain, args=(urls[i],)) for i in range(len(urls))]
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    print('主线程结束')
elif howget=='2':
    with open('url.txt', 'r') as f:
        urls_list = f.read().split('\n')
    urls = []
    twoList = [[] for i in range(xc)]
    for i, e in enumerate(urls_list):
        twoList[i % xc].append(e)
    for i in twoList:
        urls.append(i)
    print('主线程开始')
    thread_list = [threading.Thread(target=FindDarkchain, args=(urls[i],)) for i in range(len(urls))]
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()
    print('主线程结束')
else:
    print('输入错误，告辞！')
    exit()