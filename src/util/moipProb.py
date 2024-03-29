# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 11:30:04 2018

@author: Yinxing Xue
"""
import re

class MOIPProblem():
    'define the problem of a MOBIP'
    
    def __init__(self, objCount, varCount, attrCount):
        
        self.objectiveCount = 0 
        self.featureCount = 0 
        self.attributeCount = 0
    
        self.objectNames = {}
        self.featureNames = {}
        self.attributeNames = {}
        """
        each sparse map is to represent one objectives, and use the list to store all the objectives maps
        """
        self.objectiveSparseMapList = [] 
    
        """
        each sparse map is to represent one constraint in inequation, and use the list to store all the inequation constraints
        """
        self.sparseInequationsMapList = [] 
        
        """
        each item in the list is the operation for the corrpesonding constraint in the self.sparseInequationsMapList
        """
        self.sparseInequationSensesList =[]
    
        """
        each sparse map is to represent one constraint in equation, and use the list to store all the equation constraints
        """
        self.sparseEquationsMapList = []
    
        self.attributeMatrix = [[]]
        self.objectiveCount = objCount
        self.featureCount = varCount
        self.attributeCount = attrCount
    
    def displayObjectiveCount(self):
        print ("Total Objectives Num: %d" % self.objectiveCount)
    
    def displayFeatureCount(self):
        print ("Total Variables Num: %d" % self.featureCount) 
     
    def displayAttributeCount(self):
        print ("Total Attributes Num: %d" % self.attributeCount) 
        
    def displayObjectives(self):
        print ("Objectives : %s" % self.objectNames)
    
    def displayVariableNames(self):
        print ("Variables : %s" % self.featureNames)
    
    def displayObjectiveSparseMapList(self):
        print ("Objectives in sparse map: %s" % self.objectiveSparseMapList)
        
    def displaySparseInequationsMapList(self):
        print ("Inequality constraints in sparse map: %s" % self.sparseInequationsMapList)
    
    def displaySparseInequationSenseList(self):
        print ("Inequality constraints Senses in list: %s" % self.sparseInequationSensesList)
        
    def displaySparseEquationsMapList(self):
        print ("Equality constraints in sparse map: %s" % self.sparseEquationsMapList)
        
    def displayAttributeMatrix(self):
        print ("Attribute objs in matrix: %s" % self.attributeMatrix)     
        
    def load(self,objectives, sparseInequations, sparseEquations, deriveObjective = False, attributeMatrix = None): 
        if isinstance(objectives, list) : 
            if isinstance(objectives[0], dict) : 
                #the input file objectives is sparse
                self.objectiveSparseMapList = objectives
        if isinstance(sparseInequations, list) : 
            if isinstance(sparseInequations[0], dict) : 
                #the input file sparseInequations is sparse
                self.sparseInequationsMapList = sparseInequations
        if isinstance(sparseEquations, list) : 
            if isinstance(sparseEquations[0], dict) : 
                #the input file sparseEquations is sparse
                self.sparseEquationsMapList = sparseEquations
        if deriveObjective == True:                 
            self.attributeMatrix= [[ 0 for i in range(self.attributeCount) ] for j in range(self.featureCount)]
        
    def exetractFromFile(self,path):
        mode = "";
        objCount=0;
        varCount=0;
        trim= lambda x: x.replace(' ','')
        with open(path) as f:
            line = f.readline()
            while line:
                if line.startswith("objectives =="):
                    mode = "obj"
                elif  line.startswith("variables =="):
                    mode = "var"
                elif  line.startswith("Inequations =="):
                    mode = "ineql"
                elif  line.startswith("Equations =="):
                    mode = "eql"
                elif line == "" or line == "\n":
                    mode = ""
                else:
                    if mode == "obj":
                        #read the objective names
                        strText= line.replace("\n", "")
                        results = strText.split(';')
                        self.objectNames = [trim(x) for x in results]
                        objCount = len(self.objectNames)
                        self.objectiveSparseMapList = []
                        for i in range(0,objCount):
                            line = f.readline()
                            valueString = line.replace("\n", "")
                            valueString = valueString.replace("[", "")
                            valueString = valueString.replace("]", "")
                            values = valueString.split(';')
                            trimvalues = [trim(x) for x in values]
                            newDict={}
                            for j in range(0,len(trimvalues)): 
                                newDict[j] = float(trimvalues[j]) 
                            self.objectiveSparseMapList.append(newDict)
                    elif mode == "var":
                        #read variable or feature names
                        self.featureNames={}
                        feaString = line.replace("\n", "")
                        feaString = feaString.replace("{", "")
                        feaString = feaString.replace("}", "")
                        features = feaString.split(',')
                        trimFeatures = [trim(x) for x in features]
                        for feature in trimFeatures:
                            varKey = feature.split('=')
                            key = int(varKey[1])
                            self.featureNames[key] = varKey[0]
                        varCount=len(trimFeatures)
                    elif mode == "ineql":
                        #read Inequations constraints in sparse maps
                        self.sparseInequationsMapList=[]
                        reGroupTestStr = line 
                        ineqls = re.findall("{(.+?)}", reGroupTestStr)
                        for ineql in ineqls: 
                            pairs = ineql.split(',')
                            trimPairs = [trim(x) for x in pairs]
                            ineqlDict={}
                            for trimPair in trimPairs:
                                varKey = trimPair.split('=')
                                key = int(varKey[0])
                                ineqlDict[key] = float(varKey[1])
                            self.sparseInequationsMapList.append(ineqlDict)
                    elif mode == "eql":
                        #read Equations constraints in sparse maps
                        self.sparseEquationsMapList=[]
                        reGroupTestStr = line 
                        eqls = re.findall("{(.+?)}", reGroupTestStr)
                        for eql in eqls: 
                            pairs = eql.split(',')
                            trimPairs = [trim(x) for x in pairs]
                            eqlDict={}
                            for trimPair in trimPairs:
                                varKey = trimPair.split('=')
                                key = int(varKey[0])
                                eqlDict[key] = float(varKey[1])
                            self.sparseEquationsMapList.append(eqlDict)
                line = f.readline()
                
        self.attributeMatrix =self.__private_convertDenseLise__(self.objectiveSparseMapList)
        if  objCount != self.objectiveCount or varCount!= self.featureCount:
            raise Exception('input not consistent', 'eggs')
        self.reOrderObjsByRange()
        return      
    
    def reOrderObjsByRange(self):
        objRangeMap = {}
        for k in range(0,len(self.attributeMatrix)):
            kthObj= self.attributeMatrix[k]
            ub,lb = self.__private_calculteUBLB__(kthObj)
            objRange = ub - lb 
            objRangeMap[k] = objRange
        #find the objective with the largest range
        maxRange =  max(zip(objRangeMap.values(),objRangeMap.keys()))
        #debug purpose
        #print (maxRange)
        #the objective with the largest range is at index targetPos
        targetPos = maxRange[1]
        #now need to swap the first and targetPos-th element 
        temp = self.objectNames[0]
        self.objectNames[0] = self.objectNames[targetPos]
        self.objectNames[targetPos] = temp 
        temp = self.objectiveSparseMapList[0]
        self.objectiveSparseMapList[0] = self.objectiveSparseMapList[targetPos]
        self.objectiveSparseMapList[targetPos] = temp 
        temp = self.attributeMatrix[0]
        self.attributeMatrix[0] = self.attributeMatrix[targetPos]
        self.attributeMatrix[targetPos] = temp     

    def convertInequation2LeConstr(self):
        """converting the inequations in  sparseInequationsMapList in the format of LE (less or equal than) inequations
         the method is necessary for using CWMOIP and RepSol
         
         For example,   x_1 - 2* x_2 >= 1   get_rows:  {0:1, 1: -2, 2: 1}, the corresponding operator is "G" in  sparseInequationSensesList,
         and it will be {0:-1, 1:  2, 2: -1} with the corresponding operator "L" in sparseInequationSensesList
         
         Args: None 
         
         Returns: the list of indexes that have been converted in the sparseInequationsMapList
         
         Raises: Exception
        """ 
        counter=0
        changeList = []
        for operator in self.sparseInequationSensesList:
            if operator=='G': 
                inequaltion=  self.sparseInequationsMapList[counter] 
                inequaltion.update({n: -1 * inequaltion[n] for n in inequaltion.keys()})
                changeList.append(counter)
                counter+=1
            elif operator=='L':
                counter+=1
                continue                
            else:
                raise Exception('Unexpected Operator:'+operator, "")
                os._exit(-1) 
        self.sparseInequationSensesList = ['L']* len(self.sparseInequationsMapList)
        return changeList
        
    def __private_calculteUBLB__(self,obj):
        ub = 0.0
        lb = 0.0
        for value in obj:
            if value > 0:
                ub = ub+ value
            else:
                lb = lb + value
        return ub, lb    
        
    def __private_convertDenseLise__(self,objectiveSparseMapList):
        listLength = len(objectiveSparseMapList)
        matrix =  [[] for i in range(listLength)]
        for i in range(listLength):
            dictionary = objectiveSparseMapList[i]
            matrix[i] = [0.0]* len(dictionary)
            for key in dictionary:
                matrix[i][key]=dictionary[key]
        return matrix
    
if __name__ == "__main__":
    prob = MOIPProblem(4,43,3)  
    prob.displayObjectiveCount()
    prob.displayFeatureCount()
    prob.exetractFromFile("../test/parameter_wp1.txt")
    prob.displayObjectives()
    prob.displayVariableNames()
    prob.displayObjectiveSparseMapList()
    prob.displaySparseInequationsMapList()
    prob.displaySparseInequationSenseList()
    prob.displaySparseEquationsMapList()
    prob.displayAttributeMatrix()
else:
    pass
    # print("moipProb.py is being imported into another module")