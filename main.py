import os
import pandas as pd

# 1. 读取各个城市各个月份的天气数据，并合并到一个全国天气的数据表中
main_folder = 'weather'  # 主文件夹路径
all_data = []

for city_folder in os.listdir(main_folder):
    city_folder_path = os.path.join(main_folder, city_folder)

    if os.path.isdir(city_folder_path):
        for filename in os.listdir(city_folder_path):
            if filename.endswith('.csv'):
                try:
                    city_data = pd.read_csv(os.path.join(city_folder_path, filename), encoding='gbk')
                    city_data['城市'] = city_folder  # 添加城市名列
                    all_data.append(city_data)
                except UnicodeDecodeError:
                    print(f"无法使用GBK编码读取文件：{filename}")
                    continue  # 跳过无法读取的文件

# 合并所有城市的天气数据
cn_temperature = pd.concat(all_data, ignore_index=True)

# 生成 ID 列
cn_temperature['id'] = range(1, len(cn_temperature) + 1)

# 调整 cn_temperature.csv 列顺序
cn_temperature = cn_temperature[['id', '城市', '日期', '最高温', '最低温', '天气', '风力风向', '空气质量指数']]
# 保存 cn_temperature.csv 文件
cn_temperature.to_csv('cn_temperature.csv', index=False)

# 2. 读取经纬度表并合并到 cn_temperature 数据中
coordinates_df = pd.read_excel('中国城市经纬度表.xls', header=2)  # 跳过前两行
coordinates_df.columns = ['城市', '经度', '纬度']  # 重命名列名
coordinates_df = coordinates_df.dropna(subset=['城市', '经度', '纬度'])  # 删除包含NaN的行
coordinates_df['城市'] = coordinates_df['城市'].str.strip()  # 去除城市名中的空格

# 读取 cn_temperature.csv
cn_temperature_with_coords = pd.read_csv('cn_temperature.csv', low_memory=False)

# 合并经纬度数据
cn_temperature_with_coords = pd.merge(cn_temperature_with_coords, coordinates_df, on='城市', how='left')

# 调整 cn_temperature_with_coords.csv 列顺序
cn_temperature_with_coords = cn_temperature_with_coords[['id', '城市', '日期', '最高温', '最低温', '天气', '风力风向', '空气质量指数', '经度', '纬度']]
# 保存 cn_temperature_with_coords.csv 文件
cn_temperature_with_coords.to_csv('cn_temperature_with_coords.csv', index=False)

# 3. 进一步处理数据
# 使用正则表达式分割日期和星期
cn_temperature_with_coords[['日期', '星期']] = cn_temperature_with_coords['日期'].str.extract(r'(\d{4}-\d{2}-\d{2})\s+(周\w)')

# 分割风力风向列为风力和风向
split_wind = cn_temperature_with_coords['风力风向'].str.extract(r'(\D+)(\d+级)')
split_wind.columns = ['风向', '风力']
cn_temperature_with_coords[['风向', '风力']] = split_wind

# 处理温度列，去掉“度”符号并转化为浮动数字类型
cn_temperature_with_coords['最高温'] = cn_temperature_with_coords['最高温'].str.replace('°', '').astype(float)
cn_temperature_with_coords['最低温'] = cn_temperature_with_coords['最低温'].str.replace('°', '').astype(float)

# 保存处理后的数据为 cn_temperature_processed.csv
cn_temperature_processed = cn_temperature_with_coords[['id', '城市', '日期', '星期', '最高温', '最低温', '天气', '风力', '风向', '空气质量指数', '经度', '纬度']]
cn_temperature_processed.to_csv('cn_temperature_processed.csv', index=False)

# 4. 计算每个城市每月的最高温，最低温和平均气温
# 提取年月
cn_temperature_processed['年月'] = pd.to_datetime(cn_temperature_processed['日期']).dt.to_period('M')

# 按城市和年月分组，计算最高温、最低温和平均气温
monthly_weather = cn_temperature_processed.groupby(['城市', '年月']).agg(
    最高温=('最高温', 'max'),
    最低温=('最低温', 'min'),
    平均气温=('最高温', 'mean')  # 计算平均气温时可以使用最高温的平均值，或者根据需要选择其他列
).reset_index()

# 保留平均气温一位小数
monthly_weather['平均气温'] = monthly_weather['平均气温'].round(1)

# 保存每月天气数据
monthly_weather.to_csv('monthly_weather.csv', index=False)

# 5. 根据最低温，增加一列舒适程度
def comfort_level(temp):
    if temp < 18:
        return '较冷'
    elif 18 <= temp <= 25:
        return '舒适'
    else:
        return '较热'

# 应用舒适度函数
cn_temperature_processed['舒适程度'] = cn_temperature_processed['最低温'].apply(comfort_level)

# 保存处理后的数据为 cn_temperature_processed_with_comfort.csv
cn_temperature_processed_with_comfort = cn_temperature_processed[['id', '城市', '日期', '星期', '最高温', '最低温', '天气', '风力', '风向', '空气质量指数', '经度', '纬度', '舒适程度']]
cn_temperature_processed_with_comfort.to_csv('cn_temperature_processed_with_comfort.csv', index=False)

# 6. 计算每个城市每年舒适天气的天数
# 提取年份
cn_temperature_processed['年份'] = pd.to_datetime(cn_temperature_processed['日期']).dt.year

# 筛选出舒适天气的数据
comfort_days = cn_temperature_processed[cn_temperature_processed['舒适程度'] == '舒适']

# 按城市和年份分组，计算每年舒适天数
comfort_days_count = comfort_days.groupby(['城市', '年份']).size().reset_index(name='舒适天数')

# 保存每年舒适天数数据
comfort_days_count.to_csv('comfort_days_count.csv', index=False)

print("数据处理完成，已保存结果。")