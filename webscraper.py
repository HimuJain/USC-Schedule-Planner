import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import cProfile
import concurrent.futures

# the url session is a global variable because i need it to be used in the fetchURL function by default,
# and i can't pass it as an argument to the fetchURL function because it is called by the ThreadPoolExecutor
urlSession = requests.Session()


# class definitions based on the sql database schema
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
        self.dcorel = courseData['CRS_DCOREL']
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
            'CRS_DCOREL': self.dcorel,
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
        self.semester = sectionData['SCT_SEMESTER']

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
            'SCT_UNITS': self.units,
            'SCT_SEMESTER': self.semester
        }

class Schedule:
    def __init__(self, scheduleData):
        self.sectionID = scheduleData['SCT_ID']
        self.scheduleID = scheduleData['SCH_ID']
        self.day = scheduleData['SCH_DAY']
        self.start = scheduleData['SCH_STTIME']
        self.end = scheduleData['SCH_ENTIME']

    def to_dict(self):
        return {
            'SCT_ID': self.sectionID,
            'SCH_ID': self.scheduleID,
            'SCH_DAY': self.day,
            'SCH_STTIME': self.start,
            'SCH_ENTIME': self.end
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

# Parameters: url
# Returns: BeautifulSoup object
# Description: fetches the html content of the url and returns a BeautifulSoup object
def fetchURL(url):
    r = urlSession.get(url)
    return BeautifulSoup(r.content, 'lxml')

# Parameters: generalEducations, geafDict, geghDict, dCoreSet
def readGeneralEducation(generalEducations, geafDict, geghDict, dCoreSet):
    print("reading general education")
    geUrls = []
    geResponses = []
    geCategories = []
    for ge in generalEducations:
        geCode = str(ge.get('data-code'))
        geTitle = str(ge.get('data-title'))
        if("Seminar" in geTitle):
            continue
        elif("Core " in geTitle):
            geCategory = "L"
        else:
            geTitle = geTitle.replace("Category ", "")
            geCategory = geTitle[0]
        geCategories.append(geCategory)
        geUrls.append('https://classes.usc.edu/term-20251/classes/' + geCode + '/')
    
    for i in range(len(geUrls)):
        r = urlSession.get(geUrls[i])
        geResponses.append(r)

    for i in range(len(geResponses)):
        r = geResponses[i]
        geCategory = geCategories[i]
        soup = BeautifulSoup(r.content, 'lxml')
        soup = soup.find('div', id='content-main')
        soup.extract()
        s = soup.find('div', class_='course-table')
        classes = s.find_all('div', class_='course-info expandable')

        for line in classes:
            lineStr = str(line.get('id'))
            lineStr = lineStr.replace("<div class=\"course-info expandable\" id=\"", "")
            lineStr = lineStr.replace("\"></div>", "")
            crs_id = lineStr.replace("-", "")

            if(geCategory >= 'A' and geCategory <= 'F'):
                geafDict[crs_id] = geCategory
            elif(geCategory >= 'G' and geCategory <= 'H'):
                geghDict[crs_id] = geCategory
            elif(geCategory == 'L'):
                dCoreSet.add(crs_id)



def readSchoolsDepartments(departments, schoolList, departmentList):
    print("reading schools and departments")
    schl_code = ''
    for department in departments:
        depType = str(department.get('data-type'))
        if("Requirements" in str(department.get('data-school')) and "Seminar" not in str(department.get('data-title'))):
            # already dealt with general education
            continue
        if(depType == 'school'):
            schl_code = str(department.get('data-code'))
            schl_name = department.text
            schl_name = schl_name.strip()
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


def readCourses(departmentSoups, departmentList, courseList, sectionSoupDict, geafDict, geghDict, dCoreSet):
    print("reading courses")
    for department in departmentList:

        # r = departmentRequests[department.id]
        # soup = BeautifulSoup(r.content, 'lxml')
        soup = departmentSoups[department.id]
        soup = soup.find('div', id='content-main')
        soup.extract()
        s = soup.find('div', class_='course-table')
        classes = s.find_all('div', class_='course-info expandable')
        # print(department.name)

        for line in classes:

            lineStr = str(line.get('id'))
            lineStr = lineStr.replace("<div class=\"course-info expandable\" id=\"", "")
            lineStr = lineStr.replace("\"></div>", "")


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
                    print("error in units")
            
            crs_note = courseDetails.find('ul', class_='notes')
            crs_preq = courseDetails.find('li', class_='prereq')
            if crs_preq is None:
                crs_preq = ""
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

            crs_id = department.id + crs_num
            crs_geaf = ""
            crs_gegh = ""
            crs_dcorel = False
            if crs_id in geafDict:
                crs_geaf = geafDict[crs_id]
            if crs_id in geghDict:
                crs_gegh = geghDict[crs_id]
            if crs_id in dCoreSet:
                crs_dcorel = True

            courseObj = Course({
                'DEP_ID': department.id,
                'CRS_NUM': str(crs_num),
                'CRS_CODE': crs_code,
                'CRS_NAME': crs_name,
                'CRS_DESC': crs_desc,
                'CRS_GEAF': crs_geaf,
                'CRS_GEGH': crs_gegh,
                'CRS_DCOREL': crs_dcorel,
                'CRS_UNITSTR': crs_unitstr,
                'CRS_UNITS': crs_unit,
                'CRS_PREREQ': crs_preq,
                'CRS_COREQ': crs_coreq,
                'CRS_NOTE': crs_notes
            })

            courseList.append(courseObj)

            sections = courseDetails.find('table', class_='sections responsive')
            # print(sections.prettify())
            sectionHTML = sections.find_all('tr')
            sectionHTML = sectionHTML[1::]

            counter = 0
            for section in sectionHTML:
                sectionSoupDict[department.id + " " + crs_num + " " + str(counter)] = section
                counter += 1
        
        
            line.extract()

def createSchedule(scheduleSoup, sct_id, scheduleList, scheduledSet):
    if(sct_id in scheduledSet):
        return

    schedTime = scheduleSoup.find(class_ = 'time').extract()
    schedTime = schedTime.text

    schd_sttime = ""
    schd_entime = ""

    meridiem = schedTime[-2::]
    schedTime = schedTime[:-2]
    schedTime = schedTime.split('-')

    if("pm" in meridiem):
        for time in schedTime:
            time = time.split(':')
            if(time[0] != "12"):
                time[0] = str(int(time[0]) + 12)
            time = ':'.join(time)
            if(schd_sttime == ""):
                schd_sttime = time
            else:
                schd_entime = time
    elif("am" in meridiem):
        for time in schedTime:
            time = time.split(':')
            if(time[0] == "12"):
                time[0] = "00"
            time = ':'.join(time)
            if(schd_sttime == ""):
                schd_sttime = time
            else:
                schd_entime = time

    schedDay = scheduleSoup.find(class_ = 'days').extract()
    schedDay = schedDay.text

    schd_day = []

    capCount = 0

    for i in schedDay:
        if(i.isupper()):
            capCount += 1

    if("TBA" in schedDay):
        schd_day = [""]
    elif("," in schedDay):
        schedDay = schedDay.split(', ')
        for day in schedDay:
            schd_day.append(day[:3].strip().upper())
    elif(capCount > 1):
        if("M" in schedDay):
            schd_day.append("MON")
        
        if("Tu" in schedDay):
            schd_day.append("TUE")
        
        if("W" in schedDay):
            schd_day.append("WED")
        
        if("Th" in schedDay):
            schd_day.append("THU")

        if("F" in schedDay):
            schd_day.append("FRI")

        if(len(schd_day) == 0):
            print("error in day")
            print(schedDay)
    else:
        schd_day.append(schedDay[:3].upper())
        
    for day in schd_day:
        scheduleObj = Schedule({
            'SCT_ID': sct_id,
            'SCH_ID': len(scheduleList) + 1,
            'SCH_DAY': day,
            'SCH_STTIME': schd_sttime,
            'SCH_ENTIME': schd_entime
        })
        scheduleList.append(scheduleObj)
    

    scheduledSet.add(sct_id)
    
    


        

def readSections(sectionSoupDict, sectionList, instructorListDict, scheduleList, scheduledSet, semester):
    sectionTitles = False
    sct_num = ""
    sct_title = ""
    sct_id = ""

    
    for secID, sectionHTML in sectionSoupDict.items():
        classType = str(sectionHTML.find('td').get('class'))
        if(classType == "[\'section-title\']"):
            sectionTitles = True
            sct_title = sectionHTML.find('td', class_='section-title').text
            sct_num = sectionHTML.get('class')[-1]
            continue
        elif(sectionTitles and classType == "[\'section\']"):
            if(sectionHTML.get('data-section-id') != sct_num):
                sct_title = ""
            sectionTitles = False
        elif("secondline" in str(sectionHTML.get('class'))):
            createSchedule(sectionHTML, sct_id, scheduleList, scheduledSet)
            continue
        else:
            sct_title = ""

        sct_num = sectionHTML.get('class')[0]
        sct_id = sectionHTML.find('td', class_='section').text

        sct_type = sectionHTML.find('td', class_='type').text
        
        sct_enr = sectionHTML.find('td', class_='registered').text
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


        sct_loc = sectionHTML.find('td', class_='location')
        sct_build = ""
        sct_room = ""
        if(sct_loc.find('a') is None):
            sct_build = sct_loc.text
            sct_room = ""
        else:
            sct_build = sct_loc.find('a').text
            sct_room = (sct_loc.text).replace(sct_build, "")

        sct_unit = ""
        if(not (sectionHTML.find('td', class_='units') is None)):
            sct_unit = sectionHTML.find('td', class_='units').text
            sct_unit = sct_unit.split('.')[0]
            if(sct_unit.isdigit()):
                sct_unit = int(sct_unit)
            else:
                sct_unit = ""
            
        secID = secID.split(' ')
        dep_id = secID[0]
        crs_num = secID[1]

        createSchedule(sectionHTML, sct_id, scheduleList, scheduledSet)
        sectionObj = Section({
            'DEP_ID': dep_id,
            'CRS_NUM': str(crs_num),
            'SCT_ID': sct_id,
            'SCT_TYPE': sct_type,
            'SCT_REG': sct_reg,
            'SCT_SEATS': sct_seat,
            'SCT_BUILD': sct_build,
            'SCT_ROOM': str(sct_room),
            'SCT_TITLE': sct_title,
            'SCT_UNITS': sct_unit,
            'SCT_SEMESTER': semester
        })

        sectionList.append(sectionObj)
        instructors = sectionHTML.find('td', class_='instructor')
        if instructors is not None and instructors.text != "":

            instructorText = instructors.text
            instructorText = instructorText.split(',')
            for instructor in instructorText:
                instructorListDict[sct_id] = instructor

        instructors.extract()
        
        sectionHTML.extract()

def readInstructors(instructorListDict, instructorList, teachingList):

    instructorDict = {}

    for sct_id, instructor in instructorListDict.items():
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
    scheduleList = []

    #     import logging

    # # These two lines enable debugging at httplib level (requests->urllib3->http.client)
    # # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # # The only thing missing will be the response.body which is not logged.
    #     try:
    #         import http.client as http_client
    #     except ImportError:
    #         # Python 2
    #         import http.client as http_client
    #     http_client.HTTPConnection.debuglevel = 1

    #     # You must initialize logging, otherwise you'll not see debug output.
    #     logging.basicConfig()
    #     logging.getLogger().setLevel(logging.DEBUG)
    #     requests_log = logging.getLogger("requests.packages.urllib3")
    #     requests_log.setLevel(logging.DEBUG)
    #     requests_log.propagate = True

    semester = 20231

    r = urlSession.get('https://classes.usc.edu/term-' + str(semester) + '/')
    soup = BeautifulSoup(r.content, 'lxml')
    departments = soup.find('ul', id='sortable-classes')
    departments.extract()
    generalEducation = departments.find_all('li', {"data-school":"GE Requirements for Students Beginning College in Fall 2015 or Later"})

    geafDict = {}
    geghDict = {}
    dCoreSet = set()
    readGeneralEducation(generalEducation, geafDict, geghDict, dCoreSet)

    departments = departments.find_all('li')
    readSchoolsDepartments(departments, schoolList, departmentList)



    # depUrlList = []
    # departmentRequests = {}
    # print("requesting departments")
    # for department in departmentList:
    #     print(department.name)
    #     departmentRequests[department.id] = urlSession.get('https://classes.usc.edu/term-' + str(semester) + '/classes/' + department.id + '/')
    # print("finished requesting departments")


    # readCourses(departmentRequests, departmentList, courseList, sectionList, instructorList, instructorDict, teachingList, scheduleList, geafDict, geghDict, dCoreSet, semester)



    depUrlList = []
    for department in departmentList:
        depUrlList.append('https://classes.usc.edu/term-' + str(semester) + '/classes/' + department.id + '/')

    print("future stuff")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(fetchURL, depUrlList)
    print("after future stuff")

    departmentSoups = {}

    for soup in results:
        depID = soup.find('abbr').text
        departmentSoups[depID] = soup

    sectionSoupDict = {}
    readCourses(departmentSoups, departmentList, courseList, sectionSoupDict, geafDict, geghDict, dCoreSet)

    instructorListDict = {}

    scheduledSet = set()

    readSections(sectionSoupDict, sectionList, instructorListDict, scheduleList, scheduledSet, semester)

    readInstructors(instructorListDict, instructorList, teachingList)

    print("before export")
    pd.DataFrame([school.to_dict() for school in schoolList]).to_csv('schools.csv', index=False)
    pd.DataFrame([department.to_dict() for department in departmentList]).to_csv('departments.csv', index=False)
    pd.DataFrame([course.to_dict() for course in courseList]).to_csv('courses.csv', index=False)
    pd.DataFrame([section.to_dict() for section in sectionList]).to_csv('sections.csv', index=False)
    pd.DataFrame([instructor.to_dict() for instructor in instructorList]).to_csv('instructors.csv', index=False)
    pd.DataFrame([teaching.to_dict() for teaching in teachingList]).to_csv('teaches.csv', index=False)
    pd.DataFrame([schedule.to_dict() for schedule in scheduleList]).to_csv('schedules.csv', index=False)
    print("after export")

if __name__ == '__main__':
    main()