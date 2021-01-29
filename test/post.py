import requests
import random
import time
import json
import base64
import sched


# 生成100个假名
# import uuid
# pse = []
# for i in range(100):
# 	res = str(uuid.uuid4())
# 	res = res.replace('-', '')
# 	pse.append(res[:8])
# print(pse)
# pseudonyms = ['b3341d72', 'ec7825ff', '1dd0ef8f', 'd0e2b914', '36192d5f',
#               '97047fca', 'e7007fc2', '23d83fea', '5a54bec6', 'eea2d5ff',
#               '90ea2c0b', '559d2a1a', '95d9888f', '8da01a47', '984086d5',
#               '14f8dd20', '2f6dc469', '083a7fe1', '6a7a68d1', 'ddf4ef23',
#               'a370d6f4', '82a9520e', '39b1ed1b', '364c292d', 'a9fb982d',
#               '861501ee', 'bf8c406f', 'b62620d9', 'de2ba1c6', 'abc54a26',
#               'df6e99f1', '98b6dad4', 'f517de88', 'e2e75871', 'cbd5bda5',
#               'e63be25b', 'fad51aea', '3968d4ca', 'f2d62a92', 'f1aee0cc',
#               'f4cc9ae6', 'b8211f56', '5ded1e86', '1698ecf2', 'af575bb3',
#               '222d4804', 'e789be6b', '7ebf28f7', '429d3776', 'a903bdea',
#               'df4160d7', 'eceb9e37', '6d1fe3e0', '35ee7610', 'da9d1af0',
#               'c66e1c8f', '0e75e666', '7f3e5214', 'f67c08ea', '7a02668e',
#               '4d4f20eb', 'f7805ca3', 'f1902fbb', '2f7596db', 'ba956a53',
#               '4ca526a5', '41bcdfbd', '49d6e809', '28f55bf6', 'd0abe544',
#               '7f6ed0cb', 'dfd040e7', '12db15c3', '2f4b67ad', '6248ae34',
#               '9a6100b9', '201e54a5', 'fa562713', '5d229c6a', '515f0ce7',
#               '88f60bf9', '67041fc8', '680b5f5c', 'fe8c9985', '8334c156',
#               'c4420510', 'f11ebb12', '560f7d8a', '97b5ca33', '06b7b992',
#               'c883ab51', '8ded55ea', 'f6809153', '0d22953d', 'c63f161b',
#               'f4b1580a', '72d66c1c', 'c87047eb', 'cf4e66a6', 'f0679d4b']


# payload示例
# payload = {
#   "reportId": "1",
#   "generationTime": "2021-01-01 13:28:28",
#   "suspectId": "a1b2c3d4",
#   "reporterId": "b44c9d78",
#   "longitude": 116.311,
#   "latitude": 39.990,
#   "errorType": "SELF",
#   "errorCode": "01"
# }

class MBR:
    reportId = 0
    LONG_MIN = 116.25
    LONG_MAX = 116.35
    LAT_MIN = 39.95
    LAT_MAX = 40.00
    types = ['SELF', 'CERT', 'SEMANTIC']
    codeRange = [8, 11, 9]
    pseudonyms = ['b3341d72', 'ec7825ff', '1dd0ef8f', 'd0e2b914', '36192d5f',
                  '97047fca', 'e7007fc2', '23d83fea', '5a54bec6', 'eea2d5ff',
                  '90ea2c0b', '559d2a1a', '95d9888f', '8da01a47', '984086d5',
                  '14f8dd20', '2f6dc469', '083a7fe1', '6a7a68d1', 'ddf4ef23',
                  'a370d6f4', '82a9520e', '39b1ed1b', '364c292d', 'a9fb982d',
                  '861501ee', 'bf8c406f', 'b62620d9', 'de2ba1c6', 'abc54a26',
                  'df6e99f1', '98b6dad4', 'f517de88', 'e2e75871', 'cbd5bda5',
                  'e63be25b', 'fad51aea', '3968d4ca', 'f2d62a92', 'f1aee0cc',
                  'f4cc9ae6', 'b8211f56', '5ded1e86', '1698ecf2', 'af575bb3',
                  '222d4804', 'e789be6b', '7ebf28f7', '429d3776', 'a903bdea',
                  'df4160d7', 'eceb9e37', '6d1fe3e0', '35ee7610', 'da9d1af0',
                  'c66e1c8f', '0e75e666', '7f3e5214', 'f67c08ea', '7a02668e',
                  '4d4f20eb', 'f7805ca3', 'f1902fbb', '2f7596db', 'ba956a53',
                  '4ca526a5', '41bcdfbd', '49d6e809', '28f55bf6', 'd0abe544',
                  '7f6ed0cb', 'dfd040e7', '12db15c3', '2f4b67ad', '6248ae34',
                  '9a6100b9', '201e54a5', 'fa562713', '5d229c6a', '515f0ce7',
                  '88f60bf9', '67041fc8', '680b5f5c', 'fe8c9985', '8334c156',
                  'c4420510', 'f11ebb12', '560f7d8a', '97b5ca33', '06b7b992',
                  'c883ab51', '8ded55ea', 'f6809153', '0d22953d', 'c63f161b',
                  'f4b1580a', '72d66c1c', 'c87047eb', 'cf4e66a6', 'f0679d4b']

    def __init__(self, eType=-1, timeMode='now', startTime=None, endTime=None):
        self.reportId = str(MBR.reportId).zfill(6)
        MBR.reportId += 1

        timeTick = 0
        # timeMode = 'history' 随机生成时间
        if timeMode == 'history':
            startTimeStamp = time.mktime(time.strptime(startTime, '%Y-%m-%d %H:%M:%S'))
            endTimeStamp = time.mktime(time.strptime(endTime, '%Y-%m-%d %H:%M:%S'))
            timeTick = random.randrange(startTimeStamp, endTimeStamp)
        # timeMode = 'now' 用当前时间
        else:
            timeTick = time.time()
        # 转化为本地时间，字符串格式；时间字符串格式均为：2020-01-01 11:11:11
        self.generationTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeTick))

        # 位置
        self.longitude = random.uniform(MBR.LONG_MIN, MBR.LONG_MAX)
        self.latitude = random.uniform(MBR.LAT_MIN, MBR.LAT_MAX)

        # errorType
        if eType not in range(3):
            eType = random.randint(0, 2)
        self.errorType = MBR.types[eType]

        #errorCode
        self.errorCode = str(random.randint(0, MBR.codeRange[eType]-1)).zfill(2)

        # 根据异常类型生成举报者和被举报者的id，从列表中随机抽样，自报告假名相同，其他两种两个不同假名
        x, y = '', ''
        if eType == 0:
            x = y = random.sample(MBR.pseudonyms, 1)[0]
        else:
            x, y = random.sample(MBR.pseudonyms, 2)
        self.suspectId = x
        self.reporterId = y


def get_auth(name, pwd):
    auth = str(base64.b64encode(f'{name}:{pwd}'.encode('utf-8')), 'utf-8')
    return auth


if __name__ == '__main__':
    username = 'grlzjl'
    password = 'grlzjl'
    auth = get_auth(username, password)

    # 上传报告的api地址
    url = 'http://127.0.0.1:8000/api/mbrs/'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth}'
    }

    startTime = '2020-01-01 00:00:00'
    endTime = '2020-12-31 23:59:59'

    # test-上传单条数据
    # mbr = MBR(timeMode='history', startTime=startTime, endTime=endTime)
    # payload = json.dumps(mbr.__dict__)
    # print(payload)
    # response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text.encode('utf8'))

    # test-批量上传数据（生成100条历史数据，作为数据分析素材）
    # n = 100
    # for i in range(n):
    #     mbr = MBR(timeMode='history', startTime=startTime, endTime=endTime)
    #     payload = json.dumps(mbr.__dict__)
    #     response = requests.request("POST", url, headers=headers, data=payload)

    def send_post():
        payload = json.dumps(MBR().__dict__)
        response = requests.request("POST", url, headers=headers, data=payload)
        return response

    # 定时发送
    schedule = sched.scheduler(time.time, time.sleep)

    def interval_post():
        send_post()
        # 间隔时间，随机，10~60s发送一次
        inc = random.randint(10, 60)
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), f'Next POST: {inc}s later')
        schedule.enter(inc, 0, interval_post, ())
        schedule.run()

    schedule.enter(0, 0, interval_post, ())
    schedule.run()
