# IoT 資料接收服務：HTTP GET → MongoDB + WebSocket 轉發
# 對應原始：iot_data/iot_data.py（Docker hostname iot_mongo/iot_www → localhost）
# 完整管線：ESP32 → MQTT → mqtt_sub_http.py → 本程式 → MongoDB & home.py
# 依賴：pip install flask pymongo requests
# 啟動：python iot_data.py
# 測試：curl "http://localhost:12321/?tmp=3110"

from flask import Flask, request
from time import localtime, strftime
import pymongo
import requests as req
import json

DATA_PORT  = 12321
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
WWW_URL    = 'http://localhost:8000/datacominginws'
DB_NAME    = 'iot'
COL_NAME   = 'temp'

db_client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
docs = db_client[DB_NAME][COL_NAME]

app = Flask(__name__)


@app.route('/')
def index():
    try:
        tmp = int(request.args.get('tmp'))
        data = {'dt': strftime('%Y-%m-%d %H:%M:%S', localtime()), 'tmp': tmp}
        docs.insert_one(data)
        del data['_id']
        req.post(WWW_URL, json={'D': json.dumps(data)}, timeout=2)
    except Exception as e:
        print('Exception:', e)
    finally:
        return '.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=DATA_PORT)
