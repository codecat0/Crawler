#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File   :selenuim_crawler.py
@Author :CodeCat
@Date   :2024/5/21 21:51
"""
import os
import time
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Selenium浏览器设置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62")

driver = webdriver.Chrome(options=chrome_options)


class DongCheDiCrawler(object):
    def __init__(self):
        """
        初始化函数，用于设置默认的请求头信息。
        Args:
            无参数。
        Returns:
            无返回值。
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62',
        }

    def get_html_info(self, url=None, html_path=None):
        """
        根据传入的url或html文件路径获取HTML内容，并返回BeautifulSoup对象。

        Args:
            url (str, optional): 目标网页的URL地址。默认为None。
            html_path (str, optional): 本地HTML文件的路径。默认为None。

        Returns:
            BeautifulSoup: 返回一个BeautifulSoup对象，用于进一步解析HTML内容。

        Raises:
            Exception: 当未传入url或html_path参数时，抛出异常。
        """
        # 如果传入了url参数
        if url is not None:
            # 发送HTTP请求获取网页内容
            response = requests.get(url, headers=self.headers)
            # 使用BeautifulSoup解析网页内容
            bs = BeautifulSoup(response.text, 'html.parser')
        # 如果传入了html_path参数
        elif html_path is not None:
            # 打开本地HTML文件并读取内容
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            # 使用BeautifulSoup解析HTML内容
            bs = BeautifulSoup(html, 'html.parser')
        # 如果url和html_path参数都未传入
        else:
            # 抛出异常，提示用户输入url或html_path
            raise Exception('请输入url或html_path')
        # 返回解析后的BeautifulSoup对象
        return bs

    @staticmethod
    def elk_test_parser(csv_name, url=None):
        """
        解析网页信息并保存为CSV文件

        Args:
            csv_name (str): CSV文件保存路径及名称
            url (str, optional): 目标网页的URL地址，默认为None

        Returns:
            None
        """
        info = {
            '名称': [],
            '麋鹿入桩速度': [],
            '实测车型': [],
            '参数链接': [],
            '评分链接': []
        }
        driver.get(url)
        try:
            # 获取网页的初始滚动高度
            last_height = driver.execute_script('return document.body.scrollHeight')

            # 不断滚动页面并加载更多内容
            while True:
                # 滚动到页面底部
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                # 等待一段时间，让页面加载完成
                time.sleep(2)
                # 获取滚动后的页面高度
                new_height = driver.execute_script('return document.body.scrollHeight')

                # 如果页面高度没有变化，说明已经滚动到页面底部，退出循环
                if new_height == last_height:
                    break
                # 更新页面高度
                last_height = new_height

                # 使用BeautifulSoup解析页面源代码
                bs = BeautifulSoup(driver.page_source, 'html.parser')

                # 查找包含车型名称的链接
                links = bs.find_all(class_='tw-leading-28 tw-h-28 tw-truncate')
                param_link_pre = 'https://www.dongchedi.com/auto/params-carIds-x-'
                score_link_pre = 'https://www.dongchedi.com/auto/series/score/'
                for link in links:
                    # 查找包含车型名称的元素
                    b = link.find(class_='tw-font-semibold')
                    # 将车型名称添加到info字典中
                    info['名称'].append(b.get_text())
                    # 获取链接的href属性值
                    href = b['href']
                    _id = href.split('/')[-1]
                    # 拼接参数链接和评分链接，并添加到info字典中
                    info['参数链接'].append(param_link_pre + _id)
                    info['评分链接'].append(score_link_pre + _id)

                # 查找包含麋鹿入桩速度的元素
                div_tags = bs.find_all(class_='tw-py-16 tw-text-center')
                for div_tag in div_tags:
                    velocity = div_tag.find(class_='list_value__2G-53')
                    # 将麋鹿入桩速度添加到info字典中
                    info['麋鹿入桩速度'].append(velocity.get_text())

                # 查找包含实测车型的元素
                span_tags = bs.find_all('span')
                for span_tag in span_tags:
                    if span_tag.has_attr('class') and 'list_name__1x2Qz' in span_tag['class']:
                        measured_car = span_tag.text
                        # 截取字符串，将实测车型添加到info字典中
                        info['实测车型'].append(measured_car[5:])
        # except Exception as e:
        #     # 处理在解析过程中可能发生的任何异常
        #     print(f"An error occurred: {e}")

        finally:
            # 关闭浏览器驱动
            try:
                driver.quit()
            except Exception as e:
                print(f"Failed to quit driver: {e}")

        # 将info字典转换为DataFrame，并保存为CSV文件
        info_csv = pd.DataFrame(info)
        # 去除重复的行，并保存为CSV文件
        info_csv.drop_duplicates(inplace=True)
        info_csv.to_csv(csv_name, index=False, encoding='gbk')

    @staticmethod
    def accelerate_parser(csv_name, url=None):
        """
        解析网页信息并保存为CSV文件，包含车型名称、百公里加速时间、实测车型、参数链接和评分链接。

        Args:
            csv_name (str): CSV文件保存路径及名称。
            url (str, optional): 目标网页的URL地址，默认为None。

        Returns:
            None
        """
        info = {
            '名称': [],
            '百公里加速': [],
            '实测车型': [],
            '参数链接': [],
            '评分链接': []
        }
        # 访问目标网页
        driver.get(url)
        try:
            # 获取网页的初始滚动高度
            last_height = driver.execute_script('return document.body.scrollHeight')

            # 不断滚动页面并加载更多内容
            while True:
                # 滚动到页面底部
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                # 等待一段时间，让页面加载完成
                time.sleep(2)
                # 获取滚动后的页面高度
                new_height = driver.execute_script('return document.body.scrollHeight')

                # 如果页面高度没有变化，说明已经滚动到页面底部，退出循环
                if new_height == last_height:
                    break
                # 更新页面高度
                last_height = new_height

                # 使用BeautifulSoup解析页面源代码
                bs = BeautifulSoup(driver.page_source, 'html.parser')

                # 查找包含车型名称的链接
                links = bs.find_all(class_='tw-leading-28 tw-h-28 tw-truncate')
                param_link_pre = 'https://www.dongchedi.com/auto/params-carIds-x-'
                score_link_pre = 'https://www.dongchedi.com/auto/series/score/'
                for link in links:
                    # 查找包含车型名称的元素
                    b = link.find(class_='tw-font-semibold')
                    # 将车型名称添加到info字典中
                    info['名称'].append(b.get_text())
                    # 获取链接的href属性值
                    href = b['href']
                    # 从href中提取车型ID
                    _id = href.split('/')[-1]
                    # 拼接参数链接和评分链接，并添加到info字典中
                    info['参数链接'].append(param_link_pre + _id)
                    info['评分链接'].append(score_link_pre + _id)

                # 查找包含百公里加速时间的元素
                div_tags = bs.find_all(class_='tw-py-16 tw-text-center')
                for div_tag in div_tags:
                    accelerate = div_tag.find(class_='list_value__2G-53')
                    # 将百公里加速时间添加到info字典中
                    info['百公里加速'].append(accelerate.get_text())

                # 查找包含实测车型的元素
                span_tags = bs.find_all('span')
                for span_tag in span_tags:
                    if span_tag.has_attr('class') and 'list_name__1x2Qz' in span_tag['class']:
                        measured_car = span_tag.text
                        # 截取实测车型名称，并添加到info字典中
                        info['实测车型'].append(measured_car[5:])

        except Exception as e:
            # 处理在解析过程中可能发生的任何异常
            print(f"An error occurred: {e}")

        finally:
            # 关闭浏览器驱动
            try:
                # 关闭浏览器驱动
                driver.quit()
            except Exception as e:
                print(f"Failed to quit driver: {e}")

        # 将info字典转换为DataFrame，并保存为CSV文件
        info_csv = pd.DataFrame(info)
        info_csv.drop_duplicates(inplace=True)
        info_csv.to_csv(csv_name, index=False, encoding='gbk')

    @staticmethod
    def brake_parser(csv_name, url=None):
        """
        解析网页信息并保存为CSV文件，包含车型名称、制动距离、实测车型、参数链接和评分链接。

        Args:
            csv_name (str): CSV文件保存路径及名称。
            url (str, optional): 目标网页的URL地址，默认为None。

        Returns:
            None
        """

        info = {
            '名称': [],
            '制动距离': [],
            '实测车型': [],
            '参数链接': [],
            '评分链接': []
        }
        driver.get(url)
        try:
            # 获取网页的初始滚动高度
            last_height = driver.execute_script('return document.body.scrollHeight')

            # 不断滚动页面并加载更多内容
            while True:
                # 滚动到页面底部
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                # 等待一段时间，让页面加载完成
                time.sleep(2)
                # 获取滚动后的页面高度
                new_height = driver.execute_script('return document.body.scrollHeight')

                # 如果页面高度没有变化，说明已经滚动到页面底部，退出循环
                if new_height == last_height:
                    break
                # 更新页面高度
                last_height = new_height

                # 使用BeautifulSoup解析页面源代码
                bs = BeautifulSoup(driver.page_source, 'html.parser')

                links = bs.find_all(class_='tw-leading-28 tw-h-28 tw-truncate')
                param_link_pre = 'https://www.dongchedi.com/auto/params-carIds-x-'
                score_link_pre = 'https://www.dongchedi.com/auto/series/score/'
                for link in links:
                    b = link.find(class_='tw-font-semibold')
                    info['名称'].append(b.get_text())
                    href = b['href']
                    _id = href.split('/')[-1]
                    info['参数链接'].append(param_link_pre + _id)
                    info['评分链接'].append(score_link_pre + _id)

                div_tags = bs.find_all(class_='tw-py-16 tw-text-center')
                for div_tag in div_tags:
                    brake_dist = div_tag.find(class_='list_value__2G-53')
                    info['制动距离'].append(brake_dist.get_text())

                span_tags = bs.find_all('span')
                for span_tag in span_tags:
                    if span_tag.has_attr('class') and 'list_name__1x2Qz' in span_tag['class']:
                        measured_car = span_tag.text
                        info['实测车型'].append(measured_car[5:])

        except Exception as e:
            # 处理在解析过程中可能发生的任何异常
            print(f"An error occurred: {e}")

        finally:
            # 关闭浏览器驱动
            try:
                driver.quit()
            except Exception as e:
                print(f"Failed to quit driver: {e}")

        info_csv = pd.DataFrame(info)
        info_csv.drop_duplicates(inplace=True)
        info_csv.to_csv(csv_name, index=False, encoding='gbk')

    @staticmethod
    def sale_parser(csv_name, url=None):
        """
        解析网页信息并保存为CSV文件，包含车型名称、销量、参数链接和评分链接。

        Args:
            csv_name (str): CSV文件保存路径及名称。
            url (str, optional): 目标网页的URL地址，默认为None。

        Returns:
            None
        """
        # 初始化一个字典，用于存储车型名称、销量、参数链接和评分链接
        info = {
            '名称': [],
            '销量': [],
            '参数链接': [],
            '评分链接': []
        }

        # 使用浏览器驱动访问目标网页
        driver.get(url)

        try:
            # 获取网页的初始滚动高度
            last_height = driver.execute_script('return document.body.scrollHeight')

            # 不断滚动页面并加载更多内容
            while True:
                # 滚动到页面底部
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                # 等待一段时间，让页面加载完成
                time.sleep(2)
                # 获取滚动后的页面高度
                new_height = driver.execute_script('return document.body.scrollHeight')

                # 如果页面高度没有变化，说明已经滚动到页面底部，退出循环
                if new_height == last_height:
                    break
                # 更新页面高度
                last_height = new_height

                # 使用BeautifulSoup解析页面源代码
                bs = BeautifulSoup(driver.page_source, 'html.parser')

                # 查找包含车型名称的链接
                links = bs.find_all(class_='tw-leading-28 tw-h-28 tw-truncate')

                # 定义参数链接和评分链接的前缀
                param_link_pre = 'https://www.dongchedi.com/auto/params-carIds-x-'
                score_link_pre = 'https://www.dongchedi.com/auto/series/score/'

                # 遍历链接，提取车型名称、参数链接和评分链接
                for link in links:
                    # 查找包含车型名称的元素
                    b = link.find(class_='tw-font-semibold')
                    # 将车型名称添加到info字典中
                    info['名称'].append(b.get_text())
                    # 获取链接的href属性值
                    href = b['href']
                    # 从href中提取车型ID
                    _id = href.split('/')[-1]
                    # 拼接参数链接和评分链接，并添加到info字典中
                    info['参数链接'].append(param_link_pre + _id)
                    info['评分链接'].append(score_link_pre + _id)

                # 查找包含销量的元素
                div_tags = bs.find_all(class_='tw-py-16 tw-text-center')

                # 遍历包含销量的元素，提取销量并添加到info字典中
                for div_tag in div_tags:
                    sale = div_tag.find(class_='tw-text-18 tw-font-semibold tw-leading-28')
                    info['销量'].append(sale.get_text())

        except Exception as e:
            # 处理在解析过程中可能发生的任何异常
            print(f"An error occurred: {e}")

        finally:
            # 关闭浏览器驱动
            try:
                driver.quit()
            except Exception as e:
                print(f"Failed to quit driver: {e}")

        # 将info字典转换为DataFrame，并保存为CSV文件
        info_csv = pd.DataFrame(info)
        # 删除重复的行
        info_csv.drop_duplicates(inplace=True)
        # 保存CSV文件
        info_csv.to_csv(csv_name, index=False, encoding='gbk')

    def param_parser(self, csv_name, is_json=False, url=None, html=None):
        """
        从网页中提取参数信息并保存到CSV或JSON文件中。

        Args:
            csv_name (str): CSV文件的保存路径及名称。
            is_json (bool, optional): 是否将结果保存为JSON文件，默认为False。
            url (str, optional): 目标网页的URL地址，如果提供了html参数，则忽略此参数。
            html (str, optional): 本地HTML文件的路径，如果提供了url参数，则忽略此参数。

        Returns:
            None
        """
        bs = self.get_html_info(url, html)
        time.sleep(1)
        tables = bs.find_all(class_='table_root__14vH_')
        names = tables[0].find_all(class_='cell_car__28WzZ line-2')
        col_names = []
        for name in names:
            col_names.append(name.get_text())
        print(col_names)
        col_num = len(col_names)
        info = {}
        for table in tables[1:]:
            table_info = table.find_all(class_='table_row__yVX1h')
            table_name = table_info[0].find(class_='cell_title__1COfA').get_text()
            info[table_name] = {}
            for item in table_info[1:]:
                if 'data-row-anchor' in item.attrs:
                    row_name = item.find_all(class_='table_col__3Pc3_')[0].get_text()
                    info[table_name][row_name] = []
                    for row_value in item.find_all(class_='table_col__3Pc3_')[1:]:
                        info[table_name][row_name].append(row_value.get_text())

        if is_json:
            json_file = csv_name[:-len('.csv')] + '.json'
            json_data = json.dumps(info, indent=4, ensure_ascii=False)
            with open(json_file, 'w', encoding='utf8') as f:
                f.write(json_data)

        cols = [[] for _ in range(col_num + 1)]

        for key in info.keys():
            table = info[key]
            for k in table.keys():
                row_name = k
                if len(table[k]) == col_num:
                    cols[0].append(row_name)
                    for idx in range(col_num):
                        cols[idx + 1].append(table[k][idx])
                elif len(table[k]) > col_num + 1:
                    j = 1
                    for _ in range(len(table[k]) // col_num):
                        cols[0].append(row_name)
                        for i in range(col_num):
                            cols[i + 1].append(table[k][j])
                            j += 1
                else:
                    cols[0].append(row_name)
                    for idx in range(len(table[k]) - 1):
                        cols[idx + 1].append(table[k][idx + 1])

        info_dict = {
            '参数名称': cols[0]
        }
        for idx in range(col_num):
            info_dict[col_names[idx]] = cols[idx + 1]
        info_csv = pd.DataFrame(info_dict)
        info_csv.to_csv(csv_name, index=False, encoding='gbk')

    @staticmethod
    def show(names, row1, row2):
        """
        绘制雷达图

        Args:
            names (list): 雷达图特征名称列表，包含列名
            row1 (list): 雷达图第一个数据列表，包含数值
            row2 (list): 雷达图第二个数据列表，包含数值

        Returns:
            None

        """
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.style.use('ggplot')

        values = [float(x) for x in row1[1:]]
        values2 = [float(x) for x in row2[1:]]
        features = names[1:]

        angles = np.linspace(0, 2 * np.pi, len(values), endpoint=False)

        values = np.concatenate((values, [values[0]]))
        values2 = np.concatenate((values2, [values2[0]]))
        an = np.concatenate((angles, [angles[0]]))

        fig = plt.figure()
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles, values, 'o-', linewidth=2, label='当前车系得分')
        ax.fill(angles, values, alpha=0.25)
        ax.plot(an, values2, 'o-', linewidth=2, label='同价位评价分')
        ax.fill(angles, values2, alpha=0.25)
        ax.set_thetagrids(angles[:-1] * 180 / np.pi, features)
        ax.set_ylim(0, 5)
        plt.legend(loc='best')
        ax.grid(True)
        plt.show()

    @staticmethod
    def func(text):
        row2 = text[-4:]
        row1 = text[-8:-4]
        name = text[-len(text):-8]
        return name, row1, row2

    def get_scores(self, csv_name, is_show=False, url=None, html_path=None):
        """
        从网页获取车型评分信息，并保存为CSV文件。

        Args:
            csv_name (str): CSV文件保存路径及名称。
            is_show (bool, optional): 是否展示评分信息，默认为True。
            url (str, optional): 目标网页的URL地址，默认为None。
            html_path (str, optional): 本地HTML文件的路径，默认为None。

        Returns:
            None

        Raises:
            Exception: 当未传入url或html_path参数时。
        """
        # 获取HTML信息
        bs = self.get_html_info(url, html_path)

        # 初始化列表
        names, row1, row2 = [], [], []

        # 获取综合评分
        compresive_score = bs.find(class_='jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 style_comprehensive__KQ0-W')
        # 调用func函数处理综合评分文本
        scores_info = self.func(compresive_score.get_text())

        # 将综合评分添加到列表中
        names.append(scores_info[0])
        row1.append(scores_info[1])
        row2.append(scores_info[2])

        # 查找其他评分
        scores = bs.find_all(class_='jsx-2173306956 style_clearBorder__aC9Rm tw-w-1/8 tw-h-94 null')
        for score in scores:
            # 调用func函数处理评分文本
            scores_info = self.func(score.get_text())

            # 将评分添加到列表中
            names.append(scores_info[0])
            row1.append(scores_info[1])
            row2.append(scores_info[2])

        # 判断是否展示评分信息
        if is_show:
            # 调用show函数展示评分信息
            self.show(names, row1, row2)

        # 构建字典保存评分信息
        score_dict = {
            '项目': ['当前车系得分', '同价位平均分']
        }
        for idx, key in enumerate(names):
            score_dict[key] = [row1[idx], row2[idx]]

        # 将字典转换为DataFrame
        score_csv = pd.DataFrame(score_dict)

        # 将评分信息保存为CSV文件
        score_csv.to_csv(csv_name, index=False, encoding='gbk')


if __name__ == '__main__':
    dongchedi_crawler = DongCheDiCrawler()
    dongchedi_crawler.sale_parser(
        csv_name='sale.csv',
        url='https://www.dongchedi.com/sales/sale-x-x-x-x-x-x'
    )
    df = pd.read_csv('sale.csv', encoding='gbk')
    names = df['名称']
    param_links = df['参数链接']
    score_links = df['评分链接']
    # 3. 爬取汽车参数信息和评分信息
    os.makedirs('参数')
    os.makedirs('得分')
    num_cars = len(names)
    for idx in range(num_cars):
        name = names[idx]  # 汽车名称
        param_link = param_links[idx]  # 汽车参数链接
        score_link = score_links[idx]  # 汽车评分链接
        _id = param_link.split('-')[-1]  # 汽车ID
        dongchedi_crawler.param_parser(
            url=param_link,
            csv_name=f'参数/{name}_{_id}.csv',
        )
        dongchedi_crawler.get_scores(
            url=score_link,
            csv_name=f'得分/{name}_{_id}.csv',
            is_show=False,
        )
