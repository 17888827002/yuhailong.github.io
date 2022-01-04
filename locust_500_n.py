# -*- coding: utf-8 -*-
# author:liucong

import json
import os
import time
from datetime import datetime

from locust.contrib.fasthttp import FastHttpUser
from locust import TaskSet, task

from faker import Faker
import queue
import threading

mutex = threading.Lock()

q = queue.Queue()
data_path = os.path.join(os.getcwd(), 'data.json')
stamp = datetime.now().strftime('%m%d%H%M')
fake = Faker('zh_CN')
times_tamp = datetime.now().strftime("%Y%m%d%H%M%S")
log_path = os.path.join(os.getcwd(), '{}.log'.format(times_tamp))


# 读取参数
def get_info(path):
    with open(path, 'r', encoding='utf-8') as f:
        info = json.load(f)
    return info


def writ_log(content, path=log_path):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(content)


def get_video_info(path):
    with open(path, 'r', encoding='utf-8') as f:
        info = f.read()
    return info


data = get_info(data_path)


def change_params(params):
    # 替换订单相关信息
    random_num = str(fake.phone_number())
    # params['orderInfo']['orderId'] = ""
    # params['orderInfo']['orderId'] = "D" + random_num
    # if random_num[-1] == '9' or random_num[-1] == '8':
    #     params['orderInfo']['orderId'] = ""
    # else:
    #     params['orderInfo']['orderId'] = "D" + random_num
    params['orderInfo']['insuranceNo'] = random_num
    params['orderInfo']['insureAppliNo'] = "T" + random_num
    params['orderInfo']['businessType'] = fake.job()
    params['orderInfo']['policyHolder'] = fake.name()
    params['orderInfo']['productCode'] = fake.country_code()
    params['orderInfo']['account'] = "A" + random_num
    params['orderInfo']['channel'] = "python-" + stamp
    params['orderInfo']['platform'] = "python-" + stamp
    params['orderInfo']['productName'] = fake.street_name()

    # 替换任务号
    params['taskId'] = fake.md5()
    # q.put(params['taskId'])
    # 使用实时的时间戳
    # timestamp = int(round(time.time() * 1000))
    # params['timestamp'] = timestamp
    # params['recordInfo'] = video_info['record_info']

    return params


def get_video_path(n):
    path = os.path.join(os.getcwd(), '{}.txt'.format(n))
    return path


class KHS(TaskSet):

    @task(1)
    def post_1(self):
        post_params = change_params(data)
        task_id = fake.md5()
        order_id = "D" + str(fake.phone_number())
        for i in range(10):
            time.sleep(1)
            if isinstance(post_params, str):
                post_params = json.loads(post_params)
            video_path = get_video_path(i)
            video_info = get_video_info(video_path)
            post_params['recordInfo'] = video_info
            timestamp = int(round(time.time() * 1000))
            post_params['timestamp'] = timestamp
            post_params['orderInfo']['orderId'] = order_id
            post_params['taskId'] = task_id
            post_params = json.dumps(post_params)
            try:
                req = self.client.post('/record/recording', data=post_params)
                # print("返回值：", req.text)
                result = json.loads(req.text)
                if result['msg'] == 'OK':
                    return_taskid = result['result']['taskId']
                    # print('返回值：,{}\n{}------{} 视频片段{}   success'.format(req.text, task_id, return_taskid, i + 1))
                    print('视频片段{}success,       task_id:{}'.format(i + 1, task_id))
                    writ_log('视频片段{}success,       task_id:{}\n'.format(i + 1, task_id))
            except Exception as err:
                writ_log('视频片段{}错误：{},     task_id:{}\n'.format(i + 1, err, task_id))
                print('视频片段{}错误：{},     task_id:{}'.format(i + 1, err, task_id))


class WebsiteUser(FastHttpUser):
    host = "http://beta-idr-record-video.situdata.com/"
    tasks = [KHS]
