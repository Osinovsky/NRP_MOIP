# ################################## #
# mainly from SPLC, yinxing xue      #
# DONG Shi, dongshi@mail.ustc.edu.cn #
# naiveSol.py, created: 2020.10.23   #
# Last Modified: 2020.10.23          #
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

    # recusively execute
    def recuse(self, level, low, up):
        if level == 0:
            # solve
            # start_clock = clock()
            self.solver.solve()
            # self.record['solve'] += 1
            # self.record[l] = clock()-start_clock
            status = self.solver.solution.get_status_string()
            if status.find("optimal") >= 0:
                # process solutions
                result_variables = self.solver.solution.get_values()
                cplex_result = CplexSolResult(result_variables, status, self.problem)
                self.addTocplexSolutionSetMap(cplex_result)
                return {cplex_result.getResultID():result_variables}
            else:
                return dict()
        else:
            # prepare all solutions set
            all_solutions = dict()
            # get the up and low bound
            relaxed_up = math.ceil(up[level])
            relaxed_low = math.ceil(low[level])
            constraint_name = 'obj_' + str(level)
            for l in range(relaxed_up, relaxed_low-1, -1):
                # update rhs
                self.solver.linear_constraints.set_rhs(constraint_name, l)
                solutions = self.recuse(level-1, low, up)
                all_solutions = {**all_solutions, **solutions}
            # end for
            return all_solutions
    
    # execute
    def execute(self):
        # prepare attribute and variable num
        attribute = self.problem.attributeMatrix
        attribute_np = np.array(attribute)
        k = len(attribute)
        var_len = len(attribute[0])
        # boundary of other boundays
        low = [.0] * k
        up = [.0] * k
        for i in range(1, k):
            low[i], up[i] = self.calculteUBLB(attribute[i])
        # prepare the objective
        only_objective = attribute_np[0]
        self.solver.objective.set_linear(zip(list(range(var_len)), only_objective.tolist()))
        self.solver.objective.set_sense(self.solver.objective.sense.minimize)
        self.solver.objective.set_name("only_obj")
        # add other objectives constraints
        for i in range(1, k):
            objective = attribute[i]
            rows = []
            variables = []
            coefficient = []
            for index in range(var_len):
                variables.append('x' + str(index))
                coefficient.append(objective[index])
            rows.append([variables, coefficient])
            constraint_name = 'obj_' + str(i)
            self.solver.linear_constraints.add(lin_expr = rows, senses = 'L', rhs = [up[i]], names = [constraint_name])
        # solve
        self.recuse(k-1, low, up)
        # end while
        self.buildCplexPareto()

        # fout = open('epsilon.json', 'w+')
        # json_object = json.dumps(self.record, indent=4)
        # fout.write(json_object)
        # fout.close()
