# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 16:10:27 2019

@author: miguelurla
"""
import pandas as pd
import numpy as np
import prepareTeachers as pT





### This routine reads the Proceso file, creates the Courses list, creates the classes list, and also assigns the classes to the teachers in case they are already assigned
## input: proceso file
## output: Courses, Classes, and updated teachers assignments
def readDarwined(teachers,file):
    # we initially load the datafile
    data=pd.read_excel(file)
    
    # we create the Courses and the Classes dictionary
    Courses={}
    Classes={}
    
    # We scan all the rows
    for row in np.arange(data.shape[0]):
        # we retrieve the information
        coursename=data.iloc[row,3]  # The name of the course
        coursekey=str(data.iloc[row,2])   # The catalog number
        #component=data.iloc[row,10]   # Component # does not matter here
        section=data.iloc[row,26].astype(int) # The section
        classkey=coursekey+'-%d'%section  # building the classkey
        classnumber=data.iloc[row,9]      # The class number
        teacherID=data.iloc[row,19]   # The teacher ID in int format
        [teachername,CC]=findTeacherfromID(teachers,teacherID)
        #nhours=data.iloc[row,38]      # The section's hours # not needed here
        hourini=data.iloc[row,11]     # The initial hour
        day=data.iloc[row,6]           # The day of the week
        
        # We update the Courses dictionary:
        updateCourses(Courses,coursekey,classkey,coursename)

        # we update the class dictionary:
        colday=getjfromday(day)
        rowhour=getifromtime(hourini)
        updateClasses(Classes,classkey,classnumber,CC,colday,rowhour,1)
              
    # When all classes are scanned we proceed to update the teacher information
    for classkey, clas in Classes.items():
        updateTeacher(clas[0],teachers,Classes,classkey)
    # We also proceed to update the orphan information
    pT.updateOrphan(teachers,Courses)
    return [Courses,Classes]



# This routine updates the Courses dictionary with new classes, if the course does not exists, it creates the new entry

# This routine updates the courses list
def updateCourses(courses,coursekey,classkey,coursename):
    # We check whether the course is already created:
    try:
        if classkey not in courses[coursekey][1]:
            courses[coursekey][1].append(classkey)
    # If the course is not created
    except:
        courses[coursekey]=[coursename,[classkey]]


# this routine updates the classes list
def updateClasses(classes,classkey,classnumber,CC,col,row,nhours):
    # we check whether the class is already created
    try:
        # we change the class schedule
        classes[classkey][-1][row:row+nhours,col]=1
    # if the class is not created, we crete a new entry
    except:
        # We create the times array
        times=np.zeros((13,6),dtype=int)
        times[row:row+nhours,col]=1         # row 0-12 col 0-5
        classes[classkey]=[CC,classnumber,times]
        
# This routine updates the teacher timetable and classlist
def updateTeacher(CC,teachers,classes,classkey):
    if CC!=0:  # The teacher is not the orphan teacher
        # we get the times where there is class
        times=np.where(classes[classkey][2]==1)
        # We update the teachers schedule
        teachers[CC][4][times]=classkey  
        # To add the class to the class list we check whether its there
        teachers[CC][5].append(classkey)
    else:
        teachers[CC][5].append(classkey)

# It gets the row in the timetable
def getifromtime(strtime):
    times=strtime.split(sep=':')
    # if its is pm
    if times[2]=='PM':
        hour=int(times[0])+12
        if hour==24:
            hour=12
    elif times[2]=='AM':
        hour=int(times[0])
    return hour-7

# It gets the column in the timetable according to the day
def getjfromday(strday):
    if strday==' Lunes':
        return 0
    elif strday==' Martes':
        return 1
    elif strday==' Miercoles':
        return 2
    elif strday==' Jueves':
        return 3
    elif strday==' Viernes':
        return 4
    elif strday==' Sabado':
        return 5

# This routine finds the teachername from the ID
def findTeacherfromID(teachers,ID):
    output=[0,0]
    # We sacn over all teachers
    for CC,teacher in teachers.items():
        if teacher[0]==ID:
            output=[teacher[1],CC]
            break
#    print(output)
    return output
