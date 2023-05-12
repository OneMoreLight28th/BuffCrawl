import time
import requests
import json
import pymongo
from bson.binary import Binary
import logging

'''

 * @author ELEVEN28th
 * @creat 2023-3-10
 
'''

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

data_list = []

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["csgo_items"]
collection = db["newcsgo_items"]


def read_data():
    with open('csgoItemsInfoFixed1.json', 'r') as f:
        data = json.load(f)
    global goods_read
    goods_read = []
    for items in data:
        goods_read.append(items)


def print_hi():
    with open('cookie.txt', 'r') as f:
        cookie_str = f.read().strip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'
    }
    Cookie = {
        'Cookie': cookie_str
    }
    proxy = {'http': 'http://113.124.86.24:9999'
             }

    read_data()

    orignal_url = 'https://buff.163.com/api/market/goods/bill_order?game=csgo&goods_id='

    data_to_save = []  # 用于存储要保存到数据库的数据
    timestamp = int(time.time())  # 时间戳

    for i in range(len(goods_read)):

        all_id_url = orignal_url + str(goods_read[i])

        print(goods_read[i])

        try:
            html_response = requests.get(url=all_id_url, headers=headers, cookies=Cookie, proxies=proxy)
            html_json = html_response.json()
            html_items = html_json['data']['items']
        except Exception as e:
            logging.error(f"Error occurred while getting HTML response for url: {all_id_url}. {e}")
            continue

        item_list = []  # 用于保存当前物品的所有数据
        for item in html_items:
            try:
                inspection_img_url = item['asset_info']['info'].get('inspect_url', '')  # 获取检视图链接
                if inspection_img_url:
                    inspection_img = requests.get(url=inspection_img_url).content
                else:
                    inspection_img = None
            except Exception as e:
                logging.error(f"Error occurred while getting inspection image for url: {inspection_img_url}. {e}")
                inspection_img = None

            print(inspection_img_url)

            stickers = item['asset_info']['info'].get('stickers', [])
            itemfloat = item['asset_info']['paintwear']
            paintseed = item['asset_info']['info']['paintseed']
            price = item['price']
            transaction_time = item['transact_time']
            stickers_info = []
            for sticker in stickers:

                try:
                    img_url = sticker.get('img_url', '')
                    name = sticker.get('name', '')
                    slot = sticker.get('slot', '')
                    wear = sticker.get('wear', '')

                    if img_url:
                        img_data = requests.get(img_url).content
                    else:
                        img_data = None
                    sticker_info = {
                        'img_data': Binary(img_data) if img_data else None,
                        'name': sticker.get('name', ''),
                        'slot': sticker.get('slot', ''),
                        'wear': sticker.get('wear', '')
                    }

                    stickers_info.append(sticker_info)
                except requests.exceptions.RequestException as e:
                    logging.exception(f"Request exception occurred while accessing sticker image : {all_id_url}.{e}")
                    continue  # 这个请求失败，继续下一个循环

            try:
                item_data = {
                    'inspection_img': requests.get(url=inspection_img_url).content,  # 获取检视图图片数据并保存
                    'itemfloat': itemfloat,
                    'paintseed':paintseed,
                    'price': price,
                    'transaction_time': transaction_time,
                    'stickers': stickers_info
                }
                print(all_id_url)
                item_list.append(item_data)
            except requests.exceptions.RequestException as e:
                logging.exception(f"Request exception occurred while accessing inspection image : {all_id_url}.{e}")
                continue

        id = goods_read[i]

        data_to_save.append({
            'id': id,
            'timestamp': timestamp,
            'data': item_list
        })

        # 一次性更新所有文档
        for id in set(g['id'] for g in data_to_save):
            query = {'id': id}
            updates = []
            for data in data_to_save:
                if data['id'] == id:
                    updates.append({
                        '$set': {
                            'container.' + str(data['timestamp']): data['data']
                        }
                    })
            collection.update_many(query, updates)

        time.sleep(2)

print_hi()
