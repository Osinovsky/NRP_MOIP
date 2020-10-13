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
 

class CwmoipSol(BaseSol):  
    'define the CWMOIP solution of a MOBIP'
    def __init__(self, moipProblem):  
        #override parent initializer  
        BaseSol.__init__(self,moipProblem)  
        # record objective index mapping to constraint name
        # self.objective_constraint = dict()
        # DEBUG VARIABLES
        # self.record = dict()
        # self.record['solve'] = 0
        # self.record['boundary solve'] = 0

    def getMaxForObjKonMe(self, objIn,solutions):
        values = [float("-inf")]
        array1 = np.array(objIn)
        for key in solutions:
            newSol= solutions[key]
            array2 = np.array(newSol)
            values.append(float(np.dot(array1,array2)))
        result = MOOUtility.round(max(values))
        return result - 1

    def calculteUBLB(self,obj):
        ub = 0.0
        lb = 0.0
        for value in obj:
            if value > 0:
                ub = ub+ value
            else:
                lb = lb + value
        return lb, ub

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
        # self.record['boundary solve'] += 1
        low = self.solver.solution.get_objective_value()
        # solve upper bound
        self.solver.objective.set_sense(self.solver.objective.sense.maximize)
        self.solver.solve()
        # self.record['boundary solve'] += 1
        up = self.solver.solution.get_objective_value()
        # return
        return (low, up)

    # recursive cwmoip
    def recursive_cwmoip(self, obj_ind, objectives, up, pass_dict):
        solution_out = {}
        if obj_ind == 0:
            # touch the bottom
            self.updateSolver(pass_dict)
            self.solver.solve()
            # self.record['solve'] += 1
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
            solutions = self.recursive_cwmoip(obj_ind-1, objectives, up, pass_dict)
            # pass_dict[self.objective_constraint[obj_ind]] = None
            # check if still got new solutions
            if len(solutions) == 0:
                break
            #Step 2: put solutions into all_soltuions, find the new l
            solution_out = {**solution_out, **solutions}
            l = self.getMaxForObjKonMe(objectives[obj_ind], solutions)
        # end while
        return solution_out

    # another epsilon-like prepare
    def prepare(self):
        BaseSol.prepare(self)

    # another epsilon-like execute
    def _execute(self):
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
        # calculate w
        interval = up - low + 1
        w = [Decimal(1.0)/Decimal(MOOUtility.round(itv)) for itv in interval]
        
        # convert multi-objective problem into single-objetive one
        # foldl l+w[ind]*r zeros(var_len) [o1, o2, ..., ok]
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
        self.recursive_cwmoip(k-1, attribute_np, up, pass_dict)
        self.buildCplexPareto()

        # record dump
        # fin = open('cwmoip.json', 'w+')
        # json_object = json.dumps(self.record, indent = 4)
        # fin.write(json_object)
        # fin.close()

    def execute(self):
        # prepare all I need
        attribute = self.moipProblem.attributeMatrix
        attribute_np = np.array(attribute)
        # objective num
        var_len = len(attribute[0])
        # calculate true boundary of each objective
        # low = .0
        # up = .0
        # low, up = self.caliper(attribute[1], var_len)
        low, up = self.calculteUBLB(attribute[1])
        # calculate w
        # w = Decimal(1.0)/Decimal(MOOUtility.round(up - low + 1.0))
        # set objective
        # only_objective = attribute_np[0] +  float(w) * attribute_np[1]
        # single_objective = only_objective.tolist()
        # self.solver.objective.set_linear(zip(list(range(var_len)), single_objective))
        # self.solver.objective.set_name("single_obj")
        # self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        # add constriants
        objective = attribute[1]
        rows = []
        variables = []
        coefficient = []
        for index in range(var_len):
            variables.append('x' + str(index))
            coefficient.append(objective[index])
        rows.append([variables, coefficient])
        # name the constraint
        # obj <= up
        constraint_name = 'second_obj'
        self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [up], names = [constraint_name])

        # solving
        l = up
        while True:
            self.solver.linear_constraints.set_rhs(constraint_name, l)
            self.solver.solve()
            status = self.solver.solution.get_status_string()
            if status.find("optimal") >= 0:
                result_variables = self.solver.solution.get_values()
                cplex_result = CplexSolResult(result_variables, status, self.moipProblem)
                self.addTocplexSolutionSetMap(cplex_result)
                l = self.getMaxForObjKonMe(objective, {cplex_result.getResultID():result_variables})
            else:
                break
        # end while
        self.buildCplexPareto()

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
