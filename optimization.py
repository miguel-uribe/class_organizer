import numpy as np
import copy
import collections
import prepareCourses as pC
import prepareTeachers as pT
import multiprocessing as mp
import pandas as pd

# This function calculates the professor fitness
def getProfessorFitness(teacher,classes,Courses,mode):
    fitness=0 # The initial fitness
    ########################################
    # The common penalties
    pout=500  # penalty per hours outside disponibility
    poff=2  # penalty per hour below nopt per teaching day
    pdistdown=100 # penalty per 10% below assignment
    pdistup=200 # penalty per 10% above assignment
    plong=500 # penalty for staying too long per day at the university
    plunch=1000 # The penalty for having class from 11am to 3pm per day
    
    #################################################
    # Catedra penalties
    pcourses=100 # penalty for having more than two different courses
    
    #################################################
    # Planta penalties
    pplanta=1500 # Penalty if a planta teacher has an additional or missing class from the original schedule    
    pdist=500 # penalty per hour above of below assignment
    #################################################
    # Orphan penalties
    porphan=1500 # The penalty per orphan course
    
    ###################################################
    if teacher[0]!=0: # Normal teacher
        ##################################################
        ####    CATEDRA TEACHERS
        if teacher[2]=='CATEDRA':
            #################################################################
            # There is a penalty for having classes outside the disponibility
            nout=0  # The number of hours outside
            # We scan all classes
            for classkey in teacher[5]:
                nout+=np.sum(classes[classkey][-1]-teacher[3]*classes[classkey][-1])
            fitness+=nout*pout    
            #################################################################
            # There is a penalty for having too many hours in one day
            nopt=4 # we set the optimal day as 4
            noffset=0 # the deviation from nopt
            # Getting the number of classes per day
            classesperday=collections.Counter(np.where(teacher[4]!=None)[1])
            # checking every day
            for day, nclasses in classesperday.items():
                #print(nclasses)
                # we also take into account the initial and final times
                hours=np.where(teacher[4][:,day]!=None)[0]
                span=max(hours)-min(hours)+1  # The span of the teaching time
                pspan=1 # originally there is no penalty for the span
                #print(span)
                if nclasses>4 and span/nclasses<=1.35:  # if the classes are too packed
                    # We add an extra factor
                    pspan=5
                if span/nclasses>=2.2: # if classes are too stretched
                    # we add an extra factor
                    pspan=5
                if nclasses>nopt: # if it is more, we apply an squared rule
                    noffset+=pspan*np.abs(nclasses-nopt)**2
                else:
                    noffset+=pspan*np.abs(nclasses-nopt)
                ###############################
                ### Penalty for staying too long at the University
                if span>=10: # if 10 or more hours
                    fitness+=plong
                ###############################
                ## Penalty for not having lunch
                if len(np.where(teacher[4][4:8,day]!=None)[0])==4:
                    fitness+=plunch
            fitness+=noffset*poff
            
            ############################################################
            # there is also a penalty if the proffesor is off its optimal number of hours
            ntotal=len(np.where(teacher[4]!=None)[0]) # the total number of hours
            # we find the offset
            nassign=(ntotal-teacher[6])
    #        print(nassign)
            if nassign>=0: # It is very bad if the number is positive
                fitness+=nassign*pdistup
            else:  # if the number of assigned ours is below the optimal
                fitness+=np.abs(nassign*pdistdown)
                if ntotal==0:  # if no hours are asigned
                    fitness+=teacher[6]*pdistup
            #############################################################
            # Finally there is a penalty if the number of courses is larger than two
            noptclass=2
            teachercourses=[]
            for classkey in teacher[5]:
                course=classkey.split(sep='-')[0]
                if course not in teachercourses:
                    teachercourses.append(course)
            ncourses=len(teachercourses)
            npen=max(0,ncourses-noptclass)
            fitness+=npen*pcourses
            
            return [fitness,nout,noffset,nassign,npen]
        ##################################################
        ####    PLANTA TEACHERS        
        else:    
            #################################################################
            # There is a penalty for having classes outside the disponibility
            nout=0  # The number of hours outside
            # We scan all classes
            for classkey in teacher[5]:
                nout+=np.sum(classes[classkey][-1]-teacher[3]*classes[classkey][-1])
            fitness+=nout*pout    
            #################################################################
            # There is a penalty for having too many hours in one day
            nopt=3 # we set the optimal day as 4
            noffset=0 # the deviation from nopt
            # Getting the number of classes per day
            classesperday=collections.Counter(np.where(teacher[4]!=None)[1])
            # checking every day
            for day, nclasses in classesperday.items():
                #print(nclasses)
                # we also take into account the initial and final times
                hours=np.where(teacher[4][:,day]!=None)[0]
                span=max(hours)-min(hours)  # The span of the teaching time
                pspan=1 # originally there is no penalty for the span
                #print(span)
                if nclasses>4 and span/nclasses<=1.35:  # if the classes are too packed
                    # We add an extra factor
                    pspan=5
                if nclasses>nopt: # if it is more, we apply an squared rule
                    noffset+=pspan*np.abs(nclasses-nopt)**2
                else:
                    noffset+=pspan*np.abs(nclasses-nopt)
                ###############################
                ### Penalty for staying too long at the University
                if span>=10: # if 10 or more hours
                    fitness+=plong
                ###############################
                ## Penalty for not having lunch
                if len(np.where(teacher[4][4:8,day]!=None)[0])==4:
                    fitness+=plunch
            fitness+=noffset*poff
            #######################################
            ############### Mode 0 - We check the courses
            #############################################
            if mode==0:
                #####   penalty for not compkying with the assigned courses
                # We first scan the assigned classes to the teacher
                assigned={}
                for classkey in teacher[5]:
                    course=classkey.split(sep='-')[0]
                    try:
                        assigned[course]=assigned[course]+1
                    except:
                        assigned[course]=1
                # we now compare the dictinary entries
                diff=0
                for course,N in teacher[7].items():
                    try:
                        diff+=np.abs(assigned[course]-N)
                    except:
                        diff+=N
                fitness+=diff*pplanta
                return [fitness,nout,noffset,0,0]
            #######################################
            ############### Mode 1 - We check the hours
            #############################################
            if mode==1:
                ############################################################
                # Penalty if the proffesor is off its optimal number of hours
                ntotal=len(np.where(teacher[4]!=None)[0]) # the total number of hours
                # we set the penalty
                nassign=np.abs(ntotal-teacher[6])
                fitness+=pdist*nassign
                return [fitness,nout,noffset,nassign,0]
    #############################################################
    else: # The teacher is the list of orphan classes
        norphan=0
        #############################################
        #####   penalty for not compkying with the assigned courses
        # We first scan the assigned classes to the teacher
        assigned={}
        for classkey in teacher[5]:
            course=classkey.split(sep='-')[0]
            try:
                assigned[course]=assigned[course]+1
            except:
                assigned[course]=1
        # we now compare the dictinary entries
        for course,N in teacher[7].items():
            try:
                norphan+=np.abs(assigned[course]-N)
            except:
                norphan+=N
        fitness+=norphan*porphan
        #print("Calculating fitness to orphan")
        #print(norphan)
        return [fitness,norphan]
        pass
    

# Getting all the fitnesses list
def getFitnesses(teachers):
    # we define the fitness list
    fitnesses=[teacher[-1] for CC,teacher in teachers.items()]
    return fitnesses

# Choosing two teachers to mate based on their fitness
def findTwoProfessor(fitnesses,teachers):
    # We get two teachers indexes using the fitness as probability
    couple=np.random.choice(list(teachers.keys()),2,fitnesses)
    return [couple[0],couple[1]]


# Check whether a professor can accept agiven class
def professorAcceptsClass(teacher,classkey,classes):
    # if the teacher is orphan, it accepts all standard courses
    if teacher[0]==0:
        # first we check the Course is accepted by the teacher
        course=classkey.split(sep='-')[0]
        if course in teacher[7].keys():
            return True
        else:
            return False
    # if it is not orphan
    else:
        # first we check the Course is accepted by the teacher
        course=classkey.split(sep='-')[0]
        if course in teacher[7].keys():
            # We then check whether the class interferes with the already given classes
            for existingclasskey in teacher[5]:
                if np.max(classes[existingclasskey][-1]+classes[classkey][-1])>1:
                    return False
            # We further check the disponibility of the teacher
            if np.sum(teacher[3]*classes[classkey][-1])!=np.sum(classes[classkey][-1]):
                return False
            return True
        else:
            return False


## Removing a class to professor, should never be used alone
def removeClassToProfessor(teacher,classkey,classes):
    # if the teacher is orphan
    if teacher[0]==0:
        teacher[5].remove(classkey)
    else: # The teacher is a regular teacher
         # We update the teacher timetable
        index=np.where(classes[classkey][2]==1)
        teacher[4][index]=None
        # we update the classlist
        teacher[5].remove(classkey)


##Adding a class to a professor, shuld never be used alone
def addClassToProfessor(teacher,classkey,classes):
    #if the teacher is orphan
    if teacher[0]==0:
        if classkey not in teacher[1]:
            teacher[5].append(classkey) # adding to the orphan classlist
        else:
            print("warning!! class %s already assigned to professor %s"%(classkey,teacher[1]))
            return
    # if teacher is not orphan
    else:
        if classkey not in teacher[5]:
            # We update the teacher timetable
            index=np.where(classes[classkey][2]==1)
            teacher[4][index]=str(classkey)
            # we update the classlist
            teacher[5].append(classkey)
        else:
            print("warning!! class %s already assigned to professor %s"%(classkey,teacher[1]))
            return
        
        
## This transfers a class from one professor to the other
def classTransfer(teacherG,teacherR,classkey,classes):
    # We first remove the class
    removeClassToProfessor(teacherG,classkey,classes)
    # We add it to the other professor
    addClassToProfessor(teacherR,classkey,classes)
    
    
# This function attempts one effective swipe attempt
def swipeAttempt(fitnesses,teachers,classes,courses,l,mode):
    swipeFailed=True
    # we try until a possible swipe is found
    while swipeFailed:
        # we first get two professors
        [CCg,CCr]=findTwoProfessor(fitnesses,teachers)
        # we randomly chose on of the classes in CCg
        try:
            classkey=np.random.choice(teachers[CCg][5])
            # we check whether the new professor accepts the class
            if professorAcceptsClass(teachers[CCr],classkey,classes):
                # We execute the swipe
                swipeFailed=False
                fitnesses=swipeExecute(fitnesses,CCg,CCr,teachers,classkey,classes,courses,l,mode)
                return fitnesses
            return fitnesses
        except:
            return fitnesses
        
        
#This function simulates a transfer and calculates the new fitness
def swipeExecute(fitnesses,CCg,CCr,teachers,classkey,classes,courses,l,mode):
    # we calculate the initial fitness
    fitness0=teachers[CCr][-1]+teachers[CCg][-1]
#   print(fitness0)
    
    #print(teachers[CCr])
    # we create the surrogate teachers
    surrR=copy.deepcopy(teachers[CCr])
    surrG=copy.deepcopy(teachers[CCg])
    

    # we transfer the class
    classTransfer(surrG,surrR,classkey,classes)
    
    #print(surrR)
    #print(teachers[CCr])
    # we calculate the new fitness of the two teachers
    fitness1=getProfessorFitness(surrG,classes,courses,mode)[0]+getProfessorFitness(surrR,classes,courses,mode)[0]
#    print(fitness1)
    # The change in fitness 
    deltafitness=fitness1-fitness0
#    print(deltafitness)
    # Montecarlo random parameter
    r=np.random.random()
    kbT=np.mean(fitnesses)
    
    # if the swipe is thermally possible
    if r<np.exp(-deltafitness/kbT*l):
    #if deltafitness<0:
        # The class is really transferred
        classTransfer(teachers[CCg],teachers[CCr],classkey,classes)
        # The fitnesses are updated
        teachers[CCg][-1]=getProfessorFitness(teachers[CCg],classes,courses,mode)[0]
        teachers[CCr][-1]=getProfessorFitness(teachers[CCr],classes,courses,mode)[0]
        fitnesses=getFitnesses(teachers)
        # The class information is also updated
        classes[classkey][0]=CCr

    return fitnesses
        
        
# The minimization procedure
def minimizeFitness(seed,l, Nsteps, mode):
    np.random.seed(seed)
    [teachers, Classes, Courses]=initialize(mode)
    # We get the initial fitnesses
    fitnesses=getFitnesses(teachers)
    bestfitness=np.sum(fitnesses)
    jmin=0
    #print(fitnesses)

    for j in range(Nsteps):
        fitnesses=swipeAttempt(fitnesses,teachers,Classes,Courses,l,mode)
        # if we get a global minimum
        if np.sum(fitnesses)<bestfitness:
            bestfitness=np.sum(fitnesses)
            bestteachers=copy.deepcopy(teachers)
            bestclasses=copy.deepcopy(Classes)
            bestfitnesses=copy.deepcopy(fitnesses)
            jmin=j
    print("Best is %d in %d with seed %d"%(bestfitness,jmin,seed))
    try:           
        return [bestfitnesses,bestteachers,bestclasses,Courses,seed]
    except:
        return [fitnesses,teachers,Classes,Courses,seed]

# The minimization procedure in parallel
def minimizeFitnessPar(seed,l,Nsteps,mode,queue):
    np.random.seed(seed)
    [teachers, Classes, Courses]=initialize(mode)
    # We get the initial fitnesses
    fitnesses=getFitnesses(teachers)
    bestfitness=np.sum(fitnesses)
    jmin=0
    #print(fitnesses)
    for j in range(Nsteps):
        fitnesses=swipeAttempt(fitnesses,teachers,Classes,Courses,l,mode)
        # if we get a global minimum
        if np.sum(fitnesses)<bestfitness:
            bestfitness=np.sum(fitnesses)
            bestteachers=copy.deepcopy(teachers)
            bestclasses=copy.deepcopy(Classes)
            bestfitnesses=copy.deepcopy(fitnesses)
            jmin=j
    print("Best is %d in %d with seed %d"%(bestfitness,jmin,seed))
    try:          
        queue.put([bestfitnesses,bestteachers,bestclasses,Courses,seed])
    except:
        queue.put([fitnesses,teachers,Classes,Courses,seed])

# the optimization script
def optparallel(Nprocesses,l, Nsteps,mode):
    # getting the number of Cores available
    Ncpu=mp.cpu_count()
    results=[]
    i=0
    while i<Nprocesses:
        # The real number of processes
        nproc=min([Ncpu,Nprocesses-i])
        print(nproc)
        #creating a queue
        q=mp.Queue()
    
        # The list of processes
        processes=[mp.Process(target=minimizeFitnessPar, args=(i+j, l, Nsteps, mode, q)) for j in range(nproc)]
         
        # Running the processes
        for p in processes:
            p.start()
                
        # get the results
        resultsN=[q.get() for p in processes]

        # Exit the completed process
        for p in processes:
            p.join()
        
        # adding to the main results list
        results=results+resultsN
        
        # we perform the processes in Ncpu steps
        i+=Ncpu
        
    #printing
    return results

        
    
# This script reads the best results in case a Results file is given
def readResults(teachers,classes,Courses,file):
    # We first empty all classes to teachers
    for CC, teacher in teachers.items():
        # we scan over all classes
        classkeys=list(teacher[5])
        for classkey in classkeys:
            # The class is transferred to the orphan
            classTransfer(teacher,teachers[0],classkey,classes)
             # The class information is also updated
            classes[classkey][0]=0
    
    # We now read the file
    data=pd.read_excel(file)
    
    # We scan line by line
    for row in range(len(data)):
        try:
            # The CC
            CC=data.iloc[row,0]
            # the classes list
            classstr=data.iloc[row,10:14]
            # We transfer each class from orphan to professor
            for cstr in classstr:
                try:
                    classkey=cstr.split()[0] # We retrieve the classkey
                    classTransfer(teachers[0],teachers[CC],classkey,classes)
                    classes[classkey][0]=CC
                except:
                    pass
        except:
            pass


# This script initiallizes the system
def initialize(mode):
    # We create the dictionaries
    teachers={} 
    
    # We read the required files
    fileDisp="files/ReporteDisponibilidad_2020_2_PHYS.xlsx"
    fileAvCat="files/DisponibilidadProfesoresCatedra_2020_2_PHYS.xlsx"
    fileAsPl="files/AsignacionProfesoresPlanta_2020_2_PHYS.xlsx"
#    fileProc="files/Proceso_57.xlsx"
    fileDarw="files/ReporteSIGA_PHYS.xlsx"
    fileResults="results/BEST.xlsx"
    pT.createTeachersAndDisponibility(teachers,fileDisp)
    pT.updateCapabilityCatedra(teachers,fileAvCat)
    pT.updateAssignmentPlanta(teachers,fileAsPl)
    [Courses,Classes]=pC.readDarwined(teachers,fileDarw)
    
    ##########################################
    ######### If there are some good result
    readResults(teachers,Classes,Courses,fileResults)
    #############################################################
    
    
    
    
    # we calculate all professor's fitnesses
    for CC, teacher in teachers.items():
        teacher[-1]=getProfessorFitness(teacher,Classes,Courses,mode)[0]
    
    return [teachers, Classes, Courses]
    


# Report Results
def exportResults(teachers,classes,Courses,seed,l,mode):
    # We get the fitnesses
    fitnesses=getFitnesses(teachers)
    filename="results/optResults_%d_seed_%d_l_%d.csv"%(np.sum(fitnesses),seed,l)
    teacherfile=open(filename, 'w')
    teacherfile.write("CC,Nombre,fitness,nout,noffset,nassign,npen,Clases\n")
    # scanning the teachers
    for CC,teacher in teachers.items():
        try:
            [fitness,nout,noffset,nassign,npen]=getProfessorFitness(teacher,classes,Courses,mode)
            teacherfile.write("%s,%s,%f,%d,%d,%d,%d,"%(CC,teacher[1],fitness,nout,noffset,nassign,npen))
            teacherhours=0
            for classkey in teacher[5]:
                teacherhours+=np.sum(classes[classkey][-1])
            teacherfile.write("%d,%d,%d"%(teacherhours,teacher[6],teacher[8]))
            for classkey in teacher[5]:
                teacherfile.write(",%s (%d)"%(classkey,classes[classkey][1]))
            teacherfile.write("\n")
        except:
            [fitness,norphan]=getProfessorFitness(teacher,classes,Courses,mode)
            teacherfile.write("%s,%d,%d"%(teacher[0],fitness,norphan))
            for classkey in teacher[5]:
                teacherfile.write(",%s"%(classkey))
            teacherfile.write("\n")
            pass
            

    teacherfile.close()
        

            