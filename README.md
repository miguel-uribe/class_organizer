# class_organizer
This program has been created to properly assign the pool of classes to the pool of lecturers hired by the Faculty each semester.

Each class is caracterized by the following attributes:
- Class number
- Subject
- Schedule
- Assigned lecturer (could be void)

Each lecturer is characterized by the followind attributes:
- ID
- Kind (lecturer or faculty)
- Depending on the kind: if lecturer a list of possible subjects; if faculty the number of classes to assign for each possible subject.
- If lecturer: a target in the total hours per week
- Availability schedule

The model also has some global parameters:
- The optimal number of classes per day
- The established penalties for not meeting with the optimal values.
