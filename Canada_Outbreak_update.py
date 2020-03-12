'''
Canada Outbreak update
    scrape through Canada's website, send email for daily update
    including cases around province
    including travel notice 
'''

from selenium import webdriver



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
 
    return row_delim.join(
               col_delim.join(
                   format.format(cell, width)
                   for format, cell, width in zip(row_format, row, col_widths))
               for row_format, row in zip(table_format, table))



driver = webdriver.Chrome()
driver.implicitly_wait(3)
driver.get('https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection.html#a1')

# navigate to the web tb, store info in tb
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

travel_tb.append([x.text for x in thlist])

web_travel_tbody = driver.find_element_by_tag_name('tbody')
trlist = web_travel_tbody.find_elements_by_tag_name('tr')
for row in trlist:
    tdlist = row.find_elements_by_tag_name('td')
    line = [x.text for x in tdlist]
    if line:
        travel_tb.append(line)

driver.close() 



# show tables
print(format_matrix(tb[0], tb[1:]))
print(format_matrix(travel_tb[0], travel_tb[1:]))



