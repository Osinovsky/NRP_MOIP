# ################################## #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# altSol.py, created: 2020.10.15     #
# Last Modified: 2020.10.15          #
# ################################## #

import math
import numpy as np
import cplex
from cplex import Cplex
from moipSol import CplexSolResult
from mooUtility import MOOUtility
from decimal import Decimal
# from time import clock
# import json

# re construct cwmoip without any heritage class
class CwmoipSol:
    # initialize
    def __init__(self, problem):
        #instance variable: the solution set found by solver 
        self.cplexSolutionSet = []
        #instance variable: the solution map, the key is the solution obj values, the value is the solution 
        self.cplexResultMap = {}
        #instance variable: the map of the solutions in the pareto front  
        self.cplexParetoSet = {}
        # problem
        self.problem = problem
        # solver 
        self.solver = Cplex()
        # boundary solver
        self.boundary_solver = Cplex()
        # record solving time
        # self.record = dict()
        # self.record['boundary solve'] = 0
        # self.record['solve'] = 0

    # solve the boundary
    def caliper(self, objective, var_len):
        # assume constraints are all ready
        # but objective constraints not add yet
        self.boundary_solver.objective.set_name("boundary")
        assert var_len == len(objective)
        self.boundary_solver.objective.set_linear(zip(list(range(var_len)), objective))
        # solve lower bound
        self.boundary_solver.objective.set_sense(self.boundary_solver.objective.sense.minimize)
        self.boundary_solver.solve()
        # self.record['boundary solve'] += 1
        low = self.boundary_solver.solution.get_objective_value()
        # solve upper bound
        self.boundary_solver.objective.set_sense(self.boundary_solver.objective.sense.maximize)
        self.boundary_solver.solve()
        up = self.boundary_solver.solution.get_objective_value()
        # return
        return (low, up)

    # prepare, put all constraints into solvers
    def prepare(self):
        # solver
        self.solver.set_results_stream(None)
        self.solver.set_warning_stream(None)
        self.solver.set_error_stream(None)
        self.solver.parameters.threads.set(1)
        self.solver.parameters.parallel.set(1)
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        # boundary solver
        self.boundary_solver.set_results_stream(None)
        self.boundary_solver.set_warning_stream(None)
        self.boundary_solver.set_error_stream(None)
        self.boundary_solver.parameters.threads.set(1)
        self.boundary_solver.parameters.parallel.set(1)
        self.boundary_solver.objective.set_sense(self.boundary_solver.objective.sense.minimize)
        # add variables
        vars_num = self.problem.featureCount
        types = ['B'] * vars_num
        variables = ['x'+str(i) for i in range(vars_num)]
        self.solver.variables.add(obj=None, lb=None, ub=None, types=types, names=variables)
        self.boundary_solver.variables.add(obj=None, lb=None, ub=None, types=types, names=variables)
        # add constraints
        counter = 0
        for ineqlDic in self.problem.sparseInequationsMapList:
            rows = []
            vari = []
            coef = []
            rs = ineqlDic[vars_num]
            for key in ineqlDic: 
                if key != vars_num:
                    vari.append('x'+str(key))
                    coef.append(ineqlDic[key])
            rows.append([vari, coef])
            self.solver.linear_constraints.add(lin_expr=rows, senses='L', rhs=[rs], names=['c'+str(counter)])
            self.boundary_solver.linear_constraints.add(lin_expr=rows, senses='L', rhs=[rs], names=['c'+str(counter)])
            counter += 1

    # copied from moipSol
    def addTocplexSolutionSetMap(self, cplexResults):
        if(cplexResults.getResultID() in self.cplexResultMap.keys()): 
            return
        self.cplexSolutionSet.append(cplexResults)
        self.cplexResultMap[cplexResults.getResultID()] = cplexResults

    # copied from original cwmoipSol
    def getMaxForObjKonMe(self, objIn,solutions):
        values = [float("-inf")]
        array1 = np.array(objIn)
        for key in solutions:
            newSol= solutions[key]
            array2 = np.array(newSol)
            values.append(float(np.dot(array1,array2)))
        result = MOOUtility.round(max(values))
        return result - 1
    
    # copied from moipSol
    def buildCplexPareto(self):
        inputPoints = [list(map(float,resultID.split('_'))) for resultID in self.cplexResultMap.keys()]
        #debugging purpose
        #print (inputPoints)
        if(len(inputPoints)==0):
            self.cplexParetoSet = []
        else: 
            paretoPoints, dominatedPoints = MOOUtility.simple_cull(inputPoints,MOOUtility.dominates)
            #print ("Pareto size: ", len(paretoPoints), " Pareto front: ",  paretoPoints)
            self.cplexParetoSet = paretoPoints
        
    # execute
    def execute(self):
        # prepare attribute and variable num
        attribute = self.problem.attributeMatrix
        attribute_np = np.array(attribute)
        var_len = len(attribute[0])
        # boundary of second objective
        low, up = self.caliper(attribute[1], var_len)
        w = Decimal(1.0)/Decimal(MOOUtility.round(up - low + 1.0))
        only_objective = attribute_np[0] +  float(w) * attribute_np[1]
        self.solver.objective.set_linear(zip(list(range(var_len)), only_objective.tolist()))
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        self.solver.objective.set_name("only_obj")
        # add second objective constraint
        objective = attribute[1]
        rows = []
        variables = []
        coefficient = []
        for index in range(var_len):
            variables.append('x' + str(index))
            coefficient.append(objective[index])
        rows.append([variables, coefficient])
        constraint_name = 'second_obj'
        self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [up], names = [constraint_name])
        # solve
        l = math.ceil(up)
        while True:
            if l < low:
                break
            self.solver.linear_constraints.set_rhs(constraint_name, l)
            # start_clock = clock()
            self.solver.solve()
            # self.record['solve'] += 1
            # self.record[l] = clock()-start_clock
            status = self.solver.solution.get_status_string()
            if status.find("optimal") >= 0:
                result_variables = self.solver.solution.get_values()
                cplex_result = CplexSolResult(result_variables, status, self.problem)
                self.addTocplexSolutionSetMap(cplex_result)
                l = self.getMaxForObjKonMe(objective, {cplex_result.getResultID():result_variables})
            else:
                break
        # end while
        self.buildCplexPareto()

        # fout = open('cwmoip.json', 'w+')
        # json_object = json.dumps(self.record, indent=4)
        # fout.write(json_object)
        # fout.close()

class NaiveSol:
    # initialize
    def __init__(self, problem):
        #instance variable: the solution set found by solver 
        self.cplexSolutionSet = []
        #instance variable: the solution map, the key is the solution obj values, the value is the solution 
        self.cplexResultMap = {}
        #instance variable: the map of the solutions in the pareto front  
        self.cplexParetoSet = {}
        # problem
        self.problem = problem
        # solver 
        self.solver = Cplex()
        # # record
        # self.record = dict()
        # self.record['solve'] = 0

    # prepare, put all constraints into solvers
    def prepare(self):
        # solver
        self.solver.set_results_stream(None)
        self.solver.set_warning_stream(None)
        self.solver.set_error_stream(None)
        self.solver.parameters.threads.set(1)
        self.solver.parameters.parallel.set(1)
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        # add variables
        vars_num = self.problem.featureCount
        types = ['B'] * vars_num
        variables = ['x'+str(i) for i in range(vars_num)]
        self.solver.variables.add(obj=None, lb=None, ub=None, types=types, names=variables)
        # add constraints
        counter = 0
        for ineqlDic in self.problem.sparseInequationsMapList:
            rows = []
            vari = []
            coef = []
            rs = ineqlDic[vars_num]
            for key in ineqlDic: 
                if key != vars_num:
                    vari.append('x'+str(key))
                    coef.append(ineqlDic[key])
            rows.append([vari, coef])
            self.solver.linear_constraints.add(lin_expr=rows, senses='L', rhs=[rs], names=['c'+str(counter)])
            counter += 1

    # copied from moipSol
    def addTocplexSolutionSetMap(self, cplexResults):
        if(cplexResults.getResultID() in self.cplexResultMap.keys()): 
            return
        self.cplexSolutionSet.append(cplexResults)
        self.cplexResultMap[cplexResults.getResultID()] = cplexResults

    # calculate ub lb
    def calculteUBLB(self,obj):
        ub = 0.0
        lb = 0.0
        for value in obj:
            if value > 0:
                ub = ub+ value
            else:
                lb = lb + value
        return lb, ub
    
    # copied from moipSol
    def buildCplexPareto(self):
        inputPoints = [list(map(float,resultID.split('_'))) for resultID in self.cplexResultMap.keys()]
        #debugging purpose
        #print (inputPoints)
        if(len(inputPoints)==0):
            self.cplexParetoSet = []
        else: 
            paretoPoints, dominatedPoints = MOOUtility.simple_cull(inputPoints,MOOUtility.dominates)
            #print ("Pareto size: ", len(paretoPoints), " Pareto front: ",  paretoPoints)
            self.cplexParetoSet = paretoPoints
        
    # execute
    def execute(self):
        # prepare attribute and variable num
        attribute = self.problem.attributeMatrix
        attribute_np = np.array(attribute)
        var_len = len(attribute[0])
        # boundary of second objective
        low, up = self.calculteUBLB(attribute[1])
        w = Decimal(1.0)/Decimal(MOOUtility.round(up - low + 1.0))
        only_objective = attribute_np[0]
        self.solver.objective.set_linear(zip(list(range(var_len)), only_objective.tolist()))
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        self.solver.objective.set_name("only_obj")
        # add second objective constraint
        objective = attribute[1]
        rows = []
        variables = []
        coefficient = []
        for index in range(var_len):
            variables.append('x' + str(index))
            coefficient.append(objective[index])
        rows.append([variables, coefficient])
        constraint_name = 'second_obj'
        self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [up], names = [constraint_name])
        # solve
        up_relaxed = math.ceil(up)
        low_relaxed = math.floor(low)
        for l in range(up_relaxed, low_relaxed-1, -1):
            self.solver.linear_constraints.set_rhs(constraint_name, l)
            # start_clock = clock()
            self.solver.solve()
            # self.record['solve'] += 1
            # self.record[l] = clock()-start_clock
            status = self.solver.solution.get_status_string()
            if status.find("optimal") >= 0:
                result_variables = self.solver.solution.get_values()
                cplex_result = CplexSolResult(result_variables, status, self.problem)
                self.addTocplexSolutionSetMap(cplex_result)
            else:
                break
        # end while
        self.buildCplexPareto()

        # fout = open('epsilon.json', 'w+')
        # json_object = json.dumps(self.record, indent=4)
        # fout.write(json_object)
        # fout.close()