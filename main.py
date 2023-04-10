# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:40:52 2019

@author: miguelurla
"""
import numpy as np
import copy
import optimization as op
import multiprocessing as mp

if __name__ == '__main__':
    # We first set the mode in which we will calculate the fitness
    # mode 0: we check the specific courses
    # mode 1: we check the total number of hours
    mode=1
    
##################################################
#######      JUST THE INITIALIZATION
#
    [teachers, Classes, Courses]=op.initialize(mode)
    # We get the initial fitnesses
    fitnesses=op.getFitnesses(teachers)

#################################################
    ########### SERIAL PROGRAMMING

#    nproc=1
#    Nsteps=20000
#    l=3
#    seeds=np.arange(nproc)
#    seeds=[33]
#    results=[]
#    for seed in seeds:
#        results.append(op.minimizeFitness(seed,l,Nsteps,mode))
###
    ###########################################
    ### PARALLEL

    # ls=[1,3,5,7,9]
    # for l in ls:
    #     nproc=200 # number of optimization processes
    #     Nsteps=50000
    #     results=op.optparallel(nproc,l,Nsteps,mode)

    #     ###############################
    #     ######## ANALIZING THE RESULS
    #     bestfitness=1e6
    #     for result in results:
    #         if np.sum(result[0])<bestfitness:
    #             bestfitness=np.sum(result[0])
    #             teachers=copy.deepcopy(result[1])
    #             Classes=copy.deepcopy(result[2])
    #             Courses=copy.deepcopy(result[3])
    #             bestfitnesses=copy.deepcopy(result[0])
    #             bestseed=result[4]
    #             print("New best is %d"%bestfitness)
       
    #     ########### printing
    #     op.exportResults(teachers,Classes,Courses,bestseed,l,mode)