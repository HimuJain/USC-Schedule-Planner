import requests
from bs4 import BeautifulSoup
import re

schl_names = []

dep_schl_names = []
dep_ids = []

crs_dep_ids = []
crs_nums = []
crs_codes = []
crs_names = []
crs_descs = []
crs_geaf = []
crs_gegh = []
crs_unitstrs = []
crs_units = []
crs_preqs = []
crs_coreqs = []
crs_notes = []

sct_ids = []
sct_types = []
sct_regs = []
sct_seats = []
sct_builds = []
sct_rooms = []
sct_titles = []
sct_crs_nums = []
sct_crs_dep_ids = []
sct_units = []

teach_instr_ids = []
teach_sct_ids = []

instr_id = []
instr_names = []

depID = 'csci'
r = requests.get('https://classes.usc.edu/term-20251/classes/' + depID + '/')

# Parsing the HTML  
soup = BeautifulSoup(r.content, 'html.parser')

soup = soup.find('div', id='content-main')
soup.extract()
s = soup.find('div', class_='course-table')
classes = s.find_all('div', class_='course-info expandable')


for line in classes:
    crs_dep_ids.append(depID)

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
    crs_name = courseID.text
    crs_names.append((crs_name.split(':')[1]).split('(')[0].strip())


    courseDetails = line.find('div', class_='course-details')
    crs_desc = courseDetails.find('div', class_='catalogue').text
    crs_descs.append(crs_desc)

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
    
    crs_note = courseDetails.find('ul', class_='notes')
    crs_preq = courseDetails.find('li', class_='prereq')
    if crs_preq is None:
        crs_preqs.append("")
    else:
        crs_preq = crs_preq.text
        crs_preq = crs_preq.replace("1 from ", "")
        crs_preqs.append(crs_preq)

    
    crs_coreq = courseDetails.find('li', class_='corereq')
    if crs_coreq is None:
        crs_coreqs.append("")
    else:
        crs_coreq = crs_coreq.text
        crs_coreq = crs_coreq.replace("1 from ", "")
        crs_coreqs.append(crs_coreq)
        
    crs_notes.append(crs_note)

    sections = courseDetails.find('table', class_='sections responsive')
    sections = sections.find('tbody')
    sections = sections.find_all('tr')
    sections = sections[1::]
    for section in sections:
        # deal with titles
        sct_id = section.find('td', class_='section').text
        sct_ids.append(sct_id)

        sct_type = section.find('td', class_='type').text
        sct_types.append(sct_type)

        sct_seats = section.find('td', class_='registered').text

        sct_seats = sct_seats.split(' of ')
        sct_reg = sct_seats[0]
        if(sct_seats[0].isdigit()):
            sct_regs.append(int(sct_seats[0]))
        else:
            sct_regs.append("")
        
        sct_seats = sct_seats[1]
        if(sct_seats.isdigit()):
            sct_seats.append(int(sct_seats[1]))
        else:
            sct_seats.append("")

        sct_loc = section.find('td', class_='location')
        sct_loc = sct_loc.split(' ')

        sct_build = sct_loc[0]
        if(sct_build.isalpha()):
            sct_builds.append(sct_build)
        else:
            sct_builds.append("")
        
        sct_room = sct_loc[1]
        if(sct_room.isdigit()):
            sct_rooms.append(sct_room)
        else:
            sct_rooms.append("")

        

        sct_titles.append(section.find('td', class_='title').text)
        sct_crs_nums.append(crs_num)
        sct_crs_dep_ids.append(depID)
        sct_units.append(section.find('td', class_='units').text)

        instructors = section.find('td', class_='instructor')
        instructors = instructors.find_all('a')
        for instructor in instructors:
            instr_id.append(instructor.get('href').replace("/term-20251/instructors/", ""))
            instr_names.append(instructor.text)
            teach_instr_ids.append(instructor.get('href').replace("/term-20251/instructors/", ""))
            teach_sct_ids.append(sct_ids[-1])