#!/usr/bin/python
# -*- encoding: utf-8 -*-

'''
    企鹅滑动验证模拟登录
    python3 + seleniuum + cv2 + numpy
    后续优化可使用 pillow 将图片进一步灰度化处理
'''
import ssl

import requests

__doc__ = '小额通登录功能'

__author__ = 'billy'



import os
import cv2
import time
import random
import numpy as np
from PIL import Image
from urllib.request import urlretrieve

# selenium-part
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# third-part
from packages import config, util

save_path = os.path.join(config.APP_ROOT, 'data', 'xiaoetong.cookies')

headers = {
    # 'upgrade-insecure-requests': '1',
    # 'sec-fetch-site': 'none',
    # 'sec-fetch-mode': 'navigate',
    # 'sec-fetch-user': '?1',
    # 'dnt': '1',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'if-modified-since': 'Thu, 26 Mar 2020 23:50:00 GMT',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'cookie': 'pgv_pvi=2471064576; pgv_pvid=5782002132; RK=ONolY5oif/; ptcz=a47870ca7ab81fada934148d6f51e3b0f277d6392a83da1500c67160e342c143; fp3_id1=1100440A15DCB3607EBA9783B987E536B5B521433EED99ED52A9088B37DA960BFCE46BFDBAAF02D2619C6CC32454932FF3EE; pac_uid=0_5e72d24333325; XWINDEXGREY=0; pgv_info=ssid=s4198525417',
    'cache-control': 'max-age=0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}

class Login(object):


    def __init__(self, **kwargs):
        # 初始变量信息
        self.__init_args__(**kwargs)

        # 运行主功能
        # try:
        #     self.run()
        # except Exception as e:
        #     util.traceback_info(e)
        # # 退出浏览器
        # self.after_quit()

    def __init_args__(self, **kwargs):
        self.count = "15889391177"
        self.pwd = "elecfans@2018"
        self.url = "https://admin.xiaoe-tech.com/login_page?xeuti=ituex#/acount"

    @staticmethod
    def show(name):
        cv2.imshow('Show', name)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def get_postion(chunk, canves):
        """
        判断缺口位置
        :param chunk: 缺口图片是原图
        :param canves:
        :return: 位置 x, y
        """
        otemp = chunk
        oblk = canves
        target = cv2.imread(otemp, 0)
        template = cv2.imread(oblk, 0)
        # w, h = target.shape[::-1]
        temp = 'temp.jpg'
        targ = 'targ.jpg'
        cv2.imwrite(temp, template)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        target = abs(255 - target)
        cv2.imwrite(targ, target)
        target = cv2.imread(targ)
        template = cv2.imread(temp)
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)
        # print(result.argmax(), [x, y])
        return x, y
        # # 展示圈出来的区域
        # cv2.rectangle(template, (y, x), (y + w, x + h), (7, 249, 151), 2)
        # cv2.imwrite("yuantu.jpg", template)
        # show(template)

    @staticmethod
    def get_track(distance):
        """
        模拟轨迹 假装是人在操作
        :param distance:
        :return:
        """
        # 初速度
        v = 0
        # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
        t = 0.2
        # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
        tracks = []
        # 当前的位移
        current = 0
        # 到达mid值开始减速
        mid = distance * 7 / 8
        distance += 10  # 先滑过一点，最后再反着滑动回来
        # a = random.randint(1,3)
        while current < distance:
            if current < mid:
                # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
                a = random.randint(2, 4)  # 加速运动
            else:
                a = -random.randint(3, 5)  # 减速运动
            # 初速度
            v0 = v
            # 0.2秒时间内的位移
            s = v0 * t + 0.5 * a * (t ** 2)
            # 当前的位置
            current += s
            # 添加到轨迹列表
            tracks.append(round(s))
            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t
        # 反着滑动到大概准确位置
        for i in range(4):
            tracks.append(-random.randint(2, 3))
        for i in range(4):
            tracks.append(-random.randint(1, 3))
        return tracks

    def after_quit(self):
        """
        关闭浏览器
        :return:
        """
        self.driver.quit()
        # driver.close()关闭当前窗口
        # driver.quit()退出驱动关闭所有窗口

    def put_msg(self):
        try:
            # 获取手机号码输入框
            text_box = self.wait.until(
                expected_conditions.presence_of_element_located((By.XPATH, '//div[@class="inputBox"]/input')))
            text_pwd = self.wait.until(expected_conditions.presence_of_element_located(
                (By.XPATH, '//div[@class="passwordWrapper"]/div/input[@type="password"]')))
            # 获取发送验证按钮
            send_btn = self.wait.until(
                expected_conditions.presence_of_element_located((By.XPATH, '//div[@data-sensors="登录_登录页_点击登录"]')))
        except Exception as e:
            print(e)
            raise RuntimeError("获取 手机号码输入框 或者 发送验证按钮 失败，程序结束")
        text_box.send_keys(self.count)
        text_pwd.send_keys(self.pwd)
        try:
            action = ActionChains(self.driver)
            action.click(send_btn).perform()
        except Exception as e:
            print(util.traceback_info(e))
            return False

    def start_dirver(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)
        print('webdriver get: {0}'.format(self.url))
        self.driver.get(self.url)
        self.wait = WebDriverWait(self.driver, 10)

    def save_img(self, file_name, img_url):
        print('fetch img: {0}'.format(img_url))
        try:
            rs = requests.get(img_url, headers=headers, timeout=20)
        except Exception as e:
            print(e)
            time.sleep(0.5)
            rs = requests.get(img_url, headers=headers, timeout=20)
        content = rs.content
        save_path = os.path.join(config.APP_ROOT, 'data', file_name)
        with open(save_path, 'wb') as fp:
            fp.write(content)
        print('保存图片成功')

    def run(self):
        ssl._create_default_https_context = ssl._create_unverified_context
        requests.packages.urllib3.disable_warnings()
        self.start_dirver()
        # 填写用户信息并点击
        self.put_msg()
        time.sleep(3)
        # 判断是否需要进行验证
        if 'muti_index' in self.driver.current_url:
            return self.click_into_shop()
        else:
            self.driver.switch_to.frame(1)  # 切换到iframe模块
            time.sleep(3)
            # 等待图片加载完成
            slideBg = self.wait.until(
                expected_conditions.presence_of_element_located((By.XPATH, '//div/img[@id="slideBg"]')))
            # 判断图片是否加载完成
            bk_block = slideBg.get_attribute('src')  # 大图 url
            if not bk_block:
                print('等待图片加载中 ... ')
                time.sleep(2)
            # 获取背景图
            bk_block = self.driver.find_element_by_xpath('//img[@id="slideBg"]')  # 大图
            web_image_width = bk_block.size['width']
            bk_block_x = bk_block.location['x']

            # 获取缺口图
            slide_block = self.driver.find_element_by_xpath('//img[@id="slideBlock"]')  # 小滑块
            slide_block_x = slide_block.location['x']

            # 保存图片至本地
            slide_block_img = slide_block.get_attribute('src')
            bk_block_img = bk_block.get_attribute('src')

            # 保存图片
            img_bg_path = os.path.join(config.APP_ROOT, 'data', 'img_bg.png')
            img_slider_path = os.path.join(config.APP_ROOT, 'data', 'img_slider.png')
            self.save_img('img_slider.png', slide_block_img)
            self.save_img('img_bg.png', bk_block_img)

            # 获取web图与示例图的比例
            img_bkblock = Image.open(img_bg_path)
            real_width = img_bkblock.size[0]
            width_scale = float(real_width) / float(web_image_width)

            # 计算缺口位置
            position = self.get_postion(img_bg_path, img_slider_path)
            real_position = position[1] / width_scale
            # 减去滑块起始位置的距离
            real_position = real_position - (slide_block_x - bk_block_x)
            # 获取滑动距轨迹列表
            track_list = self.get_track(real_position)
            print('滑动轨迹:', int(real_position), track_list)
            # print('第一步,获取滑动按钮')
            button = self.wait.until(
                expected_conditions.presence_of_element_located((By.XPATH, '//div[@class="tc-drag-thumb"]')))
            ActionChains(self.driver).click_and_hold(on_element=button).perform()  # 点击鼠标左键，按住不放
            time.sleep(0.2)
            # print('第二步,拖动元素')
            for track in track_list:
                ActionChains(self.driver).move_by_offset(xoffset=track, yoffset=0).perform()  # 鼠标移动到距离当前位置（x,y）
                time.sleep(0.002)
            # ActionChains(driver).move_by_offset(xoffset=-random.randint(0, 1), yoffset=0).perform()   # 微调，根据实际情况微调
            time.sleep(0.5)
            # print('第三步,释放鼠标')
            ActionChains(self.driver).release(on_element=button).perform()
            time.sleep(3)
            # 进入店铺激活usr_token 保存cookie
            return self.click_into_shop()


    def click_into_shop(self):
        '''进入店铺激活user_token'''
        try:
            shop = self.wait.until(expected_conditions.presence_of_element_located((By.XPATH, '//a[@class="shop-list-item shop-list-item__active"]')))
            ActionChains(self.driver).click(shop).perform()
        except Exception as e:
            print(util.traceback_info(e))
            return False
        print('等待3秒 ...')
        time.sleep(3)
        if '/index' in self.driver.current_url:
            return self.catch_cookies()
        return False

    def catch_cookies(self):
        '''
        成功缓存当前cookeis
        不成功 退出
        '''
        cookies = self.driver.get_cookies()
        _cookie_dict = {}
        for vo in cookies:
            _cookie_dict[vo['name']] = vo['value']
        # 保存cookie
        util.file(save_path, _cookie_dict)
        print('更新cookies成功')
        return True

if __name__ == '__main__':
    login = Login().run()

