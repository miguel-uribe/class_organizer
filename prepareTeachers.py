## This module reads the Availability Report and creates the teachers associated to it


import pandas as pd
import numpy as np
import xlrd
import collections
import copy
import multiprocessing

# This script will read the ReporteDisponibilidad file and create a list of teachers and their disponibility, it will differenciate the teachers between planta and catedra
## Input: Availability report
## Output: List of teachers with their availability
def createTeachersAndDisponibility(teachers, file):
    # We scan the file using pandas
    data=pd.read_excel(file)
    
    # We scan over each professor
    for i in range(len(data)):
        CC=data.iloc[i,2]
        ID=data.iloc[i,0].astype(int)
        name=data.iloc[i,3]
        if data.iloc[i,10]=='DOCENTE PLANTA':
            kind='PLANTA'
        elif data.iloc[i,10]=='DOCENTE CATEDRA':
            kind='CATEDRA'
        disp=np.column_stack(tuple(np.split(data.iloc[i,16:94].astype(int).values,6)))
        # raise in alarm if the department meeting is not set
        if kind=='PLANTA' and disp[4,1]==1:
            print("Warning, teacher %s is not available for the Department Meeting"%name)
        # raise in alarm if the Faculty meeting is not set
        if kind=='PLANTA' and disp[4,4]==1:
            print("Warning, teacher %s is not available for the Faculty Meeting"%name)
      
        schedule=np.empty((13,6),dtype=object)
        assigned=[]
        expectedhours=0
        capability={}
        fitness=0
        teachers[CC]=[ID,name,kind,disp,schedule,assigned,expectedhours,capability,fitness]
    
    # We also add the orphan teacher with ID 0
    teachers[0]=[0,'orphan','orphan',0,0,[],0,{},0]


# This script reads the DisponibilidadProfesoresCatedraFile and updates the teachers list
## Input: Disponibility request 
## Output: List of catedra teachers with their capabilities
def updateCapabilityCatedra(teachers, file):
    # We scan the file using pandas
    data=pd.read_excel(file)
    
    # We scan over all professors
    for i in range(len(data)):
        CC=data.iloc[i,0]  # We read the CC
        teachers[CC][6]=data.iloc[i,2] # We assign the ExpectedHoursParameter
        # we obtain the list of Capabilities
        capability=np.array(list(data))[3:][data.iloc[i,3:]=='X']
        #print(CC)
        #print(capability)
        # We check for empty capability
        if len(capability)==0:
            print("Warning, profesor %s has no capability"%teachers[CC][1])
        # We update the capability dictionary with a default value of one
        for course in capability:
            teachers[CC][7][course]=1
            
            
# this script reads the AsignacionProfesoresPlanta and updates both the capabilities and the assignment
# input: Planeacion File
# output: Planta teachers with expected hours and capability updated
def updateAssignmentPlanta(teachers, file):
    # We scan the file using pandas
    data=pd.read_excel(file) 
    # We scan each of the professors
    for i in np.where(~np.isnan(data.iloc[:,0].values))[0]:
        CC=data.iloc[i,0]   # We read the CC
#        print(CC)
        if teachers[CC][2]=='PLANTA':   # Only if we are talking about a planta teacher
            teachers[CC][6]=data.iloc[i,2]
            # creating a filter
            index=np.arange(4,16)   # Reading all the course columns
            mask=np.where(~np.isnan(data.iloc[i,index].values.astype(float)))[0]  # getting the indices for which there are classes
            courses=data.iloc[0,index[mask]].values.astype(int).astype(str) # Getting the class list
            nclasses=data.iloc[i,index[mask]].values.astype(int) # getting the number of each class
            # Updating the capability
            for j in range(len(courses)):  # We scan over the assigned classesquit
                teachers[CC][7][courses[j]]=nclasses[j] # We update the capability
#                print(courses[j])


# This script updates the orphan teacher with the information of ALL courses
def updateOrphan(teachers,Courses):
    # we call the orphan teacher
    orphan=teachers[0]
    # The external courses are fixed
    external=[]
    # We set all the expectations initially to zero
    for coursekey,courses in Courses.items():
        if coursekey not in external:
            orphan[7][coursekey]=0
    # Here we set all the cancelations
    # orphan[7]['21101']=13
#    orphan[7]['21107']=4
#    orphan[7]['21201']=1
#    orphan[7]['21203']=1
#    orphan[7]['21301']=1
#    orphan[7]['21303']=2
#    orphan[7]['21401']=3
#    orphan[7]['21402']=1