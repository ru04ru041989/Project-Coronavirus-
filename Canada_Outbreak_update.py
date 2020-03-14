'''
Canada Outbreak update
    scrape through Canada's website, send email for daily update
    including cases around province
    including travel notice 
'''

from selenium import webdriver
import pandas as pd
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from email_info import username, password


# print list as table
## source: author: campkeith @ stackoverflow, question: #9535954: printing-lists-as-tabular-data
## partically modify
def format_matrix(header, matrix,
                  top_format = '{:^{}}', left_format = '{:<{}}', cell_format = '{:>{}}', 
                  row_delim = '\n', col_delim = ' | ', print_header = True):
    #table = [header] + [[name] + row for name, row in zip(header, matrix)]
    table = [header] + matrix

    table_format = [['{:^{}}'] + len(header) * [top_format]] \
                 + len(matrix) * [[left_format] + len(header) * [cell_format]]
    
    col_widths = [max(
                      len(format.format(cell, 0))
                      for format, cell in zip(col_format, col))
                  for col_format, col in zip(zip(*table_format), zip(*table))]

    if print_header:
        table = [header] + [['='* int(n) for n in col_widths]] +matrix
        table_format.append([left_format] + len(header) * [cell_format])
        
    return row_delim.join(
               col_delim.join(
                   format.format(cell, width)
                   for format, cell, width in zip(row_format, row, col_widths))
               for row_format, row in zip(table_format, table))


# create table as html
def tbody_html(tb):
    add_td = []
    for row in tb:
        add_td.append('<td>' + '</td><td>'.join(row)  + '</td>')
    
    return '<tr>' + '</tr><tr>'.join(add_td) + '</tr>'

driver = webdriver.Chrome()
driver.implicitly_wait(3)
driver.get('https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection.html#a1')

# navigate to the web tb, store info in tb

# updated date
updated_date = driver.find_element_by_tag_name('caption')
updated_date = updated_date.text

# table
tb = []
web_tb = driver.find_element_by_class_name('table-responsive')

thlist = web_tb.find_elements_by_tag_name('th')
tb.append([x.text for x in thlist])


trlist = web_tb.find_elements_by_tag_name('tr')
for row in trlist:
    tdlist = row.find_elements_by_tag_name('td')
    line = [x.text for x in tdlist]
    if line:
        tb.append(line)


# scrape travel notice in CAD
driver.get('https://travel.gc.ca/travelling/health-safety/travel-health-notices')

search_id = driver.find_element_by_class_name('dataTables_filter')
search = search_id.find_element_by_tag_name('input')

search.clear()
search.send_keys('COVID-19')

travel_tb = []
web_travel_thead = driver.find_element_by_tag_name('thead')
thlist = web_travel_thead.find_elements_by_tag_name('th')
travel_th = [x.text for x in thlist] + ['Note']
travel_tb.append(travel_th)

web_travel_tbody = driver.find_element_by_tag_name('tbody')
trlist = web_travel_tbody.find_elements_by_tag_name('tr')

# add meaning of each level
lv = {}
panel_headings = driver.find_elements_by_class_name('panel-heading')
for line in panel_headings:
    lv[line.text.split(' - ')[0]] = line.text.split(' - ')[1]

for row in trlist:
    tdlist = row.find_elements_by_tag_name('td')
    line = [x.text for x in tdlist]
    if line:
        line.append(lv[line[-1]])
        travel_tb.append(line)

for row in travel_tb:
    del row[1]

driver.close() 

# read csv file, extract canada data
df = pd.read_csv('COVID19.csv')
now = datetime.now().strftime('%Y-%m-%d')
focus_col = ['Total Cases','New Cases','Total Deaths','Total Recovered','Active Cases','Date']

df = df[df['Country, Other'] == 'Canada'][focus_col]
df = df.fillna('0')
df_body = df.values.tolist()


## sending email

msg = MIMEMultipart()
msg['Subject'] = 'Coronavirus stats in Canada today!'
msg['From'] = username
msg['To'] = username

# create html
html = '''\
<html>
<head>
<title>Coronavirus stats in Canada today!</title>
<body>
<div id='container'>
    <div>
    <h2> COVID19 in Canada @ '''+ now + '''  </h2>
    <p> Info from https://www.worldometers.info/coronavirus/</p>
    <table style="border:3px #cccccc solid;" cellpadding="10" border='1'>
        <thead>
            <tr> <th>'''+ '</th><th>'.join(focus_col) +''' </th></tr>
        </thead>
        <tbody>
            ''' + tbody_html(df_body) +'''
        </tbody>
    </table>
    </div>
    <hr>
    <div>
    <h2> ''' + updated_date + ''' </h2>
    <p>Info from https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection.html</p>
    <table style="border:3px #cccccc solid;" cellpadding="10" border='1'>
        <thead>
            <tr> <th>'''+ '</th><th>'.join(tb[0]) +''' </th></tr>
        </thead>
        <tbody>
            ''' + tbody_html(tb[1:]) +'''
        </tbody>
    </table>
    </div>
    
    <div>
    <h2> Travel notice </h2>
    <table style="border:3px #cccccc solid;" cellpadding="10" border='1'>
        <thead>
            <tr> <th>'''+ '</th><th>'.join(travel_tb[0]) +''' </th></tr>
        </thead>
        <tbody>
            ''' + tbody_html(travel_tb[1:]) +'''
        </tbody>
    </table>
    </div>   
</div>
</body>
</head>
</html>
    '''

context = MIMEText(html,_subtype='html',_charset='utf-8')
msg.attach(context)

try:
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(username, password)
    mail.sendmail(username, username, msg.as_string())
    mail.quit()
    print('Email send')

except:
    print('Email not send')
