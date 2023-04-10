# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 20:39:31 2019

@author: Miguel
"""

# looking for teachers who can take classes in orphan
for classkey in teachers[0][5]:
    print(classkey)
    for CC,teacher in teachers.items():
        if op.professorAcceptsClass(teacher,classkey,Classes):
            print(teacher[1])
            
# finding competition between classes
for classkey in teachers[0][5]:
    print(classkey)
    print("Competitors")
    for classkey2,clase in Classes.items() :
        if np.max(clase[-1]+Classes[classkey][-1])>1:
            print(classkey2)          
            
# finding time availability of professors between classes
for classkey,clase in Classes.items():
    print(classkey)
    print("Possible Teachers")
    for CC,teacher in teachers.items():
        ndisp=np.sum(teacher[3]*clase[-1])
        #print(teacher[3]*Classes[classkey][-1]-Classes[classkey][-1])
        if ndisp==np.sum(clase[-1]):
            print([ndisp,CC,teacher[1]])
    
# Finding the available classes per disponibility for professor
for CC,teacher in teachers.items():
    print(teacher[1])
    for classkey,clase in Classes.items():
        noff=np.sum(teacher[3]*clase[-1]-clase[-1])
        if noff >=-1:
            print(classkey)
            print(np.sum(teacher[3]*clase[-1]-clase[-1]))


# Finding the available classes per disponibility for professor
classes=['21202-7']
for CC,teacher in teachers.items():
    print(teacher[1])
    for classkey in classes:
        noff=np.sum(teacher[3]*Classes[classkey][-1]-Classes[classkey][-1])
        if noff >=-1:
            print(classkey)
            print(np.sum(teacher[3]*Classes[classkey][-1]-Classes[classkey][-1]))
            print(teacher[3]*Classes[classkey][-1]-Classes[classkey][-1])

# Finding the total sum of physics courses
physics=['21202', '21302', '801401']
times=np.zeros((13,6))
for course in physics:
    for classkey in Courses[course][1]:
        times=times+Classes[classkey][-1]
        
# finding the teacher availability
tphys=[80213725,80177123,80029662,19389336,33365661,80817852,40046403,80072390]
tdisp=np.zeros((13,6))
for CC in tphys:
    tdisp=tdisp+teachers[CC][3]
    

# finding classes for each teacher
tphys=[80213725,80177123,80029662,19389336,33365661,80817852,40046403]
for CC in tphys:
    print(teachers[CC][1])
    for classkey,clase in Classes.items():
        if op.professorAcceptsClass(teachers[CC],classkey,Classes):
            print(classkey)

# Getting the sum of all disponibilities
disp=np.zeros((13,6))
for teacher in teachers.values():
    disp+=teacher[3]
