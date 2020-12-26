from src.NRP import NRPProblem
from src.util.ObjectiveSpace import ObjectiveSpace3D


nrp = NRPProblem()
nrp.variables = list(range(10))
nrp.inequations = []

profit = [10, 3, 8, 9, 2, 5, 6, 1, 7, 4]
cost = [9, 4, 1, 5, 10, 7, 3, 2, 6, 8]
urgency = [3, 1, 0, -1, 4, -3, -4, 5, -2, 2]

nrp.objectives = [
    {k: -v for k, v in enumerate(profit)},
    {k: v-5 for k, v in enumerate(cost)},
    {k: -v for k, v in enumerate(urgency)}
]

space = ObjectiveSpace3D(nrp)
s, p = space.HR_sample()

# ps = []
# for _ in range(10):
#     s, p = space.HR_sample()
#     while not s:
#         s, p = space.HR_sample()
#     print(s, p)
#     ps.append(p)
# space.plot(ps)
