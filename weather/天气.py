import requests
import json
import csv
from bs4 import BeautifulSoup

# 城市编码映射表
city_codes = {
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://tianqi.2345.com/wea_history/54511.htm',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'areaInfo[areaId]': '',
    'areaInfo[areaType]': '2',
    'date[year]': '2024',
    'date[month]': '3',
}

def fetch_weather_data(city_code, year, month):
    params['areaInfo[areaId]'] = city_code
    params['date[year]'] = year
    params['date[month]'] = str(int(month))
    response = requests.get('https://tianqi.2345.com/Pc/GetHistory', params=params, headers=headers)
    try:
        rsp = response.json()
        return rsp
    except:
        print(response.text)
        return {"code": 0}
    

def parse_weather_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    weather_data = []
    
    # 解析表格数据
    table = soup.find('table', {'class': 'history-table'})
    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:  # 跳过表头
            cols = row.find_all('td')
            date = cols[0].text.strip()
            high_temp = cols[1].text.strip()
            low_temp = cols[2].text.strip()
            weather = cols[3].text.strip()
            wind = cols[4].text.strip()
            try:
                aqi = cols[5].text.strip()
            except:
                aqi = 'null'
            weather_data.append([date, high_temp, low_temp, weather, wind, aqi])
    
    return weather_data
import os
import time

def save_to_csv(city_name, year, month, weather_data):
    os.makedirs(f'./{city_name}', exist_ok=True)
    with open(f'./{city_name}/{year}{month}.csv', 'w', newline='', encoding='gbk') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['日期', '最高温', '最低温', '天气', '风力风向', '空气质量指数'])
        writer.writerows(weather_data)

def create_timerange():
    start_year = 2023
    stop_year = 2024

    # 创建一个列表容器，储存函数返回值
    weather_database = []
    # 日期生成器
    for date_year in range(start_year, stop_year + 1):
        for date_month in range(1, 13):
            # time.sleep(5)  # 延迟一秒，减少对网站压力。
            date_month_str = f"{date_month:02d}"  # 使用 f-string 格式化月份，确保是两位数
            date_f = (date_year,date_month_str)
            weather_database.append(date_f)
    return weather_database[11:-1]

time_range = create_timerange()
# 主程序
for city_name, city_code in city_codes.items():
    for year, month in time_range:
        response_data = fetch_weather_data(city_code, year, month)
        if response_data['code'] == 1:
            weather_data = parse_weather_data(response_data['data'])
            save_to_csv(city_name,year, month,weather_data)
            print(f"已保存 {city_name} 的天气数据到 {city_name}_weather.csv")
        else:
            print(f"获取 {city_name} 的天气数据失败")
