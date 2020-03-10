# package
from selenium import webdriver
import pandas as pd
from datetime import datetime
import os.path


driver = webdriver.Chrome()
driver.get('https://www.worldometers.info/coronavirus/')

# get table header
tb_head = driver.find_element_by_xpath('//*[@id="main_table_countries"]/thead/tr[1]')
df_header = []

thlist = tb_head.find_elements_by_tag_name('th')
for col in thlist:
    df_header.append(col.text.replace('\n',' '))

# ['Country, Other', 'Total Cases', 'New Cases', 'Total Deaths', 'New Deaths', 
# 'Total Recovered', 'Active Cases', 'Serious, Critical', 'Tot Cases/ 1M pop']


# get the table body
tb_body = driver.find_element_by_xpath('//*[@id="main_table_countries"]/tbody[1]')
df_body = []

# get tr element list
trlist = tb_body.find_elements_by_tag_name('tr')
for row in trlist:
    tdlist = row.find_elements_by_tag_name('td')
    each_row = []
    for col in tdlist:
        try:
            each_row.append(col.text)
        except:
            pass
    df_body.append(each_row)


driver.close()       


# create COVID df
df = pd.DataFrame(df_body, columns = df_header)

# adding date to df
now = datetime.now().strftime('%Y-%m-%d')
date = [now]*len(df)

df['Date'] = date

# append df to csv, if csv not exist, create and save df
# if csv exist, check if date information has been update, if not, append to csv
if os.path.isfile('COVID19.csv'):
    csv_df = pd.read_csv('COVID19.csv')
    if now not in list(df['Date']):
        df.to_csv('COVID19.csv', mode = 'a', header = False, index = False)
else:
    df.to_csv('COVID19.csv', index = False)