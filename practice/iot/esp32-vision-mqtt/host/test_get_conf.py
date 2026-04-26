# 驗證 config.json 設定是否正確，改完 config.json 後執行
# 用法：python test_get_conf.py

import json

with open('config.json') as f:
    conf = json.load(f)

print(conf)
print('mqtt_broker:', conf['mqtt_broker'])
print('mqtt_port  :', conf['mqtt_port'])
print('topic_head :', conf['topic_head'])
print('topic_servo:', conf['topic_head'] + conf['topic_servo'])
print('topic_lcd  :', conf['topic_head'] + conf['topic_lcd'])
print('topic_relay:', conf['topic_head'] + conf['topic_relay'])
