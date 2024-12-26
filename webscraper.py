import requests
from bs4 import BeautifulSoup


depID = 'csci'
r = requests.get('https://classes.usc.edu/term-20251/classes/' + depID + '/')

# Parsing the HTML  
soup = BeautifulSoup(r.content, 'html.parser')

s = soup.find('div', class_='course-table')
classIDs = s.find_all('div', class_='course-info expandable')
dep_ids = []
crs_nums = []
crs_codes = []
crs_names = []
crs_descs = []
crs_geaf = []
crs_gegh = []
crs_unitstrs = []
crs_units = []

for line in classIDs:
    dep_ids.append(depID)

    lineStr = str(line.get('id'))
    lineStr = lineStr.replace("<div class=\"course-info expandable\" id=\"", "")
    lineStr = lineStr.replace("\"></div>", "")

    tempCode = lineStr
    # ? necessary?

    crs_num = lineStr.split('-')[1]
    crs_nums.append(crs_num)

    courseID = line.find('div', class_='course-id')
    courseID = courseID.find('a')
    crs_code = courseID.find('strong').text

    crs_codes.append(crs_code.replace(":", ""))

    crs_desc = courseID.text
    crs_descs.append((crs_desc.split(':')[1]).split('(')[0].strip())

    unitsEl = courseID.find('span', class_ = 'units')
    unitsStr = (unitsEl.text)[1:-1:]
    if('-' in unitsStr or 'max' in unitsStr):
        crs_unitstrs.append(unitsStr)
        crs_units.append("")
    else:
        crs_unitstrs.append("")
        if(unitsStr.split('.')[0].isdigit()):
            crs_units.append(int(unitsStr.split('.')[0]))
        else:
            crs_units.append("error")
# ! WAIT HOW THE HELL DO WE DO PREREQUISITES

    courseDetails = line.find('div', class_='course-details')


# s = soup.find('div', class_='course-info expandable')
# s = soup.find('div', class_='course-details')
# s = soup.find('div', id='CSCI-102-details')
# print(s.prettify())
# s = soup.find('div', id='CSCI-103-details')
# content = soup.find_all('p')
print(crs_units)
print(crs_unitstrs)
# print(crs_codes)
# print(s.prettify())