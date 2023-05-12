import json
import re
import time
import logging

import requests

sleeptime = 2
data_list = []
logging.basicConfig(filename='myapp.log', level=logging.ERROR)


def initialization():  # 初始化头信息即cookies
    global headers
    global cookies
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.69'
    }
    Cookie = {
        'Cookie': ''
    }
    proxy = {
        "http": "http://202.109.157.63:9000"

    }

    with open('weapons_name/weapons.json', 'r') as f:

        data = json.load(f)

    # 创建一个空列表来存储数据
    category_list = []

    # 将数据添加到列表中
    for item in data:
        category_list.append(item)

    root_url = 'https://buff.163.com/api/market/goods?game=csgo&'
    # 拼接网站格式拿到json数据
    source_page_url = "https://buff.163.com/api/market/goods?game=csgo&page_num=1&"
    for i in range(len(category_list)):
        category_url = source_page_url + "&category=weapon_" + category_list[i]
        page_response = requests.get(url=category_url, headers=headers, cookies=Cookie, proxies=proxy)
        html_text1 = page_response.text
        # 报错IndexError: list index out of range，加入异常处理,输出日志文件
        try:
            page_num_list = re.findall(r'"total_page": (.*)', html_text1, re.M)
            page_num = page_num_list[0]
            print(page_num)
        except IndexError:
            logging.error(f'IndexError: {category_url}')
            page_num = None
            continue
        time.sleep(sleeptime)

        for page in range(1, int(page_num) + 1):
            time.sleep(sleeptime)
            page_str = 'page_num=' + str(page)
            url = root_url + page_str + "&category=weapon_" + category_list[i]
            detail_response = requests.get(url=url, headers=headers, cookies=Cookie, proxies=proxy)
            html_text2 = detail_response.text
            print(url)
            # 这段代码报错json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
            # 另一个错误KryError:'data'
            # 加入异常处理防止程序中断,输出日志文件
            try:
                jsonobj = json.loads(html_text2)
                if 'data' in jsonobj:
                    conjsonobj = [item['id'] for item in jsonobj['data']['items']]
                    print(conjsonobj)
                else:
                    raise KeyError('JSON object does not contain the key "data"')
            except json.decoder.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                logging.error(f'JSONDecodeError: {e}, url: {url}')
            except KeyError as e:
                print(f"Error accessing JSON key: {e}")
                logging.error(f'KeyError: {e}, url: {url}')
            except Exception as e:
                print(f"Unknown error: {e}")
                logging.error(f'Unknown error: {e}, url: {url}')

            for id1 in conjsonobj:
                data_list.append(id1)

            with open('Itemsid.json', 'w') as outfile:
                json.dump(data_list, outfile)


initialization()
