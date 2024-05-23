# 懂车帝汽车排行榜信息爬取
## 介绍
本项目是一个基于`Python+Selenium+Reqeusts+BeautifulSoup`的汽车排行榜信息爬取项目，旨在从懂车帝网站（https://www.dongchedi.com/） 爬取销量榜、麋鹿测试榜、加速榜和制动榜汽车信息。
1. 爬取**汽车排行榜信息**，并将这些数据分别保存为`CSV`文件
2. 爬取`CSV`文件中车辆的**详细参数信息**，并将这些数据保存为`CSV`文件

- 销量榜
![img.png](pics/img.png)
- 麋鹿测试榜
![img_1.png](pics/img_1.png)
- 加速榜
![img.png](pics/img_2.png)
- 制动榜
![img.png](pics/img_3.png)
- 详细参数
![img.png](pics/img_4.png)

## 运行环境
本项目依赖以下Python库：
- `requests`
- `selenium`
- `bs4`
- `pandas`
- `numpy`
- `matplotlib`

**注意：请确保安装了Chrome浏览器和对应版本的ChromeDriver，并将ChromeDriver的路径添加到系统环境变量中，[安装方法](https://blog.csdn.net/Z_Lisa/article/details/133307151)。**

## 代码结构
```
懂车帝汽车信息爬取项目/
│
├── sale.csv - 存储从懂车帝网站爬取的销量排行榜信息。
├── elk_test.csv - 存储从懂车帝网站爬取的麋鹿测试排行榜信息。
├── accelerate.csv - 存储从懂车帝网站爬取的汽车模型信息。
├── brake.csv - 存储从懂车帝网站爬取的汽车模型信息。
│
├── 参数/ - 该目录下包含所有下载的汽车的参数信息。
│   ├── {销量排行榜}/
│   │   ├── {汽车名称}_{汽车ID}.csv
│   │   └── ...
│   ├── {麋鹿测试排行榜}/
│   │   ├── {汽车名称}_{汽车ID}.csv
│   │   └── ...
│   ├── {加速排行榜}/
│   │   ├── {汽车名称}_{汽车ID}.csv
│   │   └── ...
│   ├── {制动排行榜}/
│   │   ├── {汽车名称}_{汽车ID}.csv
│   │   └── ...
├── 得分/ - 该目录下包含所有下载的汽车的评分信息。
│   ├── {销量排行榜}/
│   │   ├── {汽车名称}_{汽车ID}.csv
│   │   └── ...
│   ├── {麋鹿测试排行榜}/
│   │   ├── {汽车名称}_{汽车ID}.csv
│   │   └── ...
│   ├── {加速排行榜}/
│   │   ├── {汽车名称}_{汽车ID}.csv
│   │   └── ...
│   ├── {制动排行榜}/
│   │   ├── {汽车名称}_{汽车ID}.csv
│   │   └── ...
|
└── request_crawler.py - 使用requests和BeautifulSoup爬取汽车参数和评分的脚本。
└── selenuim_crawler.py - 使用Selenium和BeautifulSoup爬取汽车参数和评分的脚本。
```

## 使用方法

```python
from selenuim_crawler import DongciediCrawler
import pandas as pd
import os

dongchedi_crawler = DongCheDiCrawler()

# 1. 爬取销量排行榜信息
dongchedi_crawler.sale_parser(
    csv_name='202404.csv',
    url='https://www.dongchedi.com/sales/sale-x-x-x-x-x-x'
)

# 2. 读取销量排行榜信息
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
    dongchedi_crawler.score_parser(
        url=score_link,
        csv_name=f'得分/{name}_{_id}.csv',
    )
```
## 运行结果
- 销量排行榜信息
![img_2.png](pics/img_5.png)
- 参数信息
![img_1.png](pics/img_6.png)
- 评分信息
![img_3.png](pics/img_7.png)
## 注意事项
- 请在合法范围内使用此爬虫项目，遵守《懂车帝》网站的爬虫政策和相关法律法规。
- 为避免给目标网站服务器带来不必要的负担，建议在爬取数据时适当增加等待时间。