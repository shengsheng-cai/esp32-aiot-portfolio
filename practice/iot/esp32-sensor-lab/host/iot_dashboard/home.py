# IoT 溫度儀表板 Web 服務：CanvasJS 曲線圖 + WebSocket 即時更新
# 對應原始：iot_www/home.py（Docker hostname iot_mongo → localhost）
# 依賴：pip install flask flask-socketio eventlet pymongo
# 啟動：python home.py
# 瀏覽器：http://localhost:8000
# 注意：需要 templates/index.html（原始碼未含，需自行建立或從課程 Docker image 取出）
#       需要 templates/ctrl.js 和 templates/jquery.canvasjs.min.js

from flask import Flask, request, render_template
from flask_socketio import SocketIO
import pymongo
import json

PORT       = 8000
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
DB_NAME    = 'iot'
COL_NAME   = 'temp'

db_client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
docs = db_client[DB_NAME][COL_NAME]

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/ctrl.js')
def ctrl_js():
    return render_template('ctrl.js')


@app.route('/jquery.canvasjs.min.js')
def canvasjs():
    return render_template('jquery.canvasjs.min.js')


@app.route('/get_data.jsp', methods=['POST'])
def get_data():
    data = list(docs.find(
        {'tmp': {'$exists': True}, 'dt': {'$exists': True}},
        {'_id': 0, 'tmp': 1, 'dt': 1}
    ).sort('dt', pymongo.DESCENDING))
    print(len(data))
    return json.dumps(data)


@app.route('/datacominginws', methods=['POST'])
def data_coming():
    data = request.json.get('D')
    print('receive data:', data)
    socketio.emit('datacoming', {'data': data}, broadcast=True)
    return ''


@socketio.on('hello')
def ev_hello():
    print('*** event hello ***')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=PORT)
