# simple introduction

## 文件简介

直接从 SPLC_MOIP 复制来的文件（或已简单修改）：cwmoipSol, dimacsMoipProb, moipProb, moipSol, mooUtility, naiveSol, 
ncgopSol, normalConstraint

config 是工程的设置文件，里边包含各种全局变量。

altSol 里边是单线程最简洁版本的 cwmoipSol 和 naiveSol 用于研究问题出在哪。

entrance 是工程的入口，用于设定运行计划。

loaders 是所有数据集的封装，用于载入数据提供给 NRP

NRP 定义了 Next Release Problem，类似于 MOIPProblem。使用 loaders 载入不同的数据集，并根据需求将问题建模成某个单目标问题或者双目标问题，并将NRP转化成其他 solver 可以使用的问题形式，包括：MOIPProblem(used in SPLC_MOIP)、jMetal Problem 以及直接返回原始数据（所谓'searchSol'）

JNRP 是 jMetal 问题的定义形式，由 NRP 调用。

solvers 是所有 Solver 的封装。

searchSol 是直接基于空间搜索的adhoc算法，还没完成，只是写着玩。

analyzer 是结果分析类，负责处理结果，得出分数、pareto front。

runner 是实验控制类，负责处理 entrance 传入的设定，控制载入某一数据集、建模、solver 调用、求解、计时等，不负责结果分析。

## 数据流动

实验控制流程在 runner 中。数据集由 NRP 使用 loader 载入，根据 'form' （single/binary）和 'method' （选择求解方法）进行建模，得到相应的问题。然后 runner 根据相应的 method 以及可能需要的参数 option，使用 Solver 创建相应的 solver，并将问题载入进 solver。
最后，调用 run 进行求解并计时，得到解集，将除解集外所有信息存入 checklist.json ，解集存入相应的配置文件夹中。

后续分析需要调用 analyzer 中的 Comparator，它将根据数据集把运行比较并存入 comparison.json。


## 类

TODO: 