from src import NextReleaseProblem
from src.Solvers import QuantumAnnealing
# from src.Solvers.BaseSolver import BaseSolver


problem = NextReleaseProblem('classic_1')
problem.premodel({})
# nrp = problem.model('bireq', {})
nrp = problem.model('binary', {})

profit = nrp.objectives[0]
cost = nrp.objectives[1]
W = int(sum(cost.values())/2)

qa = QuantumAnnealing(nrp)
qa.prepare()
qa.quadratic.set_bireq_W(W)
print(len(qa.quadratic.variables))
qa.execute()

# cp = BaseSolver(nrp)
# cp.add_constriant('cst', {k: c for k, c in cost.items()})
# cp.set_objective(profit, True)
# cp.set_rhs('cst', W)
# cp.solve()
# print(cp.get_objective_value())

# classic_1
# qa: 192.53 ms, 2817, (total 489s, from call sapi to recived solution)
# cp: 55.97 ms, 4185

# classic_2
# cannot handle
