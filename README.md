# USC Schedule Planner

A web app I'm creating to help USC students with planning their schedules.

Features planned:

* Course list (updated weekly, straight from classes.usc.edu)
* Requirement list (inputed manually by the student, specifies specific single or multiple courses along with GE requirements)
* Account/Export file (saves all of the info)
* GPA Calculator (only using grades that the student will input every time, to allow for no sensitive data being stored) (is that necessary? or workaround to save the gpa)
* Day scheduler (classes are inputted automatically, but additional events can also be planned)
* iCal exporter (using the USC Academic Calendar found online to populate the specific dates)
* Map of campus (will show the classes for the day on a map, and MIGHT show the most efficient route across campus to each class)

Full description of each feature:

## Course List (0.1.5)

* The course list will be updated weekly, scraped using a python script from classes.usc.edu, and put through a SQL database (first SQLite, then MySQL or PostgreSQL) to parse
* In case the course list is not available for that semester yet, the app will give an option to use the course list of previous semesters as a stopgap (and will then ask(? or overwrite directly) to change when the new schedule is out)
* It will have all of the details of the course (save for the syllabus and extra info not directly available in WebReg)
* To facilitate scheduling (and to solve the issue that students have when they're alerted of D-Clearance upon checkout), D-Clearance will be signaled with a different colour on the schedule, and a small alert that can be temporarily or permanently dismissed
* Based on the amount of units the student has inputted as their maximum, the scheduler will have a small alert in case the student adds more units than they have
* The course list inputted for previous years will remain on the account, to make it easier for requirements

## Requirement List (0.2.0)

* The requirement list will include requirements for the student's major(s), minor(s), and general USC requirements (WRIT, GESM, GEs)
* If a requirement exists but was fulfilled by a high school or other credit, there will be an option to select "already previously fulfilled" and it will be remembered in their account
* When a course is added that fulfills a requirement, it will show in both the course list and the requirement list (which INCLUDES GEs, so no more guessing if a class you did earlier or a class you chose fullfills the wrong requirement or not)
* Students will NOT be able to just import their STARS report, as that contains sensitive info

## Account/Export file (0.3.0)

* Simple login and password to store the info, or a json file that has all of their info (or both!)
* If the login and password is implemented, then students **MUST NOT** use a username or password that is used in other accounts, as the login for these accounts will NOT be very well secured
  
## GPA Calculator (0.4.0)

* A gpa calculator will be available on the app, which lets you input a specific grade or gpa into each course and calculate the gpa for the semester
* Will either be simple, or will also allow you to calculate gpa over the course of the semester by taking the information from the syllabus and using inputted grades (and selected default values for things like homeworks, i.e. defauly hw value is 80% and that value is populated until a new homework is updated)
* Shouldn't ba saved on the account (due to sensitive data), **MIGHT** be able to be exported? so a gpa json file can be imported every time
* Will also allow you to calculate a "required gpa" for future semesters depending on a specific goal in mind
  
## Day Scheduler (0.7.0)

* Very rudementary, almost the exact same as WebReg, except will support multiple colours and will have additional notifications/alerts
* Different colours for courses fulfilling requirements vs not fulfilling requirements, maybe different for GEs, etc.
* Basic details are available at a glance, but mouseovers or a selected option will give more details (like section number)
* Will notify if over the unit limit, or if class is D-clearance (and will allow to dismiss alert accordingly)
* Will store locations and send them to the campus map portion to plan
* Will also allow for personal event scheduling (to make class scheduling easy), and if the building or location of event is recurring and on campus (like the Trojan Marching Band or the Rocket Propulsion Lab), then locations can either be typed in or **might** be able to be selected/dragged on the campus map
* **might** also support changing lecture times to exam times + adding different exam times?

## iCal Exporter (0.7.5)

* Will be able to export the calendar created through the day Scheduler
* **might?** also support subscribing to a google calendar
* Will scrape from the USC Academic Calendar to look for specified start and end dates, along with holidays to populate the calendar

## Campus Map (0.9.0)

* Will have the locations for each of your classes on the map (along with the room next to the specific dot)
* As said before, might be able to support dragging personal events on the map to allow for better route planning
* Can add options for going through buildings or not (*will then need extensive campus research to see when and how buildings can be gone through*)
* **might** add path planning using algorithms like Dijkstra's or A* Search

## Chat Feature (?)

## Add ratemyprof

Then at the end of all of this means 1.0 release!
