'''
Canada Outbreak update
    scrape through Canada's website, send email for daily update
    including cases around province
    including travel notice 
'''

from selenium import webdriver


driver = webdriver.Chrome()
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

search_id = driver.find_element_by_id('wb-auto-4_filter')
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


