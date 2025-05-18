import requests
import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures
from collections import defaultdict

# the url session is a global variable because i need it to be used in the fetchURL function by default,
# and i can't pass it as an argument to the fetchURL function because it is called by the ThreadPoolExecutor
urlSession = requests.Session()


# class definitions based on the sql database schema

# Semester class stores the different semesters 
class Semester:
    def __init__(self, semesterData):
        self.semester = semesterData['SEM_ID']
        self.name = semesterData['SEM_NAME']
    
    def to_dict(self):
        return {
            'SEM_ID': self.semester,
            'SEM_NAME': self.name
        }

# School class stores the different schools (school of engineering, school of business, etc.)
class School:
    def __init__(self, schoolData):
        self.code = schoolData['SCHL_CODE']
        self.semester = schoolData['SEM_ID']
        self.name = schoolData['SCHL_NAME']

    def to_dict(self):
        return {
            'SCHL_CODE': self.code,
            'SEM_ID': self.semester,
            'SCHL_NAME': self.name
        }
    
# Department class stores the different course departments (computer science, electrical engineering, etc.)
class Department:
    def __init__(self, departmentData):
        self.id = departmentData['DEP_ID']
        self.schoolCode = departmentData['SCHL_CODE']
        self.semester = departmentData['SEM_ID']
        self.name = departmentData['DEP_NAME']

    def to_dict(self):
        return {
            'DEP_ID': self.id,
            'SCHL_CODE': self.schoolCode,
            'SEM_ID': self.semester,
            'DEP_NAME': self.name
        }

# Course class stores the different courses (CSCI 104, EE 109, etc.) and their details (GE requirements, units)
class Course:
    def __init__(self, courseData):
        self.courseID = courseData['CRS_UID']
        self.semester = courseData['SEM_ID']
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
        self.crosslist = courseData['CRS_CROSS']
        self.notes = courseData['CRS_NOTE']

    def to_dict(self):
        return {
            'CRS_UID': self.courseID,
            'SEM_ID': self.semester,
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
            'CRS_CROSS': self.crosslist,
            'CRS_NOTE': self.notes
        }


# Section class stores the different sections of a course (the lecture sections, the lab, etc. with their IDs)
class Section:
    def __init__(self, sectionData):
        self.id = sectionData['SCT_ID']
        self.courseID = sectionData['CRS_UID']
        self.semester = sectionData['SEM_ID']
        self.type = sectionData['SCT_TYPE']
        self.registered = sectionData['SCT_REG']
        self.seats = sectionData['SCT_SEATS']
        self.building = sectionData['SCT_BUILD']
        self.room = sectionData['SCT_ROOM']
        self.title = sectionData['SCT_TITLE']
        self.units = sectionData['SCT_UNITS']

    def to_dict(self):
        return {
            'SCT_ID': self.id,
            'CRS_UID': self.courseID,
            'SEM_ID': self.semester,
            'SCT_TYPE': self.type,
            'SCT_REG': self.registered,
            'SCT_SEATS': self.seats,
            'SCT_BUILD': self.building,
            'SCT_ROOM': self.room,
            'SCT_TITLE': self.title,
            'SCT_UNITS': self.units
        }

# Schedule class stores all the different schedules of a section (one row for each different day and time)
class Schedule:
    def __init__(self, scheduleData):
        self.sectionID = scheduleData['SCT_ID']
        self.scheduleID = scheduleData['SCH_ID']
        self.day = scheduleData['SCH_DAY']
        self.start = scheduleData['SCH_STARTTIME']
        self.end = scheduleData['SCH_ENDTIME']

    def to_dict(self):
        return {
            'SCT_ID': self.sectionID,
            'SCH_ID': self.scheduleID,
            'SCH_DAY': self.day,
            'SCH_STARTTIME': self.start,
            'SCH_ENDTIME': self.end
        }
# Instructor class stores the different instructors and their IDs
class Instructor:
    def __init__(self, instructorData):
        self.id = instructorData['INSTR_ID']
        self.name = instructorData['INSTR_NAME']

    def to_dict(self):
        return {
            'INSTR_ID': self.id,
            'INSTR_NAME': self.name
        }

# Teaches class stores the different instructors and the sections they teach by ID (multiple different instructors can teach the same section)
class Teaches:
    def __init__(self, teachingData):
        self.instructorID = teachingData['INSTR_ID']
        self.sectionID = teachingData['SCT_ID']
        self.semester = teachingData['SEM_ID']

    def to_dict(self):
        return {
            'INSTR_ID': self.instructorID,
            'SCT_ID': self.sectionID,
            'SEM_ID': self.semester
        }

# Parameters: url
# Returns: BeautifulSoup object
# Description: fetches the html content of the url and returns a BeautifulSoup object
def fetchURL(url):
    r = urlSession.get(url)
    return BeautifulSoup(r.content, 'lxml')

# Parameters: generalEducations, geafDict, geghDict, dCoreSet
# Returns: None
# Description: reads the general education requirements and stores them in the appropriate dictionaries to assign them later
def readGeneralEducation(generalEducations, geafDict, geghDict, dCoreSet, semester):
    print("reading general education")

    # list of urls to batch process them
    geUrls = []
    # the responses from the batch processing
    geResponses = []
    # the categories of the general education requirements, ordered by the order they appear in the html
    geCategories = []

    # loops through the different html sections, and gets their details
    for ge in generalEducations:
        # the code that's used in the url for the general education requirement
        geCode = str(ge.get('data-code'))
        # the title of the requirement (Category A, Category B, etc.)
        geTitle = str(ge.get('data-title'))
        # don't want to go through all the seminars
        if("Seminar" in geTitle):
            continue
        # core is not a ge, but a dornsife thing, so still keep it
        elif("Core " in geTitle):
            geCategory = "L"
        else:
            geTitle = geTitle.replace("Category ", "")
            geCategory = geTitle[0]
        geCategories.append(geCategory)
        geUrls.append('https://classes.usc.edu/term-' + str(semester) + '/classes/' + geCode + '/')
    
    # batch processing the urls
    for i in range(len(geUrls)):
        geResponses.append(urlSession.get(geUrls[i]))

    for i in range(len(geResponses)):
        # goes through each category
        r = geResponses[i]
        geCategory = geCategories[i]
        soup = BeautifulSoup(r.content, 'lxml')
        # soup = soup.find('div', id='content-main')
        # soup.extract()
        s = soup.find('div', class_='course-table')

        # gets all the classes in that page
        classes = s.find_all('div', class_='course-info expandable')

        # goes through each class and stores the class id with its ge in the dictionaries
        for line in classes:
            lineStr = str(line.get('id'))
            lineStr = lineStr.replace("<div class=\"course-info expandable\" id=\"", "")
            lineStr = lineStr.replace("\"></div>", "")
            crs_id = lineStr

            # classes can have one ge from a-f, one ge from g or h, and can be a dornsife core class
            # so record the relevant ge being parsed right now and put the relevant course in the relevant dictionary
            # print(geCategory + " " + crs_id)
            if(geCategory >= 'A' and geCategory <= 'F'):
                geafDict[crs_id] = geCategory
            elif(geCategory >= 'G' and geCategory <= 'H'):
                geghDict[crs_id] = geCategory
            elif(geCategory == 'L'):
                dCoreSet.add(crs_id)

            line.decompose()


# Parameters: departments, schoolList, departmentList
# Returns: None
# Description: reads the schools and departments, creates School and Department objects and appends them to the appropriate lists
def readSchoolsDepartments(departments, schoolList, departmentList):
    # reads the schools and departments
    print("reading schools and departments")

    # store the schl code outside of the loop so it stays static for all subsequent departments
    # until a new school comes along
    schl_code = ''
    for department in departments:
        depType = str(department.get('data-type'))
        # skip if it's gen end, but NOT a seminar (it's a unique category and doesn't overlap any actual departments, so we still have to populate the tablle)
        if("Requirements" in str(department.get('data-school')) and "Seminar" not in str(department.get('data-title'))):
            # already dealt with general education
            continue
        if(depType == 'school'):
            # if it's a school, create the object and update the school code
            schl_code = str(department.get('data-code'))
            if(any(school.code == schl_code for school in schoolList)):
                continue
            schl_name = department.text
            schl_name = schl_name.strip()
            schoolObj = School({
                'SCHL_CODE': schl_code,
                'SCHL_NAME': schl_name
            })
            schoolList.append(schoolObj)
        elif(depType == 'department'):
            # if it's a department, create the object and append it to the list
            dep_id = str(department.get('data-code'))
            if(any(department.id == dep_id for department in departmentList)):
                continue
            dep_name = str(department.get('data-title'))

            depObj = Department({
                'SCHL_CODE': schl_code,
                'DEP_ID': dep_id,
                'DEP_NAME': dep_name
            })
            departmentList.append(depObj)

# Parameters: departmentSoups, departmentList, courseList, sectionSoupDict, geafDict, geghDict, dCoreSet
# Returns: None
# Description: reads the courses and creates Course objects and the section Soup objects and appends them to the appropriate lists
def readCourses(departmentSoups, departmentList, courseList, sectionSoupDict, geafDict, geghDict, dCoreSet, semester):
    print("reading courses")
    # first get the specific department soup from the dictionary
    for department in departmentList:
        if department.id in departmentSoups:
            soup = departmentSoups[department.id]
        else:
            continue
        # soup = soup.find('div', id='content-main')
        # soup.extract()
        s = soup.find('div', class_='course-table')
        classes = s.find_all('div', class_='course-info expandable')

        # filter it for the classes and iterate through them

        for line in classes:
            lineStr = str(line.get('id'))
            lineStr = lineStr.replace("<div class=\"course-info expandable\" id=\"", "")
            lineStr = lineStr.replace("\"></div>", "")

            # get the course number by splitting the course id by the dash
            crs_num = lineStr.split('-')[1]

            # this is to get the course display code (sometimes it's got extra letters from the display number)
            courseID = line.find('div', class_='course-id')
            courseID = courseID.find('a')
            crs_code = courseID.find('strong').text
            crs_code = crs_code.replace(":", "")

            # get the course title
            crs_name = courseID.text
            crs_name = (crs_name.split(':')[1]).split('(')[0].strip()

            # get the descriptio of the course
            courseDetails = line.find('div', class_='course-details')
            crs_desc = courseDetails.find('div', class_='catalogue').text

            # sometimes the course can have different units based on the section
            # so record the unit number if it's got only one possible set of units
            # or just record the variety of units if it's got multiple
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
            
            # get the notes of the course (straight html for now)
            notes = courseDetails.find('ul', class_='notes')
            notesJSON = defaultdict(list)
            crs_note = {}

            if notes is not None:
                for li in notes.find_all('li'):
                    HTMLclass = li.get("class")
                    HTMLclass = HTMLclass[0] if HTMLclass is not None else ""
                    text = li.get_text() # ! use strip?

                    if not HTMLclass:
                        notesJSON["other"].append(text)
                    else:
                        notesJSON[HTMLclass].append(text)

                crs_note = dict(notesJSON)

            # if the course is crosslisted, get the department that offers the course
            crs_cross = courseDetails.find('li', class_='crosslist')
            if (crs_cross is None):
                crs_cross = ""
            else:
                crs_cross = crs_cross.find_all('a')
                crs_cross = crs_cross[2].text
                crs_cross = crs_cross.replace(" ", "-")

            # get the prerequisites and corequisites of the course
            # (include only brackets, ANDs and ORs so that with further logic, the course numbers
            # can just be replaced with "TRUE" if taken and "FALSE" if not, to see if you fulfill the prereqs/coreqs for the course)
            crs_preq = courseDetails.find('li', class_='prereq')
            if crs_preq is None:
                crs_preq = ""
            else:
                crs_preq = crs_preq.text
                crs_preq = crs_preq.replace("1 from ", "")
                crs_preq = crs_preq.replace("Prerequisite: ", "")

            
            crs_coreq = courseDetails.find('li', class_='coreq')
            if crs_coreq is None:
                crs_coreq = ""
            else:
                crs_coreq = crs_coreq.text
                crs_coreq = crs_coreq.replace("1 from ", "")
                
            # get the course id recorded in the dictionary for gen eds
            # and get update the relevant fields if it is a gen ed
            crs_id = department.id + "-" + crs_num
            crs_geaf = ""
            crs_gegh = ""
            crs_dcorel = False
            if crs_id in geafDict:
                crs_geaf = geafDict[crs_id]
                # print(crs_id)
            if crs_id in geghDict:
                crs_gegh = geghDict[crs_id]
                # print(crs_id)
            if crs_id in dCoreSet:
                crs_dcorel = True
                # print(crs_id)

            courseObj = Course({
                'CRS_UID': '0',
                'SEM_ID': semester,
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
                'CRS_CROSS': crs_cross,
                'CRS_NOTE': crs_note
            })

            courseList.append(courseObj)

            # if the course is crosslisted, then don't add it to the soup dictionary, so only the original course is added
            if(crs_cross != ""):
                continue

            # get the sections from the course soup
            sections = courseDetails.find('table', class_='sections responsive')
            sectionHTML = sections.find_all('tr')
            sectionHTML = sectionHTML[1::]

            # add them to a dictionary
            # order them by course id, but also add a counter to make sure they're unique
            # as one course can have multiple sections, but we need all the different sections
            counter = 0
            for section in sectionHTML:
                sectionSoupDict[crs_id + " " + str(counter)] = section
                counter += 1
        
            # extract the course details to remove them from the soup

# Parameters: scheduleSoup, sct_id, scheduleList, scheduledSet
# Returns: None
# Description: uses the section Soup objects to create Schedule objects and appends them to the scheduleList
def createSchedule(scheduleSoup, sct_id, scheduleList, scheduledSet):
    
    # if the section has already been scheduled, don't create a new entry
    # (this specifically happens when courses are crosslisted; the same section is in multiple courses)
    if(sct_id in scheduledSet):
        return
    
    # get the listed time
    schedTime = scheduleSoup.find(class_ = 'time').extract()
    schedTime = schedTime.text

    schd_sttime = ""
    schd_entime = ""

    # get am vs pm, and split the time into start and end times
    meridiem = schedTime[-2::]
    schedTime = schedTime[:-2]
    schedTime = schedTime.split('-')

    # deal with am and pm accordingly (to turn into 24 hour time)
    if("pm" in meridiem):
        for time in reversed(schedTime):
            if(schd_entime == ""):
                time = time.split(':')
                if(time[0] != "12"):
                    time[0] = str(int(time[0]) + 12)
                time = ':'.join(time)
                schd_entime = time
            else:
                time = time.split(':')
                if(time[0] != "12" and int(time[0]) + 12 <= int(schd_entime.split(':')[0])):
                    time[0] = str(int(time[0]) + 12)
                time = ':'.join(time)
                schd_sttime = time
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

    # get the days the section is scheduled
    schedDay = scheduleSoup.find(class_ = 'days').extract()
    schedDay = schedDay.text

    schd_day = []

    # counter for the number of capital letters in the string (for strings like "MWF" or "MWThF",
    # and also lets you know there's only one day for strings like "Friday")
    capCount = 0

    for i in schedDay:
        if(i.isupper()):
            capCount += 1

    # if TBA, then make it blank
    if("TBA" in schedDay):
        schd_day = [""]
    # if there's a comma, then split the days by the comma
    elif("," in schedDay):
        schedDay = schedDay.split(', ')
        for day in schedDay:
            schd_day.append(day[:3].strip().upper())
    # if there's more than one capital letter, then append the days accordingly
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
    # if there's only one capital letter, then just append the first three letters of the day
    else:
        schd_day.append(schedDay[:3].upper())
        
    for day in schd_day:
        scheduleObj = Schedule({
            'SCT_ID': sct_id,
            'SCH_ID': len(scheduleList) + 1,
            'SCH_DAY': day,
            'SCH_STARTTIME': schd_sttime,
            'SCH_ENDTIME': schd_entime
        })
        scheduleList.append(scheduleObj)
    
    # add the id to the set so that it doesn't get scheduled again
    scheduledSet.add(sct_id)
    
# Parameters: sectionSoupDict, sectionList, instructorListDict, scheduleList, scheduledSet, semester
# Returns: None
# Description: reads the sections and creates Section objects and appends them to the list
def readSections(sectionSoupDict, sectionList, instructorListDict, scheduleList, scheduledSet, semester):

    # these variables need to be stored outside of the loop so that they can be brought over in the next iteration
    sectionTitles = False
    sct_num = ""
    sct_title = ""
    sct_id = ""

    # for each key, value pair in the soup dictionary
    for secID, sectionHTML in sectionSoupDict.items():
        # get the type (section title vs title)
        classType = str(sectionHTML.find('td').get('class'))

        if(classType == "[\'section-title\']"):
            # if it's a section title, inform the next loop that there is a title
            sectionTitles = True
            # and assign the correct title and course id
            sct_title = sectionHTML.find('td', class_='section-title').text
            sct_num = sectionHTML.get('class')[-1]
            # and don't go through with the rest of the loop; that info will not be available
            continue
        # if there was a section title
        elif(sectionTitles and classType == "[\'section\']"):
            # but the id doesn't match, set the title to be null (which never happens, but it doesn't matter)
            if(sectionHTML.get('data-section-id') != sct_num):
                sct_title = ""
            sectionTitles = False
        # if there is still a second line, then that means an additional timing is available, so create that schedule
        elif("secondline" in str(sectionHTML.get('class'))):
            createSchedule(sectionHTML, sct_id, scheduleList, scheduledSet)
            continue
        # otherwise, reset the title and the sectionTitles boolean
        else:
            sct_title = ""

        # record the section number (and the id for secondline cases)
        sct_num = sectionHTML.get('class')[0]
        sct_id = sectionHTML.find('td', class_='section').text

        # get the type (lecture, lab, quiz, etc.)
        sct_type = sectionHTML.find('td', class_='type').text
        
        # get the number of seats and the enrollment
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

        # get the location of the section
        sct_loc = sectionHTML.find('td', class_='location')
        # split by building and by room (if there is a room)
        sct_build = ""
        sct_room = ""
        if(sct_loc.find('a') is None):
            sct_build = sct_loc.text
            sct_room = ""
        else:
            sct_build = sct_loc.find('a').text
            sct_room = (sct_loc.text).replace(sct_build, "")

        # get the units of the section (if there are any)
        sct_unit = ""
        if(sectionHTML.find('td', class_='units') is not None):
            sct_unit = sectionHTML.find('td', class_='units').text
            sct_unit = sct_unit.split('.')[0]
            if(sct_unit.isdigit()):
                sct_unit = int(sct_unit)
            else:
                sct_unit = ""
        
        # get the course id
        secID = secID.split(' ')
        dep_id = secID[0].split('-')[0]
        crs_num = secID[0].split('-')[1]

        # create the schedule for the section
        createSchedule(sectionHTML, sct_id, scheduleList, scheduledSet)

        # create the section object and append it to the list
        sectionObj = Section({
            'SCT_ID': sct_id,
            'CRS_UID': '0',
            'SEM_ID': semester,
            'SCT_TYPE': sct_type,
            'SCT_REG': sct_reg,
            'SCT_SEATS': sct_seat,
            'SCT_BUILD': sct_build,
            'SCT_ROOM': str(sct_room),
            'SCT_TITLE': sct_title,
            'SCT_UNITS': sct_unit
        })

        sectionList.append(sectionObj)


        instructors = sectionHTML.find('td', class_='instructor')
        if instructors is not None and instructors.text != "":
            # if there are instructors, split them by comma (so we can extract the html from memory for a lighter load)
            instructorText = instructors.text
            instructorText = instructorText.split(',')
            for instructor in instructorText:
                # and organize them by section id
                instructorListDict[sct_id] = instructor

        instructors.decompose()
        
        sectionHTML.decompose()

# Parameters: instructorListDict, instructorList, teachingList
# Returns: None
# Description: reads the instructors and and creates Instructor objects and Teaches objects and appends them to the list
def readInstructors(instructorListDict, instructorList, teachingList, semester):
    # use the instructor dict to make sure extra duplicate instructors aren't added
    # ! move to outside the function
    instructorDict = {}

    for sct_id, instructor in instructorListDict.items():
        # get the instructor name
        instr_name = instructor.strip()
        instr_id = 0
        if instr_name in instructorDict:
            # if the instructor has an id already, use that id
            instr_id = instructorDict[instr_name]
        else:
            # otherwise create the new instructor in the lookup list and add it to the dictionary
            instr_id = len(instructorList) + 1
            instrObj = Instructor({
                'INSTR_ID': instr_id,
                'INSTR_NAME': instr_name
            })
            instructorList.append(instrObj)
            instructorDict[instr_name] = instr_id
        # add the instructor with the correct section id to the teaches list
        teachObj = Teaches({
            'INSTR_ID': instr_id,
            'SCT_ID': sct_id,
            'SEM_ID': semester
        })
        teachingList.append(teachObj)






def main():
    print("starting!")

    # create the lists to store the data
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

    # can be changed, will use a script or a file to change it
    for i in range(9):
        a = i//3
        b = (i%3) + 1
        semester = 20230 + (a*10) + b
        sem_str = ""
        if(b == 1):
            sem_str = "Spring"
        elif(b == 2):
            sem_str = "Summer"
        elif(b == 3):
            sem_str = "Fall"
        
        sem_str += str(semester/10)
        semObj = Semester({
            'SEM_ID': semester,
            'SEM_NAME': sem_str
        })

        # read in the semester page, and get the departments and general education requirements
        print("starting semester " + str(semester))
        r = urlSession.get('https://classes.usc.edu/term-' + str(semester) + '/')
        soup = BeautifulSoup(r.content, 'lxml')
        departments = soup.find('ul', id='sortable-classes')
        departments.extract()
        generalEducation = departments.find_all('li', {"data-school":"GE Requirements for Students Beginning College in Fall 2015 or Later"})

        # create the dictionaries for holding the general education requirements and read in the ge requirements
        geafDict = {}
        geghDict = {}
        dCoreSet = set()
        readGeneralEducation(generalEducation, geafDict, geghDict, dCoreSet, semester)

        # get the schools and departments
        departments = departments.find_all('li')
        readSchoolsDepartments(departments, schoolList, departmentList)

        # get the urls for the departments (because this is the main intensive part of the program, we will use future and threading to speed it up)
        depUrlList = []
        for department in departmentList:
            depUrlList.append('https://classes.usc.edu/term-' + str(semester) + '/classes/' + department.id + '/')

        # read in every department's courses
        print("future stuff")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(fetchURL, depUrlList)
        print("after future stuff")

        departmentSoups = {}

        # for every result, add it to the dictionary ordered by department id
        for soup in results:
            depID = soup.find('abbr').text
            departmentSoups[depID] = soup

        # keep the section soup dictionary to store the sections after course processing is over
        sectionSoupDict = {}
        # then read in the courses
        readCourses(departmentSoups, departmentList, courseList, sectionSoupDict, geafDict, geghDict, dCoreSet, semester)

        instructorListDict = {} # ! move to the top, assigns ids to instructors if they exist already

        scheduledSet = set()

        # read the sections (along with the schedules inside)
        readSections(sectionSoupDict, sectionList, instructorListDict, scheduleList, scheduledSet, semester)

        # then read the instructors in
        readInstructors(instructorListDict, instructorList, teachingList, semester)

    # and export the data to csv files (named by semester)
    print("before export")
    # pd.DataFrame([school.to_dict() for school in schoolList]).to_csv('schools' + str(semester) + '.csv', index=False)
    # pd.DataFrame([department.to_dict() for department in departmentList]).to_csv('departments' + str(semester) + '.csv', index=False)
    # pd.DataFrame([course.to_dict() for course in courseList]).to_csv('courses' + str(semester) + '.csv', index=False)
    # pd.DataFrame([section.to_dict() for section in sectionList]).to_csv('sections' + str(semester) + '.csv', index=False)
    # pd.DataFrame([instructor.to_dict() for instructor in instructorList]).to_csv('instructors' + str(semester) + '.csv', index=False)
    # pd.DataFrame([teaching.to_dict() for teaching in teachingList]).to_csv('teaches' + str(semester) + '.csv', index=False)
    # pd.DataFrame([schedule.to_dict() for schedule in scheduleList]).to_csv('schedules' + str(semester) + '.csv', index=False)
    pd.DataFrame([school.to_dict() for school in schoolList]).to_csv('schools.csv', index=False)
    pd.DataFrame([department.to_dict() for department in departmentList]).to_csv('departments.csv', index=False)
    pd.DataFrame([course.to_dict() for course in courseList]).to_csv('courses.csv', index=False)
    pd.DataFrame([section.to_dict() for section in sectionList]).to_csv('sections.csv', index=False)
    pd.DataFrame([instructor.to_dict() for instructor in instructorList]).to_csv('instructors.csv', index=False)
    pd.DataFrame([teaching.to_dict() for teaching in teachingList]).to_csv('teaches.csv', index=False)
    pd.DataFrame([schedule.to_dict() for schedule in scheduleList]).to_csv('schedules.csv', index=False)
    pd.DataFrame([sem.to_dict() for sem in semObj]).to_csv('semesters.csv', index=False)
    print("after export")

if __name__ == '__main__':
    main()