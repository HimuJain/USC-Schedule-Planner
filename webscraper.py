import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

def main():

    instrID = 1

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

        
        crs_coreq = courseDetails.find('li', class_='coreq')
        if crs_coreq is None:
            crs_coreqs.append("")
        else:
            crs_coreq = crs_coreq.text
            crs_coreq = crs_coreq.replace("1 from ", "")
            crs_coreqs.append(crs_coreq)
            
        crs_notes.append(crs_note)

        sections = courseDetails.find('table', class_='sections responsive')
        # print(sections.prettify())
        sections = sections.find_all('tr')
        sections = sections[1::]

        sectionTitles = False
        sct_num = ""
        sct_title = ""

        for section in sections:
            classType = str(section.get('class'))
            if('firstline' in classType):
                sectionTitles = True
                sct_title = section.find('td', class_='section-title').text
                sct_num = sct_title
                re.sub(re.compile('^[^0-9]+'), '', sct_num)
                continue
            elif(sectionTitles and 'secondline' in classType):
                if(classType[:5] == sct_num):
                    sct_titles.append(sct_title)
                else:
                    sct_titles.append("")
                sectionTitles = False
            else:
                sct_titles.append("")
                    
            sct_id = section.find('td', class_='section').text
            sct_ids.append(sct_id)

            sct_type = section.find('td', class_='type').text
            sct_types.append(sct_type)
            
            sct_enr = section.find('td', class_='registered').text

            sct_enr = sct_enr.split(' of ')
            if(len(sct_enr) == 1):
                sct_regs.append(0)
                sct_seats.append(0)
            else:
                sct_reg = sct_enr[0]
                if(sct_enr[0].isdigit()):
                    sct_regs.append(int(sct_enr[0]))
                else:
                    sct_regs.append("")
                
                sct_seat = sct_enr[1]
                if(sct_seat.isdigit()):
                    sct_seats.append(int(sct_seat))
                else:
                    sct_seats.append("")

            sct_loc = section.find('td', class_='location')
            if(sct_loc.find('a') is None):
                sct_builds.append(sct_loc.text)
                sct_rooms.append("")
            else:
                sct_build = sct_loc.find('a').text

                if(sct_build.isalpha()):
                    sct_builds.append(sct_build)
                else:
                    sct_builds.append("")
                
                sct_room = (sct_loc.text).replace(sct_build, "")
                if(sct_room.isdigit()):
                    sct_rooms.append(sct_room)
                else:
                    sct_rooms.append("")

            
            sct_crs_nums.append(crs_num)
            sct_crs_dep_ids.append(depID)
            if(section.find('td', class_='units') is None):
                sct_units.append("")
            else:
                sct_unit = section.find('td', class_='units').text
                sct_unit = sct_unit.split('.')[0]
                if(sct_unit.isdigit()):
                    sct_units.append(int(sct_unit))
                else:
                    sct_units.append("")

            instructors = section.find('td', class_='instructor')
            if instructors is not None and instructors.text != "":
                instructors = instructors.text
                instructors = instructors.split(',')
                for instructor in instructors:
                    instr_name = instructor.strip()
                    # instructor lookup table appending
                    instr_id.append(instrID)
                    instr_names.append(instr_name)
                    # adding id and sectio info to the teaching table
                    teach_instr_ids.append(instrID)
                    teach_sct_ids.append(sct_id)
                    instrID += 1

    print("before dict")
    crs_dict = {
        'DEP_ID': crs_dep_ids,
        'CRS_NUM': crs_nums,
        'CRS_CODE': crs_codes,
        'CRS_NAME': crs_names,
        'CRS_DESC': crs_descs,
        'CRS_UNITSTR': crs_unitstrs,
        'CRS_UNITS': crs_units,
        'CRS_PREREQ': crs_preqs,
        'CRS_COREQ': crs_coreqs,
        'CRS_NOTE': crs_notes
    }

    sct_dict = {
        'SCT_ID': sct_ids,
        'SCT_TYPE': sct_types,
        'SCT_REG': sct_regs,
        'SCT_SEATS': sct_seats,
        'SCT_BUILD': sct_builds,
        'SCT_ROOM': sct_rooms,
        'SCT_TITLE': sct_titles,
        'SCT_CRS_NUM': sct_crs_nums,
        'SCT_CRS_DEP_ID': sct_crs_dep_ids,
        'SCT_UNITS': sct_units
    }

    teach_dict = {
        'INSTR_ID': teach_instr_ids,
        'SCT_ID': teach_sct_ids
    }

    instr_dict = {
        'INSTR_ID': instr_id,
        'INSTR_NAME': instr_names
    }
    print("before export")
    pd.DataFrame(crs_dict).to_csv('courses.csv', index=False)
    pd.DataFrame(sct_dict).to_csv('sections.csv', index=False)
    pd.DataFrame(teach_dict).to_csv('teaches.csv', index=False)
    pd.DataFrame(instr_dict).to_csv('instructors.csv', index=False)
    print("after export")

if __name__ == '__main__':
    main()