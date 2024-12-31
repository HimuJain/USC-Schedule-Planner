import requests
import pandas as pd
from bs4 import BeautifulSoup
import re


# ! fix the name errors for the schools

# class definitions

class School:
    def __init__(self, schoolData):
        self.code = schoolData['SCHL_CODE']
        self.name = schoolData['SCHL_NAME']

    def to_dict(self):
        return {
            'SCHL_CODE': self.code,
            'SCHL_NAME': self.name
        }
    

class Department:
    def __init__(self, departmentData):
        self.schoolCode = departmentData['SCHL_CODE']
        self.id = departmentData['DEP_ID']
        self.name = departmentData['DEP_NAME']

    def to_dict(self):
        return {
            'SCHL_CODE': self.schoolCode,
            'DEP_ID': self.id,
            'DEP_NAME': self.name
        }

class Course:
    def __init__(self, courseData):
        self.departmentID = courseData['DEP_ID']
        self.number = courseData['CRS_NUM']
        self.code = courseData['CRS_CODE']
        self.name = courseData['CRS_NAME']
        self.description = courseData['CRS_DESC']
        self.geaf = courseData['CRS_GEAF']
        self.gegh = courseData['CRS_GEGH']
        self.unitsStr = courseData['CRS_UNITSTR']
        self.units = courseData['CRS_UNITS']
        self.prerequisites = courseData['CRS_PREREQ']
        self.corequisites = courseData['CRS_COREQ']
        self.notes = courseData['CRS_NOTE']

    def to_dict(self):
        return {
            'DEP_ID': self.departmentID,
            'CRS_NUM': self.number,
            'CRS_CODE': self.code,
            'CRS_NAME': self.name,
            'CRS_DESC': self.description,
            'CRS_GEAF': self.geaf,
            'CRS_GEGH': self.gegh,
            'CRS_UNITSTR': self.unitsStr,
            'CRS_UNITS': self.units,
            'CRS_PREREQ': self.prerequisites,
            'CRS_COREQ': self.corequisites,
            'CRS_NOTE': self.notes
        }
    
class Section:
    def __init__(self, sectionData):
        self.courseDepID = sectionData['DEP_ID']
        self.courseNum = sectionData['CRS_NUM']
        self.id = sectionData['SCT_ID']
        self.type = sectionData['SCT_TYPE']
        self.registered = sectionData['SCT_REG']
        self.seats = sectionData['SCT_SEATS']
        self.building = sectionData['SCT_BUILD']
        self.room = sectionData['SCT_ROOM']
        self.title = sectionData['SCT_TITLE']
        self.units = sectionData['SCT_UNITS']

    def to_dict(self):
        return {
            'DEP_ID': self.courseDepID,
            'CRS_NUM': self.courseNum,
            'SCT_ID': self.id,
            'SCT_TYPE': self.type,
            'SCT_REG': self.registered,
            'SCT_SEATS': self.seats,
            'SCT_BUILD': self.building,
            'SCT_ROOM': self.room,
            'SCT_TITLE': self.title,
            'SCT_UNITS': self.units
        }

class Instructor:
    def __init__(self, instructorData):
        self.id = instructorData['INSTR_ID']
        self.name = instructorData['INSTR_NAME']

    def to_dict(self):
        return {
            'INSTR_ID': self.id,
            'INSTR_NAME': self.name
        }

class Teaches:
    def __init__(self, teachingData):
        self.instructorID = teachingData['INSTR_ID']
        self.sectionID = teachingData['SCT_ID']

    def to_dict(self):
        return {
            'INSTR_ID': self.instructorID,
            'SCT_ID': self.sectionID
        }




def readSchoolsDepartments(departments, schoolList, departmentList):
    schl_code = ''
    for department in departments:
        depType = str(department.get('data-type'))
        if("Requirements" in str(department.get('data-school'))):
            # ! deal with GEs too
            continue
        if(depType == 'school'):
            schl_code = str(department.get('data-code'))
            schl_name = department.text
            schoolObj = School({
                'SCHL_CODE': schl_code,
                'SCHL_NAME': schl_name
            })
            schoolList.append(schoolObj)
        elif(depType == 'department'):
            dep_id = str(department.get('data-code'))
            dep_name = str(department.get('data-title'))

            depObj = Department({
                'SCHL_CODE': schl_code,
                'DEP_ID': dep_id,
                'DEP_NAME': dep_name
            })
            departmentList.append(depObj)

def readCourses(departmentList, courseList, sectionList, instructorList, instructorDict, teachingList):
    for department in departmentList:

        r = requests.get('https://classes.usc.edu/term-20251/classes/' + department.id + '/')
        soup = BeautifulSoup(r.content, 'html.parser')
        soup = soup.find('div', id='content-main')
        soup.extract()
        s = soup.find('div', class_='course-table')
        classes = s.find_all('div', class_='course-info expandable')
        # print(department.name)
        for line in classes:

                lineStr = str(line.get('id'))
                lineStr = lineStr.replace("<div class=\"course-info expandable\" id=\"", "")
                lineStr = lineStr.replace("\"></div>", "")

                tempCode = lineStr
                # ? necessary?

                crs_num = lineStr.split('-')[1]

                courseID = line.find('div', class_='course-id')
                courseID = courseID.find('a')
                crs_code = courseID.find('strong').text
                crs_code = crs_code.replace(":", "")
                crs_name = courseID.text
                crs_name = (crs_name.split(':')[1]).split('(')[0].strip()


                courseDetails = line.find('div', class_='course-details')
                crs_desc = courseDetails.find('div', class_='catalogue').text

                unitsEl = courseID.find('span', class_ = 'units')
                unitsStr = (unitsEl.text)[1:-1:]
                crs_unitstr = ""
                crs_unit = ""
                if('-' in unitsStr or 'max' in unitsStr):
                    crs_unitstr = unitsStr
                else:
                    if(unitsStr.split('.')[0].isdigit()):
                        crs_unit = int(unitsStr.split('.')[0])
                    else:
                        crs_unit = "error"
                
                crs_note = courseDetails.find('ul', class_='notes')
                crs_preq = courseDetails.find('li', class_='prereq')
                if crs_preq is None:
                    crs_preqs = ""
                else:
                    crs_preq = crs_preq.text
                    crs_preq = crs_preq.replace("1 from ", "")

                
                crs_coreq = courseDetails.find('li', class_='coreq')
                if crs_coreq is None:
                    crs_coreq = ""
                else:
                    crs_coreq = crs_coreq.text
                    crs_coreq = crs_coreq.replace("1 from ", "")
                    
                crs_notes = crs_note

                courseObj = Course({
                    'DEP_ID': department.id,
                    'CRS_NUM': crs_num,
                    'CRS_CODE': crs_code,
                    'CRS_NAME': crs_name,
                    'CRS_DESC': crs_desc,
                    'CRS_GEAF': "",
                    'CRS_GEGH': "",
                    'CRS_UNITSTR': crs_unitstr,
                    'CRS_UNITS': crs_unit,
                    'CRS_PREREQ': crs_preq,
                    'CRS_COREQ': crs_coreq,
                    'CRS_NOTE': crs_notes
                })

                courseList.append(courseObj)

                sections = courseDetails.find('table', class_='sections responsive')
                # print(sections.prettify())
                sections = sections.find_all('tr')
                sections = sections[1::]

                readSections(sections, crs_num, department.id, sectionList, instructorList, instructorDict, teachingList)

def readSections(sectionSoup, crs_num, dep_id, sectionList, instructorList, instructorDict, teachingList):
    sectionTitles = False
    sct_num = ""
    sct_title = ""

    for section in sectionSoup:
        classType = str(section.find('td').get('class'))
        if(classType == "[\'section-title\']"):
            sectionTitles = True
            sct_title = section.find('td', class_='section-title').text
            sct_num = sct_title
            re.sub(re.compile('^[^0-9]+'), '', sct_num)
            continue
        elif(sectionTitles and classType == "[\'section\']"):
            if(classType[:5] != sct_num):
                sct_title = ""
            sectionTitles = False
        elif("secondline" in str(section.get('class'))):
            # ! handle second line (additionall timing, see bisc 544)
            continue
        else:
            sct_titles = ""
        
        sct_id = section.find('td', class_='section').text

        sct_type = section.find('td', class_='type').text
        
        sct_enr = section.find('td', class_='registered').text

        sct_enr = sct_enr.split(' of ')
        sct_reg = 0
        sct_seat = 0
        if(len(sct_enr) != 1):
            sct_reg = sct_enr[0]
            if(sct_enr[0].isdigit()):
                sct_reg = sct_enr[0]
            else:
                sct_reg = ("")
            
            sct_seat = sct_enr[1]
            if(sct_seat.isdigit()):
                sct_seat = int(sct_seat)
            else:
                sct_seat = ""
        else:
            sct_reg = 0
            sct_seat = 0


        sct_loc = section.find('td', class_='location')
        sct_build = ""
        sct_room = ""
        if(sct_loc.find('a') is None):
            sct_build = sct_loc.text
            sct_room = ""
        else:
            sct_build = sct_loc.find('a').text

            if(not sct_build.isalpha()):
                sct_build = ""
            
            sct_room = (sct_loc.text).replace(sct_build, "")
            if(not sct_room.isdigit()):
                sct_room = ""

        sct_unit = ""
        if(not (section.find('td', class_='units') is None)):
            sct_unit = section.find('td', class_='units').text
            sct_unit = sct_unit.split('.')[0]
            if(sct_unit.isdigit()):
                sct_unit = int(sct_unit)
            else:
                sct_unit = ""
        
        sectionObj = Section({
            'DEP_ID': dep_id,
            'CRS_NUM': crs_num,
            'SCT_ID': sct_id,
            'SCT_TYPE': sct_type,
            'SCT_REG': sct_reg,
            'SCT_SEATS': sct_seat,
            'SCT_BUILD': sct_build,
            'SCT_ROOM': sct_room,
            'SCT_TITLE': sct_title,
            'SCT_UNITS': sct_unit
        })

        sectionList.append(sectionObj)

        instructors = section.find('td', class_='instructor')
        if instructors is not None and instructors.text != "":
            readInstructors(instructors, sct_id, instructorList, instructorDict, teachingList)

def readInstructors(instructorSoup, sct_id, instructorList, instructorDict, teachingList):
    instructors = instructorSoup.text
    instructors = instructors.split(',')
    for instructor in instructors:
        instr_name = instructor.strip()
        # instructor lookup table appending
        instr_id = 0
        if instr_name in instructorDict:
            instr_id = instructorDict[instr_name]
        else:
            instr_id = len(instructorList) + 1
            instrObj = Instructor({
                'INSTR_ID': instr_id,
                'INSTR_NAME': instr_name
            })
            instructorList.append(instrObj)
            instructorDict[instr_name] = instr_id
        # adding id and sectio info to the teaching table
        teachObj = Teaches({
            'INSTR_ID': instr_id,
            'SCT_ID': sct_id
        })
        teachingList.append(teachObj)




def main():
    print("starting!")
    schoolList = []
    departmentList = []
    courseList = []
    sectionList = []
    instructorList = []
    teachingList = []

    semester = "20251"

    r = requests.get('https://classes.usc.edu/term-' + semester + '/')
    soup = BeautifulSoup(r.content, 'html.parser')
    departments = soup.find('ul', id='sortable-classes')
    departments.extract()
    departments = departments.find_all('li')
    readSchoolsDepartments(departments, schoolList, departmentList)
    instructorDict = {}
    readCourses(departmentList, courseList, sectionList, instructorList, instructorDict, teachingList)

    print("before export")
    pd.DataFrame([school.to_dict() for school in schoolList]).to_csv('schools.csv', index=False)
    pd.DataFrame([department.to_dict() for department in departmentList]).to_csv('departments.csv', index=False)
    pd.DataFrame([course.to_dict() for course in courseList]).to_csv('courses.csv', index=False)
    pd.DataFrame([section.to_dict() for section in sectionList]).to_csv('sections.csv', index=False)
    pd.DataFrame([instructor.to_dict() for instructor in instructorList]).to_csv('instructors.csv', index=False)
    pd.DataFrame([teaching.to_dict() for teaching in teachingList]).to_csv('teaches.csv', index=False)
    print("after export")

if __name__ == '__main__':
    main()