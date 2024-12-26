# USC Schedule Planner
A web app I'm creating to help USC students with planning their schedules.

Features planned:
* Course list (updated weekly, straight from classes.usc.edu)
* Requirement list (inputed manually by the student, specifies specific single or multiple courses along with GE requirements)
* Day scheduler (classes are inputted automatically, but additional events can also be planned)
* Map of campus (will show the classes for the day on a map, and MIGHT show the most efficient route across campus to each class)
* iCal exporter (using the USC Academic Calendar found online to populate the specific dates)

Full description of each feature:




Some specifics:
* Students can create their own login, but MUST NOT use a username or password that is used in other accounts, as the login for these accounts are NOT secured
  * Alternatively, students can export their data into a json or other file, and import it into the app everytime
* Students will NOT be able to upload their STARS report into the app to get their requirement list
  * (As much as I'd like to implement this, the credits and other sensitive info of the student may and can be leaked)
