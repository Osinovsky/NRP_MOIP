# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 15:42:17 2018

@author: Yinxing Xue
"""
import sys
import os
import math
import numpy as np
import json
from dimacsMoipProb import DimacsMOIPProblem 
from moipSol import BaseSol
from naiveSol import NaiveSol
from moipSol import CplexSolResult
from mooUtility import MOOUtility
from decimal import Decimal
 

class CwmoipSol(NaiveSol):  
    'define the CWMOIP solution of a MOBIP'
    def __init__(self, moipProblem):  
        #override parent initializer  
        NaiveSol.__init__(self,moipProblem)  
        #each sparse map is to represent extra constraints in inequation, and use the list to store all the inequation constraints
        self.sparseInequationsMapList = [] 
        #each sparse map is to represent extra constraints in inequation, and use the list to store all the equation constraints
        self.sparseEquationsMapList = [] 
        #the variable to record the original objective
        self.oriObj = None
        # record objective index mapping to constraint name
        self.objective_constraint = dict()
        # DEBUG VARIABLES
        self.record = dict()
        self.record['solve'] = 0
        self.record['boundary solve'] = 0
       
    """
    model the problem as a single objective problem, and preparation solver for this
    override the parent method
    """
    def _prepare(self):
        BaseSol.prepare(self)
        objName = self.solver.objective.get_name()
        linearCoeff = self.solver.objective.get_linear()
        objSense = self.solver.objective.get_sense()
        self.oriObj = (objName,linearCoeff,objSense)
        
    #override the parent method 
    def _execute(self):    
        k = len(self.moipProblem.attributeMatrix)
        solutionMap={}
        #swap the 3rd and 4th obj for testing purpose
        #temp = self.moipProblem.attributeMatrix[2]
        #self.moipProblem.attributeMatrix[2] =  self.moipProblem.attributeMatrix[3] 
        #self.moipProblem.attributeMatrix[3] = temp
        objMatrix = np.array(self.moipProblem.attributeMatrix)
        solutionMap = self.solveBySingleObj(self.sparseInequationsMapList,self.sparseEquationsMapList, objMatrix, objMatrix,k, solutionMap, self.cplexResultMap)
        self.buildCplexPareto()
        # dump self.record
        fin = open('cwmoip.json', 'w+')
        json_object = json.dumps(self.record, indent = 4)
        fin.write(json_object)
        fin.close()
        
    def solveBySingleObj(self, inequationsMapList,equationsMapList,  objMatIn, objMatOut,k, solutionMap, resultMap):
        solutionMapOut = {}
        lbs= np.zeros((1,self.moipProblem.featureCount))
        ubs= np.ones((1,self.moipProblem.featureCount))
        feasibleFlag = False
        if k == 1 :
            # The single-objective problem
            (rsltObj,rsltXvar,rsltSolString)=  self.intlinprog (objMatOut[k-1],inequationsMapList,equationsMapList,lbs,ubs)
            #check whether it is optimal
            if(rsltSolString.find("optimal")>=0):
                cplexResults = CplexSolResult(rsltXvar,rsltSolString,self.moipProblem)
                self.addTocplexSolutionSetMap(cplexResults)
                solutionMapOut[cplexResults.getResultID()] = rsltXvar
        else: 
            fGUB=np.zeros(k)
            fGLB=np.zeros(k)
            fRange=np.zeros(k)
            w= Decimal(1.0)
            for i in range(0,k):
                feasibleFlag= True 
                (rsltObj,rsltXvar,rsltString) = self.intlinprog (objMatOut[i],inequationsMapList,equationsMapList,lbs,ubs)   
                self.record['bound solve'] += 1
                if (rsltString.find("optimal")>=0):
                    fGLB[i] = 1.0* MOOUtility.round(rsltObj)
                    objOutNeg =  objMatOut[i] * (-1)
                    rslt2Obj,rslt2Xvar,rslt2String= self.intlinprog(objOutNeg,inequationsMapList,equationsMapList,lbs,ubs)
                    self.record['bound solve'] += 1
                    fGUB[i] = -1.0 * MOOUtility.round(rslt2Obj)
                    fRange[i] = fGUB[i]-fGLB[i] +1
                    w =  w*  MOOUtility.round(fRange[i])
                else:
                    feasibleFlag=False
                    break
                #end of if-esle
            #end of for
            if (feasibleFlag==True):
                w = Decimal(1)/ w
                w =float(w)
                l = fGUB[k-1]
                #shallow copy 
                new_inequationsMapList = list(inequationsMapList)
                new_equationsMapList= list(equationsMapList)
                while True:
                    # Step 1: Solve the CW(k-1)OIP problem with l  
                    solutions = []
                    objMat_out1 =np.zeros((k-1,self.moipProblem.featureCount))
                    for i in range(0,k-1):
                        objMat_out1[i]= objMatOut[i]+ w*objMatOut[k-1]
                    lastConstr = {}
                    if len(new_inequationsMapList) > 0:
                        lastConstr = new_inequationsMapList[len(new_inequationsMapList)-1]
                    if len(inequationsMapList)> 0 and MOOUtility.arrayEqual(lastConstr,objMatIn[k-1]):
                        lastConstr[self.moipProblem.featureCount]= l
                    else:
                        #add the new constraint to new_inequationsMapList
                        self.addNewConstrToInequationsMapList(new_inequationsMapList,objMatIn[k-1],l )
                    solutions = self.solveBySingleObj(new_inequationsMapList,new_equationsMapList, objMatIn, objMat_out1,k-1,solutionMap, resultMap)
                    if  len(solutions)  ==0:
                        break
                    else:
                        #Step 2: put ME into E, find the new l
                        solutionMap= {**solutionMap,**solutions}
                        solutionMapOut = {**solutionMapOut,**solutions}
                        l = self.getMaxForObjKonMe(objMatIn[k-1],solutions)
                        if str(k) not in self.record:
                            self.record[str(k)] = [l]
                        else:
                            self.record[str(k)].append(l)
                        lastConstr = new_inequationsMapList[len(new_inequationsMapList)-1]
                        lastConstr[self.moipProblem.featureCount]= l
               #end of while
            #end of if
        return solutionMapOut
    
    
    def addNewConstrToInequationsMapList(self, inequationsMapList,objIn,l ):
        newInequation = {}
        for i in range(0,len(objIn)):
            newInequation[i] = objIn[i]
        newInequation[len(objIn)] = l
        inequationsMapList.append(newInequation)
        return 
    
    def getMaxForObjKonMe(self, objIn,solutions):
        maxVal = float("-inf")
        for key in solutions:
            newSol= solutions[key]
            #newSol= map(int,solutions[key])
            array1 = np.array(objIn)
            array2 = np.array(newSol)
            solSum = np.dot(array1,array2) 
            if(solSum> maxVal):
               maxVal = solSum;
        result = MOOUtility.round(maxVal)
        result = result -1
        return result
    
    """             
    May not use lbs and ubs
    """
    def intlinprog(self,obj,inequationsMapList,equationsMapList,lbs,ubs):
        variableCount = self.moipProblem.featureCount
        constCounter = 0 
        tempConstrList = []
        #add the temp inequation constraints to the solver
        for ineqlDic in inequationsMapList:
            rows = []
            rs = float("-inf")
            variables = []
            coefficient = []
            for key in ineqlDic: 
                if key != variableCount:
                    variables.append('x'+str(key))
                    coefficient.append(int(ineqlDic[key])) # NOTE: I change numpy.int32 to int, cause it made cplex panic
                else: 
                    rs = ineqlDic[key]
            row=[]
            row.append(variables)
            row.append(coefficient)
            rows.append(row)       
            constCounter= constCounter+1
            constName= 'new_c'+str(constCounter)
            indices = self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [rs], names = [constName] )
            tempConstrList.append(constName)
        #add the temp equation constraints to the solver
        for eqlDic in equationsMapList:
            rows = []
            rs = float("-inf")
            variables = []
            coefficient = []
            for key in eqlDic: 
                if key != variableCount:
                    variables.append('x'+str(key))
                    coefficient.append(eqlDic[key])
                else: 
                    rs = eqlDic[key]
            row=[]
            row.append(variables)
            row.append(coefficient)
            rows.append(row)       
            constCounter= constCounter+1
            constName= 'new_c'+str(constCounter)
            indices = self.solver.linear_constraints.add(lin_expr = rows, senses = 'E', rhs = [rs], names = [constName] )
            tempConstrList.append(constName)
        #reset the objective
        self.solver.objective.set_name("tempObj")
        coff= obj.tolist()
        indics= list(range(0,variableCount))
        self.solver.objective.set_linear(zip(indics,coff))
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        #solve the problem
        self.solveCounter += 1
        self.solver.solve()
        self.record['solve'] += 1
      
        rsltXvar = []
        rsltObj = float("+inf")
        rsltSolString = self.solver.solution.get_status_string()
        if(rsltSolString.find("optimal")>=0):
            #bug fixed here, rsltSol should not be returned as the constraints will be modified at the end of the method
            #rsltSol = self.solver.solution
            rsltXvar = self.solver.solution.get_values()
            rsltObj =  self.solver.solution.get_objective_value()
        #remove the temp constraints
        self.solver.linear_constraints.delete(tempConstrList)
        return (rsltObj,rsltXvar,rsltSolString)

    # solve the boundary
    def caliper(self, objective, var_len):
        # assume constraints are all ready
        # but objective constraints not add yet
        self.solver.objective.set_name("tempObj")
        assert var_len == len(objective)
        self.solver.objective.set_linear(zip(list(range(var_len)), objective))
        # solve lower bound
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        self.solver.solve()
        self.record['boundary solve'] += 1
        low = self.solver.solution.get_objective_value()
        # solve upper bound
        self.solver.objective.set_sense(self.solver.objective.sense.maximize)
        self.solver.solve()
        self.record['boundary solve'] += 1
        up = self.solver.solution.get_objective_value()
        # return
        return (low, up)

    # recursive cwmoip
    def recursive_cwmoip(self, obj_ind, objectives, up, pass_dict, all_solutions):
        solution_out = {}
        if obj_ind == 0:
            # touch the bottom
            self.updateSolver(pass_dict)
            self.solver.solve()
            self.record['solve'] += 1
            # check optimal
            status = self.solver.solution.get_status_string()
            if status.find("optimal") >= 0:
                result_variables = self.solver.solution.get_values()
                cplex_result = CplexSolResult(result_variables, status, self.moipProblem)
                self.addTocplexSolutionSetMap(cplex_result)
                solution_out[cplex_result.getResultID()] = result_variables
            return solution_out
        # end if
        l = up[obj_ind]
        while True:
            # Step 1: Solve the CW(k-1)OIP problem with l 
            pass_dict[self.objective_constraint[obj_ind]] = l
            solutions = self.recursive_cwmoip(obj_ind-1, objectives, up, pass_dict, all_solutions)
            pass_dict[self.objective_constraint[obj_ind]] = None
            # check if still got new solutions
            if len(solutions) == 0:
                break
            #Step 2: put solutions into all_soltuions, find the new l
            all_solutions = {**all_solutions, **solutions}
            solution_out = {**solution_out, **solutions}
            last_l = l
            l = self.getMaxForObjKonMe(objectives[obj_ind], solutions)
            assert l < last_l
        # end while
        return solution_out

    # another epsilon-like prepare
    def prepare(self):
        BaseSol.prepare(self)

    # another epsilon-like execute
    def execute(self):
        # prepare all I need
        attribute = self.moipProblem.attributeMatrix
        attribute_np = np.array(attribute)
        inequations = self.moipProblem.sparseInequationsMapList
        # objective num
        k = len(attribute)
        var_len = len(attribute[0])
        
        # calculate true boundary of each objective
        low = np.zeros(k)
        up = np.zeros(k)        
        for obj_ind in range(k):
            low[obj_ind], up[obj_ind] = self.caliper(attribute[obj_ind], var_len)
        # TODO: ordering objectives by their range
        # calculate w
        interval = up - low + 1
        w = [Decimal(1.0)/Decimal(MOOUtility.round(itv)) for itv in interval]
        
        # convert multi-objective problem into single-objetive one
        # # finnal objective = foldr l+w[ind]*r zeros(var_len) [o1, o2, ..., ok]
        # only_objective = attribute_np[k-1]
        # # obj_ind = k-1, k-2, ..., 1
        # for obj_ind in range(k-2, 0, -1):
        #     only_objective = attribute_np[obj_ind] + w[obj_ind+1] * only_objective
        # foldl try
        only_objective = attribute_np[0]
        for obj_ind in range(1, k):
            only_objective = only_objective + float(w[obj_ind]) * attribute_np[obj_ind]
        # set objective
        single_objective = only_objective.tolist()
        self.solver.objective.set_name("single_obj")
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        self.solver.objective.set_linear(zip(list(range(var_len)), single_objective))

        # convert each objective into constraint
        for obj_ind in range(1, k):
            objective = attribute[obj_ind]
            assert var_len == len(objective)
            rows = []
            variables = []
            coefficient = []
            for index in range(var_len):
                variables.append('x' + str(index))
                coefficient.append(objective[index])
            rows.append([variables, coefficient])
            # name the constraint
            # obj <= up
            constraint_name = 'o'+str(k)
            self.objective_constraint[obj_ind] = constraint_name
            self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [up[obj_ind]], names = [constraint_name])
        # end for

        # start cwmoip
        pass_dict = dict()
        solutions = {}
        self.recursive_cwmoip(k-1, attribute_np, up, pass_dict, solutions)
        self.buildCplexPareto()

        # record dump
        fin = open('cwmoip.json', 'w+')
        json_object = json.dumps(self.record, indent = 4)
        fin.write(json_object)
        fin.close()

if __name__ == "__main__":
    if len(sys.argv)!=2: 
        os._exit(0) 
    para = sys.argv[1]
    projectName = para 
    prob = DimacsMOIPProblem(projectName)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.displayObjectives()
    prob.displayVariableNames()
    prob.displayObjectiveSparseMapList()
    prob.displaySparseInequationsMapList()
    prob.displaySparseEquationsMapList()
    prob.displayAttributeMatrix()
    
         
    #moipInputFile = '../test/{goalNum}_input_{name}_{mode}.txt'.format(goalNum=problemGoalNum, name=projectName,mode=modelingMode)
    paretoOutputFile = '../result/MOIP/Pareto_{project}.txt'.format(project=projectName)
    #fullResultOutputFile = '../result/{goalNum}-obj/FullResult_{goalNum}_{name}_{mode}.txt'.format(goalNum=problemGoalNum, name=projectName,mode=modelingMode)
    sol= CwmoipSol(prob)
    sol.prepare()
    sol.execute()
    #sol.outputCplexParetoMap("../result/Pareto_js1.txt")
    DimacsMOIPProblem.convertRslt2OldFormat(sol.cplexParetoSet,prob.featureCount,paretoOutputFile)
    sol.displaySolvingAttempts()
    sol.displayObjsBoundsDictionary()
    sol.displayCplexSolutionSetSize()
    sol.displayCplexResultMap()
    sol.displayCplexParetoSet()
    sol.displayVariableLowerBound()
    sol.displayVariableUpperBound()
    sol.displayVariableTypes()
    sol.displayVariableNames()
 
else:
    print("cwmoipSol.py is being imported into another module")
